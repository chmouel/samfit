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
import datetime
import re

import config

PACEREG = r"^(\d{1,2})'(\d\d)$"


class InvalidPaceSpec(Exception):
    pass


def totalseconds(spec):
    match = re.match(PACEREG, spec)
    if not match:
        raise InvalidPaceSpec()

    minute, secs = match.groups()
    return (int(minute) * 60) + int(secs)


def pace2speed(pace):
    ts = totalseconds(pace)
    return (1000 / ts) * 3.6


def speed2centimetersms(speed):  # garmin stuff
    return speed / 3600 / 0.001


def pace2seconds(pace):
    if "'" in pace:
        quote = "'"
    elif ":" in pace:
        quote = ":"
    return (int(pace[: pace.find(quote)]) * 60) + int(pace[pace.find(quote) + 1 :])


def seconds2pace(seconds):
    sp = str(datetime.timedelta(seconds=seconds)).split(":")
    sec = "%.2d" % int(sp[2][: sp[2].find(".")])
    return f"{sp[1]}'{sec}"


def convertTreshold(wtype, percent, run_pace, swim_pace, ftp):
    if percent == 0:
        return "still 🧘"

    if config.TP_TYPE[wtype] == "Running":
        tresholds = pace2seconds(run_pace)
        return seconds2pace(tresholds / percent * 100)
    if config.TP_TYPE[wtype] == "Swim":
        tresholds = pace2seconds(swim_pace)
        return seconds2pace(tresholds / percent * 100)
    elif config.TP_TYPE[wtype] == "Cycling":
        return round(ftp * percent / 100)


def timePace2distance(timeseconds, pace):
    timehour = timeseconds / 3600
    speed = pace2speed(pace)
    return (timehour * speed) * 1000
