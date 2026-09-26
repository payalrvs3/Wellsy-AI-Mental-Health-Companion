import streamlit as st

from core import db, safety, stats, ui
from core.content import ACTIVITIES, EMOTIONS, MOODS

user = st.session_state.user
uid, zone = user["id"], ui.tz()

ui.header("Mood tracker", "A quick check-in helps you notice patterns over time.")

with st.form("check_in"):
    score = st.select_slider(
        "How are you feeling?", options=list(MOODS), value=3, format_func=lambda s: f"{MOODS[s][0]} {MOODS[s][1]}"
    )
    emotions = st.pills("What best describes it?", EMOTIONS, selection_mode="multi")
    activities = st.pills("What have you been up to?", ACTIVITIES, selection_mode="multi")
    sleep = st.number_input(
        "Hours slept last night (optional)", 0.0, 16.0, value=None, step=0.5, placeholder="e.g. 7.5"
    )
    note = st.text_area("Anything you'd like to note?", max_chars=500, height=90)
    saved = st.form_submit_button("Save check-in", type="primary")

if saved:
    db.insert(
        "moods",
        user_id=uid,
        score=score,
        emotions=",".join(emotions),
        activities=",".join(activities),
        sleep_hours=sleep,
        note=note.strip(),
    )
    st.toast("Check-in saved", icon="✅")
    if safety.is_crisis(note):
        ui.crisis_card(user["country"])
    elif score <= 2:
        st.info("That sounds like a hard moment. A short breathing exercise can help you settle.")
        st.page_link("views/toolkit.py", label="Open the toolkit", icon=":material/self_improvement:")

st.subheader("Recent check-ins")
recent = db.rows("moods", uid, order="logged_at DESC, id DESC", limit=8)
if not recent:
    st.caption("Nothing here yet. Your check-ins will appear after you save one.")
for entry in recent:
    emoji, label = MOODS[entry["score"]]
    with st.container(border=True):
        text, remove = st.columns([12, 1], vertical_alignment="center")
        details = [
            entry["emotions"].replace(",", ", "),
            f"{entry['sleep_hours']:g} h sleep" if entry["sleep_hours"] else "",
        ]
        text.markdown(f"{emoji} **{label}** · {stats.local(entry['logged_at'], zone)}")
        if any(details):
            text.caption(" · ".join(filter(None, details)))
        if entry["note"]:
            text.caption(f"“{entry['note']}”")
        if remove.button(
            ":material/delete:", key=f"remove_{entry['id']}", type="tertiary", help="Delete this check-in"
        ):
            db.delete("moods", entry["id"], uid)
            st.rerun()
