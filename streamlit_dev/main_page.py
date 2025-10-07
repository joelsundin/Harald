# landing page
import streamlit as st

ss = st.session_state
ss.setdefault('counter', 0)
ss.setdefault('start', False)
ss.setdefault('stop', False)
ss.setdefault('button_label', ['START', 'SUBMIT', 'RELOAD'])
ss.setdefault('current_quiz', [])
ss.setdefault('user_answers', [])
ss.setdefault('grade', 0)
ss.setdefault('final_quiz_score', 0)

# Add the Google Font
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanchenjunga:wght@400;500;600;700&family=Libre+Baskerville:wght@700&display=swap');

    .big-text {
        font-family: 'Libre Baskerville', serif;
        font-size: 100px;
        font-style: bold-700;
        text-align: center;
        margin-top: 30vh;  /* vertically centers */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display text
st.markdown("<div class='big-text'>Harald</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='big-text' style='font-size:15px; margin-top:0vh; color:#888888;'> Harald is an interactive chatbot designed to help students practice and improve their Swedish language skills. Harald engages in free-form conversation and provides feedback on grammar, spelling, and word choice. The goal is to support language learning in a natural and motivating way. </div>",
    unsafe_allow_html=True
)
