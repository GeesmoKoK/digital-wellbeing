import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dtos import AppSession, Block, ParsedUser, PassiveGlance, Pickup, UsageBlock

FOLDER = Path(__file__).parent


def to_time(millis):
    return datetime.fromtimestamp(millis / 1000, timezone.utc).replace(tzinfo=None)


def end_session(session, end, sessions):
    if session and end > session["start"]:
        seconds = int((end - session["start"]).total_seconds())
        is_bedtime = session["start"].hour >= 23 or session["start"].hour < 6
        sessions.append(AppSession(session["name"], session["category"], session["start"], end, seconds, is_bedtime))
    return None

def parse(events):
    pickups = []
    glances = []
    usage_blocks = []
    sessions = []
    blocks = []

    screen_level = 0
    screen_start = None
    unlocked = False
    last_screen_on = None
    waiting_unlock = False
    session = None

    for e in events:
        time = to_time(e["timestamp_millis"])
        kind = e["event_type"]

        if kind == "SCREEN_ON":
            if screen_level == 0:
                screen_start = time
                unlocked = False
            screen_level += 1
            last_screen_on = time
            waiting_unlock = True

        elif kind == "USER_PRESENT":
            if waiting_unlock:
                pickups.append(Pickup(last_screen_on, time))
                waiting_unlock = False
                unlocked = True

        elif kind == "SCREEN_OFF" and screen_level > 0:
            screen_level -= 1
            if screen_level == 0:  # the screen is really dark now
                if unlocked:
                    usage_blocks.append(UsageBlock(screen_start, time, int((time - screen_start).total_seconds())))
                else:
                    glances.append(PassiveGlance(screen_start, time))
                waiting_unlock = False
                session = end_session(session, time, sessions)

        elif kind == "BLOCK":
            blocks.append(Block(time, e["package_name"] or e["url_domain"], e["category"], e["block_type"]))
            session = end_session(session, time, sessions)

        elif kind in ("APP_FOREGROUND", "URL_VISIT"):
            name = e["package_name"] or e["url_domain"]
            if session is None or session["name"] != name:
                end_session(session, time, sessions)
                session = {"name": name, "category": e["category"], "start": time}

    end_session(session, to_time(events[-1]["timestamp_millis"]), sessions)
    return ParsedUser(pickups, glances, usage_blocks, sessions, blocks)


def parse_user(user):
    events = json.loads((FOLDER / "data" / f"events_user_{user}.json").read_text())
    return parse(events)


if __name__ == "__main__":
    for user in sys.argv[1:] or ["a", "b"]:
        result = parse_user(user)
        print(user, {name: len(items) for name, items in vars(result).items()})
