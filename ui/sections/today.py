"""Section 0: today's numbers (the last day in the data, treated as "today")."""

from datetime import time as dt_time

import streamlit as st

from components import kpi_row
from data import UserData


def render(data: UserData):
    st.header("Hoy")
    today = data.table.iloc[-1]
    first_pickup = today["first_pickup"]
    pickup_text = first_pickup.strftime("%H:%M") if isinstance(first_pickup, dt_time) else "—"
    kpi_row([
        ("Puntuación", f"{today['score']:.0f}", ""),
        ("Pantalla", f"{today['screen_minutes'] / 60:.1f} h", ""),
        ("Offline", f"{today['offline_minutes'] / 60:.1f} h", ""),
        ("Primer pickup", pickup_text, ""),
        ("Desbloqueos", f"{today['pickups']:.0f}", ""),
        ("Noche (min)", f"{today['bedtime_minutes']:.0f}", ""),
        ("Bloqueos", f"{today['blocks']:.0f}", ""),
    ])
    st.caption(f"{today['day']:%A %d %b}, tratado como hoy.")
