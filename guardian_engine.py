import sys

from dtos import DailyMetrics, DailyScore, GuardianDay, GuardianStatus
from metrics_aggregator import aggregate
from parse_events import parse_user
from score_engine import score_days

LOW_SCORE = 50
NIGHT_MINUTES = 30
SENSITIVE_ATTEMPTS = 3
STREAK_DAYS = 3


def to_guardian_days(scores: list[DailyScore], daily: list[DailyMetrics]) -> list[GuardianDay]:
    return [GuardianDay(score.day, score.score, metrics.bedtime_minutes, metrics.sensitive_blocks) for score, metrics in zip(scores, daily)]


def guardian_status(days: list[GuardianDay]) -> list[GuardianStatus]:
    statuses = []
    low_score_streak = 0
    night_streak = 0
    sensitive_streak = 0
    calm_days = 0
    attention = False
    for day in days:
        bad_day = day.score < LOW_SCORE or day.bedtime_minutes >= NIGHT_MINUTES or day.sensitive_blocks >= SENSITIVE_ATTEMPTS
        low_score_streak = low_score_streak + 1 if day.score < LOW_SCORE else 0
        night_streak = night_streak + 1 if day.bedtime_minutes >= NIGHT_MINUTES else 0
        sensitive_streak = sensitive_streak + 1 if day.sensitive_blocks >= SENSITIVE_ATTEMPTS else 0
        calm_days = 0 if bad_day else calm_days + 1
        was_attention = attention
        if max(low_score_streak, night_streak, sensitive_streak) >= STREAK_DAYS:
            attention = True
        elif calm_days >= STREAK_DAYS:
            attention = False
        status = "ATTENTION_NEEDED" if attention else "HEALTHY"
        statuses.append(GuardianStatus(day.day, status, notify=attention and not was_attention))
    return statuses


if __name__ == "__main__":
    for user in sys.argv[1:] or ["a", "b"]:
        daily = aggregate(parse_user(user))
        statuses = guardian_status(to_guardian_days(score_days(daily), daily))
        attention = sum(s.status == "ATTENTION_NEEDED" for s in statuses)
        print(f"user {user}: {attention} of {len(statuses)} days ATTENTION_NEEDED, "
              f"notified on: {[str(s.day) for s in statuses if s.notify] or 'never'}")
