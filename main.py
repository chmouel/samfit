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
import zwift


ZWIFT_BASE_DIR = os.path.expanduser("~/Documents/Zwift/Workouts")
BASE_DIR = os.path.expanduser("~/Dropbox/Documents/Fitness/traineroad")
DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]

PLAN_NAME = None

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


def parse_plan(tpsess, plan, plan_number):
    plan_name = plan['ShortName'].replace(" ", "_")
    base_plandir = os.path.join(BASE_DIR, plan_name, "workouts")
    base_zwiftdir = os.path.join(ZWIFT_BASE_DIR, "Trainerroad-" + plan_name)
    text = ""
    plan_textfile = os.path.join(BASE_DIR, plan_name, "README.md")

    text = f"# Trainer Road Plan: {plan['ShortName']}\n\n"

    for currentweek in plan['Weeks']:
        text += f"## {currentweek['Name']}\n\n"
        text += ("<pre>\n" +
                 html2text.html2text(currentweek['Description']).strip() +
                 "\n</pre>\n"
        )

        for key in DAYS:
            if key not in currentweek:
                continue
            text += (f"\n### {key} \n\n")
            if not currentweek[key]:
                text += (f"Rest Day\n\n")
                continue
            for workout in currentweek[key]:
                w = workout["Workout"]
                wdetailfile = os.path.join(base_plandir, f'{w["Id"]}.json')
                wdetail = write_get_tp(
                    tpsess, 'workoutdetails', w['Id'], wdetailfile)
                zfile = os.path.join(base_zwiftdir, w["Name"] + ".zwo")
                zwift.generate_zwo(wdetail, plan_number, zfile)

                humantime = humanfriendly.format_timespan(w['Duration'] * 60)
                text += (f'* **Name**: {w["Name"]}\n'
                         f'* **Duration**: {humantime}\n'
                         f'* **TSS**: {w["TSS"]}\n'
                         f'* **NP**: {round(w["NormalizedPower"])}\n'
                         f'* **IF**: {round(w["IntensityFactor"])}%\n\n')
                text += ("**Description**:\n")
                text += ("<pre>\n" +
                         html2text.html2text(w['Description']).strip() +
                         "\n</pre>\n")

    if not os.path.exists(plan_textfile):
        print("W" + " " + plan_textfile)
        open(plan_textfile, 'w').write(text)
    open(plan_textfile, 'w').write(text)


if __name__ == '__main__':
    PLAN_NUMBER = 146

    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainerroad", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()
    username = 'samfit'

    tpsess = get_session(username, password)
    plan_file = os.path.join(BASE_DIR, "plan-" + str(PLAN_NUMBER) + ".json")
    plan = write_get_tp(tpsess, "plans", PLAN_NUMBER, plan_file)
    parse_plan(tpsess, plan, PLAN_NUMBER)
