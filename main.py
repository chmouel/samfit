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
import argparse
import sys

import trainingpeaks.library as tplib
import trainingpeaks.calendar as tpcal
import traineroad
import config
import showplan


def parse_args():
    parser = argparse.ArgumentParser(description='SamFIiiT.')

    mainparser = parser.add_subparsers(help='action to run', dest='action')
    parser.add_argument(
        '--tp-user',
        type=str,
        default=config.TP_USERNAME,
        help="Trainingpeaks username",
    )
    parser.add_argument(
        '--tp-password',
        type=str,
        help="Trainingpeaks password",
    )

    parser.add_argument(
        '--tr-user',
        type=str,
        default=config.TR_USERNAME,
        help="Trainerroad username",
    )

    parser.add_argument(
        '--user-ftp',
        type=int,
        default=config.USER_FTP,
        help="User FTP",
    )

    parser.add_argument(
        '--user-pace',
        type=str,
        default=config.USER_PACE,
        help="User Treshold Pace",
    )

    parser.add_argument(
        '-t',
        '--test',
        action='store_true',
        default=False,
        help="Test mode",
    )

    tp_add_cadence_to_library = mainparser.add_parser(
        'tp_add_cadence_to_library',
        help="Add a cadence to all library workouts")

    tp_add_cadence_to_library.add_argument(
        '-l',
        '--filter-library-regexp',
        default=r"^TR-",
        type=str,
        help="Rexgexp for Libraries",
    )

    tp_get_all_workouts = mainparser.add_parser(
        'tp_get_all_workouts',
        help="Get all TrainingPeaks workouts id to a JSON file")

    tp_get_all_workouts.add_argument(
        '-l',
        '--filter-library-regexp',
        default=r"^TR-",
        type=str,
        help="Rexgexp for Libraries",
    )

    show_plan = mainparser.add_parser('show_plan', help="Show plan.")
    show_plan.add_argument(
        dest="plan_file",
        type=str,
        help="Plan file",
    )

    tp_import_plan = mainparser.add_parser(
        'tp_import_plan',
        help="Import our own generated plan starting from a date.")

    tp_import_plan.add_argument(
        dest="plan_file",
        type=str,
        help="Plan file",
    )

    tp_import_plan.add_argument(
        dest="start_date",
        type=str,
        help="Start date",
    )

    tp_get_calendar_workouts = mainparser.add_parser(
        'tp_get_calendar_workouts',
        help="Get all TrainingPeaks workouts from calendar dates and "
        " output it nicely to a file.")

    tp_get_calendar_workouts.add_argument(
        dest="from_date",
        type=str,
        help="From date",
    )

    tp_get_calendar_workouts.add_argument(
        dest="to_date",
        type=str,
        help="To date",
    )

    tp_get_calendar_workouts.add_argument(
        dest="output_file",
        type=str,
        help="Output file",
    )

    tp_import_tr_workouts = mainparser.add_parser(
        'tp_import_tr_workouts', help="Import all TR workouts in TP libraries")

    tp_import_tr_workouts.add_argument(
        '--include-dummies',
        action='store_true',
        default=False,
        help="Do we incly the dummy workout that doesn't have any comments?",
    )

    tp_import_tr_workouts.add_argument(
        '--library-name',
        type=str,
        default="TrainerRoad",
        help="The library name where to upload the workout we want",
    )

    tr_plan_to_tp = mainparser.add_parser(
        'tr_plan_to_tp', help="Output TR plan to TP calendar")

    tr_plan_to_tp.add_argument(
        '-p',
        '--plan-number',
        required=True,
        type=str,
        help="Plan number",
    )

    tr_plan_to_tp.add_argument(
        '--library-name',
        required=True,
        type=str,
        help="Library name where we are going to add the stuff",
    )

    tr_plan_to_tp.add_argument(
        '-s',
        '--start-date',
        required=True,
        type=str,
        help="Start date of the plan",
    )

    return parser


def main(arguments):
    parser = parse_args()
    args = parser.parse_args(arguments)

    if args.action == "tp_get_all_workouts":
        return tplib.get_all_workouts_library(args)

    if args.action == "tp_import_tr_workouts":
        return tplib.import_tr_workouts(args)

    if args.action == "tr_plan_to_tp":
        return traineroad.parse_plans(args)

    if args.action == "tp_get_calendar_workouts":
        return tpcal.get_calendar_workouts(args)

    if args.action == "tp_import_plan":
        return tpcal.import_plan(args)

    if args.action == "tp_add_cadence_to_library":
        return tplib.add_cadence_plan(args)

    if args.action == "show_plan":
        return showplan.show_plan(args)

    parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
    # tp = trainingpeaks.TPSession.get_session()
    # tp.init()
