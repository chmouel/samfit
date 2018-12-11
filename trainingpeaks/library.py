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
import re
import html2text

import trainingpeaks.session as tpsess
import utils
import config


def convert_tr2tp(workout):
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


def get_all_workouts_library(args):
    tp = tpsess.get_session(args.tp_user, args.tp_password)
    libraries = utils.get_or_cache(tp.get, "/exerciselibrary/v1/libraries",
                                   f"tp_libraries_{args.tp_user}")
    libraries = [
        x['exerciseLibraryId'] for x in libraries
        if re.match(args.filter_library_regexp, x['libraryName'])
    ]

    ret = {}
    for library in libraries:
        ljson = utils.get_or_cache(
            tp.get, f'/exerciselibrary/v1/libraries/{library}/items',
            f"tp_library_{library}")
        for exercise in ljson:
            ret[exercise['itemName']] = (exercise['itemName'],
                                         exercise['exerciseLibraryItemId'])

    return ret
