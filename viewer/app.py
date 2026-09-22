"""Progress viewer: one tab per finished step. It calls the parser and shows the DTOs it returns.

Run (from the viewer folder):  ../.venv/bin/streamlit run app.py
To add a step: write a render function in its own file and add it to STEPS.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))  # to import the parser from the project folder

from parse_events import parse_user
from step1 import render_step1
from step2 import render_step2
from step3 import render_step3
from step4 import render_step4

STEPS = {"Paso 1 · Parser": render_step1, "Paso 2 · Métricas diarias": render_step2,
         "Paso 3 · Puntuación": render_step3,
         "Paso 4 · Nudges y tutor": render_step4}

st.set_page_config(page_title="Bienestar Digital · pasos", layout="wide")
st.title("Bienestar Digital · progreso por pasos")

user = st.sidebar.radio("Usuario", ["a", "b"], format_func=lambda u: f"Usuario {u.upper()}")
parsed = parse_user(user)

for tab, render in zip(st.tabs(list(STEPS)), STEPS.values()):
    with tab:
        render(parsed)
