"""Altair charts shared by the dashboard and insights pages."""

import altair as alt
import pandas as pd

from core.content import MOOD_COLORS
from core.stats import WEEKDAYS

BRAND = "#2F8FD8"
MOOD_SCALE = alt.Scale(domain=[1, 3, 5], range=[MOOD_COLORS[0], MOOD_COLORS[2], MOOD_COLORS[4]])
MOOD_AXIS = alt.Scale(domain=[1, 5])


def trend(daily, height=240):
    """Daily average mood with a 7-day rolling average."""
    data = daily.assign(rolling=daily["mood"].rolling(7, min_periods=3).mean())
    base = alt.Chart(data).encode(x=alt.X("day:T", title=None, axis=alt.Axis(format="%d %b")))
    points = base.mark_circle(size=70).encode(
        y=alt.Y("mood:Q", scale=MOOD_AXIS, title=None),
        color=alt.Color("mood:Q", scale=MOOD_SCALE, legend=None),
        tooltip=[alt.Tooltip("day:T", format="%d %b"), alt.Tooltip("mood:Q", format=".1f", title="Mood")],
    )
    line = base.mark_line(color=BRAND, strokeWidth=2.5, interpolate="monotone").encode(
        y=alt.Y("rolling:Q", scale=MOOD_AXIS)
    )
    return (points + line).properties(height=height)


def bars(series, horizontal=True, diverging=False):
    """Bar chart for a labelled Series. Weekday labels keep calendar order."""
    data = series.rename_axis("label").reset_index(name="value")
    label = alt.Y("label:N", title=None, sort="-x") if horizontal else alt.X("label:N", title=None, sort=WEEKDAYS)
    value = alt.X("value:Q", title=None) if horizontal else alt.Y("value:Q", title=None, scale=MOOD_AXIS)
    color = (
        alt.condition(alt.datum.value > 0, alt.value(MOOD_COLORS[4]), alt.value(MOOD_COLORS[1]))
        if diverging
        else alt.value(BRAND)
    )
    encoding = {"y": label, "x": value} if horizontal else {"x": label, "y": value}
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(color=color, tooltip=["label", alt.Tooltip("value:Q", format=".2f")], **encoding)
        .properties(height=240)
    )


def calendar(daily):
    """GitHub-style heatmap: one cell per day, weeks across, weekdays down."""
    data = daily.assign(
        week=daily["day"] - pd.to_timedelta(daily["day"].dt.weekday, unit="D"), weekday=daily["day"].dt.strftime("%a")
    )
    return (
        alt.Chart(data)
        .mark_rect(cornerRadius=3, stroke="white", strokeWidth=2)
        .encode(
            x=alt.X("yearmonthdate(week):O", title=None, axis=alt.Axis(format="%d %b", labelAngle=0)),
            y=alt.Y("weekday:O", sort=WEEKDAYS, title=None),
            color=alt.Color("mood:Q", scale=MOOD_SCALE, legend=None),
            tooltip=[alt.Tooltip("day:T", format="%a %d %b"), alt.Tooltip("mood:Q", format=".1f", title="Mood")],
        )
        .properties(height=190)
    )


def scatter(data):
    """Sleep hours against mood with a fitted line."""
    base = alt.Chart(data).encode(
        x=alt.X("sleep_hours:Q", title="Hours slept", scale=alt.Scale(zero=False)),
        y=alt.Y("score:Q", title="Mood", scale=MOOD_AXIS),
    )
    return (
        base.mark_circle(size=80, color=BRAND, opacity=0.7)
        + base.transform_regression("sleep_hours", "score").mark_line(color=MOOD_COLORS[1])
    ).properties(height=240)


def scores(data, top):
    """Questionnaire scores over time."""
    return (
        alt.Chart(data)
        .mark_line(point=True, color=BRAND, strokeWidth=2.5)
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b")),
            y=alt.Y("score:Q", scale=alt.Scale(domain=[0, top]), title=None),
            tooltip=[alt.Tooltip("date:T", format="%d %b %Y"), "score"],
        )
        .properties(height=220)
    )
