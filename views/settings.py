import json

import streamlit as st

import core
from core import auth, db, safety, ui
from core.ai import PERSONAS

user = st.session_state.user
uid = user["id"]


@st.dialog("Delete your account?")
def delete_account():
    st.write(
        "This permanently deletes your account, chats, journal, mood history and safety plan. It cannot be undone."
    )
    password = st.text_input("Enter your password to confirm", type="password")
    if st.button("Delete everything", type="primary"):
        try:
            auth.delete_account(uid, password)
        except auth.AuthError as error:
            st.error(str(error))
        else:
            st.session_state.clear()
            st.rerun()


ui.header("Settings")

with st.form("profile"):
    st.subheader("Profile")
    name = st.text_input("Display name", user["display_name"], max_chars=40)
    country = st.selectbox(
        "Country",
        safety.COUNTRIES,
        index=safety.COUNTRIES.index(user["country"]) if user["country"] in safety.COUNTRIES else None,
        placeholder="Choose your country",
        help="Used to show the right helplines.",
    )
    persona = st.selectbox("Default persona for new chats", list(PERSONAS), index=list(PERSONAS).index(user["persona"]))
    use_context = st.toggle(
        "Personalise replies using a short summary of my recent mood, check-ins and journal tags",
        value=bool(user["use_context"]),
    )
    if st.form_submit_button("Save changes", type="primary"):
        db.update_user(
            uid,
            display_name=name.strip() or user["username"],
            country=country,
            persona=persona,
            use_context=int(use_context),
        )
        st.session_state.user = auth.get_user(uid)
        st.rerun()

with st.form("password", clear_on_submit=True):
    st.subheader("Password")
    current = st.text_input("Current password", type="password")
    new = st.text_input("New password", type="password", help="At least 8 characters.")
    if st.form_submit_button("Update password"):
        try:
            auth.change_password(uid, current, new)
            st.success("Password updated.")
        except auth.AuthError as error:
            st.error(str(error))

with st.container(border=True):
    st.subheader("Your data")
    st.caption("Download everything Wellsy has stored for you, or permanently delete your account.")
    first, second = st.columns(2)
    first.download_button(
        "Download my data (JSON)",
        json.dumps(db.export_all(uid), indent=2),
        "wellsy-data.json",
        "application/json",
        icon=":material/download:",
        width="stretch",
    )
    if second.button("Delete my account", icon=":material/delete_forever:", width="stretch"):
        delete_account()

with st.expander("About and privacy"):
    st.markdown(
        f"**Wellsy {core.__version__}** is a supportive companion, not a medical or emergency service.\n\n"
        "Your account, journal, check-ins and chats are stored in this app's database. Chat messages, "
        "journal reflections you request, and (if enabled above) a short summary of your recent mood, "
        "check-in scores and journal tags are sent to Groq to generate replies. Screening questionnaires "
        "(PHQ-9, GAD-7) are free to use and were developed by Spitzer, Williams, Kroenke and colleagues."
    )
