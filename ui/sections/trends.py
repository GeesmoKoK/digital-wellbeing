"""Section 2: the 30-day trend charts. White on black, one message per chart."""

import plotly.express as px
import plotly.graph_objects as go

from components import label
from data import UserData
from style import GRAY, WHITE, show_chart


def bar_chart(table, column: str):
    figure = px.bar(table, x="day", y=column, color_discrete_sequence=[WHITE])
    show_chart(figure)


def score_chart(table):
    """Daily score in gray and the 7-day average in white, on a fixed 0-100 axis."""
    figure = go.Figure()
    figure.add_scatter(x=table["day"], y=table["score"], name="Diaria", line=dict(color=GRAY, width=2))
    figure.add_scatter(x=table["day"], y=table["score"].rolling(7).mean(), name="Media de 7 días", line=dict(color=WHITE, width=3))
    figure.update_yaxes(range=[0, 100])
    show_chart(figure)


def render(data: UserData):
    table = data.table
    label("Puntuación")
    score_chart(table)
    label("Tiempo de pantalla (min)")
    bar_chart(table, "screen_minutes")
    label("Desbloqueos")
    bar_chart(table, "pickups")
    label("Uso nocturno, 23:00-06:00 (min)")
    bar_chart(table, "bedtime_minutes")
