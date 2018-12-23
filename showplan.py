import datetime

import config
import utils


def conver_pace_to_seconds(pace):
    return (int(pace[:pace.find("'")]) * 60) + int(pace[pace.find("'") + 1:])


def convert_seconds_to_pace(seconds):
    sp = str(datetime.timedelta(seconds=seconds)).split(":")
    sec = "%.2d" % int(sp[2][:sp[2].find(".")])
    return f"{sp[1]}'{sec}"


def convertTreshold(wtype, percent):
    if config.TP_TYPE[wtype] == 'Running':
        tresholds = conver_pace_to_seconds(config.USER_PACE)
        return convert_seconds_to_pace(tresholds / percent * 100)
    elif config.TP_TYPE[wtype] == 'Cycling':
        return round(config.USER_FTP * percent / 100)


def show_workout(workout):
    ret = ''
    if not workout['structure'] or 'structure' not in workout['structure']:
        return
    emoji = '🚴'
    if config.TP_TYPE[workout['workoutTypeValueId']] == 'Running':
        emoji = '🏃'
    ret += f"* {emoji} - {workout['title']} \n"
    for structure in workout['structure']['structure']:
        ret += "  - "
        if structure['type'] == 'repetition' and  \
           structure['length']['value'] != 1:
            ret += f"{structure['length']['value']} * "

        if len(structure['steps']) > 1:
            ret += "("
        for step in structure['steps']:
            mm = round(step['length']['value'] / 60)
            if mm == 0:
                ret += str(step['length']['value']) + " seconds "
            else:
                ret += str(mm) + " minute"
                if mm > 1:
                    ret += "s"
                ret += " "
            if step['intensityClass'] == "warmUp":
                s = "Warm Up"
            elif step['intensityClass'] == "coolDown":
                s = "Warm Down"
            elif step['intensityClass'] in ("active", "rest"):
                s = step['intensityClass'].title()
            else:
                s = step['intensityClass']
            ret += s + " "
            median = (step['targets'][0]['minValue'] +
                      step['targets'][0]['maxValue']) / 2
            ret += str(round(median)) + "% "

            pace = convertTreshold(workout['workoutTypeValueId'],
                                   round(median))
            if config.TP_TYPE[workout['workoutTypeValueId']] == 'Cycling':
                ret += f"FTP {pace}W‍"
            elif config.TP_TYPE[workout['workoutTypeValueId']] == 'Running':
                ret += f"Treshold {pace}"

            if structure['steps'][-1] != step:
                ret += " / "

        if len(structure['steps']) > 1:
            ret += ")"
        ret += "\n"
    return ret


def show_plan(args):
    plan = utils.get_filej(args.plan_file)
    if not plan:
        raise Exception(f"Cannot find plan: {args.plan_file}")
    for week in plan:
        utils.ppt(f"\nWeek: {week['Week']}", ppt='=')
        for day in week['Workouts']:
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
                print(f"\n/{day}: Rest Day/")
            else:
                s = f"\n{day}: {numberOfWorkouts} Workouts, {round(tssPlanned)} TSS planned "
                utils.ppt(s)

            for w in daysw:
                if w['workoutTypeValueId'] in (config.TP_NOTE_TYPE_ID,
                                               config.TP_REST_TYPE_ID,
                                               config.TP_OTHER_TYPE_ID):
                    continue

                pw = show_workout(w)

                if pw:
                    print(pw)
                else:
                    print("%s: %s" % (config.TP_TYPE[int(
                        w['workoutTypeValueId'])], w['title']))
