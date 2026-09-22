"""Step 2 view: daily metrics."""

from dataclasses import asdict

import pandas as pd
import streamlit as st

from metrics_aggregator import aggregate

CHARTS = {
    "screen_minutes": "Tiempo de pantalla (min)",
    "bedtime_minutes": "Minutos en horario nocturno, 23:00-06:00 (min)",
    "pickups": "Desbloqueos",
    "longest_offline_minutes": "Mayor tramo sin móvil (min)",
    "distinct_apps": "Apps y sitios distintos",
    "app_switches": "Cambios de app",
    "blocks": "Bloqueos",
    "sensitive_blocks": "Bloqueos sensibles (adulto, apuestas, desnudez)",
}


def render_step2(parsed):
    daily = pd.DataFrame([asdict(d) for d in aggregate(parsed)]).set_index("day")
    for column, title in CHARTS.items():
        st.subheader(title)
        st.bar_chart(daily[column])
    with st.expander("Ver como tabla"):
        st.dataframe(daily, width="stretch")
