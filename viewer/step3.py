"""Step 3 view: daily wellbeing score."""

from dataclasses import asdict

import altair as alt
import pandas as pd
import streamlit as st

from metrics_aggregator import aggregate
from score_engine import score_days

PENALTIES = ["screen_penalty", "fragmentation_penalty", "bedtime_penalty", "restricted_penalty"]


def render_step3(parsed):
    scores = pd.DataFrame([asdict(s) for s in score_days(aggregate(parsed))]).set_index("day")
    st.metric("Puntuación media", round(scores["score"].mean(), 1))
    st.subheader("Puntuación diaria (0-100)")
    line = alt.Chart(scores.reset_index()).mark_line(point=True).encode(
        x=alt.X("day:T", title=None), y=alt.Y("score:Q", title=None, scale=alt.Scale(domain=[0, 100])),
        tooltip=["day:T", "score:Q"],
    )
    st.altair_chart(line, width="stretch")
    st.subheader("Puntos perdidos por día")
    st.bar_chart(scores[PENALTIES])
    with st.expander("Ver como tabla"):
        st.dataframe(scores, width="stretch")
