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

import config


def get_password_from_osx(service, account):
    return subprocess.Popen([
        "security", "find-generic-password", "-a", account, "-s", service, "-w"
    ],
                            stdout=subprocess.PIPE).communicate()[0].strip()


def get_or_cache(getter, url, obj):
    if obj.startswith("/"):
        fpath = obj + ".json"
    else:
        fpath = os.path.join(config.BASE_DIR, "cache", obj + ".json")

    if os.path.exists(fpath):
        return json.load(open(fpath, 'r'))
    if os.path.exists(fpath + ".gz"):
        return json.load(gzip.open(fpath + ".gz"))

    if not os.path.exists(fpath):
        jeez = getter(url)
        json.dump(jeez, open(fpath, 'w'))
        return jeez


def get_filej(fff):
    pf = None
    if not fff.startswith("/"):
        pf = os.path.join(config.BASE_DIR, "plans", f"{fff}.json")
    if os.path.exists(pf + ".gz"):
        pf = pf + ".gz"

    if not pf:
        return {}

    if pf.endswith(".gz") or os.path.exists(pf + ".gz"):
        fp = gzip.open(pf)
    else:
        fp = open(pf)

    return json.load(fp)


def ppt(ss, ppt='-'):
    print(ss)
    print(ppt * len(ss))
