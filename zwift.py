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
import glob
import os
import re

import html2text

import config
import utils

ZWIFT_DEFAULT_XML = """
<workout_file>
    <author>Trainer Road</author>
    <name>{name}</name>
    <description>{description}
    </description>
    <sportType>bike</sportType>
"""


def parse(workout):
    name = f"{workout['Details']['WorkoutName']} - "\
        f"{utils.secondsToText(int(workout['Details']['Duration']) * 60)}/" \
        f"{int(workout['Details']['TSS'])}/" \
        f"{int(workout['Details']['IntensityFactor'])}%"

    if not workout['Plans']:  # If not part of any plans just skip it
        return None, None

    description = html2text.html2text(workout['Details']['GoalDescription'])
    zxml = ZWIFT_DEFAULT_XML.format(name=name, description=description)

    tags = ""
    for tag in workout["Tags"]:
        tags += f'\t<tag name="{tag["Text"]}"/>'

    zxml += f"\t<tags>{tags}</tags>\n"
    zxml += "<workout>\n"
    for interval in workout['intervalData'][1:]:
        ts = float(interval['End'] - interval['Start'])
        power = interval['StartTargetPowerPercent'] / 100
        cadence = ""
        # TODO(chmou):configurable
        if power > 0.50:
            cadence = 'Cadence="90"'
        zxml += f'\t<SteadyState Duration="{ts}" Power="{power}" {cadence}/>\n'

    zxml += "</workout></workout_file>"
    return (workout['Details']['WorkoutName'] + ".zwo", zxml)


def generate_zwo(args):
    if 'all' in args.workout:
        workouts = sorted([
            int(re.sub(r"(\d+).json(.gz)?", r"\1", os.path.basename(x)))
            for x in glob.glob(
                os.path.join(config.BASE_DIR, "workout", "*.json*"))
        ])
    else:
        workouts = args.workout

    for workoutnumber in workouts:
        workout = utils.get_filej(str(workoutnumber), dtype='workout')
        fname, zwo = parse(workout)
        if not fname:
            continue
        fullfname = os.path.join(os.path.expanduser(args.output_dir), fname)
        print(f"Writting: {fullfname}")
        open(fullfname, 'w').write(zwo)
