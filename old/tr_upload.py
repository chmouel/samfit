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
import subprocess
import os
import glob
import json
import gzip
import random

import tp

TP_USERNAME = 'chmouel'
BASE_DIR = os.path.expanduser("~/Dropbox/Documents/Fitness/traineroad")

if __name__ == '__main__':
    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainerroad", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()
    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainingpeaks", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()
    tpsess = tp.TPconnect(TP_USERNAME, password)

    RANGE = [x for x in glob.glob(
        os.path.join(BASE_DIR, "workout", "*.json*"))]
    
    for x in RANGE:
        if x.endswith(".gz"):
            workoutd = json.load(gzip.open(x))
        else:
            workoutd = json.load(open(x))

        tpsess.create_tr_workout(workoutd, 12345)
