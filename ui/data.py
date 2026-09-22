"""Runs the layers for one user and gives the sections everything they need. The only file that knows the layers."""

import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))  # to import the layers from the project folder

from guardian_engine import guardian_status, to_guardian_days
from metrics_aggregator import aggregate, usage_by_app
from nudge_engine import find_nudges
from parse_events import parse_user
from score_engine import score_days

DAYS = 30  # both users have 30 days; B's last minutes of a 31st day would look like a real day


@dataclass
class UserData:
    table: pd.DataFrame  # one row per day: the daily metrics and the score
    apps: list  # AppUsage, most used first (stays on the phone)
    blocked_categories: Counter  # what got blocked (stays on the phone)
    nudges: list  # Nudge (shown on the phone)
    sent: list  # GuardianDay: the only data that leaves the phone
    statuses: list  # GuardianStatus: what the guardian sees


def load_user(user: str) -> UserData:
    parsed = parse_user(user)
    daily = aggregate(parsed)[:DAYS]
    scores = score_days(daily)
    sent = to_guardian_days(scores, daily)
    return UserData(
        table=pd.DataFrame([{**asdict(d), "score": s.score} for d, s in zip(daily, scores)]),
        apps=usage_by_app(parsed),
        blocked_categories=Counter(str(block.category) for block in parsed.blocks),
        nudges=find_nudges(parsed),
        sent=sent,
        statuses=guardian_status(sent),
    )
