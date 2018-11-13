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
import gzip
import html2text
import humanfriendly
import json
import os.path
import re
import subprocess
import time
import tr
import zwift


ZWIFT_BASE_DIR = os.path.expanduser("~/Documents/Zwift/Workouts")
BASE_DIR = os.path.expanduser("~/Dropbox/Documents/Fitness/traineroad")
DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]

PLAN_NAME = None


def wash_description(text):
    text = text.replace("\r", "\n")
    text = html2text.html2text(text).strip()
    return "\n".join(["> " + x for x in text.split("\n")])


def get_session(username, password):
    tpsess = tr.TRconnect(username, password)
    tpsess.init()
    return tpsess


def write_get_tp(tpsess, tptype, iid, output_file):
    if os.path.exists(output_file):
        return json.load(open(output_file))
    elif os.path.exists(output_file + ".gz"):
        return json.load(gzip.open(output_file + ".gz"))

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    url = f'https://www.trainerroad.com/api/{tptype}/{iid}'
    print("Getting: " + url)
    cp = tpsess.session.get(url)

    if cp.status_code != 200:
        raise Exception("Humm booya")

    open(output_file, 'w').write(cp.text)
    time.sleep(2)
    return cp.json()


def parse_plan(tpsess, plan, plan_number):
    plan_name = plan['ShortName']

    plan_category = plan['CategoryJson']['Child']['Name']
    if 'Child' in plan['CategoryJson']['Child'] and \
       plan['CategoryJson']['Child']['Child']:
        plan_category += "-" + plan['CategoryJson']['Child']['Child']['Name']

    base_zwiftdir = os.path.join(ZWIFT_BASE_DIR,
                                 'Trainerroad',
                                 plan_category,
                                 plan_name)

    plan_textfile = os.path.join(BASE_DIR,
                                 "docs",
                                 plan_category.replace(" ", "_") +
                                 "-" +
                                 plan_name.replace(" ", "_") + ".md")

    text = f"# Trainer Road Plan: {plan['Name']}\n\n"
    text += wash_description(plan['Description']) + "\n\n"

    for currentweek in plan['Weeks']:
        text += f"## {currentweek['Name']}\n\n"
        text += wash_description(currentweek['Description']) + "\n"

        for key in DAYS:
            if key not in currentweek:
                continue
            text += (f"\n### {key} \n\n")
            if not currentweek[key]:
                text += (f"Rest Day\n\n")
                continue

            multiple = len(currentweek[key]) > 1
            idx = 0
            for workout in currentweek[key]:
                idx += 1
                if multiple:
                    text += (f"#### Workout {idx}\n")

                w = workout["Workout"]
                # TRIATHLON
                if w['Id'] == 0:
                    wdetail = w
                else:
                    wdetailfile = os.path.join(
                        BASE_DIR, "workout", f'{w["Id"]}.json')
                    wdetail = write_get_tp(
                        tpsess, 'workoutdetails', w['Id'], wdetailfile)

                    zfile = os.path.join(base_zwiftdir, w["Name"] + ".zwo")
                    zwift.generate_zwo(wdetail, plan_number, zfile)

                if w['Duration'] != 0:
                    humantime = (
                        humanfriendly.format_timespan(w['Duration'] * 60))
                else:
                    humantime = None
                text += (f'* **Name**: {w["Name"]}\n')
                if humantime:
                    text += (f'* **Duration**: {humantime}\n')
                if round(w['TSS']) != 0:
                    text += (f'* **TSS**: {w["TSS"]}\n')
                if round(w['NormalizedPower']) != 0:
                    text += (f'* **NP**: {round(w["NormalizedPower"])}\n')
                if round(w['TSS']) != 0:
                    text += (f'* **IF**: {round(w["IntensityFactor"])}%')
                text += ("\n\n")
                text += ("**Description**:\n\n")
                text += wash_description(w['Description']) + "\n\n"

    if not os.path.exists(os.path.dirname(plan_textfile)):
        os.makedirs(os.path.dirname(plan_textfile))
    open(plan_textfile, 'w').write(text)
    return plan_textfile


if __name__ == '__main__':
    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainerroad", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()
    username = 'samfit'
    tpsess = get_session(username, password)

    # RANGE = [216, 217, 218]
    import glob
    RANGE = sorted([
        int(re.sub(r"plan-(\d+).json(.gz)?", r"\1", os.path.basename(x)))
        for x in glob.glob(os.path.join(BASE_DIR, "plans", "*.json*"))])

    # RANGE = range(234, 245 + 1)
    # RANGE = range(160, 165 + 1)

    for plan_number in RANGE:
        plan_file = os.path.join(BASE_DIR, "plans", "plan-" +
                                 str(plan_number) + ".json")
        plan = write_get_tp(tpsess, "plans", plan_number, plan_file)
        parse_plan(tpsess, plan, plan_number)
