import calendar
import datetime

import config
import utils

import dateutil.parser as dtparser

import ical


def convert_pace_to_seconds(pace):
    if "'" in pace:
        quote = "'"
    elif ":" in pace:
        quote = ":"
    return (int(pace[:pace.find(quote)]) * 60) + int(
        pace[pace.find(quote) + 1:])


def convert_seconds_to_pace(seconds):
    sp = str(datetime.timedelta(seconds=seconds)).split(":")
    sec = "%.2d" % int(sp[2][:sp[2].find(".")])
    return f"{sp[1]}'{sec}"


def convertTreshold(wtype, percent, run_pace, swim_pace, ftp):
    if percent == 0:
        return "still 🧘"

    if config.TP_TYPE[wtype] == 'Running':
        tresholds = convert_pace_to_seconds(run_pace)
        return convert_seconds_to_pace(tresholds / percent * 100)
    if config.TP_TYPE[wtype] == 'Swim':
        tresholds = convert_pace_to_seconds(swim_pace)
        return convert_seconds_to_pace(tresholds / percent * 100)
    elif config.TP_TYPE[wtype] == 'Cycling':
        return round(ftp * percent / 100)


def show_workout(args,
                 workout,
                 colorize=True,
                 showtss=True,
                 extranewlines=False):
    if config.TP_TYPE[workout['workoutTypeValueId']] == 'Running':
        emoji = '🏃'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Cycling':
        emoji = '🚴'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Swim':
        emoji = '🏊'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Other':
        emoji = '💡'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Note':
        emoji = '📝'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Rest':
        emoji = '😴🛌💤'
    elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Strength':
        emoji = '🏋️‍♂️'
    else:
        emoji = ''
    title = f"{emoji}"

    title += f"{workout['title']}"

    if workout.get('structure') and len(workout['structure']['structure']) > 1:
        if 'end' in workout['structure']['structure'][-1]:
            total_time = utils.secondsToText(
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
            ret += f"{s} *"

        # if len(structure['steps']) > 1:
        #     ret += "("
        for step in structure['steps']:
            st = ''
            maxvalue = step['targets'][0].get('maxValue',
                                              step['targets'][0]['minValue'])
            median = (step['targets'][0]['minValue'] + maxvalue) / 2
            color = ''
            if step['intensityClass'] == "warmUp":
                s = "Warm Up for"
                color = 'white_italic'
            elif step['intensityClass'] == "coolDown":
                s = "Warm Down for"
                color = 'white_italic'
            elif step['intensityClass'] == "rest":
                if median == 0:
                    s = "Rest"
                else:
                    s = "Easy"
                if structure['length']['value'] > 1:
                    color = 'cyan'
                else:
                    color = 'white_italic'
            elif step['intensityClass'] == "active":
                if structure['length']['value'] == 1:
                    s = 'Active for'
                else:
                    s = ''

                color = 'green'
                if median > 80:
                    color = 'blue'
                if median > 90:
                    color = 'yellow'
                if median > 100:
                    color = 'red'
            else:
                s = step['intensityClass']
            st += f"{s} "
            st += utils.secondsToText(step['length']['value']) + " "
            pace = convertTreshold(workout['workoutTypeValueId'],
                                   round(median), args.user_run_pace,
                                   args.user_swim_pace, args.user_cycling_ftp)
            st += f"at {pace}"
            if config.TP_TYPE[workout['workoutTypeValueId']] == 'Cycling':
                st += f"W‍"

            if median > 0:
                st += " [" + str(round(median)) + "%]"

            ret += utils.colourText(st, color, colorize=colorize)

            if structure['steps'][-1] != step:
                ret += " / "

        ret += "\n"
        if extranewlines:
            ret += "\n"
    return (title, ret)


def show_plan(args):
    ret = ''
    cursor_date = dtparser.parse(args.start_date)
    cursor_date = cursor_date - datetime.timedelta(days=1)

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
            else:
                tdd = args.today
            if args.today and \
               (cursor_date.strftime("%Y%m%d") != tdd.strftime("%Y%m%d")):
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
                s = f"\n* {cursor_date.strftime('%A %d %b')}: \n\tRest Day 😴🛌💤"
                color = 'cyan_italic'
            else:
                s = f"\n{cursor_date.strftime('%A %d %b')}: {numberOfWorkouts} Workout"
                color = "cyan_surligned"
            s = utils.colourText(s, color)
            week_str += s + "\n"

            for w in daysw:
                # NOTE(chmou): this is already done workout, let's skip this
                if w['distance']:
                    continue

                if w['workoutTypeValueId'] in (config.TP_NOTE_TYPE_ID,
                                               config.TP_REST_TYPE_ID,
                                               config.TP_OTHER_TYPE_ID):
                    continue

                title, pw = show_workout(args, w)

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
                if args.description and w['description']:
                    week_str += utils.colourText("Description:",
                                                 "yellow") + "\n" + "\n"
                    week_str += utils.addSpaceToString(
                        w['description']) + "\n\n"

                if w['coachComments']:
                    week_str += utils.colourText("Coach Comment:",
                                                 "yellow") + "\n"
                    week_str += utils.addSpaceToString(
                        w['coachComments']) + "\n\n"

        if args.week and not print_week:
            continue
        ret += week_str

    if args.today and not ret:
        print("Nothing to do today 💤 Zzz🎮🍸👩‍❤️‍👨")
    elif ret:
        print(ret)


def plan_to_ical(args):
    events = []
    cursor_date = dtparser.parse(args.start_date)
    cursor_date = cursor_date - datetime.timedelta(days=1)

    plan = utils.get_filej(args.plan_name)
    if not plan:
        raise Exception(f"Cannot find plan: {args.plan_name}")

    for week in plan:
        for day in list(calendar.day_name):
            cursor_date = cursor_date + datetime.timedelta(days=1)
            cursor_date = cursor_date.replace(hour=6, minute=0)

            if day not in week["Workouts"] \
               or not week["Workouts"][day]:  # empty
                continue

            daysw = week['Workouts'][day]
            for current in daysw:
                event = ical.generate_event(current, args, cursor_date)
                events.append(event)

    output = ical.generate_ical(args, events)
    open(args.output_file, "w").write(output)
    print(f"Generated iCS Calendar to: {args.output_file}")