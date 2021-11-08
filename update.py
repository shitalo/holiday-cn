#!/usr/bin/env python3
"""Script for updating data. """

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, tzinfo
from tempfile import mkstemp
from typing import Iterator
from zipfile import ZipFile

from tqdm import tqdm

from fetch_holidays import CustomJSONEncoder, fetch_holiday
from generate_ics import generate_ics, generate_main_ics


class ChinaTimezone(tzinfo):
    """Timezone of china."""

    def tzname(self, dt):
        return "UTC+8"

    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta()


__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.join(__dirname__, *other)


def update_data(year: int) -> Iterator[str]:
    """Update and store data for a year."""

    json_filename = _file_path(f"{year}.json")
    ics_filename = _file_path(f"{year}.ics")
    with open(json_filename, "w", encoding="utf-8", newline="\n") as f:
        data = fetch_holiday(year)

        json.dump(
            dict(
                (
                    (
                        "$schema",
                        "https://raw.githubusercontent.com/Lonense/holiday-cn/master/schema.json",
                    ),
                    (
                        "$id",
                        f"https://raw.githubusercontent.com/Lonense/holiday-cn/master/{year}.json",
                    ),
                    *data.items(),
                )
            ),
            f,
            indent=4,
            ensure_ascii=False,
            cls=CustomJSONEncoder,
        )

    yield json_filename
    generate_ics(data["days"], ics_filename)
    yield ics_filename


def update_main_ics(fr_year, to_year):
    all_days = []
    for year in range(fr_year, to_year + 1):
        filename = _file_path(f"{year}.json")
        if not os.path.isfile(filename):
            continue
        with open(filename, "r", encoding="utf8") as inf:
            data = json.loads(inf.read())
            all_days.extend(data.get("days"))

    filename = _file_path("holiday-cn.ics")
    generate_main_ics(
        all_days,
        filename,
    )
    return filename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all years since 2007, default is this year and next year",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="create new release if repository data is not up to date",
    )
    args = parser.parse_args()

    now = datetime.now(ChinaTimezone())
    is_release = args.release

    filenames = []
    progress = tqdm(range(2007 if args.all else now.year, now.year + 2))
    for i in progress:
        progress.set_description(f"Updating {i} data")
        filenames += list(update_data(i))
    progress.set_description("Updating holiday-cn.ics")
    filenames.append(update_main_ics(now.year - 4, now.year + 1))
    print("")


if __name__ == "__main__":
    main()
