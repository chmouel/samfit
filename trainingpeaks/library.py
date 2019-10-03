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
import glob
import re
import time

import html2text
import requests

import traineroad
import trainingpeaks.session as tpsess
import utils
import config


def import_tr_workouts(args):
    if args.everything:
        todos = sorted([
            int(re.sub(r"(\d+).json(.gz)?", r"\1", os.path.basename(x)))
            for x in glob.glob(
                os.path.join(config.BASE_DIR, "workout", "*.json*"))
        ])
    else:
        todos = args.workout_ids

    tr = traineroad.get_session(args)
    tp = tpsess.get_session(args.tp_user, args.tp_password)
    libraries = utils.get_or_cache(tp.get, "/exerciselibrary/v1/libraries",
                                   f"tp_libraries_{args.tp_user}")
    libraries = [
        x['exerciseLibraryId'] for x in libraries
        if x['libraryName'] == args.library_name
    ]
    if not libraries:
        raise Exception(
            f"TP library name '{args.library_name}' could not be found")
    library_id = libraries[0]

    args.filter_library_regexp = f"^{args.library_name}$"
    workouts = get_all_workouts_library(args)

    for workout_id in todos:
        cache_path = os.path.join(config.BASE_DIR, "workout", str(workout_id))

        workout = utils.get_or_cache(
            tr.get,
            f"/workoutdetails/{workout_id}",
            cache_path,
        )

        if not workout:
            print(f"Skipping '{workout_id}', there is an issue loading it")
            continue

        if 'Workout' in workout:
            workout = workout['Workout']

        workout_name = workout["Details"]["WorkoutName"]
        if workout_name in workouts:
            print(f"Skipping '{workout_name}' already added")
            continue

        convert = convert_tr2tp(workout, library_id)
        if not convert:
            print(f"Skipping '{workout_name}' not an interesting one")
            continue

        add_workout(args, library_id, convert)

        if not args.test:
            time.sleep(2)


def add_workout(args, library_id, dico):
    try:
        if not args.test:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.post(f"/exerciselibrary/v1/libraries/{library_id}/items",
                        dico)
            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        from pprint import pprint as p
        p(dico)
        raise err

    print(f"Adding '{dico['itemName']}' to '{args.library_name}' library")


def convert_tr2tp(workout, library_id):
    if not workout['Details']['WorkoutDescription'] or not \
       workout['Details']['GoalDescription']:
        return {}

    category_text = ''
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
        "exerciseLibraryId": library_id,
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


def get_all_workouts_library(args, full=False):
    tp = tpsess.get_session(args.tp_user, args.tp_password)
    libraries = utils.get_or_cache(tp.get, "/exerciselibrary/v1/libraries",
                                   f"tp_libraries_{args.tp_user}")
    libraries = [
        x['exerciseLibraryId'] for x in libraries
        if re.match(args.filter_library_regexp, x['libraryName'])
    ]

    if not libraries:
        raise Exception("Could not find anything in the libraries")
    ret = {}
    for library in libraries:
        ljson = utils.get_or_cache(
            tp.get, f'/exerciselibrary/v1/libraries/{library}/items',
            f"tp_library_{library}")
        for exercise in ljson:
            if full:
                ret[exercise['itemName']] = exercise
            else:
                ret[exercise['itemName']] = (exercise['itemName'],
                                             exercise['exerciseLibraryItemId'])

    return ret


def update_workout(args, library_id, item_id, dico):
    try:
        if not args.test:
            tp = tpsess.get_session(args.tp_user, args.tp_password)
            r = tp.put(
                f"/exerciselibrary/v1/libraries/{library_id}/items/{item_id}",
                dico)
            r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        from pprint import pprint as p
        p(dico)
        raise err

    print(f"Updated '{dico['itemName']}' to '{library_id}' library")


def add_cadence_plan(args):
    workouts = get_all_workouts_library(args, full=True)

    for name in workouts:
        w = workouts[name]
        steps = []
        for step in w['structure']['structure']:
            for sub in step['steps']:
                if sub['intensityClass'] == 'active' and \
                   len(sub['targets']) == 2:
                    sub['targets'] = [sub['targets'][0]]

                if sub['intensityClass'] == 'active' and \
                   len(sub['targets']) == 1:
                    step['steps'][0]['targets'].append({
                        "maxValue":
                        config.ACTIVE_CADENCE_MAX,
                        "minValue":
                        config.ACTIVE_CADENCE_MIN,
                        "unit":
                        "roundOrStridePerMinute",
                    })
            steps.append(step)
        w['structure']['structure'] = steps
        libraryid = w['exerciseLibraryId']
        itemid = w['exerciseLibraryItemId']
        update_workout(args, libraryid, itemid, w)
        time.sleep(3)
