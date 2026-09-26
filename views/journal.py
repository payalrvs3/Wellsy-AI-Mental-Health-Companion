import streamlit as st

from core import ai, db, safety, stats, ui
from core.content import JOURNAL_PROMPTS

REFLECT = (
    "Reflect this private journal entry back to the writer in 3 to 4 warm sentences: name the main feelings, "
    "point out one strength or helpful pattern, and end with one gentle question. Do not diagnose."
)

user = st.session_state.user
uid, zone = user["id"], ui.tz()


def clean_tags(text):
    return ",".join(tag.strip() for tag in text.split(",") if tag.strip())


@st.dialog("Edit entry", width="large")
def edit_entry(entry):
    title = st.text_input("Title", entry["title"], max_chars=80)
    body = st.text_area("Entry", entry["body"], height=260)
    tags = st.text_input("Tags (comma separated)", entry["tags"])
    if st.button("Save changes", type="primary") and body.strip():
        db.update(
            "journal", entry["id"], uid, title=title.strip() or "Untitled", body=body.strip(), tags=clean_tags(tags)
        )
        st.rerun()


ui.header("Journal", "Writing things down can make them feel lighter.")
write, browse = st.tabs(["New entry", "My entries"])

with write:
    prompt = st.selectbox("Prompt", list(JOURNAL_PROMPTS))
    st.caption(JOURNAL_PROMPTS[prompt])
    with st.form("entry", clear_on_submit=True, border=False):
        title = st.text_input("Title (optional)", max_chars=80)
        body = st.text_area("What's on your mind?", height=240)
        tags = st.text_input("Tags (optional, comma separated)")
        if st.form_submit_button("Save entry", type="primary"):
            if body.strip():
                db.insert(
                    "journal", user_id=uid, title=title.strip() or prompt, body=body.strip(), tags=clean_tags(tags)
                )
                st.toast("Entry saved", icon="✅")
                if safety.is_crisis(body):
                    ui.crisis_card(user["country"])
            else:
                st.warning("Write a few words before saving.")

with browse:
    term = st.text_input("Search", placeholder="Search titles, text or tags", label_visibility="collapsed")
    where, args = ("title LIKE ? OR body LIKE ? OR tags LIKE ?", (f"%{term}%",) * 3) if term else ("", ())
    entries = db.rows("journal", uid, where, args, order="created_at DESC, id DESC", limit=50)
    if not entries:
        st.caption("No entries found." if term else "Your entries will appear here after you save one.")
    for entry in entries:
        with st.expander(f"{stats.local(entry['created_at'], zone, '%d %b %Y')} · {entry['title']}"):
            st.markdown(entry["body"])
            if entry["tags"]:
                st.caption("Tags: " + entry["tags"].replace(",", ", "))
            edit, reflect, remove = st.columns(3)
            if edit.button("Edit", key=f"edit_{entry['id']}", icon=":material/edit:", width="stretch"):
                edit_entry(entry)
            if reflect.button(
                "Reflect with Wellsy", key=f"reflect_{entry['id']}", icon=":material/auto_awesome:", width="stretch"
            ):
                with st.spinner("Reflecting..."):
                    try:
                        st.info(ai.complete(f"{REFLECT}\n\nTitle: {entry['title']}\n\n{entry['body']}"))
                    except ai.AIError as error:
                        st.error(str(error))
            if remove.button("Delete", key=f"delete_{entry['id']}", icon=":material/delete:", width="stretch"):
                db.delete("journal", entry["id"], uid)
                st.rerun()
