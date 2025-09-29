import streamlit as st
import pandas as pd
import numpy as np

# --- Define your pages ---
main_page = st.Page("main_page.py", title="Home")
page_2 = st.Page("page_2.py", title="Harald")
page_3 = st.Page("page_3.py", title="Quizzes")
pg = st.navigation([main_page, page_2, page_3])




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
