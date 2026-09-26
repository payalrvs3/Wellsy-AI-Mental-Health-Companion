import random

import streamlit as st

from core import auth
from core.content import AFFIRMATIONS


def enter(action, *credentials):
    try:
        st.session_state.user = action(*credentials)
    except auth.AuthError as error:
        st.error(str(error))
    else:
        st.rerun()


_, center, _ = st.columns([1, 1.6, 1])
with center:
    logo = st.columns([1, 1.3, 1])[1]
    logo.image("img/logo.png", width="stretch")
    st.markdown('<p class="tagline">Your safe space for mental wellbeing</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="tagline"><em>“{st.session_state.setdefault("quote", random.choice(AFFIRMATIONS))}”</em></p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        sign_in, sign_up = st.tabs(["Sign in", "Create account"])
        with sign_in, st.form("sign_in", border=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary", width="stretch"):
                enter(auth.login, username, password)
        with sign_up, st.form("sign_up", border=False):
            new_username = st.text_input("Choose a username", help="3-30 letters, numbers or underscores.")
            new_password = st.text_input("Choose a password", type="password", help="At least 8 characters.")
            confirm = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create account", type="primary", width="stretch"):
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    enter(auth.register, new_username, new_password)

    st.markdown(
        '<p class="tagline" style="font-size:.85rem">'
        "Wellsy is a supportive companion, not a medical or emergency service. "
        "Your messages are stored in this app's database and sent to Groq to generate replies.<br>"
        "© 2026 Payal Sumbhe · Vrapo.Tech</p>",
        unsafe_allow_html=True,
    )
