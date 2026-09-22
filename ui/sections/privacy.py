"""Section 3: the privacy line. The same month seen by the user (left) and by the guardian (right)."""

import pandas as pd
import streamlit as st
from dataclasses import asdict

from components import html, label, pill, short_name, word_list
from data import UserData


def user_side(data: UserData):
    st.subheader("Lo que ve el usuario")
    html("<p>Todo esto se queda en su móvil.</p>")
    label("Apps y sitios con más tiempo")
    word_list([(short_name(app.name), f"{app.minutes:.0f} min") for app in data.apps[:6]])
    label("Bloqueos por categoría")
    word_list([(category, f"{count} bloqueos") for category, count in data.blocked_categories.most_common()])
    label("Últimos nudges")
    for nudge in data.nudges[-3:]:
        pill(f"{nudge.time:%d %b, %H:%M} · {nudge.message}")
    if not data.nudges:
        pill("Sin nudges este mes.")


def guardian_side(data: UserData):
    st.subheader("Lo que ve el guardián")
    html("<p>Solo esto sale del móvil: una fecha y tres números por día.</p>")
    needs_attention = data.statuses[-1].status == "ATTENTION_NEEDED"
    pill("ATTENTION_NEEDED · Algo necesita tu atención" if needs_attention else "HEALTHY · Todo va bien",
         "on" if needs_attention else "outline")
    notified = [f"{s.day:%d %b}" for s in data.statuses if s.notify]
    html(f"<p>Avisos recibidos: {', '.join(notified) if notified else 'ninguno'}</p>")
    html("<p>Nunca recibe nombres de apps, URLs, ni a qué hora usaste el móvil. "
         "De los bloqueos sensibles solo sabe cuántos, no cuáles.</p>")


def received_table(data: UserData):
    label("Datos que recibe el servidor, día a día")
    received = pd.DataFrame([asdict(day) for day in data.sent]).assign(status=[s.status for s in data.statuses])
    st.dataframe(received.set_index("day"), width="stretch")


def render(data: UserData):
    st.header("El límite de privacidad")
    left, right = st.columns(2, gap="large")
    with left:
        user_side(data)
    with right:
        guardian_side(data)
    received_table(data)
