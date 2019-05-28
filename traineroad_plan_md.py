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
import calendar
import os.path
import collections

import config
import utils
import traineroad

import html2text
import humanfriendly


def wash_description(text):
    text = text.replace("\r", "\n")
    text = html2text.html2text(text).strip()
    return "\n".join(["> " + x for x in text.split("\n")])


def generate(args):
    categories = {}

    for plan_number in args.plan_number:
        cache_path = os.path.join(config.BASE_DIR, "plans",
                                  f"plan-{plan_number}")

        tr = traineroad.get_session(args)
        plan = utils.get_or_cache(
            tr.get,
            f"/plans/{plan_number}",
            cache_path,
        )
        fname, categories, md = _generate_md(plan, categories)
        fname = os.path.join(args.markdown_dir, f"{fname}.md")
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        # print(f"{fname} has been generated")
        open(fname, 'w').write(md)

    _generate_main_index(args, categories)


def _generate_main_index(args, categories):
    with open(os.path.join(args.markdown_dir, "index.md"), 'w') as ifp:
        ifp.write("# TR Workouts as Markdown Files\n")
        ifp.write("\n")

        for category in sorted(categories):
            ifp.write(f"## {category} \n\n")
            x = categories[category]
            for section in sorted(x):
                ss = section
                sp = section.replace("_-_", "_").split("-")
                if len(sp) == 3 and sp[1].startswith(sp[0]):
                    ss = sp[0] + "-" + sp[2]
                ss = ss.replace('_', ' ')
                ss = ss.replace('-', ' - ')
                ifp.write(f"* [{ss}]({section}.md)\n\n")

        ifp.write("___\n<sup>This is copyrighted by TR please "
                  "[subscribe](http://trainerroad.com/sign-up) to it ! "
                  "</sup>\n")


def _generate_md(fplan, categories):
    plan = fplan['Plan']
    plan_name = plan['ShortName']

    plan_category = plan['CategoryJson']['Child']['Name']
    if 'Child' in plan['CategoryJson']['Child'] and \
       plan['CategoryJson']['Child']['Child']:
        plan_category += "-" + plan['CategoryJson']['Child']['Child']['Name']

    text = f"# Trainer Road Plan: {plan['Name']}\n\n"
    text += wash_description(plan['Description']) + "\n\n"

    for currentweek in plan['Weeks']:
        text += f"## {currentweek['Name']}\n\n"
        text += wash_description(currentweek['Description']) + "\n"

        for key in list(calendar.day_name):
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
                if w['Duration'] != 0:
                    humantime = humanfriendly.format_timespan(
                        w['Duration'] * 60)
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

    fname = plan_category.replace(" ", "_") + "-" + plan_name.replace(" ", "_")
    if not plan['CategoryName'] in categories:
        categories[plan['CategoryName']] = []
    categories[plan['CategoryName']].append(fname)

    return (fname, categories, text)
