#!/usr/bin/env python3
import glob
import os
import re
import click
import html2text

from .args import imports, tp_token_opt, tp_username_opt
from .tpsession import do_curl
from .tpapi import TPApi
from .config import BASE_DIR, TP_TYPE_REV, ACTIVE_CADENCE_MAX, ACTIVE_CADENCE_MIN


def add_cadence_plan(workout: dict) -> list:
    steps = []
    for step in workout["structure"]["structure"]:
        for sub in step["steps"]:
            if sub["intensityClass"] == "active" and len(sub["targets"]) == 2:
                sub["targets"] = [sub["targets"][0]]

            if sub["intensityClass"] == "active" and len(sub["targets"]) == 1:
                step["steps"][0]["targets"].append(
                    {
                        # TODO: make those configurale
                        "maxValue": ACTIVE_CADENCE_MAX,
                        "minValue": ACTIVE_CADENCE_MIN,
                        "unit": "roundOrStridePerMinute",
                    }
                )
        steps.append(step)
    return steps


def convert_tr2tp(workout: dict, library_id: int) -> dict:
    if (
        not workout["Details"]["WorkoutDescription"]
        or not workout["Details"]["GoalDescription"]
    ):
        return {}

    category_text = ""
    for x in workout["Tags"]:
        category_text += "#" + x["Text"].replace(" ", "_") + " "

    desc = workout["Details"]["WorkoutDescription"] + "\n\n" + category_text

    coachComments = workout["Details"]["GoalDescription"]
    ret = {
        "description": html2text.html2text(desc),
        "coachComments": html2text.html2text(coachComments),
        "exerciseId": None,
        "workoutTypeId": TP_TYPE_REV["Cycling"],
        "itemName": workout["Details"]["WorkoutName"],
        "tssPlanned": workout["Details"]["TSS"],
        "ifPlanned": float(workout["Details"]["IntensityFactor"] / 100),
        "totalTimePlanned": float(workout["Details"]["Duration"] / 60),
        "distancePlanned": None,
        "velocityPlanned": None,
        "exerciseLibraryId": library_id,
        "structure": {
            "primaryIntensityTargetOrRange": "target",
            "primaryIntensityMetric": "percentOfFtp",
            "primaryLengthMetric": "duration",
            "structure": [],
        },
    }

    total = len(workout["intervalData"][1:]) - 1
    count = 0
    for interval in workout["intervalData"][1:]:
        name = interval["Name"]
        intensityClass = "active"

        if name == "Fake" and count == 0:
            name = "Warm up"
            intensityClass = "warmUp"
        elif name == "Fake" and count == total:
            name = "Cool Down"
            intensityClass = "coolDown"
        elif name == "Fake":
            intensityClass = "rest"
            name = "Recovery"
        step = {
            "type": "step",
            "length": {"value": 1, "unit": "repetition"},
            "steps": [
                {
                    "name": name,
                    "length": {
                        "value": int(interval["End"] - interval["Start"]),
                        "unit": "second",
                    },
                    "targets": [{"minValue": int(interval["StartTargetPowerPercent"])}],
                    "intensityClass": intensityClass,
                    "openDuration": False,
                }
            ],
        }

        count += 1
        ret["structure"]["structure"].append(step)
    return ret


@imports.command()
@tp_username_opt
@tp_token_opt
@click.option("--library-name", help="TP Library Name", required=True)
@click.option("--everything", is_flag=True, help="Import everything")
@click.argument("workout_ids", nargs=-1)
def tr_workouts_to_tp_library(
    username: str = "",
    token: str = "",
    library_name: str = "",
    workout_ids: list[str] = None,
    everything: bool = False,
):
    """Import workouts from TR to TP Library."""
    verbose = True
    if not workout_ids and not everything:
        raise click.ClickException(
            "No files specified, or at least specify --everything"
        )

    tpapi = TPApi(username=username, token=token, verbose=verbose)

    if verbose:
        print(f"Getting workouts library for user {username}")
    library_id, library_workouts = tpapi.get_workouts_from_library(library_name)
    workout_ids = set(workout_ids)
    if everything:
        workout_ids = sorted(
            [
                int(re.sub(r"(\d+).*", r"\1", os.path.basename(x)))
                for x in glob.glob(os.path.join(BASE_DIR, "workout", "*.json*"))
            ]
        )

    for workout_id in workout_ids:
        if verbose:
            print(f"Importing workout {workout_id}")
        workout = do_curl(
            token,
            f"/workoutdetails/{workout_id}",
            verbose=verbose,
            cache_id=f"workout/{workout_id}",
        )
        if "Workout" in workout:
            workout = workout["Workout"]
        workout_name = workout["Details"]["WorkoutName"]
        print(f"Workout ID: {workout_id}, Name: {workout_name}")
        if workout_name in [x["itemName"] for x in library_workouts]:
            print(f"SKIPPING: {workout_name} already exists in library")
            continue

        data = convert_tr2tp(workout, library_id)
        if not data:
            print(f"Skipping '{workout_name}' not an interesting one")
            continue
        steps = add_cadence_plan(data)
        data["structure"]["structure"] = steps
        url = f"/exerciselibrary/v1/libraries/{library_id}/items"
        method = "POST"
        do_curl(token, url, method=method, data=data, verbose=verbose).decode("utf-8")
