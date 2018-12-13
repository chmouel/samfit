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
import os
import json
import calendar
import sys

import requests
import dateutil.parser as dtparser

import config
import utils
import trainingpeaks.session as tpsess
import trainingpeaks.user as tpuser


def create_calendar_workout_from_library(
        args,
        name=None,
        athlete_id=None,
        exerciseLibraryItemId=None,
        date=None,
        testmode=None,
):
    jeez = {
        'athleteId': athlete_id,
        'exerciseLibraryItemId': exerciseLibraryItemId,
        'workoutDateTime': date.strftime("%Y-%m-%d")
    }
    try:
        if not testmode:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.post(
                f"/fitness/v1/athletes/{athlete_id}/commands/addworkoutfromlibraryitem",
                jeez)

            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    print(f"Workout: '{name}' on {date.strftime('%a %Y-%b-%d')} created")


def create_calendar_other(args,
                          banner_message=None,
                          title=None,
                          description=None,
                          athlete_id=None,
                          date=None,
                          coachComments=None,
                          name=None,
                          testmode=None):
    dico = {
        'athleteId': athlete_id,
        'workoutDay': date.strftime("%Y-%m-%d"),
        'title': title,
        'workoutTypeValueId': config.TP_OTHER_TYPE_ID,
        'description': description,
        'coachComments': coachComments,
        'completed': False,
        'publicSettingValue': 0,
        'personalRecordCount': 0
    }
    try:
        if not testmode:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.post(f"/fitness/v3/athletes/{athlete_id}/workouts", dico)
            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        raise err
    print(
        f"{banner_message}: '{name}' on {date.strftime('%a %Y-%b-%d')} created"
    )


def build_workout(current, workout, workoutdate):
    if not workout['title']:
        return current

    day = workoutdate.strftime("%A")

    # Those should not be imported back
    for x in [
            "workoutId", "athleteId", "workoutDay", "startTimePlanned",
            "sharedWorkoutInformationKey", "sharedWorkoutInformationExpireKey"
    ]:
        del workout[x]

    if day in current["Workouts"]:
        current["Workouts"][day].append(workout)
    else:
        current["Workouts"][day] = [workout]
    return current


def get_calendar_workouts(args):
    fromdate = dtparser.parse(args.from_date)
    todate = dtparser.parse(args.to_date)
    athlete_id = tpuser.get_userinfo(args.tp_user,
                                     args.tp_password)['user']['personId']

    from_str = fromdate.strftime("%Y-%m-%d")
    to_str = todate.strftime("%Y-%m-%d")

    url = f'/fitness/v1/athletes/{athlete_id}/workouts/{from_str}/{to_str}'

    calendar_days = list(calendar.day_name)

    tp = tpsess.get_session(args.tp_user, args.tp_password)
    program = utils.get_or_cache(
        tp.get,
        url,
        f"program_workouts_{athlete_id}_{from_str}_{to_str}",
    )

    weeks = []
    current = {}
    BeginningWeek = calendar_days.index("Monday")

    lock = False
    for workout in program:
        workoutdate = dtparser.parse(workout['workoutDay'])
        # detect beginning of weeks
        if workoutdate.weekday() == BeginningWeek \
           or (workoutdate.weekday() != BeginningWeek and
               program.index(workout) == 0):
            if not lock:
                if current:
                    weeks.append(current)
                current = {"Week": len(weeks) + 1, "Workouts": {}}
                lock = True

            current = build_workout(current, workout, workoutdate)
            continue

        current = build_workout(current, workout, workoutdate)
        lock = False

    if current:
        weeks.append(current)

    output_file = args.output_file
    if not args.output_file.startswith("/"):
        output_file = os.path.join(config.BASE_DIR, "plans",
                                   f"TP-{args.output_file}.json")
    total = 0
    for x in weeks:
        for w in x['Workouts']:
            total += 1
    print(f"Wrote: {output_file}\nWeeks: {len(weeks)}\n"
          f"Total number of Workouts: {total}")
    json.dump(weeks, open(output_file, 'w'))
