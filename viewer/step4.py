"""Step 4 view: nudges (on the device) and guardian status (what the server sees)."""

from dataclasses import asdict

import pandas as pd
import streamlit as st

from guardian_engine import guardian_status, to_guardian_days
from metrics_aggregator import aggregate
from nudge_engine import find_nudges
from score_engine import score_days


def render_step4(parsed):
    st.header("En el móvil · Nudges")
    nudges = find_nudges(parsed)
    st.metric("Nudges mostrados", len(nudges))
    if nudges:
        st.dataframe(pd.DataFrame([asdict(n) for n in nudges]), hide_index=True, width="stretch")
    else:
        st.info("Sin nudges: no hay bucles de frustración ni uso nocturno.")

    st.header("En el servidor · Lo que recibe el tutor")
    daily = aggregate(parsed)
    sent = to_guardian_days(score_days(daily), daily)
    statuses = guardian_status(sent)
    table = pd.DataFrame([{**asdict(day), **asdict(status)} for day, status in zip(sent, statuses)]).set_index("day")
    cols = st.columns(2)
    cols[0].metric("Días en ATTENTION_NEEDED", int((table["status"] == "ATTENTION_NEEDED").sum()))
    cols[1].metric("Avisos al tutor", int(table["notify"].sum()))
    st.caption("Solo salen del móvil la fecha, la puntuación y los minutos nocturnos: ni apps, ni URLs, ni categorías.")
    st.dataframe(table, width="stretch")
