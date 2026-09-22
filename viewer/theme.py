"""Chart colors (validated categorical palette) and Altair styling shared by every step."""

import altair as alt
import streamlit as st

# Fixed category -> palette slot, so a category keeps its color whatever the filters show.
_CATEGORY_ORDER = [
    "MESSAGING", "SOCIAL_MEDIA", "ENTERTAINMENT", "NEWS",
    "GAMING", "SHOPPING", "ADULT", "GAMBLING",
]
_LIGHT = {
    "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"],
    "ink": "#0b0b0b", "ink_2": "#52514e", "muted": "#898781", "grid": "#e1e0d9", "surface": "#fcfcfb",
}
_DARK = {
    "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
    "ink": "#ffffff", "ink_2": "#c3c2b7", "muted": "#898781", "grid": "#2c2c2a", "surface": "#1a1a19",
}


def palette() -> dict:
    """Light or dark palette, following the Streamlit theme."""
    try:
        return _DARK if st.context.theme.type == "dark" else _LIGHT
    except Exception:
        return _LIGHT


def category_scale() -> alt.Scale:
    """Color scale for the 9 categories; OTHER is a neutral gray, not a series hue."""
    colors = palette()
    return alt.Scale(
        domain=[*_CATEGORY_ORDER, "OTHER"],
        range=[*colors["series"], colors["muted"]],
    )


def style(chart: alt.Chart | alt.LayerChart) -> alt.Chart | alt.LayerChart:
    """Recessive grid/axes, ink-colored text, transparent background."""
    c = palette()
    return (
        chart.configure(background="rgba(0,0,0,0)")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=c["ink_2"], titleColor=c["ink_2"], gridColor=c["grid"],
            domainColor=c["grid"], tickColor=c["grid"], labelFontSize=12, titleFontSize=12,
        )
        .configure_legend(labelColor=c["ink_2"], titleColor=c["ink_2"], orient="top", labelFontSize=12)
    )
