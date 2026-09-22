import sys
from collections import Counter
from datetime import timedelta

from dtos import Nudge, ParsedUser
from parse_events import parse_user

LOOP_ATTEMPTS = 3
LOOP_MINUTES = 10
COOLDOWN_MINUTES = 60
MAX_PER_DAY = {"FRUSTRATION_LOOP": 2, "NIGHT_USE": 1}

LOOP_MESSAGE = "Parece que hay algo que cuesta soltar ahora mismo, y es normal. ¿Probamos 2 minutos de pausa? Respira hondo y estira un poco."
NIGHT_MESSAGE = "Ya es tarde. Descansar también es cuidarte: ¿dejamos el móvil hasta mañana? Tu yo de mañana te lo agradecerá."


def frustration_loops(blocks):
    nudges = []
    for i in range(LOOP_ATTEMPTS - 1, len(blocks)):
        first_attempt = blocks[i - (LOOP_ATTEMPTS - 1)]
        if blocks[i].time - first_attempt.time <= timedelta(minutes=LOOP_MINUTES):
            nudges.append(Nudge(blocks[i].time, "FRUSTRATION_LOOP", LOOP_MESSAGE))
    return nudges


def night_use(pickups):
    return [Nudge(p.unlock, "NIGHT_USE", NIGHT_MESSAGE) for p in pickups if p.unlock.hour >= 23 or p.unlock.hour < 6]


def find_nudges(parsed: ParsedUser) -> list[Nudge]:
    candidates = sorted(frustration_loops(parsed.blocks) + night_use(parsed.pickups), key=lambda n: n.time)
    shown = []
    shown_today = Counter()  # (day, kind) -> how many were shown
    for nudge in candidates:
        too_soon = bool(shown) and nudge.time - shown[-1].time < timedelta(minutes=COOLDOWN_MINUTES)
        limit_reached = shown_today[(nudge.time.date(), nudge.kind)] >= MAX_PER_DAY[nudge.kind]
        if not too_soon and not limit_reached:
            shown.append(nudge)
            shown_today[(nudge.time.date(), nudge.kind)] += 1
    return shown


if __name__ == "__main__":
    for user in sys.argv[1:] or ["a", "b"]:
        nudges = find_nudges(parse_user(user))
        print(f"user {user}: {len(nudges)} nudges")
        for n in nudges[:5]:
            print(f"  {n.time}  {n.kind}")
