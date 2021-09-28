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
import datetime
import sys

import trainingpeaks.library as tplib
import trainingpeaks.calendar as tpcal
import traineroad
import traineroad_plan_md
import ical
import config
import plans
import zwift


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
        '--garmin-user',
        type=str,
        default=config.TP_USERNAME,
        help="Garmin username",
    )
    parser.add_argument(
        '--garmin-password',
        type=str,
        help="Garmin password",
    )

    parser.add_argument(
        '--tr-user',
        type=str,
        default=config.TR_USERNAME,
        help="Trainerroad username",
    )

    parser.add_argument(
        '--tr-password',
        type=str,
        help="Trainerroad password",
    )

    parser.add_argument(
        '--user-cycling-ftp',
        type=int,
        default=config.USER_FTP,
        help="User Cycling FTP",
    )

    parser.add_argument(
        '--user-run-pace',
        type=str,
        default=config.USER_RUN_PACE,
        help="User Run Treshold Pace",
    )

    parser.add_argument(
        '--user-swim-pace',
        type=str,
        default=config.USER_SWIM_PACE,
        help="User Swim Treshold Pace",
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

    show_plan.add_argument(
        '--no-color',
        '-N',
        default=False,
        action='store_true',
        help="Don't store colours",
    )

    show_plan.add_argument(
        '--start-date',
        type=str,
        default=str(datetime.datetime.now()),
        help="Start Date",
    )

    show_plan.add_argument(
        "--end-date",
        type=str,
        help="End Date",
    )

    show_plan.add_argument(
        '--date',
        type=str,
        help="Show at this specific date",
    )

    show_plan.add_argument(
        '--today',
        '-t',
        action='store_true',
        default=False,
        help="Show only today",
    )

    show_plan.add_argument(
        '--sync-garmin',
        action='store_true',
        default=False,
        help="Sync to Garmin.",
    )

    show_plan.add_argument(
        '--sync-force',
        action='store_true',
        default=False,
        help="Force sync even if already there.",
    )

    show_plan.add_argument(
        '--sync-only-delete',
        action='store_true',
        default=False,
        help="Just delete.",
    )

    show_plan.add_argument(
        '--week',
        '-w',
        action='store_true',
        default=False,
        help="Show only this week",
    )

    show_plan.add_argument(
        '--no-description',
        '-D',
        action='store_true',
        default=False,
        help="Show description",
    )

    plan_to_ical = mainparser.add_parser('plan_to_ical',
                                         help="Generate iCal from a plan.")

    plan_to_ical.add_argument(
        dest="plan_name",
        type=str,
        help="Plan name",
    )

    plan_to_ical.add_argument(
        "calendar_title",
        type=str,
        help="Calendar title",
    )

    plan_to_ical.add_argument(
        dest="start_date",
        type=str,
        help="Start Date",
    )

    plan_to_ical.add_argument(
        dest="output_file",
        type=str,
        help="Output file",
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

    tp_calendar_workouts_ical = mainparser.add_parser(
        'tp_calendar_workouts_ical',
        help="Get all TrainingPeaks workouts from calendar and "
        " output it to an iCal file.")

    tp_calendar_workouts_ical.add_argument(
        dest="from_date",
        type=str,
        help="From date",
    )

    tp_calendar_workouts_ical.add_argument(
        dest="to_date",
        type=str,
        help="To date",
    )

    tp_calendar_workouts_ical.add_argument(
        dest="output_file",
        type=str,
        help="iCal output file",
    )

    tp_calendar_workouts_ical.add_argument(
        '--generated-output-file',
        type=str,
        help="Where to output the TP.",
    )

    tp_calendar_workouts_ical.add_argument(
        '--calendar-title',
        type=str,
        help="Calendar title.",
    )

    tp_calendar_workouts_ical.add_argument(
        '--no-cache',
        action='store_true',
        default=False,
        help="Decide if we want to use cache",
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

    tp_get_calendar_workouts.add_argument(
        '--no-cache',
        action='store_true',
        default=False,
        help="Don't do caching when getting workouts",
    )

    stuff_to_do = mainparser.add_parser('stuff_to_do',
                                        help="Do some stuff on tp calendar.")

    stuff_to_do.add_argument(
        dest="from_date",
        type=str,
        help="From date",
    )

    stuff_to_do.add_argument(
        dest="to_date",
        type=str,
        help="To date",
    )

    stuff_to_do.add_argument(
        '--no-cache',
        action='store_true',
        default=False,
        help="Don't do caching when getting workouts",
    )

    zwift_generate_zwo = mainparser.add_parser(
        'zwift_generate_zwo', help="Generate zwift workouts from activity")

    zwift_generate_zwo.add_argument(
        '--output_dir',
        type=str,
        help="Output Directory for zwift files",
    )

    zwift_generate_zwo.add_argument(
        'workout',
        type=str,
        nargs="+",
        help="Workout file name or all to get everything",
    )

    tp_import_tr_workouts = mainparser.add_parser(
        'tp_import_tr_workouts', help="Import all TR workouts in TP libraries")

    tp_import_tr_workouts.add_argument(
        '--update',
        action='store_true',
        default=False,
        help="Update instead of erroring if already present",
    )

    tp_import_tr_workouts.add_argument(
        '--no-cache',
        action='store_true',
        default=False,
        help="Don't do caching when getting workouts",
    )

    tp_import_tr_workouts.add_argument(
        '--include-dummies',
        action='store_true',
        default=False,
        help="Do we include the dummy workouts that doesn't have any comments?",
    )

    tp_import_tr_workouts.add_argument(
        '--everything',
        action='store_true',
        default=False,
        help="Import everything?",
    )

    tp_import_tr_workouts.add_argument(
        '--library-name',
        type=str,
        default="TrainerRoad",
        help="The library name where to upload the workout we want",
    )

    tp_import_tr_workouts.add_argument(
        'workout_ids',
        nargs='+',
        type=int,
        help='Import those workout ids',
    )

    tr_generate_md = mainparser.add_parser('tr_generate_md',
                                           help="Generate TR Plan in markdown")

    tr_generate_md.add_argument(
        '--markdown-dir',
        required=True,
        type=str,
        help="Document dire where we generate the markdown file",
    )

    tr_generate_md.add_argument(
        '-p',
        '--plan-number',
        required=True,
        nargs="+",
        type=str,
        help="Plan number",
    )

    tr_get_plan = mainparser.add_parser(
        'tr_get_plan', help="Get TR Plan and dump it in the cache")

    tr_get_plan.add_argument(
        '-p',
        '--plan-number',
        required=True,
        nargs="+",
        type=str,
        help="Plan number",
    )

    tr_plan_to_tp = mainparser.add_parser('tr_plan_to_tp',
                                          help="Output TR plan to TP calendar")

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

    tr_unapply_plan_on_tp = mainparser.add_parser('tr_unapply_plan_on_tp',
                                                  help="Unapply plan on TP")

    tr_unapply_plan_on_tp.add_argument(
        '-p',
        '--plan-number',
        required=True,
        type=str,
        help="Plan number",
    )

    tr_unapply_plan_on_tp.add_argument(
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

    if args.action == "tr_unapply_plan_on_tp":
        return traineroad.unapply_plan(args)

    if args.action == "tr_get_plan":
        return traineroad.get_plan(args)

    if args.action == "tr_generate_md":
        return traineroad_plan_md.generate(args)

    if args.action == "tp_get_calendar_workouts":
        return tpcal.get_calendar_workouts(args)

    if args.action == "stuff_to_do":
        return tpcal.stuff_to_do(args)

    if args.action == "tp_calendar_workouts_ical":
        return tpcal.calendar_workouts_ical(args)

    if args.action == "tp_import_plan":
        return tpcal.import_plan(args)

    if args.action == "tp_add_cadence_to_library":
        return tplib.add_cadence_plan(args)

    if args.action == "show_plan":
        return plans.show_plan(args)

    if args.action == "plan_to_ical":
        return ical.plan_to_ical(args)

    if args.action == "zwift_generate_zwo":
        return zwift.generate_zwo(args)

    parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
    # tp = trainingpeaks.TPSession.get_session()
    # tp.init()
