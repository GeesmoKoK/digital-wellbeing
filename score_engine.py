import sys

from dtos import DailyMetrics, DailyScore
from metrics_aggregator import aggregate
from parse_events import parse_user

SCREEN = (120, 360, 30)
FRAGMENTATION = (25, 75, 25)
BEDTIME = (0, 60, 25)
RESTRICTED = (3, 50, 20)


def penalty(value, rule):
    free, full, max_points = rule
    share = (value - free) / (full - free)
    return round(max_points * min(max(share, 0.0), 1.0), 1)


def score_day(day: DailyMetrics) -> DailyScore:
    screen = penalty(day.screen_minutes, SCREEN)
    fragmentation = penalty(day.pickups, FRAGMENTATION)
    bedtime = penalty(day.bedtime_minutes, BEDTIME)
    restricted = penalty(day.blocks, RESTRICTED)
    score = round(100 - screen - fragmentation - bedtime - restricted, 1)
    return DailyScore(day.day, score, screen, fragmentation, bedtime, restricted)


def score_days(daily: list[DailyMetrics]) -> list[DailyScore]:
    return [score_day(day) for day in daily]


if __name__ == "__main__":
    for user in sys.argv[1:] or ["a", "b"]:
        scores = score_days(aggregate(parse_user(user)))
        print(f"user {user}:  day          score  screen  fragment  bedtime  restricted")
        for s in scores:
            print(f"  {s.day}  {s.score:6}  {s.screen_penalty:6}  {s.fragmentation_penalty:8}  "
                  f"{s.bedtime_penalty:7}  {s.restricted_penalty:10}")
        print(f"  average score: {sum(s.score for s in scores) / len(scores):.1f}")
