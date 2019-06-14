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
import calc
import config
import utils


def _add_step(step, workout, args, order):
    if step['intensityClass'] == 'warmUp':
        stepTypeId = 1
        stepTypeKey = "warmup"
    elif step['intensityClass'] == 'coolDown':
        stepTypeId = 2
        stepTypeKey = "cooldown"
    elif step['intensityClass'] == 'rest':
        stepTypeId = 4
        stepTypeKey = "recovery"
    else:
        stepTypeId = 3
        stepTypeKey = "interval"

    maxvalue = step['targets'][0].get('maxValue',
                                      step['targets'][0]['minValue'])
    gpacemin = calc.speed2centimetersms(
        calc.pace2speed(
            calc.convertTreshold(workout['workoutTypeValueId'],
                                 step['targets'][0]['minValue'],
                                 args.user_run_pace, args.user_swim_pace,
                                 args.user_cycling_ftp)))
    gpacemax = calc.speed2centimetersms(
        calc.pace2speed(
            calc.convertTreshold(workout['workoutTypeValueId'], maxvalue,
                                 args.user_run_pace, args.user_swim_pace,
                                 args.user_cycling_ftp)))

    if gpacemin > gpacemax:
        gpacemin, gpacemax = gpacemax, gpacemin

    endCondition = {"conditionTypeKey": "time", "conditionTypeId": 2}
    endConditionValue = step['length']['value']
    description = None
    if order == 1 and stepTypeKey == "warmup":
        endConditionValue = None
        endCondition = {"conditionTypeKey": "lap.button", "conditionTypeId": 1}
        description = "🏃 Run for at least " + utils.secondsToText(
            step['length']['value'])

    return {
        "type": "ExecutableStepDTO",
        "stepId": None,
        "stepOrder": order,
        "childStepId": None,
        "description": description,
        "stepType": {
            "stepTypeId": stepTypeId,
            "stepTypeKey": stepTypeKey
        },
        "endCondition": endCondition,
        "preferredEndConditionUnit": None,
        "endConditionValue": endConditionValue,
        "endConditionCompare": None,
        "endConditionZone": None,
        "targetType": {
            "workoutTargetTypeId": 6,  # TODO: CYCLING
            "workoutTargetTypeKey": "pace.zone"  # TODO: CYCLING
        },
        "targetValueOne": gpacemin,
        "targetValueTwo": gpacemax,
        "zoneNumber": None,
    }


def tpWorkoutGarmin(workout, tdd, args):
    atype = config.TP_TYPE[workout['workoutTypeValueId']]
    if atype not in ('Running'):
        return

    gtype = list(config.GARMIN_TYPE.keys())[list(
        config.GARMIN_TYPE.values()).index(atype)]

    title = f"{tdd.strftime('%A %d %b %Y')} - {workout['title']}"

    gsteps = []
    order = 1
    for structure in workout['structure']['structure']:
        gstep = {}
        if structure['type'] == 'repetition' and  \
           structure['length']['value'] != 1:
            wsteps = []
            worder = 1
            for step in structure['steps']:
                wsteps.append(_add_step(step, workout, args, worder))
                worder += 1

            gstep.update({
                'stepId': None,
                'stepOrder': order,
                'stepType': {
                    'stepTypeId': 6,
                    'stepTypeKey': 'repeat',
                },
                "numberOfIterations": structure['length']['value'],
                "smartRepeat": False,
                "childStepId": 1,
                "workoutSteps": wsteps,
                "type": "RepeatGroupDTO"
            })
        else:
            for step in structure['steps']:
                gstep.update(_add_step(step, workout, args, order))
        gsteps.append(gstep)
        order += 1

    ret = {
        'sportType': {
            'sportTypeId': gtype,
            'sportTypeKey': atype.lower()
        },
        'workoutName':
        title,
        'description':
        workout['description'],
        'workoutSegments': [{
            'segmentOrder': 1,
            'sportType': {
                'sportTypeId': gtype,
                'sportTypeKey': atype.lower(),
            },
            'workoutSteps': gsteps,
        }]
    }

    import json
    print(json.dumps(ret, indent=True))
    import sys
    sys.exit(0)
