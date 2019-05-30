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

import ics

import config
import plans


def generate_ical(args, events):
    @ics.Calendar._outputs
    def o_custom(calendar, container):
        if args.calendar_title:
            container.append(f"X-WR-CALNAME:{args.calendar_title}")
            container.append(f"X-WR-CALDESC: Road to {args.calendar_title}")
        container.append(f"X-WR-TIMEZONE: {config.TIME_ZONE}")

    return str(ics.Calendar(events=events))


def generate_event(current, args, cursor_date):
    event = ics.Event()

    if current["totalTimePlanned"]:
        event.duration = datetime.timedelta(
            seconds=(current["totalTimePlanned"] * (60 * 60)))

    event.description = current["description"] and current[
        "description"].replace("\r", "") or ""

    title, pp = plans.show_workout(
        args, current, colorize=False, showtss=False, extranewlines=True)
    event.name = title or ""
    if pp:
        event.description += "\nExercises:\n\n" + pp.replace("\r", "\n")

    if current["coachComments"]:
        event.description += "\n\nCommentaire du Coach:\n"
        event.description += current["coachComments"].replace("\r", "\n")

    event.begin = cursor_date
    if current["totalTimePlanned"]:
        cursor_date = cursor_date + datetime.timedelta(
            minutes=30) + datetime.timedelta(
                seconds=current["totalTimePlanned"] * (60 * 60))

    return event
