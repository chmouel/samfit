#!/usr/bin/env python3
import calendar
import datetime
import click
import dateutil.parser as dtparser
import html2text

from .args import imports, tp_token_opt, tp_username_opt
from .tpapi import TPApi
from .tpsession import get_cache


@imports.command()
@tp_username_opt
@tp_token_opt
@click.option("--library-name", help="TP Library Name", required=True)
@click.option("--start-date", type=str, required=True)
@click.option("--plan-id", type=int, required=True)
def tr_plans_to_tp_calendar(
    username: str = "",
    token: str = "",
    library_name: str = "",
    plan_id: int = 0,
    start_date: str = None,
    verbose: bool = False,
):
    """Import plans from TR to TP Calendar."""
    verbose = True
    tpapi = TPApi(username=username, token=token, verbose=verbose)
    start_date = dtparser.parse(start_date)
    if start_date.weekday() != 0:
        raise Exception(f"{start_date.strftime('%a %d/%m')} should start on a monday")
    cursor_date = start_date - datetime.timedelta(days=1)

    plan = get_cache(f"plans/{plan_id}", verbose=verbose)["Plan"]
    if not plan:
        raise Exception(f"Plan {plan_id} was not found")

    _, workoutsLibrary = tpapi.get_workouts_from_library(library_name)
    athlete_id = tpapi.get_user_info()["user"]["personId"]
    plan_name = plan["Name"]
    if verbose:
        print(f"Import Plan: {plan_id}/{plan_name}")
    ret = {}

    switch_days = {"Tuesday": "Monday", "Thursday": "Wednesday", "Saturday": "Friday"}
    newplan = []
    for week in plan["Weeks"]:
        newweek = {}
        for item in week:
            if item not in calendar.day_name:
                newweek[item] = week[item]
        for key, value in switch_days.items():
            newweek[value] = week[value] + week[key]

        newplan.append(newweek)

    for week in newplan:
        for day in list(calendar.day_name):
            cursor_date = cursor_date + datetime.timedelta(days=1)
            if day == "Monday":
                wmon = {
                    "title": f'{week["Name"]} - {plan_name}',
                    "description": week["Description"],
                    "coachComment": week["Tips"],
                }
                ret.setdefault(cursor_date, []).append(wmon)
            if not day in week or not week[day]:  # empty
                continue

            for todayworkouts in week[day]:
                for w in workoutsLibrary:
                    wname = w["itemName"]
                    if wname == todayworkouts["Workout"]["Name"]:
                        # TODO: multiples??
                        ret.setdefault(cursor_date, []).append(
                            [w["exerciseLibraryItemId"], wname]
                        )
                        break

    for date, day in ret.items():
        for workout in day:
            if isinstance(workout, dict):  # NOTE: this is a note
                coachComment = (
                    workout["coachComment"]
                    and html2text.html2text(workout["coachComment"])
                    or ""
                )
                description = html2text.html2text(workout["description"] or "")
                tpapi.create_calendar_note(
                    banner_message="Note",
                    athlete_id=athlete_id,
                    date=date,
                    name=workout["title"],
                    coachComment=coachComment,
                    description=description,
                    title=workout["title"],
                )
            else:
                exerciseItemId, name = workout
                tpapi.create_calendar_workout_from_library(
                    name=name,
                    athlete_id=athlete_id,
                    exerciseLibraryItemId=exerciseItemId,
                    date=date,
                )
