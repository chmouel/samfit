# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import fcntl
import requests
import tempfile
import time
import re
import html2text

import config


class TPSession(object):
    categories = []
    _obligatory_headers = {"Referer": "https://home.trainingpeaks.com/login"}
    _reauthAttempts = 1

    def __init__(self, username, password):
        self.username = username
        self.password = password
        rate_lock_path = tempfile.gettempdir() + "/tp_rate.localhost.lock"
        # Ensure the rate lock file exists (...the easy way)
        open(rate_lock_path, "a").close()
        self._rate_lock = open(rate_lock_path, "r+")

        self.session = None
        self.athlete_id = None

    def init(self):
        if self.session is None:
            self._get_session()

    def _request_with_reauth(self, req_lambda, email=None, password=None):
        for i in range(self._reauthAttempts + 1):
            session = self._get_session(email=email, password=password)
            self._rate_limit()
            result = req_lambda(session)
            if result.status_code not in (403, 500):
                return result
        return result

    def _rate_limit(self):
        min_period = 1
        fcntl.flock(self._rate_lock, fcntl.LOCK_EX)
        try:
            self._rate_lock.seek(0)
            last_req_start = self._rate_lock.read()
            if not last_req_start:
                last_req_start = 0
            else:
                last_req_start = float(last_req_start)

            wait_time = max(0, min_period - (time.time() - last_req_start))
            time.sleep(wait_time)

            self._rate_lock.seek(0)
            self._rate_lock.write(str(time.time()))
            self._rate_lock.flush()
        finally:
            fcntl.flock(self._rate_lock, fcntl.LOCK_UN)

    def _get_session(self):
        session = requests.Session()
        data = {
            "Username": self.username,
            "Password": self.password,
        }
        params = {}
        preResp = session.get(
            "https://home.trainingpeaks.com/login", params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" % (preResp.status_code,
                                                          preResp.text))

        ssoResp = session.post(
            "https://home.trainingpeaks.com/login",
            params=params,
            data=data,
            allow_redirects=False)
        if ssoResp.status_code != 302 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception(
                "TPLogin error %s %s" % (ssoResp.status_code, ssoResp.text))
        session.headers.update(self._obligatory_headers)

        self.session = session

    def get(self, url):
        if not self.session:
            self.init()
        return self.session.get('https://tpapi.trainingpeaks.com' + url).json()

    def post(self, url, jeez):
        if not self.session:
            self.init()
        return self.session.post(
            'https://tpapi.trainingpeaks.com' + url, json=jeez)


def get_session():
    password = config.get_password_from_osx("chmouel", "trainingpeaks")
    return TPSession(config.TP_USERNAME, password)


def get_all_workouts_library(args):
    tp = get_session()
    libraries = config.get_or_cache(tp.get, "/exerciselibrary/v1/libraries",
                                    "tp_libraries")
    libraries = [
        x['exerciseLibraryId'] for x in libraries
        if re.match(args.filter_library_regexp, x['libraryName'])
    ]

    ret = {}
    for library in libraries:
        ljson = config.get_or_cache(
            tp.get, f'/exerciselibrary/v1/libraries/{library}/items',
            f"tp_library_{library}")
        for exercise in ljson:
            ret[exercise['itemName']] = (exercise['itemName'],
                                         exercise['exerciseLibraryItemId'])

    return ret


def get_userinfo(username):
    tp = get_session()
    return (config.get_or_cache(tp.get, "/users/v3/user", f"user_{username}"))


def convert_tr_workout_to_tp(workout):
    category_text = ''
    if 'Tags' in workout:
        for x in workout['Tags']:
            category_text += "#" + x['Text'].replace(" ", "_") + " "

    desc = workout['Details']['WorkoutDescription'] + "\n\n" + category_text

    coachComments = workout['Details']['GoalDescription']
    ret = {
        'description': html2text.html2text(desc),
        'coachComments': html2text.html2text(coachComments),
        "exerciseId": None,
        "workoutTypeId": config.TP_CYCLING_TYPE_ID,
        "itemName": workout["Details"]["WorkoutName"],
        "tssPlanned": workout["Details"]["TSS"],
        "ifPlanned": float(workout["Details"]["IntensityFactor"] / 100),
        "totalTimePlanned": float(workout["Details"]["Duration"] / 60),
        "distancePlanned": None,
        "velocityPlanned": None,
        "structure": {
            "primaryIntensityTargetOrRange": "target",
            "primaryIntensityMetric": "percentOfFtp",
            "primaryLengthMetric": "duration",
            'structure': []
        }
    }

    total = len(workout['intervalData'][1:]) - 1
    count = 0
    for interval in workout['intervalData'][1:]:
        name = interval['Name']
        intensityClass = "active"

        if name == "Fake" and count == 0:
            name = "Warm up"
            intensityClass = "warmUp"
        elif name == "Fake" and count == total:
            name = "Cool Down"
            intensityClass = "coolDown"
        elif name == "Fake":
            intensityClass = "rest"
            name = "Recovery"
        step = {
            "type":
            "step",
            "length": {
                "value": 1,
                "unit": "repetition"
            },
            "steps": [{
                "name":
                name,
                "length": {
                    "value": int(interval['End'] - interval['Start']),
                    "unit": "second"
                },
                "targets": [{
                    "minValue":
                    int(interval['StartTargetPowerPercent'])
                }],
                "intensityClass":
                intensityClass,
                "openDuration":
                False
            }]
        }

        count += 1
        ret['structure']['structure'].append(step)
    return ret


def create_calendar_workout_from_library(athleteId, jeez):
    tp = get_session()
    return tp.post(
        f"/fitness/v1/athletes/{athleteId}/commands/addworkoutfromlibraryitem",
        jeez)


def create_calendar_workout(athleteId, jeez):
    tp = get_session()
    return tp.post(f"/fitness/v3/athletes/{athleteId}/workouts", jeez)
