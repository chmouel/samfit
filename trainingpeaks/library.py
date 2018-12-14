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
    RANGE = sorted([
        int(re.sub(r"(\d+).json(.gz)?", r"\1", os.path.basename(x)))
        for x in glob.glob(
            os.path.join(config.BASE_DIR, "workout", "*.json*"))
    ])

    tr = traineroad.get_session()
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

    for workout_id in RANGE:
        cache_path = os.path.join(config.BASE_DIR, "workout", str(workout_id))

        workout = utils.get_or_cache(
            tr.get,
            f"/workoutdetails/{workout_id}",
            cache_path,
        )

        if not workout:
            print(f"Skipping '{workout_id}', there is an issue loading it")
            continue

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
       workout['Details']['GoalDescription'] or len(workout['Tags']) == 0:
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


# curl 'https://tpapi.trainingpeaks.com/exerciselibrary/v1/libraries/1245297/items/3634034' -X PUT -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Accept-Language: en,en-US;q=0.8,fr;q=0.5,fr-FR;q=0.3' --compressed -H 'Referer: https://app.trainingpeaks.com/' -H 'Content-Type: application/json' -H 'Origin: https://app.trainingpeaks.com' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%22150482dc-faef-4f65-88bd-5c3c41145bb7%22; Production_tpAuth=PWMNXmv09kK0Q7eirxYP88HyuD9rqLASz27ZbxxA7j0AU2CwTrMCC288XrV1c2oezPEoZQnEh_ZvCzyE3UnF3T1yy8FGWlnBXD75x5-mCUTKLbYHXKlNBOw5_8zvTfx8vWY2rtJ8yDH83lZmuqIZAYGF-nfQcpZRCkmC_-dQdsnG-FMEiLZTnrsZDGxC8uxAsUzot1MZgBvoZbR2cKEFrDWFzZvDB2mZJE2PRh-eZKgHH9g1Ss0O7ymqs_X9f9YiuFHGpr5DUfDrDnCF9ApDkYFpnbruGvLp2-px4VTEuZWcuPata_Wb0mkmoRffaLkHaUm6KI523oVZyEjoRj4q8BSRYrFJH73CVjWvMR0-oRamAugf5rI7drgE4E1rgYGkEZsD8IX5A1XSgOUIK8h2KxrrUeyp4wQaUGlbU_y569L1oLDoT4N5iC9lcJTIZflehpq3GjVPCthAWk6c-10tVc9dP5xgVqura5AupCC85raJgRpR9uR-r972b71dnkmM9uwd69nc2nIHHovpGIb8No5n-JgRfBl_JsTZ7wrgzU4I4rIBE7oKnzwWSstkTjCVKS2IXf-uN--pSs7OWoxiwv1wcyanwnGQ5mS3L4ytIQJwGfp7oVTWco-11bLNbZ3K5CPOehLEHXNO0KCzcsan20Vw4XItFkuJWne-XapVQvI7K-DA0-uCQmPaFZu_XFqVWU6_lGrk6nXZQPxuBmUA7FzVuF7tPI06nkNpYBIF0y9Xkm-yVDSjPG-GZfXmTxQYDG1WLFwYyEnrWQzbkGfyJ9TTDQGnA9v6q4W0UNPvu2MonEHK1jyqk-E6alxCCRvMeeDCIrobu_iLOTd41Gb9TBKxvqOc1Dav0GKoKbQFmEEq6yN88FhQSDueqGD2IpfXlrpdCEYx8tcBQqzO0jS5zHjwM58BDTy9BeLGgUEiJM-_Vl1hL3Pkv7kcvSyef2IvL90FNWdixlQZbpK_9i-LvC2f1xEvcs8N-CrDseQDtt4firHIG-GeSBks7Lzy1uHgUTI2355s10yL1ch6ECVaUSBAJZeXvADDOPmrAiFTNrVLprddw3Y-azX81bwSC2G6Nb9stcPLgoVamLU7NQuvwvyUIhzqXkt6xYokWxijcViXMFCxK9kSdtubpCXdc4mIy2YLMwxhYtd9PEdVvlh995BRi2r60xfysaEjXwc_nogS_PJKP4RrgEmBgwLbPs2gQHtleagtIz6OIh5bZUx33pSTw8MNAZwGmIH7iPUcDEzdUiZ4-mGoKB7W2Ad2ACF8bhLjiupqU48M2GhCFWb3qIsDcarjMtQG4W2sgGSyJaPnl-TWC3UxCZJx2XKoWlByMmMsWYjypzDPhhinnuK7imu8FPYpzQiHAzsUlWunfhY_GlQRw5kJ0rqHlS2oFyu3GnMECP1LhoN1wbSGksvUb1nyVSuGzbc0YkFbc5Uq3rgrqZ8VBCZl0sQxzVyVMGzdsoAZ52kXK-Uhbe0OiwgOPhiC_W9waBDgpuqld1DJoZF56t1T3XFecqlLWn8nWZ9LFA7dXqCzS8YqE7MmTtP-5L7VL5ONBUKMvWqwE0PhcKb1dJRvo0Bth7YeFpxWBzdj7Z-XrFlApfJ_d1lXkBO7uHILmvQ2UZJjVCz4x1_qqRjcQ9QXUTNNBg7qxuqC_Ev5_u_DYuI12E1dv6CLVEdHMVHlHeTtgQV_uiUiO4onEOADsvG40Lx7jqDHt8zsjVpXBKdfoRBNqWNL2zOKtNGZJyeCpBj5ErMG-uomGLTdDImpWAj7_rTXQEHD31pcmpJvIOleuE2vGUsvXaXGE9DCcXFqgs0nG-C1hR7xrApUP2GTbu745AwTJBybzF8vF_Y6Bt88OUPTqtCuFVU4qFkR3RBkUm4Y10Q0UCxPrBdo-cqqUGhDbDTS6pQRdoTyUblJ31qK0jjBK23EAF-iQku7AQ2' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'TE: Trailers'


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
