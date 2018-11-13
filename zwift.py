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
import html2text
import os.path

# workout = json.load(open("/tmp/traineroad/Low_Volume_II/workouts/1650.json"))

ZWIFT_XML = """
<workout_file>
    <author>Trainer Road - {plan_name}</author>
    <name>{name}</name>
    <description>{description}
    </description>
    <sportType>bike</sportType>
    <tags/>
    <workout>
"""

def generate_zwo(workout, plan_number, output_file):
    if os.path.exists(output_file):
        return
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    plan_name = [x['PlanName'] for x in workout['Plans']
                 if x['PlanId'] == plan_number][0]
    name = workout['Details']['WorkoutName']
    description = html2text.html2text(workout['Details']['GoalDescription'])
    zxml = ZWIFT_XML.format(
        plan_name=plan_name, name=name, description=description)

    for interval in workout['intervalData'][1:]:
        ts = float(interval['End'] - interval['Start'])
        power = interval['StartTargetPowerPercent'] / 100
        zxml += f'\t<SteadyState Duration="{ts}" Power="{power}" pace="0"/>\n'

    zxml += "</workout></workout_file>"
    open(output_file, 'w').write(zxml)
