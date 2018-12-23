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

TR_USERNAME = 'samfit'
TP_USERNAME = 'chmouel'
BASE_DIR = os.path.expanduser("~/Dropbox/Documents/Fitness/traineroad")

# TODO: remove this and move to TP_TYPE
TP_CYCLING_TYPE_ID = 2
TP_OTHER_TYPE_ID = 100
TP_NOTE_TYPE_ID = 10
TP_REST_TYPE_ID = 7

TP_TYPE = {
    100: 'Other',
    10: 'Note',
    1: 'Swim',
    2: 'Cycling',
    3: 'Running',
    7: 'Rest',
    9: 'Strength',
}

ACTIVE_CADENCE_MIN = 95
ACTIVE_CADENCE_MAX = 105

USER_FTP = 245
USER_PACE = "4'50"

# In osx keychain if we don't want to pass the password in clears
TP_SECURITY_ACCOUNT = 'chmouel'
TP_SECURITY_SERVICE = 'trainingpeaks'
