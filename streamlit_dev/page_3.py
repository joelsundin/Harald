# quiz

import streamlit as st
import random
from quiz_data import questions 

st.header("Swedish Quiz 🇸🇪")
st.markdown("Test your basic Swedish vocabulary knowledge. Press START to begin!")

ss = st.session_state
ss.setdefault('counter', 0)
ss.setdefault('start', False)
ss.setdefault('stop', False)
ss.setdefault('button_label', ['START', 'SUBMIT', 'RELOAD'])
ss.setdefault('current_quiz', [])
ss.setdefault('user_answers', [])
ss.setdefault('grade', 0)

ss.setdefault('final_quiz_score', 0)       
ss.setdefault('quiz_total_questions', 10)  
ss.setdefault('highest_score', 0)
ss.setdefault('failed_questions', [])

def grade_quiz():
    """Calculates the score, updates the grade, and checks for a new highest score."""
    correct_count = 0
    ss.user_answers = []
    total_q = len(ss.current_quiz)
    
    # Check ans's
    for i in range(total_q):
        question_data = ss.current_quiz[i]
        correct_ans = ss.current_quiz[i].get('correct') 
        user_ans = ss.get(f'Q{i}')
        
        # if ans matches correct
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
    
    # update persistent scores after a successful SUBMIT
    ss['final_quiz_score'] = ss.grade
    ss['quiz_total_questions'] = total_q
    
    if ss.grade > ss.highest_score:
        ss.highest_score = ss.grade
        st.toast(f"New High Score: {ss.highest_score}/{total_q}!", icon='🏆')

def button_clicked():
    """Handles the buttons (START -> SUBMIT -> RELOAD)."""
    
    # State 0: START is clicked -> Move to quiz display
    if ss.counter == 0:
        ss.counter = 1
        ss.start = True
        # Randomly select 10 questions (ensure questions list has at least 10 items)
        try:
            ss.current_quiz = random.sample(questions, 10)
        except ValueError:
            st.error("Error: Not enough questions available. Need at least 10.")
            ss.counter = 0 # Stay on START
            return

    # State 1: SUBMIT
    elif ss.counter == 1:
        ss.counter = 2
        grade_quiz()

    # state 2: reload
    elif ss.counter == 2:
        persistent_data = {
            'highest_score': ss.highest_score,
            'final_quiz_score': ss.final_quiz_score,
            'quiz_total_questions': ss.quiz_total_questions,
            'failed_questions': ss.failed_questions
        }
        
        st.session_state.clear()
        
        # restore the persistent data
        for key, value in persistent_data.items():
            st.session_state[key] = value

        # Set the counter back to 0 (START state)
        st.session_state['counter'] = 0


def quiz_app():
    if ss.start:
        with st.container(border=True):
            st.subheader("Quiz in Progress!")
            
            for i in range(len(ss.current_quiz)):
                question_data = ss.current_quiz[i]
                question_number = i + 1
                radio_key = f"Q{i}"
                
                st.markdown(f"**Question {question_number}.** {question_data.get('question')}")
                st.radio(
                    label="Choose your answer:",
                    options=question_data.get("options"),
                    index=None,
                    key=radio_key,
                    label_visibility="collapsed"
                )
                
                if ss.stop:
                    # Check if ss.user_answers has the result for the current question
                    if i < len(ss.user_answers): 
                        is_correct = ss.user_answers[i]
                        correct_ans = question_data.get('correct')

                        if is_correct:
                            st.success(f"✅ **CORRECT!**")
                        else:
                            st.error(f"❌ **INCORRECT.** The correct answer was: **{correct_ans}**")
                        
                st.markdown("---")


# --- 4. Main App Execution ---

# Highest score in the sidebar
if ss.highest_score > 0:
    st.sidebar.markdown(f"🏆 **Highest Score:** **{ss.highest_score}** / {ss.quiz_total_questions}")

st.button(
    label=ss.button_label[ss.counter], 
    key='main_button', 
    on_click=button_clicked,
    use_container_width=True
)

quiz_app()

if ss.stop:
    st.markdown("##")
    st.metric(label="Your Final Score", value=f"{ss.grade} / {len(ss.current_quiz)}")