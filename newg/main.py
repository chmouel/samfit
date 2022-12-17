#!/usr/bin/env python3
# pylint: disable=unused-import
import samfit.args
import samfit.tr_workouts_to_tp_library
import samfit.tr_plans_to_tp_calendar
import samfit.tp_plans_to_plans


def main():
    args = samfit.args.cli()
    print(args)


if __name__ == "__main__":
    main()
