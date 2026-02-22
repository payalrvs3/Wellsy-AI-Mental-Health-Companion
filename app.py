import streamlit as st
from database import init_db, create_new_session, get_sessions, rename_session, delete_session, save_chat, load_chat_history
from auth import show_auth_page
from chatbot import get_response


def auto_scroll():
    st.markdown(
        """
        <script>
            const chatContainer = window.parent.document.querySelector('section.main');
            if (chatContainer) {
                chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
            }
        </script>
        """,
        unsafe_allow_html=True,
    )


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Wellsy",
    page_icon="img/icon.png",
    layout="wide",
)

# ---------- DB INIT ----------
init_db()

# ---------- SESSION DEFAULTS ----------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- AUTH PAGE (STOP EVERYTHING ELSE) ----------
if not st.session_state["authenticated"]:
    show_auth_page()
    st.stop()   # ⛔ nothing below renders until login


# ======================================================
# =================== CHAT PAGE ========================
# ======================================================

username = st.session_state["username"]

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            padding-top: 0rem;
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0rem;
        }

        /* Remove extra top margin above first sidebar element */
        [data-testid="stSidebar"] img {
            margin-top: -80px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- SIDEBAR + TITLE (CHAT PAGE ONLY) ----------
st.sidebar.image("img/logo.png", width=200)
st.title("Wellsy - AI Mental Health Companion - Design For Mental Wellness")

# ---------- SIDEBAR CONTENT ----------
st.sidebar.title(f"💬 {username}'s Chat Sessions")

st.sidebar.markdown("### 🧠 Choose Your AI Persona")
persona_options = {
    "Wellsy Counselor": "The balanced and supportive AI that provides empathetic yet structured mental health support.",
    "Empathetic Listener": "A deeply empathetic AI that focuses on active listening and validation.",
    "Growth Coach": "A high-energy AI that encourages and empowers users to take action for self-improvement.",
    "CBT Companion": "A rational AI that helps reframe negative thoughts using cognitive behavioral techniques.",
}

selected_persona = st.sidebar.selectbox(
    "Select a Persona:",
    list(persona_options.keys()),
    key="persona_select",
)
st.session_state["selected_persona"] = selected_persona
st.sidebar.markdown(f"📝 *{persona_options[selected_persona]}*")

# ---------- SAFETY LOCATION ----------
st.sidebar.markdown("### 🌍 Safety Support Location")

country = st.sidebar.selectbox(
    "Select your country (optional):",
    ["None", "India", "USA", "UK", "Canada"],
)

st.session_state["country"] = None if country == "None" else country

# ---------- CHAT SESSIONS ----------
user_sessions = get_sessions(username)

if "prev_session" not in st.session_state:
    st.session_state["prev_session"] = None
    st.session_state["selected_session"] = None

session_options = {name: sid for sid, name in user_sessions}

selected_session_name = st.sidebar.radio(
    "Select a chat:",
    list(session_options.keys()),
    index=None,
)

if selected_session_name:
    session_id = session_options[selected_session_name]
    if st.session_state["prev_session"] != session_id:
        st.session_state["selected_session"] = session_id
        st.session_state["prev_session"] = session_id
        st.session_state.messages = []
        st.rerun()

if st.sidebar.button("🆕 New Chat"):
    new_session_id, _ = create_new_session(username)
    st.session_state["selected_session"] = new_session_id
    st.session_state["prev_session"] = new_session_id
    st.session_state.messages = []
    st.rerun()

new_name = st.sidebar.text_input(
    "Rename chat:",
    selected_session_name if selected_session_name else "",
)

if st.sidebar.button("Rename") and selected_session_name:
    rename_session(st.session_state["selected_session"], new_name)
    st.rerun()

if st.sidebar.button("🗑️ Delete Chat") and selected_session_name:
    delete_session(st.session_state["selected_session"])
    st.session_state["selected_session"] = None
    st.session_state["prev_session"] = None
    st.session_state.messages = []
    st.rerun()

# ---------- CHAT AREA ----------
if st.session_state["selected_session"]:
    st.write(f"💬 Chat Session: **{selected_session_name}**")
    st.write(f"🧠 AI Persona: **{st.session_state['selected_persona']}**")

    if not st.session_state.messages:
        history = load_chat_history(st.session_state["selected_session"])
        for msg, res in history:
            st.session_state.messages.append({"role": "user", "content": msg})
            st.session_state.messages.append(
                {"role": "assistant", "content": res})

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user", avatar="🌸").write(message["content"])
        else:
            st.chat_message("assistant", avatar="🤖").write(message["content"])
            auto_scroll()

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.spinner("AI is thinking..."):
            response = get_response(
                username,
                user_input,
                st.session_state["selected_persona"],
                st.session_state.get("country"),
            )

            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

            save_chat(
                st.session_state["selected_session"],
                username,
                user_input,
                response,
            )

        st.rerun()

else:
    st.markdown(f"### 👋 Welcome, {username}!")
    st.markdown(
        "Select an existing chat from the left panel or start a **new chat** to begin."
    )

# ---------- LOGOUT ----------
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Log Out"):
    st.session_state.clear()
    st.rerun()
