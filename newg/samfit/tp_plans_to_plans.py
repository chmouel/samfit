#!/usr/bin/env python
import calendar as gcal
import datetime
import time

import click
import dateutil.parser as dtparser

from .args import imports, tp_token_opt, tp_username_opt
from .config import TP_TYPE_REV
from .tpapi import TPApi
from .tpsession import get_cache


@imports.command()
@tp_username_opt
@tp_token_opt
@click.argument("plan_name")
@click.argument("start_date")
def tp_plans_to_plans(
    username: str = "",
    token: str = "",
    verbose: bool = False,
    plan_name: str = "",
    start_date: str = "",
):
    """import saved tp plans to tp"""
    tpapi = TPApi(username=username, token=token, verbose=verbose)
    athlete_id = tpapi.get_user_info()["user"]["personId"]
    date = dtparser.parse(start_date)
    if date.weekday() != 0:
        raise Exception(f"{start_date} don't start on a monday")

    plan = get_cache(f"plans/TP-{plan_name}", verbose=verbose)
    if not plan:
        raise Exception(f"Plan {plan_name} was not found")

    cursor_date = date - datetime.timedelta(days=1)
    cursor_date = cursor_date.replace(hour=7, minute=0)
    ret = {}
    for week in plan:
        for day in list(gcal.day_name):
            # Do this here since they are days and before we skip to next ones,
            cursor_date = cursor_date + datetime.timedelta(days=1)
            cursor_date = cursor_date.replace(hour=7, minute=0)
            if day not in week["Workouts"] or not week["Workouts"][day]:  # empty
                continue

            dayp = []
            for workout in week["Workouts"][day]:
                workout["athleteId"] = athlete_id
                workout["lastModifiedDate"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                )
                workout["workoutDay"] = cursor_date.strftime("%Y-%m-%d")
                workout["startTimePlanned"] = cursor_date.strftime("%Y-%m-%dT%H:%m")
                dayp.append(workout)
                if workout["workoutTypeValueId"] != TP_TYPE_REV["Other"]:
                    cursor_date = cursor_date + datetime.timedelta(hours=1)
            ret[cursor_date] = dayp

    for day in ret.values():
        for workout in ret[day]:
            tpapi.create_calendar_workout(workout, day, True)
            time.sleep(2)
