import streamlit as st
import base64  # ADDED: Import the base64 library

st.set_page_config(layout="wide")
ss = st.session_state

ss.setdefault('page', 'landing')
ss.setdefault('counter', 0)
ss.setdefault('start', False)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
bin_str = get_base64_of_bin_file('harald_pic.png') # Make sure you have a file named 'background.png'

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanchenjunga:wght@400;500;600;700&family=Libre+Baskerville:wght@700&display=swap');

    /* ADDED: Background image styling */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: 30%;
        background-repeat: no-repeat;
        background-position: bottom 50px right 100px;
    }}

    .big-text {{
        font-family: 'Libre Baskerville', serif;
        font-size: 80px; /* Slightly adjusted for better fit */
        font-weight: 700;
        text-align: center;
        margin-top: 25vh;
    }}

    .description-text {{
        font-family: 'Kanchenjunga', sans-serif;
        font-size: 18px;
        text-align: center;
        color: #888888;
        padding: 0 2rem; /* Add some horizontal padding */
    }}

    .stButton>button {{
        display: block;
        margin: 0 auto;
        border: none;
        background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent white */
        color: #000000;
        padding: 12px 28px;
        border-radius: 12px;
        font-family: 'Kanchenjunga', sans-serif;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: rgba(255, 255, 255, 1); /* Opaque white on hover */
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# --- NAVIGATION LOGIC ---
def navigate_to_quiz():
    ss.page = 'quiz'

# --- PAGE DISPLAY LOGIC ---
if ss.page == 'landing':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='big-text'>Harald</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='description-text'>Harald is an interactive chatbot designed to help students practice and improve their Swedish language skills. Harald engages in free-form conversation and provides feedback on grammar, spelling, and word choice. The goal is to support language learning in a natural and motivating way.</div>",
            unsafe_allow_html=True
        )

else:
    # Clear the background for the quiz page if needed
    st.markdown("<style>.stApp { background: none; }</style>", unsafe_allow_html=True)
    st.title("The Quiz/Chatbot Page")
    st.write("Your main application logic goes here!")