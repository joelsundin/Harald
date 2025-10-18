import streamlit as st
import pandas as pd
import numpy as np
import json_storage
import traceback
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

def get_remote_ip() -> str:
    """Get remote ip."""
    ip = st.context.headers.get("X-Forwarded-For")
    print("Getting remote IP: %s", ip)
    return ip

ss = st.session_state
ss.storage = json_storage.JSONStorage(get_remote_ip())

# --- Define your pages ---
main_page = st.Page("main_page.py", title="Home")
page_2 = st.Page("page_2.py", title="Harald")
page_3 = st.Page("page_3.py", title="Quizzes")
page_4 = st.Page("page_4.py", title="Read&Write")
page_flashcards = st.Page("page_flashcards.py", title="Flashcards")
pg = st.navigation([main_page, page_2, page_3, page_4, page_flashcards])

# --- Inject CSS ---
st.markdown(
    """
    <style>
    /* Change sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    /* Style page links */
    .st-emotion-cache-1v0mbdj a {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #333333 !important;
    }

    /* Hover effect */
    .st-emotion-cache-1v0mbdj a:hover {
        color: #007BFF !important;
        text-decoration: underline;
    }

    /* Active page highlight */
    .st-emotion-cache-1v0mbdj [data-testid="stMarkdownContainer"] {
        padding: 6px 12px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Run nav ---
pg.run()
