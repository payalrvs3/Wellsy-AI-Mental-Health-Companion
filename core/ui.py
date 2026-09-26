"""Shared Streamlit helpers: styling, page headers and the crisis support card."""

import streamlit as st

from core import safety, stats

CSS = """
.block-container { padding-top: 2rem; padding-bottom: 5rem; max-width: 1080px; }
h1, h2, h3 { letter-spacing: -0.015em; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; }
.tagline { text-align: center; opacity: .75; margin-bottom: 1rem; }
.hero { background: linear-gradient(135deg, #2F8FD8 0%, #58C4D8 100%); color: #fff; border-radius: 20px;
        padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }
.hero h2 { color: #fff; margin: 0 0 .25rem; padding: 0; font-size: 1.7rem; }
.hero p { margin: 0; opacity: .95; }
.stage { position: relative; width: 260px; height: 260px; margin: 1rem auto; display: grid; place-items: center; }
.orb { width: 220px; height: 220px; border-radius: 50%;
       background: radial-gradient(circle at 30% 30%, #9BE0F2, #2F8FD8);
       box-shadow: 0 0 60px rgba(47, 143, 216, .45); }
.phase { position: absolute; color: #fff; font-weight: 600; font-size: 1.1rem; opacity: 0; }
.st-key-crisis { background: rgba(231, 111, 81, .08); border-color: rgba(231, 111, 81, .45) !important; }
"""


def inject_css():
    st.html(f"<style>{CSS}</style>")


def header(title, subtitle=""):
    st.header(title, anchor=False)
    if subtitle:
        st.caption(subtitle)


def tz():
    """The browser's IANA timezone, falling back to UTC."""
    return stats.valid_zone(st.context.timezone or "UTC")


def crisis_card(country=None):
    """Helplines for the user's country. Shown whenever risk language is detected."""
    with st.container(border=True, key="crisis"):
        st.markdown("#### 💙 You're not alone. Support is available right now.")
        for name, number, note in safety.HELPLINES.get(country, []):
            st.markdown(f"**{name}**: [{number}](tel:{safety.dial(number)}) · {note}")
        if country not in safety.HELPLINES:
            st.markdown("Select your country to see local helplines.")
        emergency = safety.EMERGENCY.get(country, "your local emergency number")
        st.caption(
            f"If you are in immediate danger, call {emergency}. "
            f"More helplines worldwide: [findahelpline.com]({safety.DIRECTORY_URL})."
        )


def metric(column, label, value, delta=None):
    column.metric(label, value, delta, border=True, height=140)
