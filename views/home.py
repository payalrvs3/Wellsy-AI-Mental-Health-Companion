import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from core import charts, db, stats, ui
from core.content import FOCUS_TIPS, MOODS

ACTIONS = [
    ("chat", "Talk to Wellsy", "chat", "A private, supportive conversation."),
    ("mood", "Log your mood", "mood", "A check-in takes under a minute."),
    ("journal", "Write a journal entry", "edit_note", "Put your thoughts into words."),
    ("toolkit", "Calm down", "self_improvement", "Breathing and grounding exercises."),
]

user = st.session_state.user
uid, zone = user["id"], ui.tz()
now = datetime.now(ZoneInfo(zone))
today = now.date()
df = stats.mood_frame(db.rows("moods", uid, order="logged_at"), zone)

greeting = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 18 else "Good evening"
tip = FOCUS_TIPS[today.toordinal() % len(FOCUS_TIPS)]
st.html(f'<div class="hero"><h2>{greeting}, {html.escape(user["display_name"])}</h2><p>Today\'s focus: {tip}</p></div>')

if today not in set(df["day"].dt.date):
    with st.container(border=True):
        st.markdown("**How are you feeling right now?**")
        for col, (score, (emoji, label)) in zip(st.columns(5), MOODS.items(), strict=True):
            if col.button(f"{emoji} {label}", key=f"quick_{score}", width="stretch"):
                db.insert("moods", user_id=uid, score=score)
                st.toast("Check-in saved", icon="✅")
                st.rerun()

week = stats.window(df, today, 7)
previous = stats.window(df, today - timedelta(days=7), 7)
delta = None if week.empty or previous.empty else f"{week['score'].mean() - previous['score'].mean():+.1f}"
journal_count = db.one(
    "SELECT COUNT(*) AS n FROM journal WHERE user_id=? AND created_at >= datetime('now', '-30 days')", uid
)["n"]

metrics = st.columns(4)
ui.metric(metrics[0], "Check-in streak", f"{stats.streak(df, today)} days")
ui.metric(metrics[1], "7-day mood", f"{week['score'].mean():.1f} / 5" if len(week) else "-", delta)
ui.metric(metrics[2], "Check-ins this week", len(week))
ui.metric(metrics[3], "Journal entries (30 days)", journal_count)

for col, (page, title, icon, blurb) in zip(st.columns(4), ACTIONS, strict=True):
    with col, st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(blurb)
        st.page_link(f"views/{page}.py", label="Open", icon=f":material/{icon}:")

st.subheader("Your last two weeks")
recent = stats.window(df, today, 14)
if recent.empty:
    st.info("Your mood trend will appear here after your first check-in.")
else:
    st.altair_chart(charts.trend(stats.daily(recent), height=200), width="stretch")
