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
import requests
import sys

import config
import trainingpeaks.session as tpsess


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
    print(f"Workout: {name} on {date.strftime('%a %Y-%b-%d')} created")


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
        f"{banner_message}: {name} on {date.strftime('%a %Y-%b-%d')} created")
