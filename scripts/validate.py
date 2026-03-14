#!/usr/bin/env python3
"""Validate private trip JSON against schema conventions."""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PRIVATE_DIR = SCRIPT_DIR.parent / "private"

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


def validate(path: Path) -> list[str]:
    errors = []

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    for field in ("trip", "version", "meta", "days", "dayDetails"):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    if errors:
        return errors

    if data.get("version") != 1:
        errors.append(f"Unsupported version: {data.get('version')} (expected 1)")


    days = data.get("days", [])
    indices = [d.get("index") for d in days]
    if indices != list(range(len(days))):
        errors.append(f"Day indices must be sequential from 0, got: {indices}")

    for i, day in enumerate(days):
        for field in ("date", "shortDate"):
            if field not in day:
                errors.append(f"days[{i}] missing '{field}'")

        after = day.get("after")
        if after is not None and not ISO_RE.match(after):
            errors.append(f"days[{i}].after invalid ISO format: {after}")

        for j, card in enumerate(day.get("cards", [])):
            ctype = card.get("type")
            if ctype not in ("transit", "game"):
                errors.append(f"days[{i}].cards[{j}].type must be transit|game, got: {ctype}")
            if "title" not in card:
                errors.append(f"days[{i}].cards[{j}] missing 'title'")
            if ctype == "game" and "matchup" not in card:
                errors.append(f"days[{i}].cards[{j}] game card '{card.get('title')}' missing matchup")
            if "matchup" in card:
                for key in ("away", "home"):
                    if key not in card["matchup"]:
                        errors.append(f"days[{i}].cards[{j}].matchup missing '{key}'")

    day_details = data.get("dayDetails", [])
    if len(day_details) != len(days):
        errors.append(f"dayDetails length ({len(day_details)}) != days length ({len(days)})")

    for c in data.get("constraints", []):
        ctype = c.get("type")
        if ctype not in ("train", "game", "lodging"):
            errors.append(f"constraint type must be train|game|lodging, got: {ctype}")
        if "label" not in c:
            errors.append("constraint missing 'label'")
        if ctype in ("train", "game") and "time" in c:
            if not ISO_RE.match(c["time"]):
                errors.append(f"constraint '{c.get('label')}' has invalid time: {c['time']}")
        if ctype == "lodging":
            for field in ("check_in", "check_out"):
                if field in c and not ISO_RE.match(c[field]):
                    errors.append(f"constraint '{c.get('label')}' has invalid {field}: {c.get(field)}")

    return errors


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PRIVATE_DIR / "2026" / "trains-and-baseball.json"

    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    errors = validate(path)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"OK: {path.name}")


if __name__ == "__main__":
    main()
