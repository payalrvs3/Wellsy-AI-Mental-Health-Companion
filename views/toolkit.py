import pandas as pd
import streamlit as st

from core import ai, db, safety, stats, ui
from core.content import BREATHING, EMOTIONS, GROUNDING, THINKING_TRAPS

REFRAME = (
    "Someone is doing a CBT thought record. In under 90 words, gently name one possible thinking trap and offer one "
    "balanced alternative thought they could consider. Do not diagnose."
)

user = st.session_state.user
uid, zone = user["id"], ui.tz()


def breathing_html(phases):
    """A CSS-only breathing guide: the orb grows and shrinks while each phase label fades in on cue."""
    total = sum(seconds for _, seconds, _ in phases)
    frames, rules, labels, elapsed = [f"0% {{ transform: scale({phases[-1][2]}) }}"], [], [], 0
    for i, (label, seconds, scale) in enumerate(phases):
        share = seconds / total * 100
        rules.append(
            f"@keyframes show{i} {{ 0%, {share:.2f}% {{ opacity: 1 }} {share + 0.01:.2f}%, 100% {{ opacity: 0 }} }} "
            f".p{i} {{ animation: show{i} {total}s linear {elapsed}s infinite }}"
        )
        elapsed += seconds
        frames.append(f"{elapsed / total * 100:.2f}% {{ transform: scale({scale}) }}")
        labels.append(f'<span class="phase p{i}">{label}</span>')
    return (
        f"<style>@keyframes breathe {{ {' '.join(frames)} }} {' '.join(rules)}</style>"
        f'<div class="stage"><div class="orb" style="animation: breathe {total}s ease-in-out infinite"></div>'
        f"{''.join(labels)}</div>"
    )


ui.header(
    "Toolkit",
    "Simple, evidence-based exercises you can use anywhere. They support, but never replace, professional care.",
)
breathe, ground, thoughts = st.tabs(["Breathing", "Grounding", "Thought record"])

with breathe:
    name = st.segmented_control(
        "Technique", list(BREATHING), default="Box breathing", required=True, label_visibility="collapsed"
    )
    description, phases = BREATHING[name]
    st.caption(f"{description} Follow the circle for a few minutes and stop if you feel dizzy.")
    st.html(breathing_html(phases))

with ground:
    st.caption("Slowly name things around you with each sense. Nothing you type here is saved.")
    filled = 0
    for count, sense in GROUNDING:
        text = st.text_input(f"{count} {'thing' if count == 1 else 'things'} {sense.lower()}", key=f"ground_{count}")
        filled += bool(text.strip())
    st.progress(filled / len(GROUNDING), text=f"{filled} of {len(GROUNDING)} senses")
    if filled == len(GROUNDING):
        st.success("Well done. Take one slow breath and notice how your body feels now.")

with thoughts:
    st.caption("Catch an upsetting thought, weigh the evidence and write a more balanced one.")
    with st.form("thought", border=False):
        situation = st.text_area("What happened?", height=80)
        thought = st.text_area("What thought went through your mind?", height=80)
        emotion = st.pills("Which feeling came with it?", EMOTIONS)
        before = st.slider("How strong was the feeling? (0-100)", 0, 100, 60)
        traps = st.pills("Thinking traps that might apply", THINKING_TRAPS, selection_mode="multi")
        evidence_for = st.text_area("Evidence for the thought", height=80)
        evidence_against = st.text_area("Evidence against the thought", height=80)
        balanced = st.text_area("A more balanced thought", height=80)
        after = st.slider("How strong is the feeling now? (0-100)", 0, 100, 40)
        ask_col, save_col = st.columns(2)
        ask = ask_col.form_submit_button("Suggest a reframe", icon=":material/auto_awesome:", width="stretch")
        save = save_col.form_submit_button("Save record", type="primary", width="stretch")

    if (ask or save) and not thought.strip():
        st.warning("Write the thought first.")
    elif ask:
        with st.spinner("Thinking..."):
            try:
                st.info(
                    ai.complete(
                        f"{REFRAME}\nSituation: {situation or 'not given'}\nThought: {thought}\n"
                        f"Feeling: {emotion or 'not given'}"
                    )
                )
            except ai.AIError as error:
                st.error(str(error))
    elif save:
        db.insert(
            "thoughts",
            user_id=uid,
            situation=situation.strip(),
            thought=thought.strip(),
            emotion=emotion or "",
            traps=",".join(traps),
            evidence_for=evidence_for.strip(),
            evidence_against=evidence_against.strip(),
            balanced=balanced.strip(),
            intensity_before=before,
            intensity_after=after,
        )
        st.toast("Thought record saved", icon="✅")
        if safety.is_crisis(f"{situation} {thought}"):
            ui.crisis_card(user["country"])

    records = db.rows("thoughts", uid, order="created_at DESC, id DESC", limit=10)
    if records:
        st.subheader("Past records")
        table = pd.DataFrame(records)
        table["Date"] = [stats.local(t, zone, "%d %b") for t in table["created_at"]]
        table = table.rename(
            columns={
                "thought": "Thought",
                "balanced": "Balanced thought",
                "intensity_before": "Before",
                "intensity_after": "After",
            }
        )
        st.dataframe(
            table[["Date", "Thought", "Balanced thought", "Before", "After"]], hide_index=True, width="stretch"
        )
