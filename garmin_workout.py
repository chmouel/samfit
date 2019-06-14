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
import garmin_connect
import utils

import sys


def _garmin_get_pace(step, workout, args):
    maxvalue = step['targets'][0].get('maxValue',
                                      step['targets'][0]['minValue'])
    gmin = calc.speed2centimetersms(
        calc.pace2speed(
            calc.convertTreshold(workout['workoutTypeValueId'],
                                 step['targets'][0]['minValue'],
                                 args.user_run_pace, args.user_swim_pace,
                                 args.user_cycling_ftp)))
    gmax = calc.speed2centimetersms(
        calc.pace2speed(
            calc.convertTreshold(workout['workoutTypeValueId'], maxvalue,
                                 args.user_run_pace, args.user_swim_pace,
                                 args.user_cycling_ftp)))
    return gmin, gmax


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

    if workout['structure'][
            'primaryIntensityMetric'] == 'percentOfThresholdPace':
        gmin, gmax = _garmin_get_pace(step, workout, args)
        targetType = {
            "workoutTargetTypeId": 6,
            "workoutTargetTypeKey": "pace.zone"
        }
        firststepdesc = "🏃 Run for at least " + utils.secondsToText(
            step['length']['value']) + " and then press lap."
    elif workout['structure']['primaryIntensityMetric'] == 'percentOfFtp':
        maxvalue = step['targets'][0].get('maxValue',
                                          step['targets'][0]['minValue'])
        gmin = calc.convertTreshold(
            workout['workoutTypeValueId'], step['targets'][0]['minValue'],
            args.user_run_pace, args.user_swim_pace, args.user_cycling_ftp)
        gmax = calc.convertTreshold(workout['workoutTypeValueId'], maxvalue,
                                    args.user_run_pace, args.user_swim_pace,
                                    args.user_cycling_ftp)
        firststepdesc = "🚴 Cycle for at least " + utils.secondsToText(
            step['length']['value']) + " and then press lap"

        targetType = {
            "workoutTargetTypeId": 2,
            "workoutTargetTypeKey": "power.zone",
            "displayOrder": 2
        }
    else:
        print(
            f"{workout['structure']['primaryIntensityMetric']} Not supported yet"
        )
        sys.exit(1)
    if gmin > gmax:
        gmin, gmax = gmax, gmin

    endCondition = {"conditionTypeKey": "time", "conditionTypeId": 2}
    endConditionValue = step['length']['value']
    description = None
    if order == 1 and stepTypeKey == "warmup":
        endConditionValue = None
        endCondition = {"conditionTypeKey": "lap.button", "conditionTypeId": 1}
        description = firststepdesc

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
        "targetType": targetType,
        "targetValueOne": gmin,
        "targetValueTwo": gmax,
        "zoneNumber": None,
    }


def tpWorkoutGarmin(workout, tdd, args):
    atype = config.TP_TYPE[workout['workoutTypeValueId']]
    if atype not in ('Running', 'Cycling'):
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
    gops = garmin_connect.GarminOPS(args)
    all_workouts = gops.get_all_workouts()
    for gw in all_workouts:
        if gw['workoutName'] == ret['workoutName']:
            if args.sync_delete:
                gops.delete_workout(gw['workoutId'])
                print(
                    f"Workout: \"{gw['workoutName']}\" id: {gw['workoutId']} has been deleted."
                )
            else:
                print(
                    f"Workout named '{ret['workoutName']}' already exist skipping"
                )
                sys.exit(1)

    import json
    jeez = json.dumps(ret, indent=True)
    resp = gops.create_workout(jeez)
    gops.schedule_workout(resp['workoutId'], tdd)

    print(
        f"Workout: \"{resp['workoutName']}\" id: {resp['workoutId']} has been created."
    )
    sys.exit(0)
