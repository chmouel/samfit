import datetime

import calc
import calendar
import config
import garmin_connect
import garmin_workout
import utils

import dateutil.parser as dtparser
import humanfriendly


def show_workout(args,
                 workout,
                 colorize=True,
                 showtss=True,
                 extranewlines=False):
    if config.TP_TYPE[
            workout['workoutTypeValueId']] in config.TP_TYPE_EMOJI_MAP:
        emoji = config.TP_TYPE_EMOJI_MAP[config.TP_TYPE[
            workout['workoutTypeValueId']]]
    else:
        emoji = '<0001f3fc><200d>♂<fe0f>'
    title = f"{emoji}"

    title += f"{workout['title']}"

    if workout.get('structure') and workout['structure'][
            'primaryLengthMetric'] == 'distance':
        wtype = 'distance'
    elif workout.get('structure') and workout['structure'][
            'primaryLengthMetric'] == 'duration':
        wtype = 'duration'

    if workout.get('structure') and len(workout['structure']['structure']) > 1:
        if 'end' in workout['structure']['structure'][-1]:
            if wtype == 'duration':
                total_time = utils.secondsToText(
                    workout['structure']['structure'][-1]['end'])
            elif wtype == 'distance':
                total_time = humanfriendly.format_length(
                    workout['structure']['structure'][-1]['end'])
        else:
            total_time = "As long as you want"
        title += f" {total_time}"

    if showtss and workout['tssPlanned']:
        title += f" - TSS: {round(workout['tssPlanned'])}"
    title += "\n"
    if extranewlines:
        title += "\n"

    title = utils.colourText(title, 'title', colorize=colorize)

    if not workout.get('structure'):
        return (title, None)

    ret = ''
    for structure in workout['structure']['structure']:
        ret += "  - "
        if structure['type'] == 'repetition' and  \
           structure['length']['value'] != 1:
            s = utils.colourText(
                structure['length']['value'], 'magenta', colorize=colorize)
            ret += f"{s} * "

        if len(structure['steps']) > 1:
            ret += "("
        for step in structure['steps']:
            st = ''
            maxvalue = step['targets'][0].get('maxValue',
                                              step['targets'][0]['minValue'])
            minvalue = step['targets'][0]['minValue']
            color = ''
            paceMax = calc.convertTreshold(
                workout['workoutTypeValueId'], maxvalue, args.user_run_pace,
                args.user_swim_pace, args.user_cycling_ftp)
            paceMin = calc.convertTreshold(
                workout['workoutTypeValueId'], minvalue, args.user_run_pace,
                args.user_swim_pace, args.user_cycling_ftp)

            if step['intensityClass'] == "warmUp":
                s = "Warm Up for"
                color = 'white_bold'
            elif step['intensityClass'] == "coolDown":
                s = "Warm Down for"
                color = 'white_bold'
            elif step['intensityClass'] == "rest":
                if minvalue == 0:
                    s = "Rest"
                else:
                    s = "Easy"
                if structure['length']['value'] > 1:
                    color = 'cyan'
                else:
                    color = 'white_bold'
            elif step['intensityClass'] == "active":
                if structure['length']['value'] == 1:
                    s = 'Active for'
                else:
                    s = ''

                color = 'green'
                if minvalue > 80:
                    color = 'blue'
                if minvalue > 90:
                    color = 'yellow'
                if minvalue > 100:
                    color = 'red'
            else:
                s = step['intensityClass']
            st += f"{s} "
            if wtype == 'duration':
                st += utils.secondsToText(step['length']['value']) + " "
            elif wtype == 'distance':
                st += humanfriendly.format_length(
                    step['length']['value']) + " "
            st += f"at {paceMin} - {paceMax}"
            if config.TP_TYPE[workout['workoutTypeValueId']] == 'Cycling':
                st += f" watts"

            if config.TP_TYPE[workout[
                    'workoutTypeValueId']] == 'Running' and wtype == 'duration':
                st += " for a distance between " + humanfriendly.format_length(
                    int(
                        calc.timePace2distance(step['length']['value'],
                                               paceMin)))
                st += " - " + humanfriendly.format_length(
                    int(
                        calc.timePace2distance(step['length']['value'],
                                               paceMax)))

            if minvalue > 0:
                st += " [" + str(round(minvalue)) + "%]"

            ret += utils.colourText(st, color, colorize=colorize)

            if structure['steps'][-1] != step:
                ret += "\n          "

        if len(structure['steps']) > 1:
            ret += ")"
        ret += "\n"

        if extranewlines:
            ret += "\n"
    return (title, ret)


def show_plan(args):
    ret = ''
    cursor_date = dtparser.parse(args.start_date)
    cursor_date = cursor_date - datetime.timedelta(days=1)

    if args.sync_garmin:
        gcnx = garmin_connect.GarminOPS(args)

    plan = utils.get_filej(args.plan_file)
    if not plan:
        raise Exception(f"Cannot find plan: {args.plan_file}")

    if args.date:
        args.today = dtparser.parse(args.date)
    elif args.today:
        args.today = datetime.datetime.now()
    if args.today:
        args.description = True

    for week in plan:
        week_str = ''
        print_week = False

        if not args.today:
            week_str += utils.ppt(f"\nWeek: {week['Week']}", ppt='=')

        for day in list(calendar.day_name):
            cursor_date = cursor_date + datetime.timedelta(days=1)
            if args.week:
                tdd = datetime.datetime.now()
            elif args.today:
                tdd = args.today
            else:
                tdd = cursor_date
            if args.today and \
               (cursor_date.strftime("%Y%m%d") != tdd.strftime("%Y%m%d")):
                continue
            elif args.sync_garmin:
                if day not in week['Workouts']:
                    continue
                for gw in week['Workouts'][day]:
                    garmin_workout.tpWorkoutGarmin(gw, tdd, args, gcnx)
                continue

            if args.week and \
               (cursor_date.strftime("%Y%m%d") == tdd.strftime("%Y%m%d")):
                print_week = True
            elif args.week and not print_week:
                continue

            if day not in week["Workouts"] \
               or not week["Workouts"][day]:  # empty
                continue

            daysw = week['Workouts'][day]

            tssPlanned = 0
            numberOfWorkouts = 0
            for w in daysw:
                if w['tssPlanned']:
                    tssPlanned += w['tssPlanned']
                if w['workoutTypeValueId'] not in (config.TP_NOTE_TYPE_ID,
                                                   config.TP_REST_TYPE_ID,
                                                   config.TP_OTHER_TYPE_ID):
                    numberOfWorkouts += 1

            if numberOfWorkouts == 0:
                s = f"\n# {cursor_date.strftime('%A %d %b')}: Rest Day 😴🛌💤"
            else:
                s = f"\n# {cursor_date.strftime('%A %d %b')}: {numberOfWorkouts} Workout"

            s = utils.colourText(s, 'white', colorize=not args.no_color)
            week_str += s + "\n"

            for w in daysw:
                # NOTE(chmou): this is already done workout, let's skip this
                if w['distance']:
                    continue

                if w['workoutTypeValueId'] in (config.TP_NOTE_TYPE_ID,
                                               config.TP_REST_TYPE_ID,
                                               config.TP_OTHER_TYPE_ID):
                    continue

                title, pw = show_workout(args, w, colorize=not args.no_color)

                if title and pw:
                    week_str += "\n* " + title + "\n" + pw + "\n"
                else:
                    tt = config.TP_TYPE[int(w['workoutTypeValueId'])]
                    emoji = ''
                    if tt == 'Swim':
                        emoji = '🏊‍'
                    elif tt == 'Strength':
                        emoji = '🏋️‍'

                    week_str += f"\n* {emoji} {tt}: {w['title']}\n\n"

                if not args.no_description and w['description']:
                    week_str += utils.colourText(
                        "Description:", "yellow",
                        colorize=not args.no_color) + "\n" + "\n"
                    week_str += utils.addSpaceToString(
                        w['description']) + "\n\n"

                if not args.no_description and w['coachComments']:
                    week_str += utils.colourText(
                        "Coach Comment:", "yellow",
                        colorize=not args.no_color) + "\n"
                    week_str += utils.addSpaceToString(
                        w['coachComments']) + "\n\n"

        if args.week and not print_week:
            continue

        ret += week_str

    if args.sync_garmin:
        return
    elif args.today and not ret:
        print(f"Nothing to do today {config.TP_TYPE_EMOJI_MAP['Rest']}")
    elif ret:
        print(ret)
