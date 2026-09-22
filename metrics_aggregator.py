import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from dtos import AppUsage, DailyMetrics, ParsedUser
from parse_events import parse_user

SENSITIVE_CATEGORIES = ("ADULT", "GAMBLING")


def split_by_day(start, end):
    parts = []
    while start.date() < end.date():
        midnight = datetime.combine(start.date() + timedelta(days=1), datetime.min.time())
        parts.append((start.date(), start, midnight))
        start = midnight
    parts.append((start.date(), start, end))
    return parts


def overlap_seconds(start, end, window_start, window_end):
    overlap = min(end, window_end) - max(start, window_start)
    return max(0, overlap.total_seconds())


def night_seconds(day, start, end):
    midnight = datetime.combine(day, datetime.min.time())
    early_morning = overlap_seconds(start, end, midnight, midnight + timedelta(hours=6))
    late_evening = overlap_seconds(start, end, midnight + timedelta(hours=23), midnight + timedelta(hours=24))
    return early_morning + late_evening


def longest_gap_minutes(intervals):
    gaps = [(next_start - end).total_seconds() for (_, end), (next_start, _) in zip(intervals, intervals[1:])]
    return max(gaps, default=0) / 60


def aggregate(parsed: ParsedUser) -> list[DailyMetrics]:
    screen_seconds = Counter()
    bedtime_seconds = Counter()
    usage_by_day = defaultdict(list)
    for block in parsed.usage_blocks:
        for day, start, end in split_by_day(block.start, block.end):
            screen_seconds[day] += (end - start).total_seconds()
            bedtime_seconds[day] += night_seconds(day, start, end)
            usage_by_day[day].append((start, end))

    pickups = Counter(pickup.unlock.date() for pickup in parsed.pickups)
    first_pickup = {}
    for pickup in parsed.pickups:
        first_pickup.setdefault(pickup.unlock.date(), pickup.unlock.time())

    apps = defaultdict(set)
    app_switches = Counter()
    for session in parsed.app_sessions:
        apps[session.start.date()].add(session.name)
        app_switches[session.start.date()] += 1

    blocks = Counter(block.time.date() for block in parsed.blocks)
    blocks_by_type = defaultdict(Counter)
    sensitive_blocks = Counter()
    for block in parsed.blocks:
        blocks_by_type[block.time.date()][block.block_type] += 1
        if block.category in SENSITIVE_CATEGORIES or block.block_type == "NUDITY":
            sensitive_blocks[block.time.date()] += 1

    all_days = [*screen_seconds, *pickups, *blocks]
    day = min(all_days)
    daily = []
    while day <= max(all_days):
        daily.append(DailyMetrics(
            day=day,
            screen_minutes=round(screen_seconds[day] / 60, 1),
            offline_minutes=round(24 * 60 - screen_seconds[day] / 60, 1),
            bedtime_minutes=round(bedtime_seconds[day] / 60, 1),
            pickups=pickups[day],
            first_pickup=first_pickup.get(day),
            longest_offline_minutes=round(longest_gap_minutes(usage_by_day[day]), 1),
            distinct_apps=len(apps[day]),
            app_switches=app_switches[day],
            blocks=blocks[day],
            blocks_by_type=dict(blocks_by_type[day]),
            sensitive_blocks=sensitive_blocks[day],
        ))
        day += timedelta(days=1)
    return daily


def usage_by_app(parsed: ParsedUser) -> list[AppUsage]:
    """Minutes per app or website over the whole period, most used first."""
    seconds = Counter()
    categories = {}
    for session in parsed.app_sessions:
        seconds[session.name] += session.seconds
        categories[session.name] = session.category
    return [AppUsage(name, categories[name], round(total / 60, 1)) for name, total in seconds.most_common()]


if __name__ == "__main__":
    for user in sys.argv[1:] or ["a", "b"]:
        print(f"user {user}:  day          screen  offline  night  pickups  first  longest_break  apps  switches  blocks  sensitive")
        for d in aggregate(parse_user(user)):
            print(f"  {d.day}  {d.screen_minutes:6}  {d.offline_minutes:7}  {d.bedtime_minutes:5}  {d.pickups:7}  "
                  f"{d.first_pickup and d.first_pickup.strftime('%H:%M')}  {d.longest_offline_minutes:13}  {d.distinct_apps:4}  "
                  f"{d.app_switches:8}  {d.blocks:6}  {d.sensitive_blocks:9}  {d.blocks_by_type}")
