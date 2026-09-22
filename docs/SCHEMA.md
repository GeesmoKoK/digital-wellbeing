# Data schema

Each file (`data/events_user_a.json`, `data/events_user_b.json`) is a single JSON
array of event objects, **sorted ascending by time**. Every object has the same eight
fields; fields that don't apply to an event type are `null`.

```json
{
  "id": 4213,
  "event_type": "BLOCK",
  "timestamp_millis": 1777673607000,
  "package_name": null,
  "url_domain": "pornhub.com",
  "category": "ADULT",
  "block_type": "NUDITY",
  "is_keyguard_locked": null
}
```

## Fields

| Field | Type | Meaning |
|---|---|---|
| `id` | int | Monotonic per file, in time order. |
| `event_type` | string | One of the six types below. |
| `timestamp_millis` | int | Epoch **milliseconds**. Wall-clock normalised to UTC (`utcfromtimestamp(ts/1000)` → local time; day boundary = local midnight). |
| `package_name` | string \| null | Android package, e.g. `com.whatsapp`. Set on `APP_FOREGROUND`, and on `BLOCK` when an app was blocked. |
| `url_domain` | string \| null | Domain only (never full path/query). Set on `URL_VISIT`, and on `BLOCK` when a site was blocked. |
| `category` | string \| null | Content category (enum below). Set on `APP_FOREGROUND` (what kind of app is in use), `URL_VISIT` (what kind of site), and `BLOCK` (what was blocked). |
| `block_type` | string \| null | Only on `BLOCK`: `APP`, `URL`, or `NUDITY` (on-device nudity detection). |
| `is_keyguard_locked` | bool \| null | Lock state when the screen event fired. `true` on a `SCREEN_ON` where the phone was **not** unlocked (a passive glance); `false` on a real unlock (`USER_PRESENT`). `null` where not applicable. |

## Event types

| `event_type` | Fires when | Key fields |
|---|---|---|
| `SCREEN_ON` | The screen lights up (a notification glance, or the start of a real pickup). | `is_keyguard_locked` |
| `USER_PRESENT` | The user actually unlocks the phone (PIN / biometric / swipe). | `is_keyguard_locked = false` |
| `SCREEN_OFF` | The screen goes dark. | — |
| `APP_FOREGROUND` | An app comes to the foreground. | `package_name`, `category` |
| `URL_VISIT` | A page is visited in the browser (allowed domains). | `url_domain`, `category` |
| `BLOCK` | The phone blocks a distracting app or an unsafe site/content. | `package_name` **or** `url_domain`, `category`, `block_type` |

**A note on pickups.** Not every `SCREEN_ON` is a real pickup — many are passive
notification glances where the phone is never unlocked. A genuine pickup is a
`SCREEN_ON` that leads to a `USER_PRESENT` (or, equivalently, a session that actually
lasts). `is_keyguard_locked` and the presence/absence of a following `USER_PRESENT`
are how you tell them apart. How you define a "meaningful pickup" is up to you —
just be explicit about it.

## `category` enum

Both apps and sites are normalised into one shared vocabulary:

```
ADULT · GAMBLING · SOCIAL_MEDIA · MESSAGING · GAMING
ENTERTAINMENT · NEWS · SHOPPING · OTHER
```

`ADULT`, `GAMBLING`, and (in a messaging/dating context) contact-based risks are the
**sensitive** categories — the ones that matter most for safety, and the ones a
guardian would most want to know about in aggregate. The rest are ordinary
distraction categories.

## What is (and isn't) in the stream

- A `BLOCK` means an attempt was **stopped** — the app/site did **not** open. A
  `URL_VISIT` or an `APP_FOREGROUND` means content actually **was** shown.
- `APP_FOREGROUND` and `URL_VISIT` both carry a `category`, so you can measure **time
  per category** (from event ordering), not only **blocks per category**.
- Sessions are implicit: you reconstruct them from `SCREEN_ON` → … → `SCREEN_OFF`.
- App/site *time* is not given — you derive it from the ordering of events (an app is
  "in front" from its `APP_FOREGROUND` until the next foreground change, block, or
  screen-off).
