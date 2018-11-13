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
import humanfriendly
import json
import tr
import subprocess
import html2text
import os.path

BASE_DIR = "/tmp/traineroad"
DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]


def get_session(username, password):
    tpsess = tr.TRconnect(username, password)
    tpsess.init()
    return tpsess


def write_get_tp(tpsess, tptype, iid, output_file):
    if os.path.exists(output_file):
        return json.load(open(output_file))

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    cp = tpsess.session.get(
        f'https://www.trainerroad.com/api/{tptype}/{iid}')

    if cp.status_code != 200:
        raise Exception("Humm booya")

    open(output_file, 'w').write(cp.text)
    return cp.json()


def parse_plan(tpsess, plan):
    plan_name = plan['ShortName'].replace(" ", "_")
    base_plandir = os.path.join(BASE_DIR, plan_name, "workouts")

    for currentweek in plan['Weeks']:
        print(currentweek['Name'] + ": ")
        print(html2text.html2text(currentweek['Description']))

        for key in DAYS:
            if key not in currentweek:
                continue
            print(f"{key}: ")
            if not currentweek[key]:
                print(f"Rest Day\n")
                continue
            for workout in currentweek[key]:
                w = workout["Workout"]
                wdetailfile = os.path.join(base_plandir, f'{w["Id"]}.json')
                print(wdetailfile)
                # wdetail = write_get_tp(
                #     tpsess, 'workoutdetails', w['Id'], wdetailfile)

                humantime = humanfriendly.format_timespan(w['Duration'] * 60)
                print(f'Workout: {w["Name"]} TSS: {w["TSS"]}'
                      f' Duration: {humantime}'
                      f' NP: {round(w["NormalizedPower"])}'
                      f' IF: {round(w["IntensityFactor"])}%')
                print("Description:")
                print(html2text.html2text(w['Description']))


if __name__ == '__main__':
    PLAN_NUMBER = 146

    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainerroad", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()
    username = 'samfit'

    tpsess = get_session(username, password)
    plan_file = f'/tmp/workout-plan-{PLAN_NUMBER}.json'
    plan = write_get_tp(tpsess, "plans", PLAN_NUMBER, plan_file)
    parse_plan(tpsess, plan)
