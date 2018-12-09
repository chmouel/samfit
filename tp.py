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
import json
import requests
import os.path
import tempfile
import time

import html2text
TP_CYCLING_TYPE_ID = 2

TP_JSON_DIR = "/tmp/tp-json"
os.path.exists(TP_JSON_DIR) or os.makedirs(TP_JSON_DIR)

CATEGORIES = {
    'Trad VO2max': 1245289,
    'Low VO2max': 1245289,
    "Endurance": 1245291,
    "High-Density": 1245295,
    "Treshold": 1245296,
    "Anaerobic Capacity": 1245297,
    "Tempo": 1245298,
    "Sweet Spot": 1245300,
    "Warm-Ups": 1245301,
    "Free Ride": 1245302,
    "Others": 1245319,
}


class TPconnect(object):
    categories = []
    _obligatory_headers = {
        "Referer": "https://home.trainingpeaks.com/login"
    }
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
        preResp = session.get("https://home.trainingpeaks.com/login",
                              params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" %
                            (preResp.status_code, preResp.text))

        ssoResp = session.post("https://home.trainingpeaks.com/login",
                               params=params,
                               data=data, allow_redirects=False)
        if ssoResp.status_code != 302 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception("TPLogin error %s %s" % (
                ssoResp.status_code, ssoResp.text))
        session.headers.update(self._obligatory_headers)

        self.session = session

    def create_tr_workout(self, workout, exercise_library):
        if not workout['Details']['WorkoutDescription'] or not \
           workout['Details']['GoalDescription'] or len(workout['Tags']) == 0:
            return

        category = ''
        category_text = ''
        for x in workout['Tags']:
            if x['Text'] in CATEGORIES.keys():
                category = x['Text']
            category_text += "#" + x['Text'].replace(" ", "_") + " "
        if not category:
            category = 'Others'

        desc = (workout['Details']['WorkoutDescription'] +
                "\n\n" + category_text)

        coachComments = workout['Details']['GoalDescription']
        ret = {
            'description': html2text.html2text(desc),
            'coachComments': html2text.html2text(coachComments),
            "exerciseId": None,
            "exerciseLibraryId": CATEGORIES[category],
            "workoutTypeId": TP_CYCLING_TYPE_ID,
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
                "type": "step",
                "length": {
                    "value": 1,
                    "unit": "repetition"
                },
                "steps": [{
                    "name": name,
                    "length": {
                        "value": int(interval['End'] - interval['Start']),
                        "unit": "second"
                    },
                    "targets": [{
                        "minValue": int(interval['StartTargetPowerPercent'])
                    }],
                    "intensityClass": intensityClass,
                    "openDuration": False
                }]
            }

            count += 1
            ret['structure']['structure'].append(step)

        workout_url = ('https://tpapi.trainingpeaks.com/'
                       f'exerciselibrary/v1/libraries/{exercise_library}'
                       '/items')

        tpjson = os.path.join(TP_JSON_DIR,
                              str(workout['Details']['Id']) + ".json")
        if not os.path.exists(tpjson):
            jeez = json.dumps(ret)
            open(tpjson, 'w').write(jeez)

        if not self.session:
            return

        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://home.trainingpeaks.com/login',
            'Cookie': ('Production_tpAuth=' +
                       self.session.cookies.get('Production_tpAuth'))
        }

        s = ['curl', '-s']
        for k, v in headers.items():
            s.append("-H")
            s.append('"%s: %s"' % (k, v))

        s.append("--data")
        s.append("@${1}")
        s.append(workout_url)

        if os.path.exists("/tmp/curl"):
            return

        open("/tmp/curl", 'w').write(" ".join(s) + "\necho\n")
