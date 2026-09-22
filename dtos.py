from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass
class Pickup:
    screen_on: datetime
    unlock: datetime


@dataclass
class PassiveGlance:
    start: datetime
    end: datetime


@dataclass
class UsageBlock:
    start: datetime
    end: datetime
    seconds: int


@dataclass
class AppSession:
    name: str
    category: str
    start: datetime
    end: datetime
    seconds: int
    is_bedtime: bool


@dataclass
class Block:
    time: datetime
    name: str
    category: str
    block_type: str


# Layer 1 output
@dataclass
class ParsedUser:
    pickups: list[Pickup]
    passive_glances: list[PassiveGlance]
    usage_blocks: list[UsageBlock]
    app_sessions: list[AppSession]
    blocks: list[Block]


# Layer 2 output: one row per day
@dataclass
class DailyMetrics:
    day: date
    screen_minutes: float
    offline_minutes: float
    bedtime_minutes: float
    pickups: int
    first_pickup: time | None
    longest_offline_minutes: float
    distinct_apps: int
    app_switches: int
    blocks: int
    blocks_by_type: dict
    sensitive_blocks: int


# Layer 2 output: time spent in one app or website over the whole period
@dataclass
class AppUsage:
    name: str
    category: str
    minutes: float


# Layer 3 output: one row per day, score = 100 minus the four penalties
@dataclass
class DailyScore:
    day: date
    score: float
    screen_penalty: float
    fragmentation_penalty: float
    bedtime_penalty: float
    restricted_penalty: float


# Layer 4, on the device: a suggestion shown to the user
@dataclass
class Nudge:
    time: datetime
    kind: str
    message: str


# Layer 4: the ONLY data that leaves the device for the guardian (a date and numbers, no names, no URLs)
@dataclass
class GuardianDay:
    day: date
    score: float
    bedtime_minutes: float
    sensitive_blocks: int


# Layer 4, on the server: what the guardian sees. status is HEALTHY or ATTENTION_NEEDED
@dataclass
class GuardianStatus:
    day: date
    status: str
    notify: bool
