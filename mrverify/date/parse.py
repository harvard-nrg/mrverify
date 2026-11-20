import re
import argparse
from datetime import datetime

FIELDS = {
    "%Y": r"(?P<Y>\d{4})",
    "%y": r"(?P<y>\d{2})",
    "%m": r"(?P<m>\d{2})",
    "%d": r"(?P<d>\d{2})",
}

def date_pattern(spec: str) -> re.Pattern:
    """argparse type: turn '_%y%m%d$' into a regex with named groups."""
    try:
        rx = re.compile(re.sub(r"%[Yymd]", lambda m: FIELDS[m.group()], spec))
    except re.error as e:
        raise argparse.ArgumentTypeError(f"invalid pattern {spec!r}: {e}")
    groups = set(rx.groupindex)
    if not (groups & {"Y", "y"} and {"m", "d"} <= groups):
        raise argparse.ArgumentTypeError(
            f"{spec!r} must contain a year (%Y or %y), %m and %d")
    return rx

def find_dates(subject_id: str, rx: re.Pattern):
    """Every valid date the pattern finds in subject_id."""
    found = []
    for m in rx.finditer(subject_id):
        g = m.groupdict()
        year, year_fmt = (g["Y"], "%Y") if g.get("Y") else (g["y"], "%y")
        try:
            found.append(
                datetime.strptime(year + g["m"] + g["d"], year_fmt + "%m%d").date())
        except ValueError:
            pass  # digits matched but aren't a real date (e.g. month 13)
    return found
