"""Small HTML pieces used by the sections. Each one is a few lines and looks the same everywhere."""

import streamlit as st


def html(markup: str):
    st.markdown(markup, unsafe_allow_html=True)


def label(text: str):
    """Small gray text above a chart or a list."""
    html(f'<div class="label">{text}</div>')


def kpi_row(cards: list[tuple[str, str, str]]):
    """A row of big numbers. Each card is (label, value, change)."""
    items = "".join(
        f'<div class="kpi"><div class="label">{name}</div><div class="value">{value}</div><div class="change">{change}</div></div>'
        for name, value, change in cards
    )
    html(f'<div class="kpis">{items}</div>')


def word_list(rows: list[tuple[str, str]]):
    """Centered bold words, like the phone launcher. Each row is (word, small gray note)."""
    items = "".join(f'<div class="word">{word}<span>{note}</span></div>' for word, note in rows)
    html(f'<div class="words">{items}</div>')


def pill(text: str, style: str = ""):
    """A rounded box. style is "" (dark), "on" (white) or "outline"."""
    html(f'<div class="pill {style}">{text}</div>')


APP_NAMES = {
    "com.amazon.kindle": "Kindle", "com.android.chrome": "Chrome", "com.duolingo": "Duolingo",
    "com.facebook.katana": "Facebook", "com.google.android.apps.maps": "Maps",
    "com.google.android.apps.messaging": "Messages", "com.google.android.calendar": "Calendar",
    "com.google.android.dialer": "Phone", "com.google.android.gm": "Gmail", "com.google.android.keep": "Keep",
    "com.google.android.youtube": "YouTube", "com.instagram.android": "Instagram", "com.microsoft.office.outlook": "Outlook",
    "com.netflix.mediaclient": "Netflix", "com.reddit.frontpage": "Reddit", "com.roblox.client": "Roblox",
    "com.snapchat.android": "Snapchat", "com.spotify.music": "Spotify", "com.twitter.android": "Twitter",
    "com.whatsapp": "Whatsapp", "org.telegram.messenger": "Telegram",
}


def short_name(name: str) -> str:
    """com.spotify.music -> Spotify. Website domains and unknown packages stay as they are."""
    return APP_NAMES.get(name, name)
