import pandas as pd
import streamlit as st

from core import charts, db, stats, ui
from core.content import ANSWERS, ASSESSMENTS

user = st.session_state.user
uid, zone = user["id"], ui.tz()

ui.header(
    "Check-ins",
    "Short, widely used questionnaires about the last two weeks. They are screening tools, not a diagnosis.",
)
kind = st.segmented_control(
    "Questionnaire",
    list(ASSESSMENTS),
    default="PHQ-9",
    required=True,
    format_func=lambda k: ASSESSMENTS[k]["title"],
    label_visibility="collapsed",
)
test = ASSESSMENTS[kind]
top = 3 * len(test["questions"])

with st.form(f"form_{kind}"):
    st.markdown("**Over the last 2 weeks, how often have you been bothered by the following?**")
    answers = [
        st.radio(
            f"{n}. {text}", range(4), index=None, format_func=ANSWERS.__getitem__, horizontal=True, key=f"{kind}_{n}"
        )
        for n, text in enumerate(test["questions"], start=1)
    ]
    submitted = st.form_submit_button("See my result", type="primary")

if submitted:
    if None in answers:
        st.warning("Please answer every question to see your result.")
    else:
        score = sum(answers)
        label, advice = stats.severity(test, score)
        db.insert("assessments", user_id=uid, kind=kind, score=score)
        with st.container(border=True):
            st.subheader(f"{score} / {top} · {label}")
            st.write(advice)
            st.caption(
                "This is a screening result, not a diagnosis. A doctor or counsellor can help you make sense of it."
            )
        risk = test["risk_item"]
        if risk is not None and answers[risk] > 0:
            ui.crisis_card(user["country"])

history = db.rows("assessments", uid, where="kind=?", args=(kind,), order="created_at")
if history:
    st.subheader("Your scores over time")
    frame = pd.DataFrame(history)
    frame["date"] = pd.to_datetime(frame["created_at"], utc=True).dt.tz_convert(zone).dt.tz_localize(None)
    st.altair_chart(charts.scores(frame, top), width="stretch")
