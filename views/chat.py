import streamlit as st

from core import ai, db, safety, stats, ui
from core.ai import PERSONAS

STARTERS = ["I've been feeling anxious", "I had a rough day", "Help me reframe a thought", "I can't sleep well"]
AVATAR = "img/icon.png"

user = st.session_state.user
uid, country, zone = user["id"], user["country"], ui.tz()


def new_chat():
    """Reuse an empty conversation if there is one, otherwise start a new one."""
    blank = db.one(
        "SELECT id FROM chats c WHERE user_id=? AND NOT EXISTS (SELECT 1 FROM messages WHERE chat_id=c.id) "
        "ORDER BY id DESC LIMIT 1",
        uid,
    )
    st.session_state.chat_id = blank["id"] if blank else db.insert("chats", user_id=uid, persona=user["persona"])


@st.dialog("Delete this conversation?")
def confirm_delete(chat_id):
    st.write("This permanently deletes the conversation and all of its messages.")
    if st.button("Delete", type="primary"):
        db.delete("chats", chat_id, uid)
        st.rerun()


if not db.rows("chats", uid, limit=1):
    new_chat()
chats = {c["id"]: c for c in db.rows("chats", uid, order="updated_at DESC, id DESC")}
if st.session_state.get("chat_id") not in chats:
    st.session_state.chat_id = next(iter(chats))

ui.header("Chat", "A private space to talk things through. Wellsy is an AI companion, not a therapist.")
pick, add, manage = st.columns([5, 1.5, 1.5], vertical_alignment="bottom")
chat_id = pick.selectbox(
    "Conversation", list(chats), key="chat_id", format_func=lambda i: chats[i]["title"], label_visibility="collapsed"
)
add.button("New chat", icon=":material/add:", on_click=new_chat, width="stretch")
chat = chats[chat_id]
history = db.messages(uid, chat_id)

with manage.popover("Manage", icon=":material/tune:", width="stretch"):
    title = st.text_input("Rename", chat["title"], key=f"title_{chat_id}", max_chars=60)
    if st.button("Save name", width="stretch") and title.strip():
        db.update("chats", chat_id, uid, title=title.strip())
        st.rerun()
    transcript = "\n\n".join(f"{'You' if m['role'] == 'user' else 'Wellsy'}: {m['content']}" for m in history)
    st.download_button("Export chat", transcript, "wellsy-chat.txt", icon=":material/download:", width="stretch")
    if st.button("Delete chat", icon=":material/delete:", width="stretch"):
        confirm_delete(chat_id)

persona = st.pills(
    "Persona",
    list(PERSONAS),
    default=chat["persona"],
    required=True,
    key=f"persona_{chat_id}",
    format_func=lambda p: f"{PERSONAS[p]['icon']} {p}",
    label_visibility="collapsed",
)
if persona != chat["persona"]:
    db.update("chats", chat_id, uid, persona=persona)
st.caption(PERSONAS[persona]["tagline"])

prompt = st.chat_input("Share what's on your mind...") or st.session_state.pop("pending", None)

for message in history:
    with st.chat_message(message["role"], avatar=AVATAR if message["role"] == "assistant" else None):
        st.markdown(message["content"])

if not history and not prompt:
    st.markdown("**How are you feeling today?** Pick a starter or write your own message below.")
    for col, text in zip(st.columns(len(STARTERS)), STARTERS, strict=True):
        if col.button(text, width="stretch"):
            st.session_state.pending = text
            st.rerun()

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    risky = safety.is_crisis(prompt)
    if risky:
        ui.crisis_card(country)
    db.add_message(uid, chat_id, "user", prompt)
    if chat["title"] == "New chat":
        db.update("chats", chat_id, uid, title=prompt.strip()[:40])
    context = ""
    if user["use_context"]:
        context = stats.context_summary(
            stats.mood_frame(db.rows("moods", uid, order="logged_at"), zone),
            db.rows("assessments", uid, order="created_at"),
            db.rows("journal", uid, order="created_at"),
            stats.today(zone),
        )
    with st.chat_message("assistant", avatar=AVATAR):
        try:
            reply = st.write_stream(
                ai.stream_reply([*history, {"role": "user", "content": prompt}], persona, country, context, risky)
            )
        except ai.AIError as error:
            st.error(str(error))
            st.stop()
    if not reply:
        st.error("I couldn't put a reply together. Please try again.")
        st.stop()
    db.add_message(uid, chat_id, "assistant", reply)
    st.rerun()
elif any(m["role"] == "user" for m in history) and safety.is_crisis(
    next(m["content"] for m in reversed(history) if m["role"] == "user")
):
    ui.crisis_card(country)
