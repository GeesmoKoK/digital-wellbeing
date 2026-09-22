"""Section 1: how the last week went, in a sentence and five numbers."""

from components import html, kpi_row
from data import UserData


def change_text(values, unit: str = "") -> str:
    """How the last 7 days compare with the 7 before, as plain text."""
    change = round(values.tail(7).mean() - values.iloc[-14:-7].mean())
    if change == 0:
        return "sin cambios"
    return f"{'↑' if change > 0 else '↓'} {abs(change)} {unit}".strip()


def week_message(score) -> str:
    this_week, last_week = score.tail(7).mean(), score.iloc[-14:-7].mean()
    if abs(this_week - last_week) < 1:
        return f"Semana estable: tu puntuación media es <b>{this_week:.0f}</b>, igual que la semana anterior."
    if this_week > last_week:
        return f"Buena semana: tu puntuación media es <b>{this_week:.0f}</b>, {this_week - last_week:.0f} puntos más que la anterior."
    return (f"Tu puntuación media es <b>{this_week:.0f}</b>, {last_week - this_week:.0f} puntos menos que la semana anterior. "
            "Ha sido una semana más difícil, y mañana es un buen día para empezar de nuevo.")


def render(data: UserData):
    table = data.table
    week = table.tail(7)
    longest = week.loc[week["longest_offline_minutes"].idxmax()]
    html(f"<p>{week_message(table['score'])}</p>")
    html(f"<p>Tu descanso más largo de la semana fue de {longest['longest_offline_minutes'] / 60:.1f} h, el {longest['day']:%d %b}.</p>")
    kpi_row([
        ("Puntuación", f"{week['score'].mean():.0f}", change_text(table["score"], "pts")),
        ("Pantalla", f"{week['screen_minutes'].mean() / 60:.1f} h", change_text(table["screen_minutes"], "min")),
        ("Desbloqueos", f"{week['pickups'].mean():.0f}", change_text(table["pickups"])),
        ("Noche (min)", f"{week['bedtime_minutes'].mean():.0f}", change_text(table["bedtime_minutes"], "min")),
        ("Bloqueos", f"{week['blocks'].mean():.0f}", change_text(table["blocks"])),
    ])
    html("<p>Media diaria de los últimos 7 días, comparada con los 7 anteriores.</p>")
