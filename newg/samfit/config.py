import subprocess


BASE_DIR = subprocess.run(
    "git rev-parse --show-toplevel",
    shell=True,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

TP_TYPE = {
    100: "Other",
    10: "Note",
    1: "Swim",
    2: "Cycling",
    3: "Running",
    4: "Brick",
    7: "Rest",
    9: "Strength",
}

TP_TYPE_REV = {v: k for k, v in TP_TYPE.items()}
ACTIVE_CADENCE_MIN = 85
ACTIVE_CADENCE_MAX = 95
