import random
import streamlit as st

ss = st.session_state

if "storage" in ss:
    ss.storage.populate_session_state(ss)

ss.setdefault("flashcards", [])
ss.setdefault("active_flashcard_idx", None)
ss.setdefault("flashcard_attempt", "")
ss.setdefault("flashcard_feedback", None)

def pick_flashcard():
    if ss.flashcards:
        ss.active_flashcard_idx = random.randrange(len(ss.flashcards))
        ss.flashcard_attempt = ""
        ss.flashcard_feedback = None

st.title("Flashcards")

if not ss.flashcards:
    st.info("No flashcards saved yet. Add some from the tutor page.")
else:
    if st.button("New card", type="primary"):
        pick_flashcard()

    if ss.active_flashcard_idx is None:
        pick_flashcard()

    if ss.active_flashcard_idx is not None:
        card = ss.flashcards[ss.active_flashcard_idx]
        prompt = card.get("prompt") or card.get("word") or card.get("term") or "Unknown"
        answer = card.get("translation") or card.get("answer") or card.get("meaning") or ""

        st.subheader("Translate this word:")
        st.markdown(f"### {prompt}")

        ss.flashcard_attempt = st.text_input(
            "Your translation",
            value=ss.flashcard_attempt,
            key="flashcard_answer_input",
        )

        if st.button("Check answer"):
            attempt = ss.flashcard_attempt.strip()
            truth = answer.strip()
            if attempt and truth and attempt.lower() == truth.lower():
                ss.flashcard_feedback = ("success", "Correct! 🎉")
            else:
                display = truth or "N/A"
                ss.flashcard_feedback = ("error", f"Not quite. Correct translation: **{display}**")

        feedback = ss.flashcard_feedback
        if feedback:
            kind, message = feedback
            if kind == "success":
                st.success(message)
            else:
                st.error(message)