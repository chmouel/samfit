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
import traineroad
import config


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
        '-t',
        '--test',
        action='store_true',
        default=False,
        help="Test mode",
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

    if args.action == "tr_plan_to_tp":
        return traineroad.parse_plans(args)


if __name__ == '__main__':
    main(sys.argv[1:])
    # tp = trainingpeaks.TPSession.get_session()
    # tp.init()
