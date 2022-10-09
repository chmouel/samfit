#!/usr/bin/env python3
# pylint: disable=unused-import
import samfit.args
import samfit.tr_workouts_to_tp_library


def main():
    args = samfit.args.cli()
    print(args)


if __name__ == "__main__":
    main()
