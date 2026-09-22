"""Look of the dashboard: black and white, big bold type, pill shapes. Nothing here calculates anything."""

import plotly.graph_objects as go
import streamlit as st

BLACK, WHITE, GRAY, DARK_GRAY, LINE = "#000000", "#ffffff", "#8a8a8a", "#1a1a1a", "#262626"
FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif'

CSS = f"""
<style>
.stApp, .stApp * {{ font-family: {FONT}; }}
header, footer, [data-testid="stToolbar"], [data-testid="stSidebar"] {{ display: none; }}
.block-container {{ max-width: 900px; padding: 4rem 1.5rem 6rem; }}

h1, h2, h3 {{ text-align: center; font-weight: 700; letter-spacing: -0.02em; }}
h1 {{ font-size: 2.6rem; margin-bottom: 2rem; }}
h2 {{ margin-top: 5rem; font-size: 1.9rem; }}
p, .stCaption {{ text-align: center; color: {GRAY}; }}

[data-testid="stElementContainer"]:has([data-testid="stButtonGroup"]) {{ align-self: center; margin-bottom: 1rem; }}
[data-testid="stButtonGroup"] button {{ border: none !important; border-radius: 999px !important; padding: 0.5rem 1.6rem; background: {DARK_GRAY} !important; color: {GRAY} !important; }}
[data-testid="stButtonGroup"] button[data-selected="true"] {{ background: {WHITE} !important; color: {BLACK} !important; font-weight: 700; }}

.kpis {{ display: flex; justify-content: space-between; margin: 2.5rem 0; text-align: center; }}
.kpi .value {{ font-size: 2.6rem; font-weight: 700; }}
.kpi .label, .kpi .change {{ color: {GRAY}; font-size: 0.85rem; }}

.label {{ color: {GRAY}; font-size: 0.85rem; text-align: center; margin: 2.5rem 0 0.5rem; }}
.words {{ text-align: center; margin: 1rem 0 2rem; }}
.word {{ font-size: 1.6rem; font-weight: 700; margin: 0.9rem 0; }}
.word span {{ display: block; color: {GRAY}; font-size: 0.8rem; font-weight: 400; }}

.pill {{ background: {DARK_GRAY}; color: {GRAY}; border-radius: 999px; padding: 0.9rem 1.4rem; margin: 0.6rem 0; text-align: center; }}
.pill.on {{ background: {WHITE}; color: {BLACK}; font-weight: 700; }}
.pill.outline {{ background: {BLACK}; border: 1px solid {WHITE}; color: {WHITE}; font-weight: 700; }}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


def show_chart(figure: go.Figure):
    """Show a chart with the dashboard look: transparent background, hairline grid, gray text, no toolbar.
    The white marks are set where each chart is made."""
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=240, bargap=0.45,
        font=dict(color=GRAY, family=FONT), margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=None, yaxis_title=None, legend=dict(orientation="h", y=1.15, title=None),
    )
    figure.update_xaxes(showgrid=False, linecolor=LINE)
    figure.update_yaxes(gridcolor=LINE, zeroline=False, rangemode="tozero")
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
