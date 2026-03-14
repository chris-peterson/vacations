#!/usr/bin/env python3
"""Detect timing conflicts in trip constraints."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PRIVATE_DIR = SCRIPT_DIR.parent / "private"

MIN_BUFFER = timedelta(hours=2)


def parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def check_conflicts(path: Path) -> tuple[list[str], list[str]]:
    data = json.loads(path.read_text())
    constraints = data.get("constraints", [])

    warnings: list[str] = []
    errors: list[str] = []

    trains = [c for c in constraints if c["type"] == "train"]
    games = [c for c in constraints if c["type"] == "game"]
    lodging = [c for c in constraints if c["type"] == "lodging"]

    # Check: train arrival vs game start
    for game in games:
        game_time = parse_dt(game["time"])
        game_loc = game["location"].split(",")[0].strip().lower()

        arriving = []
        for t in trains:
            dest = t.get("destination", "").lower()
            if not dest:
                continue
            t_time = parse_dt(t["time"])
            # Train departs before game; does destination city match?
            dest_city = dest.split(",")[0].strip()
            if dest_city in game_loc or game_loc in dest_city:
                if t_time < game_time:
                    arriving.append(t)

        if arriving:
            latest = max(arriving, key=lambda t: t["time"])
            depart_time = parse_dt(latest["time"])
            # Estimate arrival: for same-day trains, arrival = depart + travel
            # We only know departure time, so flag if departure is within buffer of game
            buffer = game_time - depart_time
            if buffer < MIN_BUFFER:
                errors.append(
                    f"TIGHT: {latest['label']} departs {latest['time']}, "
                    f"only {buffer} before {game['label']} at {game['time']}"
                )
            elif buffer < timedelta(hours=4):
                warnings.append(
                    f"BUFFER: {latest['label']} departs {latest['time']}, "
                    f"{buffer} before {game['label']} at {game['time']}"
                )


    # Check: lodging check-in vs arrival
    for lodge in lodging:
        if "check_in" not in lodge:
            continue
        checkin = parse_dt(lodge["check_in"])
        lodge_loc = lodge["location"].split(",")[0].strip().lower()

        for t in trains:
            dest = t.get("destination", "").lower()
            dest_city = dest.split(",")[0].strip() if dest else ""
            if dest_city not in lodge_loc and lodge_loc not in dest_city:
                continue
            t_time = parse_dt(t["time"])
            if t_time.date() == checkin.date() and t_time > checkin:
                warnings.append(
                    f"EARLY CHECK-IN: {lodge['label']} check-in {lodge['check_in']} "
                    f"but {t['label']} doesn't arrive until {t['time']}"
                )

    # Check: overlapping events in different locations
    timed = []
    for c in constraints:
        if "time" in c and c["type"] in ("train", "game"):
            timed.append(c)
    timed.sort(key=lambda c: c["time"])

    for i in range(len(timed) - 1):
        a, b = timed[i], timed[i + 1]
        a_time = parse_dt(a["time"])
        b_time = parse_dt(b["time"])
        gap = b_time - a_time

        if gap < timedelta(hours=0):
            a_loc = a["location"].split(",")[0].strip()
            b_loc = b["location"].split(",")[0].strip()
            if a_loc != b_loc:
                errors.append(
                    f"OVERLAP: {a['label']} at {a['time']} in {a_loc} "
                    f"overlaps {b['label']} at {b['time']} in {b_loc}"
                )

    return warnings, errors


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PRIVATE_DIR / "2026" / "trains-and-baseball.json"

    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    warnings, errors = check_conflicts(path)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if not warnings and not errors:
        print("No conflicts found.")


if __name__ == "__main__":
    main()
