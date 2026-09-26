import streamlit as st

from core import db, safety, ui
from core.content import SAFETY_PLAN_STEPS

user = st.session_state.user
uid = user["id"]

ui.header("Get help", "If you are in danger right now, contact your local emergency number first.")
default = safety.COUNTRIES.index(user["country"]) if user["country"] in safety.COUNTRIES else None
country = st.selectbox("Your country", safety.COUNTRIES, index=default, placeholder="Choose your country")
ui.crisis_card(country)

st.subheader("Feeling overwhelmed?")
st.page_link("views/toolkit.py", label="Try a breathing or grounding exercise", icon=":material/self_improvement:")
st.page_link("views/chat.py", label="Talk it through with Wellsy", icon=":material/chat:")

st.subheader("My safety plan")
st.caption("A personal plan for hard moments. It is easiest to write while you feel calm, and only you can see it.")
plan = db.get_plan(uid)
with st.form("plan"):
    values = {key: st.text_area(label, plan.get(key, ""), height=90) for key, label in SAFETY_PLAN_STEPS.items()}
    if st.form_submit_button("Save my plan", type="primary"):
        db.save_plan(uid, values)
        plan = values
        st.toast("Safety plan saved", icon="✅")
if any(plan.values()):
    text = "\n\n".join(f"{SAFETY_PLAN_STEPS[key]}\n{value}" for key, value in plan.items() if value)
    st.download_button("Download my plan", text, "wellsy-safety-plan.txt", icon=":material/download:")

st.subheader("Find professional support")
st.markdown(
    f"- Verified helplines and services worldwide: [findahelpline.com]({safety.DIRECTORY_URL})\n"
    "- India: [Tele-MANAS](https://telemanas.mohfw.gov.in), the government's free 24/7 tele-mental-health service"
)
