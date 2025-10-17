import streamlit as st
import random
from quiz_data import questions 
import base64


def get_base64_of_bin_file(bin_file):
    """ Reads a binary file and returns its Base64 encoded string. """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bin_str = get_base64_of_bin_file("cute_thinking_harald.png")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: 25%;
        background-position: center;
        background-repeat: no-repeat;
        background-position: top 70px right 50px;
    }}

    @import url('https://fonts.googleapis.com/css2?family=Kanchenjunga:wght@400;500;600;700&family=Libre+Baskerville:wght@700&display=swap');

    .smaller-text {{
        font-family: 'Libre Baskerville', serif;
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        margin-top: 10vh;
    }}
    .even-smaller-text {{
        font-family: 'Libre Baskerville', serif;
        font-size: 15px;
        font-weight: 700;
        text-align: center;
        color: #888888;
    }}
    div.stButton > button:first-child {{
        font-family: 'Libre Baskerville', serif !important;
        background-color: #ebebeb;
        color: #000000;
        border: none;
        border-radius: 12px;
    }}
    div.stButton > button:hover {{
        background-color: #d4d4d4;
        color: #000000;
        border: none;
        border-radius: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION (No changes here) ---
ss = st.session_state
ss.setdefault('counter', 0)
ss.setdefault('start', False)
ss.setdefault('stop', False)
ss.setdefault('button_label', ['Start', 'Submit', 'Quit'])
ss.setdefault('current_quiz', [])
ss.setdefault('user_answers', [])
ss.setdefault('grade', 0)
ss.setdefault('final_quiz_score', 0)       
ss.setdefault('quiz_total_questions', 10)  
ss.setdefault('highest_score', 0)
ss.setdefault('failed_questions', [])

def grade_quiz():
    json_storage = ss.get('storage')
    json_storage.populate_session_state(ss)
    """Calculates the score and identifies failed questions."""
    correct_count = 0
    # REFACTORED: Clear the list of failed questions for this specific attempt
    ss.failed_questions = [] 
    ss.user_answers = []
    total_q = len(ss.current_quiz)
    
    for i in range(total_q):
        question_data = ss.current_quiz[i]
        correct_ans = question_data.get('correct') 
        user_ans = ss.get(f'Q{i}')
        
        is_correct = (user_ans == correct_ans)
        ss.user_answers.append(is_correct)

        if is_correct:
            correct_count += 1
        else:
            ss.failed_questions.append({
                'question': question_data.get('question'),
                'options': question_data.get('options'),
                'correct': correct_ans,
                'user_answer': user_ans
            })
            
    ss.grade = correct_count
    ss.stop = True
    ss.final_quiz_score = ss.grade
    ss.quiz_total_questions = total_q
    
    if ss.grade > ss.highest_score:
        ss.highest_score = ss.grade
        st.toast(f"New High Score: {ss.highest_score}/{total_q}!", icon='🏆')
    json_storage.store_session_state(ss)

# REFACTORED: `set_up` function is removed. Its logic is now inside `button_clicked`.

def button_clicked():
    """Handles the main state transitions for the quiz."""
    
    # State 0: START clicked
    if ss.counter == 0:
        # This is the logic that was in set_up()
        ss.start = True
        ss.stop = False
        ss.counter = 1
        try:
            ss.current_quiz = random.sample(questions, 10)
        except ValueError:
            st.error("Error: Not enough questions available. Need at least 10.")
            ss.start = False
            ss.counter = 0

    # State 1: SUBMIT clicked
    elif ss.counter == 1:
        grade_quiz()
        ss.counter = 2
    
    # State 2: RESTART QUIZ clicked
    elif ss.counter == 2:
        ss.counter = 0
        ss.start = False
        ss.stop = False
        ss.current_quiz = []
        ss.user_answers = []
        ss.grade = 0


# --- MAIN APP LAYOUT ---
#st.markdown("<style>.stApp { background: none; }</style>", unsafe_allow_html=True)
st.markdown("<div class='smaller-text'>Quiz</div>", unsafe_allow_html=True)
st.markdown("<div class='even-smaller-text'> Test your basic Swedish vocabulary knowledge.</div>", unsafe_allow_html=True)
st.markdown("---")

# Display highest score in the sidebar
if ss.highest_score > 0:
    st.sidebar.markdown(f"🏆 **Highest Score:** **{ss.highest_score}** / {ss.quiz_total_questions}")

# REFACTORED: Conditional display of the quiz. This is a much cleaner flow.
if not ss.start:
    st.info("Click START to begin the quiz.")
else:
    # This container holds the questions and results
    with st.container(border=True):
        st.subheader("Quiz in Progress!")
        
        for i, question_data in enumerate(ss.current_quiz):
            radio_key = f"Q{i}"
            
            st.markdown(f"**Question {i + 1}.** {question_data.get('question')}")
            st.radio(
                label="Choose your answer:",
                options=question_data.get("options"),
                index=None,
                key=radio_key,
                label_visibility="collapsed"
            )
            
            # Show results after quiz is stopped
            if ss.stop:
                if i < len(ss.user_answers):
                    if ss.user_answers[i]:
                        st.success("✅ **CORRECT!**")
                    else:
                        correct_ans = question_data.get('correct')
                        st.error(f"❌ **INCORRECT.** The correct answer was: **{correct_ans}**")
            
            st.markdown("---")

    # Display final score metric after the quiz is submitted
    if ss.stop:
        st.markdown("##")
        st.metric(label="Your Final Score", value=f"{ss.grade} / {len(ss.current_quiz)}")

# The main button that drives the app's state

st.button(
    label=ss.button_label[ss.counter], 
    key='main_button', 
    on_click=button_clicked,
    use_container_width=True
)