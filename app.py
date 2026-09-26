import streamlit as st

from core import db, ui

st.set_page_config(page_title="Wellsy", page_icon="img/icon.png", layout="wide")


@st.cache_resource
def setup():
    db.init()


setup()
ui.inject_css()

if "user" not in st.session_state:
    st.navigation([st.Page("views/login.py", title="Sign in")], position="hidden").run()
    st.stop()


def page(name, title, icon, **options):
    return st.Page(f"views/{name}.py", title=title, icon=f":material/{icon}:", **options)


NAVIGATION = {
    "": [page("home", "Home", "home", default=True)],
    "Talk": [page("chat", "Chat", "chat")],
    "Track": [
        page("mood", "Mood tracker", "mood"),
        page("journal", "Journal", "edit_note"),
        page("insights", "Insights", "insights"),
        page("assessments", "Check-ins", "fact_check"),
    ],
    "Care": [page("toolkit", "Toolkit", "self_improvement"), page("support", "Get help", "emergency")],
    "Account": [page("settings", "Settings", "settings")],
}

st.logo("img/logo-wide.png", icon_image="img/icon.png", size="large")
current = st.navigation(NAVIGATION, expanded=True)

with st.sidebar:
    st.caption(f"Signed in as **{st.session_state.user['display_name']}**")
    if st.button("Sign out", icon=":material/logout:", width="stretch"):
        st.session_state.clear()
        st.rerun()

current.run()
