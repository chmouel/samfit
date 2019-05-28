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

import humanfriendly


def get_password_from_osx(service, account):
    return subprocess.Popen([
        "security", "find-generic-password", "-a", account, "-s", service, "-w"
    ],
                            stdout=subprocess.PIPE).communicate()[0].strip()


def get_or_cache(getter, url, obj, cache=True):
    if obj.startswith("/"):
        fpath = obj + ".json"
    else:
        fpath = os.path.join(config.BASE_DIR, "cache", obj + ".json")

    if cache:
        if os.path.exists(fpath):
            return json.load(open(fpath, 'r'))
        if os.path.exists(fpath + ".gz"):
            return json.load(gzip.open(fpath + ".gz"))

    jeez = getter(url)
    if 'ExceptionMessage' in jeez:
        print(f"Error getting: {url}: {jeez['ExceptionMessage']}")
        return None
    json.dump(jeez, open(fpath, 'w'))
    return jeez


def get_filej(fff, dtype="plans"):
    pf = None
    if not fff.startswith("/"):
        pf = os.path.join(config.BASE_DIR, dtype, f"{fff}.json")
    if os.path.exists(pf + ".gz"):
        pf = pf + ".gz"

    if not pf:
        return {}

    if pf.endswith(".gz") or os.path.exists(pf + ".gz"):
        fp = gzip.open(pf)
    else:
        fp = open(pf)

    return json.load(fp)


def ppt(ss, ppt='-', ll=None):
    if not ll:
        ll = len(ss)
    ret = ss + "\n"
    ret += ppt * ll + "\n"
    return ret


def secondsToText(amount):
    return humanfriendly.format_timespan(amount)


def colourText(text, color, colorize=True):
    if not colorize or not color:
        return text

    colours = {
        'red': "\033[1;31m",
        'title': "\033[4;40m",
        'yellow': "\033[1;33m",
        'blue': "\033[1;34m",
        'blue_reverse': "\033[1;44m",
        'cyan': "\033[1;36m",
        'cyan_surligned': "\033[4;36m",
        'cyan_italic': "\033[3;37m",
        'green': "\033[1;32m",
        'grey': "\033[1;30m",
        'magenta_surligned': "\033[4;35m",
        'magenta': "\033[1;35m",
        'white': "\033[1;37m",
        'white_italic': "\033[0;37m",
        'reset': "\033[0;0m",
    }
    s = f"{colours[color]}{text}{colours['reset']}"
    return s


def addSpaceToString(s, spaces=2):
    ret = []
    longest = 0
    for x in s.split("\r\n"):
        longest = len(x) > longest and len(x)
        ret.append(f"  {x}")
    return "\n".join(ret)
