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
import calendar
import datetime
import dateutil.parser as dtparser

import fcntl
import getpass
import os
import requests
import tempfile
import time
import html2text

import config
import utils
import trainingpeaks.calendar as tpcal
import trainingpeaks.library as tplib
import trainingpeaks.user as tpuser
import trainingpeaks.session as tpsess
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
        preResp = session.get("https://www.trainerroad.com/login", params=params)
        if preResp.status_code != 200:
            raise Exception(
                "SSO prestart error %s %s" % (preResp.status_code, preResp.text)
            )

        ssoResp = session.post(
            "https://www.trainerroad.com/login",
            params=params,
            data=data,
            allow_redirects=False,
        )
        if ssoResp.status_code != 302 or "temporarily unavailable" in ssoResp.text:
            raise Exception("TRLogin error %s %s" % (ssoResp.status_code, ssoResp.text))
        session.headers.update(self._obligatory_headers)

        self.session = session

    def get(self, url):
        if not self.session:
            self.init()
        return self.session.get("https://www.trainerroad.com/api" + url).json()


def get_session(args):
    global SESSION
    if SESSION:
        return SESSION
    password = args.tr_password or utils.get_password_from_osx(
        "trainerroad", getpass.getuser()
    )
    username = args.tr_user or config.TR_USERNAME
    SESSION = TRSession(username, password)
    return SESSION


def get_plan(args):
    plan_number = args.plan_number

    for plan_number in args.plan_number:

        cache_path = os.path.join(config.BASE_DIR, "plans", f"plan-{plan_number}")

        tr = get_session(args)
        plan = utils.get_or_cache(
            tr.get,
            f"/plans/{plan_number}",
            cache_path,
            cache=False,
        )
        if "ExceptionMessage" in plan:
            print(f"Could not find plan {plan_number}")
        else:
            print(
                f"'{plan['Plan']['Name']}' plan has been downloaded to {cache_path}.json"
            )


def parse_plans(args):
    plan_number = args.plan_number
    cache_path = os.path.join(config.BASE_DIR, "plans", f"{plan_number}")

    start_date = dtparser.parse(args.start_date)
    if start_date.weekday() != 0:
        raise exceptions.DateError("%s don't start on a monday" % (start_date.today()))

    cursor_date = start_date - datetime.timedelta(days=1)
    tr = get_session(args)
    plan = utils.get_or_cache(
        tr.get,
        f"/plans/{plan_number}",
        cache_path,
    )["Plan"]
    args.filter_library_regexp = f"^{args.library_name}$"
    workouts = tplib.get_all_workouts_library(args)
    athlete_id = tpuser.get_userinfo(args.tp_user, args.tp_password)["user"]["personId"]
    plan_name = plan["Name"]

    coachComments = f"""Number of Workout {plan['WorkoutCount']}
TSS per Week: {plan['TSSPerWeek']}
Hours Per Week: {plan['HoursPerWeek']}
"""
    tpcal.create_calendar_other(
        args,
        banner_message="Welcome Note",
        athlete_id=athlete_id,
        date=start_date,
        name=plan_name,
        coachComments=coachComments,
        description=html2text.html2text(plan["Description"]),
        title=f"Welcome to {plan['Name']} TrainerRoad plan",
        testmode=True,
    )  # TODO(chmou):

    ret = {}
    for week in plan["Weeks"]:
        for day in list(calendar.day_name):
            # Do this here since they are days and before we skip to next ones,
            cursor_date = cursor_date + datetime.timedelta(days=1)
            if day == "Monday":
                ret[cursor_date] = {
                    "title": f'{week["Name"]} - {plan_name}',
                    "description": week["Description"],
                    "coachComment": week["Tips"],
                }

            if not week[day]:  # empty
                continue

            ret[cursor_date] = [
                workouts[x["Workout"]["Name"]]
                for x in week[day]
                if x["Workout"]["Name"] in workouts
            ]
            for x in week[day]:
                if not x["Workout"]["Name"] in workouts:
                    print(
                        f"{x['Workout']['Name']} has been skipped cause not found in library"
                    )

    for _, date in ret.items():
        if ret[date] is dict:  # NOTE: this is a note
            coachComments = html2text.html2text(ret[date]["coachComment"])
            description = html2text.html2text(ret[date]["description"])
            tpcal.create_calendar_other(
                args,
                banner_message="Note",
                athlete_id=athlete_id,
                date=date,
                name=ret[date]["title"],
                coachComments=coachComments,
                description=description,
                title=ret[date]["title"],
                testmode=args.test,
            )
            continue

        for workout in ret[date]:
            itemName, itemId = workout

            tpcal.create_calendar_workout_from_library(
                args,
                name=itemName,
                athlete_id=athlete_id,
                exerciseLibraryItemId=int(itemId),
                date=date,
                testmode=args.test,
            )

            if not args.test:
                time.sleep(2)


def unapply_plan(args):
    plan_number = args.plan_number
    cache_path = os.path.join(config.BASE_DIR, "plans", f"plan-{plan_number}")

    start_date = dtparser.parse(args.start_date)
    if start_date.weekday() != 0:
        raise exceptions.DateError("%s don't start on a monday" % (start_date.today()))

    cursor_date = start_date - datetime.timedelta(days=1)
    tr = get_session(args)
    plan = utils.get_or_cache(
        tr.get,
        f"/plans/{plan_number}",
        cache_path,
    )["Plan"]
    athlete_id = tpuser.get_userinfo(args.tp_user, args.tp_password)["user"]["personId"]
    plan_name = plan["Name"]

    ret = {}
    for week in plan["Weeks"]:
        for day in list(calendar.day_name):
            # Do this here since they are days and before we skip to next ones,
            cursor_date = cursor_date + datetime.timedelta(days=1)
            if day == "Monday":
                ret[cursor_date] = [f'{week["Name"]} - {plan_name}']

            if not week[day]:  # empty
                continue

            if cursor_date in ret:
                ret[cursor_date] += [x["Workout"]["Name"] for x in week[day]]
            else:
                ret[cursor_date] = [x["Workout"]["Name"] for x in week[day]]

    from_str = list(ret)[0].strftime("%Y-%m-%d")
    to_str = list(ret)[-1].strftime("%Y-%m-%d")

    tp = tpsess.get_session(args.tp_user, args.tp_password)
    program = utils.get_or_cache(
        tp.get,
        f"/fitness/v1/athletes/{athlete_id}/workouts/{from_str}/{to_str}",
        f"program_workouts_{athlete_id}_{from_str}_{to_str}",
    )

    todelete = []
    for workout in program:
        workoutdate = dtparser.parse(workout["workoutDay"])
        if workoutdate in ret:
            for title in ret[workoutdate]:
                if title == workout["title"]:
                    todelete.append(workout["workoutId"])

    for delete in todelete:
        try:
            r = tp.delete(f"/fitness/v1/athletes/{athlete_id}/workouts/{delete}")
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to delete workoutID: {delete}: {err}")
            continue
        else:
            print(f"WorkoutID: {delete} has been deleted.")
