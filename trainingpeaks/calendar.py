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
import json
import os
import sys
import time
import tempfile

import datetime
import requests
import dateutil.parser as dtparser
import ics

import config
import exceptions
import utils
import showplan
import trainingpeaks.session as tpsess
import trainingpeaks.user as tpuser


def create_calendar_workout(args, workout=None, date=None):
    athlete_id = workout["athleteId"]
    try:
        if not args.test:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.post(f"/fitness/v3/athletes/{athlete_id}/workouts", workout)

            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    print(
        f"Workout: '{workout['title']}' on {date.strftime('%a %Y-%b-%d')} created"
    )


def create_calendar_workout_from_library(
        args,
        name=None,
        athlete_id=None,
        exerciseLibraryItemId=None,
        date=None,
        testmode=None,
):
    jeez = {
        "athleteId": athlete_id,
        "exerciseLibraryItemId": exerciseLibraryItemId,
        "workoutDateTime": date.strftime("%Y-%m-%d"),
    }
    try:
        if not testmode:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.post(
                f"/fitness/v1/athletes/{athlete_id}/commands/addworkoutfromlibraryitem",
                jeez,
            )

            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    print(f"Workout: '{name}' on {date.strftime('%a %Y-%b-%d')} created")


def create_calendar_other(
        args,
        banner_message=None,
        title=None,
        description=None,
        athlete_id=None,
        date=None,
        coachComments=None,
        name=None,
        testmode=None,
):
    dico = {
        "athleteId": athlete_id,
        "workoutDay": date.strftime("%Y-%m-%d"),
        "title": title,
        "workoutTypeValueId": config.TP_OTHER_TYPE_ID,
        "description": description,
        "coachComments": coachComments,
        "completed": False,
        "publicSettingValue": 0,
        "personalRecordCount": 0,
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
    if not workout["title"]:
        return current

    day = workoutdate.strftime("%A")

    # Those should not be imported back
    for x in [
            "lastModifiedDate",
            "workoutId",
            "athleteId",
            "workoutDay",
            "startTimePlanned",
            "sharedWorkoutInformationKey",
            "sharedWorkoutInformationExpireKey",
    ]:
        del workout[x]

    if day in current["Workouts"]:
        current["Workouts"][day].append(workout)
    else:
        current["Workouts"][day] = [workout]
    return current


def calendar_workouts_ical(args):
    ical_file = args.output_file
    tmpfile = None
    if args.generated_output_file:
        args.output_file = args.generated_output_file
    else:
        tmpfile = tempfile.mktemp(
            ".calendar_parsed.json", prefix=".tmp-samfit-", dir="/tmp/")
        args.output_file = tmpfile

    output_json = get_calendar_workouts(args)

    plan = json.load(open(output_json))
    start_date = dtparser.parse(args.from_date)
    cursor_date = start_date - datetime.timedelta(days=1)
    events = []
    for week in plan:
        for day in list(calendar.day_name):
            cursor_date = cursor_date + datetime.timedelta(days=1)
            cursor_date = cursor_date.replace(hour=7, minute=0)

            if day not in week[
                    "Workouts"] or not week["Workouts"][day]:  # empty
                continue

            for current in week["Workouts"][day]:
                event = ics.Event()
                event.name = current["title"] and current["title"] or ""

                if current["totalTimePlanned"]:
                    event.name += " " + utils.secondsToText(
                        current["totalTimePlanned"] * (60 * 60))
                    event.duration = datetime.timedelta(
                        seconds=current["totalTimePlanned"] * (60 * 60))

                event.description = current["description"] and current[
                    "description"].replace("\r", "") or ""

                pp = showplan.show_workout(
                    args, current, colorize=False, extranewlines=True)
                if pp:
                    event.description += "\nExercises:\n\n" + pp.replace(
                        "\r", "\n")

                if current["coachComments"]:
                    event.description += "\n\nCommentaire du Coach:\n"
                    event.description += current["coachComments"].replace(
                        "\r", "\n")

                # TODO(chmou):increase hours ?
                event.begin = cursor_date
                events.append(event)

    @ics.Calendar._outputs
    def o_custom(calendar, container):
        if args.calendar_title:
            container.append(f"X-WR-CALNAME:{args.calendar_title}")
            container.append(f"X-WR-CALDESC: Road to {args.calendar_title}")
        container.append(f"X-WR-TIMEZONE: {config.TIME_ZONE}")

    output = str(ics.Calendar(events=events))
    print(f"Generated iCS Calendar to: {ical_file}")
    open(ical_file, "w").write(output)
    tmpfile and os.remove(tmpfile)


def get_calendar_workouts(args):
    cache = True
    if args.no_cache:
        cache = False

    fromdate = dtparser.parse(args.from_date)
    todate = dtparser.parse(args.to_date)
    athlete_id = tpuser.get_userinfo(args.tp_user,
                                     args.tp_password)["user"]["personId"]

    from_str = fromdate.strftime("%Y-%m-%d")
    to_str = todate.strftime("%Y-%m-%d")

    url = f"/fitness/v1/athletes/{athlete_id}/workouts/{from_str}/{to_str}"

    calendar_days = list(calendar.day_name)

    tp = tpsess.get_session(args.tp_user, args.tp_password)
    program = utils.get_or_cache(
        tp.get,
        url,
        f"program_workouts_{athlete_id}_{from_str}_{to_str}",
        cache=cache)

    weeks = []
    current = {}
    BeginningWeek = calendar_days.index("Monday")

    lock = False
    for workout in program:
        workoutdate = dtparser.parse(workout["workoutDay"])
        # detect beginning of weeks
        if workoutdate.weekday() == BeginningWeek or (
                workoutdate.weekday() != BeginningWeek
                and program.index(workout) == 0):
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
        for w in x["Workouts"]:
            total += 1
    print(f"Wrote: {output_file}\nWeeks: {len(weeks)}\n"
          f"Total number of Workouts: {total}")
    json.dump(weeks, open(output_file, "w"))
    return output_file


def import_plan(args):
    athlete_id = tpuser.get_userinfo(args.tp_user,
                                     args.tp_password)["user"]["personId"]
    plan = utils.get_filej(args.plan_file)
    if not plan:
        raise Exception(f"Cannot find plan: {args.plan_file}")

    start_date = dtparser.parse(args.start_date)
    if start_date.weekday() != 0:
        raise exceptions.DateError(
            "%s don't start on a monday" % (str(start_date)))

    cursor_date = start_date - datetime.timedelta(days=1)
    cursor_date = cursor_date.replace(hour=7, minute=0)
    ret = {}
    for week in plan:
        for day in list(calendar.day_name):
            # Do this here since they are days and before we skip to next ones,
            cursor_date = cursor_date + datetime.timedelta(days=1)
            cursor_date = cursor_date.replace(hour=7, minute=0)
            if day not in week[
                    "Workouts"] or not week["Workouts"][day]:  # empty
                continue

            dayp = []
            for workout in week["Workouts"][day]:
                workout["athleteId"] = athlete_id
                workout["lastModifiedDate"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d")
                workout["workoutDay"] = cursor_date.strftime("%Y-%m-%d")
                workout["startTimePlanned"] = cursor_date.strftime(
                    "%Y-%m-%dT%H:%m")
                dayp.append(workout)
                if workout["workoutTypeValueId"] != config.TP_OTHER_TYPE_ID:
                    cursor_date = cursor_date + datetime.timedelta(hours=1)
            ret[cursor_date] = dayp

    for day in ret:
        for workout in ret[day]:
            create_calendar_workout(args, workout, day)
            time.sleep(2)
