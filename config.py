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
import json
import subprocess
import gzip

TR_USERNAME = 'samfit'
TP_USERNAME = 'chmouel'
BASE_DIR = os.path.expanduser("~/Dropbox/Documents/Fitness/traineroad")
TP_CYCLING_TYPE_ID = 2
TP_OTHER_TYPE_ID = 100


def get_password_from_osx(account, service):
    return subprocess.Popen([
        "security", "find-generic-password", "-a", account, "-s", service, "-w"
    ],
                            stdout=subprocess.PIPE).communicate()[0].strip()


def get_or_cache(getter, url, obj):
    if obj.startswith("/"):
        fpath = obj + ".json"
    else:
        fpath = os.path.join(BASE_DIR, "cache", obj + ".json")

    if os.path.exists(fpath):
        return json.load(open(fpath, 'r'))
    if os.path.exists(fpath + ".gz"):
        return json.load(gzip.open(fpath + ".gz"))

    if not os.path.exists(fpath):
        jeez = getter(url)
        json.dump(jeez, open(fpath, 'w'))
        return jeez
