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
import json
import dateutil.parser as parser
import calendar
import datetime


class DateError(Exception):
    pass


class TRToICS(object):
    def __init__(self, plan, start):
        self.plan = plan
        self.date = parser.parse(start)
        self.cursor_date = self.date - datetime.timedelta(days=1)
        if self.date.weekday() != 0:
            raise DateError("%s don't start on a monday" % (self.date.today()))

    def parse(self):
        ret = {}

        for week in self.plan['Weeks']:
            for day in week:
                if day not in list(calendar.day_name):  # not days
                    continue

                # Do this here since they are days!
                self.cursor_date = self.cursor_date + datetime.timedelta(
                    days=1)

                if not week[day]:  # empty
                    continue
                ret[self.cursor_date] = week[day]
        return ret


if __name__ == "__main__":
    jeez = json.load(open("/tmp/a.json"))
    c = TRToICS(jeez, "Monday 10 December 2018")
    import pprint
    pprint.pprint(c.parse())
