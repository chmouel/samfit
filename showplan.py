import calendar
import datetime

import config
import utils

import dateutil.parser as dtparser


def conver_pace_to_seconds(pace):
    return (int(pace[:pace.find("'")]) * 60) + int(pace[pace.find("'") + 1:])


def convert_seconds_to_pace(seconds):
    sp = str(datetime.timedelta(seconds=seconds)).split(":")
    sec = "%.2d" % int(sp[2][:sp[2].find(".")])
    return f"{sp[1]}'{sec}"


def convertTreshold(wtype, percent, pace, ftp):
    if config.TP_TYPE[wtype] == 'Running':
        tresholds = conver_pace_to_seconds(pace)
        return convert_seconds_to_pace(tresholds / percent * 100)
    elif config.TP_TYPE[wtype] == 'Cycling':
        return round(ftp * percent / 100)


def show_workout(args, workout):
    ret = ''
    if not workout['structure'] or 'structure' not in workout['structure']:
        return
    emoji = '🚴'
    if config.TP_TYPE[workout['workoutTypeValueId']] == 'Running':
        emoji = '🏃'
    ret += f"* {emoji} "

    if len(workout['structure']['structure']) > 1:
        total_time = utils.secondsToText(
            workout['structure']['structure'][-1]['end'])
        ret += f"{total_time} "

    ret += f"{workout['title']} - TSS:{round(workout['tssPlanned'])}\n"

    for structure in workout['structure']['structure']:
        ret += "  - "
        if structure['type'] == 'repetition' and  \
           structure['length']['value'] != 1:
            s = utils.colourText(structure['length']['value'], 'magenta')
            ret += f"{s} * "

        if len(structure['steps']) > 1:
            ret += "("
        for step in structure['steps']:
            st = ''
            median = (step['targets'][0]['minValue'] +
                      step['targets'][0]['maxValue']) / 2
            color = ''
            if step['intensityClass'] == "warmUp":
                s = "Warm Up"
                color = 'white_italic'
            elif step['intensityClass'] == "coolDown":
                s = "Warm Down"
                color = 'white_italic'
            elif step['intensityClass'] == "rest":
                s = "Rest"
                color = 'cyan'
            elif step['intensityClass'] == "active":
                s = step['intensityClass'].title()

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
                                   round(median), args.user_pace,
                                   args.user_ftp)
            st += f"{pace}"
            if config.TP_TYPE[workout['workoutTypeValueId']] == 'Cycling':
                st += f"W‍"

            st += " [" + str(round(median)) + "%]"

            ret += utils.colourText(st, color)

            if structure['steps'][-1] != step:
                ret += " / "

        if len(structure['steps']) > 1:
            ret += ")"
        ret += "\n"
    return ret


def show_plan(args):
    ret = ''
    cursor_date = dtparser.parse(args.start_date)
    cursor_date = cursor_date - datetime.timedelta(days=1)

    plan = utils.get_filej(args.plan_file)
    if not plan:
        raise Exception(f"Cannot find plan: {args.plan_file}")
    for week in plan:
        if not args.today:
            ret += utils.ppt(f"\nWeek: {week['Week']}", ppt='=')
        for day in list(calendar.day_name):
            cursor_date = cursor_date + datetime.timedelta(days=1)

            tdd = datetime.datetime.now().strftime("%Y%m%d")
            if args.today and \
               (cursor_date.strftime("%Y%m%d") != tdd.strftime("%Y%m%d")):
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
                s = f"\n{cursor_date.strftime('%A %d %b')}: Rest Day 😴"
                color = 'cyan_italic'
            else:
                s = f"\n{cursor_date.strftime('%A %d %b')}: {numberOfWorkouts} Workout"
                color = "cyan_surligned"
            s = utils.colourText(s, color)
            ret += s + "\n"

            for w in daysw:
                if w['workoutTypeValueId'] in (config.TP_NOTE_TYPE_ID,
                                               config.TP_REST_TYPE_ID,
                                               config.TP_OTHER_TYPE_ID):
                    continue

                pw = show_workout(args, w)
                if pw:
                    ret += "\n" + pw + "\n"
                else:
                    tt = config.TP_TYPE[int(w['workoutTypeValueId'])]
                    emoji = ''
                    if tt == 'Swim':
                        emoji = '🏊‍'
                    elif tt == 'Strength':
                        emoji = '🏋️‍'

                    ret += f"{tt}: {w['title']} {emoji}\n"

    print(ret)
