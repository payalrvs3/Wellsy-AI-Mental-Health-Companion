from datetime import timedelta

import streamlit as st

from core import charts, db, stats, ui

user = st.session_state.user
uid, zone = user["id"], ui.tz()
today = stats.today(zone)

ui.header("Insights", "Patterns in your mood, sleep and daily activities.")
days = st.segmented_control(
    "Range",
    [7, 30, 90],
    default=30,
    required=True,
    format_func=lambda d: f"Last {d} days",
    label_visibility="collapsed",
)

df = stats.mood_frame(db.rows("moods", uid, order="logged_at"), zone)
current, previous = stats.window(df, today, days), stats.window(df, today - timedelta(days=days), days)
if current.empty:
    st.info("There are no check-ins in this period yet. Log a mood to start seeing patterns.")
    st.page_link("views/mood.py", label="Log a check-in", icon=":material/mood:")
    st.stop()

average = current["score"].mean()
metrics = st.columns(4)
ui.metric(
    metrics[0],
    "Average mood",
    f"{average:.1f} / 5",
    None if previous.empty else f"{average - previous['score'].mean():+.1f}",
)
ui.metric(metrics[1], "Check-ins", len(current))
ui.metric(metrics[2], "Best weekday", stats.weekday_avg(current).idxmax())
ui.metric(metrics[3], "Current streak", f"{stats.streak(df, today)} days")

daily = stats.daily(current)
st.subheader("Mood over time")
st.caption("Dots show each day's average. The line is your 7-day average.")
st.altair_chart(charts.trend(daily), width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("By weekday")
    st.altair_chart(charts.bars(stats.weekday_avg(current), horizontal=False), width="stretch")
with right:
    st.subheader("Common feelings")
    feelings = stats.tally(current, "emotions")
    if feelings.empty:
        st.caption("Add feelings to your check-ins to see them here.")
    else:
        st.altair_chart(charts.bars(feelings), width="stretch")

lift = stats.activity_lift(current)
if not lift.empty:
    st.subheader("What lifts your mood")
    st.caption("Average mood when you log each activity, compared with your overall average.")
    st.altair_chart(charts.bars(lift, diverging=True), width="stretch")

sleep = current.dropna(subset=["sleep_hours"])
if len(sleep) >= 5:
    st.subheader("Sleep and mood")
    st.altair_chart(charts.scatter(sleep), width="stretch")

if days >= 30:
    st.subheader("Calendar")
    st.altair_chart(charts.calendar(daily), width="stretch")

st.divider()
report = stats.summary_markdown(user["display_name"], current, db.rows("assessments", uid, order="created_at"), zone)
export = current[["at", "score", "emotions", "activities", "sleep_hours", "note"]].to_csv(index=False)
first, second = st.columns(2)
first.download_button(
    "Summary for a professional",
    report,
    "wellsy-summary.md",
    "text/markdown",
    icon=":material/description:",
    width="stretch",
)
second.download_button(
    "Check-ins (CSV)", export, "wellsy-checkins.csv", "text/csv", icon=":material/download:", width="stretch"
)
