import streamlit as st
from database import authenticate_user, register_user
import base64
from pathlib import Path
import random


def centered_logo(image_path, width=180):
    img_bytes = Path(image_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center;">
            <img src="data:image/png;base64,{encoded}" width="{width}">
        </div>
        """,
        unsafe_allow_html=True
    )


QUOTES = [
    "You are not alone. Small steps matter.",
    "Healing is not linear. Be gentle with yourself.",
    "It’s okay to pause. Progress takes time.",
    "Your feelings are valid.",
    "One step at a time. You are doing enough."
]


def show_auth_page():
    # Page title and styling
    st.markdown("""
    <style>
        .block-container {
            padding-top: 0.4rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Centered logo (this WILL work)
    centered_logo("img/logo.png", width=180)

    st.markdown("<h3 style='text-align: center; color: #646464;'>Your Safe Space for Mental Wellbeing</h3>",
                unsafe_allow_html=True)

    # Quote display with styling
    st.markdown("""
    <style>
                
    /* Light theme */
    [data-theme="light"] .quote-card {
        background-color: #f6f8fb;
        color: #5f6368;
    }

    /* Dark theme */
    [data-theme="dark"] .quote-card {
        background-color: #1e1e1e;
        color: #d0d0d0;
    }

    /* Shared styling */
    .quote-card {
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
    }

    .quote-author {
        font-size: 14px;
        opacity: 0.75;
    }
    </style>
    """, unsafe_allow_html=True)

    quote = random.choice(QUOTES)

    st.markdown(f"""
    <div class="quote-card">
        <p style="font-size:17px; margin-bottom:6px;">
            “{quote}”
        </p>
        <div class="quote-author">
            — Wellsy 🌱
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None

    if not st.session_state["authenticated"]:
        # Create a clean centered layout
        col1, center_col, col2 = st.columns([1, 2, 1])

        with center_col:
            st.subheader("Welcome Back")

            # Radio choice
            option = st.radio(
                "Choose action",
                ["Login", "Register"],
                horizontal=True
            )

            # ONE form block
            with st.form(key="auth_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter username",
                    key="username_input"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter password",
                    key="password_input"
                )

                # Dynamic label
                submit_label = "Log In" if option == "Login" else "Sign Up"

                # Single submit button
                submit_button = st.form_submit_button(
                    label=submit_label,
                    use_container_width=True
                )

            # Handle after submit
            if submit_button:
                with st.spinner("Processing..."):
                    if option == "Register":
                        # Register logic
                        if register_user(username, password):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already exists.")
                    else:
                        # Login logic
                        if authenticate_user(username, password):
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

            # Add a helpful message
            st.markdown(
                "<div style='text-align: center; margin-top: 20px; color: #888;'>Your journey to mental wellness begins here</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <hr style="margin-top: 2rem; margin-bottom: 1rem;">
                <p style="text-align:center; font-size: 12px; color: #888;">
                    © 2026 Payal Sumbhe · Vrapo.Tech
                </p>
                """,
                unsafe_allow_html=True
            )
