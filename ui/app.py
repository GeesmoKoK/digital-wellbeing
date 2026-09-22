"""Layer 5: presentation dashboard (Streamlit + Plotly). It only shows what the other layers calculate.

Run (from the ui folder):  ../.venv/bin/streamlit run app.py --server.port 8502

  app.py            this file: page setup, user picker, and the sections in order
  style.py          colors, CSS and chart look
  components.py     small HTML pieces (numbers, word lists, pills)
  data.py           runs the layers for one user
  sections/         one file per part of the page: week.py, trends.py, privacy.py
"""

import streamlit as st

from data import load_user
from sections import privacy, today, trends, week
from style import apply_style

st.set_page_config(page_title="Bienestar Digital", layout="centered", initial_sidebar_state="collapsed")
apply_style()

st.title("Bienestar Digital")
user = st.segmented_control("Usuario", ["a", "b"], default="a", format_func=lambda u: f"Usuario {u.upper()}",
                            label_visibility="collapsed") or "a"
data = load_user(user)

today.render(data)
week.render(data)
trends.render(data)
privacy.render(data)
