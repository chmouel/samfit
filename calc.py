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
import re
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
    return ((1000 / ts) * 3.6)


def timePace2distance(timeseconds, pace):
    timehour = timeseconds / 3600
    speed = pace2speed(pace)
    return (timehour * speed) * 1000
