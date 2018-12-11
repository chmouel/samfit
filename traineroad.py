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
import argparse
import calendar
import datetime
import dateutil.parser as parser
import fcntl
import os
import requests
import sys
import tempfile
import time
import html2text

import config
import trainingpeaks
import exceptions

SESSION = None


class TRSession(object):
    _obligatory_headers = {"Referer": "https://www.trainerroad.com/login"}
    _reauthAttempts = 1

    def __init__(self, username, password):
        self.username = username
        self.password = password
        rate_lock_path = tempfile.gettempdir() + "/tr_rate.localhost.lock"
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
            "https://www.trainerroad.com/login", params=params)
        if preResp.status_code != 200:
            raise Exception("SSO prestart error %s %s" % (preResp.status_code,
                                                          preResp.text))

        ssoResp = session.post(
            "https://www.trainerroad.com/login",
            params=params,
            data=data,
            allow_redirects=False)
        if ssoResp.status_code != 302 or "temporarily unavailable" \
           in ssoResp.text:
            raise Exception(
                "TRLogin error %s %s" % (ssoResp.status_code, ssoResp.text))
        session.headers.update(self._obligatory_headers)

        self.session = session

    def get(self, url):
        if not self.session:
            self.init()
        return self.session.get('https://www.trainerroad.com/api' + url).json()


def get_session():
    global SESSION
    if SESSION:
        return SESSION
    password = config.get_password_from_osx("chmouel", "trainerroad")
    SESSION = TRSession(config.TR_USERNAME, password)
    return SESSION


def parse_plans(args):
    plan_number = args.plan_number
    cache_path = os.path.join(config.BASE_DIR, "plans", f"plan-{plan_number}")

    start_date = parser.parse(args.start_date)
    if start_date.weekday() != 0:
        raise exceptions.DateError(
            "%s don't start on a monday" % (start_date.today()))

    cursor_date = start_date - datetime.timedelta(days=1)
    tr = get_session()
    plan = config.get_or_cache(
        tr.get,
        f"/plans/{plan_number}",
        cache_path,
    )
    wargs = argparse.Namespace(filter_library_regexp="^TR-")
    workouts = trainingpeaks.get_all_workouts_library(wargs)
    athlete_id = trainingpeaks.get_userinfo(
        config.TP_USERNAME)['user']['personId']
    plan_name = plan['Name']

    ret = {}
    for week in plan['Weeks']:
        for day in week:
            if day not in list(calendar.day_name):  # not days
                if day == 'Name':
                    k = 'title'
                    v = f'{plan_name} - {week[day]}'
                elif day == 'Description':
                    k = 'description'
                    v = week[day]

                if cursor_date + datetime.timedelta(days=1) in ret:
                    ret[cursor_date + datetime.timedelta(days=1)][k] = v
                else:
                    ret[cursor_date + datetime.timedelta(days=1)] = {k: v}

                continue

            # Do this here since they are days and before we skip to next ones,
            cursor_date = cursor_date + datetime.timedelta(days=1)

            if not week[day]:  # empty
                continue

            ret[cursor_date] = [
                workouts[x['Workout']['Name']] for x in week[day]
            ]

    for date in ret:
        if type(ret[date]) is dict:
            dico = {
                'athleteId': athlete_id,
                'workoutDay': date.strftime("%Y-%m-%d"),
                'title': ret[date]['title'],
                'workoutTypeValueId': config.TP_OTHER_TYPE_ID,
                'description': html2text.html2text(ret[date]['description']),
                'completed': False,
                'publicSettingValue': 0,
                'personalRecordCount': 0
            }
            try:
                if not args.test:
                    r = trainingpeaks.create_calendar_workout(athlete_id, dico)
                    r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
                sys.exit(1)

            print(f"Note for {date} created")  # TODO(chmou):
            continue
        for workout in ret[date]:
            itemName, itemId = workout
            dico = {
                'athleteId': athlete_id,
                'exerciseLibraryItemId': int(itemId),
                'workoutDateTime': date.strftime("%Y-%m-%d")
            }
            # TODO: check if not already there
            try:
                if not args.test:
                    r = trainingpeaks.create_calendar_workout_from_library(
                        athlete_id, dico)
                    r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
                sys.exit(1)

            # print(f"Workout {itemName} for {date} created") # TODO(chmou):
            if not args.test:
                time.sleep(2)
