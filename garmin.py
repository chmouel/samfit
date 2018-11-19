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
import json
import os.path

import html2text

GARMIN_JSON_DIR = "/tmp/gjson"
os.path.exists(GARMIN_JSON_DIR) or os.makedirs(GARMIN_JSON_DIR)

GARMIN_ZONES = {
    1: 0,
    2: 18,
    3: 49,
    4: 69,
    5: 83,
    6: 100,
    7: 115,
}


def find_target_zone(percent):
    for i, (z, p) in enumerate(GARMIN_ZONES.items()):
        if percent >= p:
            try:
                n = GARMIN_ZONES[i + 2]
            except(KeyError):
                return 7

            if percent < n:
                return z


def generate_garmin_workout(workout):
    ret = {
        'sportType': {
            'sportTypeId': 2,
            'sportTypeKey': 'cycling'
        },
        'workoutName': '',
        'description': '',
        'workoutSegments': [
            {'segmentOrder': 1,
             'sportType': {'sportTypeId': 2,
                           'sportTypeKey': 'cycling'},
             'workoutSteps': []}]}

    ret['workoutName'] = workout["Details"]["WorkoutName"]
    ret['description'] = (
        html2text.html2text(workout['Details']['WorkoutDescription']))

    total = len(workout['intervalData'][1:]) - 1
    count = 0
    for interval in workout['intervalData'][1:]:
        step = {'childStepId': None,
                'description': None,
                'endCondition': {'conditionTypeId': 2,
                                 'conditionTypeKey': 'time'},
                'endConditionCompare': None,
                'endConditionValue': 120,
                'endConditionZone': None,
                'preferredEndConditionUnit': None,
                'stepId': None,
                'stepOrder': 1,
                'stepType': {'stepTypeId': 1, 'stepTypeKey': 'warmup'},
                'targetType': {'workoutTargetTypeId': 2,
                               'workoutTargetTypeKey': 'power.zone'},
                'targetValueOne': None,
                'targetValueTwo': None,
                'type': 'ExecutableStepDTO',
                'zoneNumber': None}

        name = interval['Name']
        stepType = (3, "interval")
        if (name == "Fake" or 'Recovery' in name) and count == 0:
            stepType = (1, "warmup")
        elif name == "Fake" and count == total:
            stepType = (2, "cooldown")
        elif name == "Fake" or 'Recovery' in name:
            stepType = (4, "recovery")

        if name != "Fake":
            step['description'] = name.title()
        else:
            step['description'] = stepType[1].title()

        step['description'] += ", target: %d%% of your FTP" % (
            int(interval['StartTargetPowerPercent']))

        step['endConditionValue'] = (
            int(interval['End'] - interval['Start'])
        )
        step['stepType'] = {'stepTypeId': stepType[0],
                            'stepTypeKey': stepType[1]}
        step['stepOrder'] = count + 1

        step['zoneNumber'] = find_target_zone(
            int(interval['StartTargetPowerPercent']))

        count += 1
        ret['workoutSegments'][0]['workoutSteps'].append(step)

    gjson = os.path.join(GARMIN_JSON_DIR,
                         str(workout['Details']['Id']) + ".json")
    if not os.path.exists(gjson):
        json.dump(ret, open(gjson, 'w'))
