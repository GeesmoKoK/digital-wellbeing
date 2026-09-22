"""Step 1 view: what the parser found in the raw events."""

from dataclasses import asdict
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from theme import category_scale, palette, style


def render_step1(parsed):
    pickups = pd.DataFrame([asdict(p) for p in parsed.pickups])
    glances = pd.DataFrame([asdict(g) for g in parsed.passive_glances])
    sessions = pd.DataFrame([asdict(s) for s in parsed.app_sessions])

    cols = st.columns(5)
    cols[0].metric("Pickups reales", len(pickups))
    cols[1].metric("Miradas pasivas", len(glances))
    cols[2].metric("Bloques de uso", len(parsed.usage_blocks))
    cols[3].metric("Sesiones app/web", len(sessions))
    cols[4].metric("Sesiones en bedtime", int(sessions["is_bedtime"].sum()))

    daily_wakeups(pickups, glances)
    day_timeline(sessions, pickups, glances)


def daily_wakeups(pickups, glances):
    st.subheader("Pickups y miradas pasivas por día")
    colors = palette()
    per_day = pd.concat([
        pd.DataFrame({"day": pickups["unlock"].dt.date, "tipo": "Pickup"}),
        pd.DataFrame({"day": glances["start"].dt.date, "tipo": "Mirada pasiva"}),
    ]).value_counts().reset_index(name="n")
    chart = alt.Chart(per_day).mark_bar(size=12, stroke=colors["surface"], strokeWidth=2).encode(
        x=alt.X("day:T", title=None, axis=alt.Axis(format="%d %b")),
        y=alt.Y("n:Q", title="Encendidos de pantalla"),
        color=alt.Color("tipo:N", title=None,
                        scale=alt.Scale(domain=["Pickup", "Mirada pasiva"], range=colors["series"][:2])),
        tooltip=["day:T", "tipo:N", "n:Q"],
    ).properties(height=240)
    st.altair_chart(style(chart), theme=None, width="stretch")


def day_timeline(sessions, pickups, glances):
    st.subheader("Un día, minuto a minuto")
    days = sorted(sessions["start"].dt.date.unique())
    day = st.select_slider("Día", options=days, format_func=lambda d: d.strftime("%a %d %b"))
    day_sessions = sessions[sessions["start"].dt.date == day]
    first_hour = day_sessions["start"].min().hour
    last_hour = min(24, day_sessions["end"].max().hour + 1)
    from_hour, to_hour = st.slider("Franja horaria", 0, 24, (first_hour, max(last_hour, first_hour + 1)))
    midnight = datetime.combine(day, datetime.min.time())
    domain = [(midnight + timedelta(hours=h)).isoformat() for h in (from_hour, to_hour)]

    colors = palette()
    lanes = ["Pickup", "Mirada pasiva", *category_scale().domain[::-1]]
    y = alt.Y("lane:N", sort=lanes, title=None)
    x_scale = alt.Scale(domain=domain)

    apps = alt.Chart(day_sessions.assign(lane=day_sessions["category"])).mark_bar(size=14, strokeWidth=1).encode(
        x=alt.X("start:T", title=None, scale=x_scale, axis=alt.Axis(format="%H:%M")), x2="end:T", y=y,
        color=alt.Color("category:N", scale=category_scale(), legend=None),
        stroke=alt.Stroke("category:N", scale=category_scale(), legend=None),
        tooltip=["name:N", "category:N", "start:T", "seconds:Q", "is_bedtime:N"],
    )
    pickup_ticks = alt.Chart(pickups[pickups["unlock"].dt.date == day].assign(lane="Pickup")).mark_tick(
        thickness=2, size=16, color=colors["ink"]).encode(x=alt.X("unlock:T", scale=x_scale), y=y)
    glance_ticks = alt.Chart(glances[glances["start"].dt.date == day].assign(lane="Mirada pasiva")).mark_tick(
        thickness=2, size=16, color=colors["muted"]).encode(x=alt.X("start:T", scale=x_scale), y=y)
    st.altair_chart(style(apps + pickup_ticks + glance_ticks).properties(height=300), theme=None, width="stretch")

    with st.expander("Ver como tabla"):
        st.dataframe(day_sessions, hide_index=True, width="stretch")
