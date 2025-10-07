# chat.py
import streamlit as st
import os
import textwrap
from io import StringIO
from google import genai
from google.genai.types import GenerateContentConfig
from api.sysp import system_prompt

# --- Configuration and Session State Retrieval ---

# Ensure the API key is set via secrets.toml or environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
MODEL_NAME = 'gemini-2.5-flash'
ss = st.session_state

# Retrieve quiz data from Session State (set by the quiz page)
final_score = ss.get('final_quiz_score')
total_questions = ss.get('quiz_total_questions')
failed_questions = ss.get('failed_questions')
highest_score = ss.get('highest_score')

# --- Gemini Client Initialization and System Prompt ---

if "client" not in ss:
    try:
        ss.client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        st.stop()
        
def build_system_prompt():
    """Builds the comprehensive system prompt including quiz data."""
    
    # 1. Base Persona (Harald the Swedish Tutor)
    prompt = textwrap.dedent(system_prompt)
    
    # 2. Quiz Performance Context
    if final_score is not None and total_questions is not None:
        
        score_percentage = (final_score / total_questions) * 100
        prompt += f"\nAnvändaren har nyligen genomfört ett ordförrådsquiz och fick {final_score} av {total_questions} ({score_percentage:.0f}%)."
        
        if highest_score is not None and highest_score > 0:
            prompt += f"Användarens bästa resultat hittills är {highest_score} av {total_questions}."

        # 3. Failed Questions for Targeted Help
        if failed_questions and len(failed_questions) > 0:
            failed_q_summary = StringIO()
            failed_q_summary.write("Användaren hade problem med följande ord/frågor:\n")
            for i, q in enumerate(failed_questions):
                failed_q_summary.write(f"  - Fråga: '{q.get('question')}' (Korrekt svar: {q.get('correct')}).\n")
            
            prompt += "\nBaserat på denna information (de missade frågorna) bör du erbjuda riktade övningar, förklaringar eller använda dessa ord naturligt i konversationen. Försök att hjälpa dem att lära sig de ord de missade. "
            prompt += failed_q_summary.getvalue()
        else:
            prompt += "\nAnvändaren klarade alla frågor! Fokusera på att bygga vidare på deras kunskap."
    else:
        prompt += "\nAnvändaren har inte genomfört quizet ännu. Fokusera på allmän konversation och uppmuntra dem att ta quizet."
        
    return prompt.strip()

# --- Chat Initialization ---

if "messages" not in ss:
    # Build the system context at startup
    system_prompt_text = build_system_prompt()
    
    # Initialize chat history for DISPLAY ONLY 
    ss.messages = [] 
    
    # Store the system prompt separately for API use
    ss.system_prompt = system_prompt_text

    # Add the initial Harald greeting
    initial_greeting = "Hallå! Jag heter Harald, din personliga svensklärare. Hur kan jag hjälpa dig idag?"
    ss.messages.append({"role": "harald", "content": initial_greeting})

if "chat_session" not in ss:
    # Initialize the configuration with the stored system prompt
    config = GenerateContentConfig(
        system_instruction=ss.system_prompt,
        # You can add safety_settings here if you want:
        # safety_settings=...
    )
    
    # Initialize the chat session
    ss.chat_session = ss.client.chats.create(
        model=MODEL_NAME,
        config=config, 
        # Convert Streamlit history format to Gemini API format
        history=[
            {"role": "model" if msg["role"] == "harald" else "user", 
             "parts": [{"text": msg["content"]}]} 
            for msg in ss.messages
        ]
    )


# --- CSS (Remains the same) ---
st.markdown(
    # ... (Your CSS style block) ...
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanchenjunga:wght@400;500;600;700&family=Libre+Baskerville:wght@700&display=swap');

    .big-text {
        font-family: 'Libre Baskerville', serif;
        font-size: 100px;
        font-weight: 700;
        color: rgba(0,0,0,0.5); /* make it light so chat is readable */
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: -1;  /* behind everything */
        pointer-events: none;  /* click through */
        user-select: none;      /* prevent selection */
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Display History ---
for message in ss.messages:
    # Map 'harald' role back to Streamlit's 'assistant' avatar
    role = "assistant" if message["role"] == "harald" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# --- Chat Input and Response Logic (Non-streaming) ---
if prompt := st.chat_input("Vad vill du fråga Harald?"):
    
    # 1. Display user message and append to history
    st.chat_message("user").markdown(prompt)
    ss.messages.append({"role": "user", "content": prompt})
    
    # 2. Call Gemini and wait for the full response
    try:
        with st.spinner("Harald tänker..."):
            # Use the synchronous send_message method
            response = ss.chat_session.send_message(prompt)
            
            # Get the text content
            full_response = response.text
    except Exception as e:
        full_response = f"Jag ber om ursäkt, ett fel uppstod vid kommunikationen: {e}"
        st.error(full_response)


    # 3. Display the full response from Harald
    with st.chat_message("assistant"):
        st.markdown(full_response)

    # 4. Add the model's final response to history
    ss.messages.append({"role": "harald", "content": full_response})