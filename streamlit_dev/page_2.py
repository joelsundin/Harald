# chat.py
import streamlit as st
import traceback
import os
import textwrap
from io import StringIO
from google import genai
from google.genai.types import Content, GenerateContentConfig, Part, Tool
from api.sysp import system_prompt
from api.functions import add_flashcard, add_flashcard_function
import base64

# Ensure the API key is set via secrets.toml or environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
MODEL_NAME = 'gemini-2.5-flash'
ss = st.session_state
print("Starting chat")
json_storage = ss.get('storage')
json_storage.populate_session_state(ss)

# Retrieve quiz data from Session State (set by the quiz page)
final_score = ss.get('final_quiz_score')
total_questions = ss.get('quiz_total_questions')
failed_questions = ss.get('failed_questions')
highest_score = ss.get('highest_score')

# ✅ Detect whether quiz data exists (used to refresh chat session)
has_quiz_data = final_score is not None

def get_base64_of_bin_file(bin_file):
    """ Reads a binary file and returns its Base64 encoded string. """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    user_avatar_path = "generic_headshot.png"
    bot_avatar_path = "headshot.png"
    user_avatar = f"data:image/png;base64,{get_base64_of_bin_file(user_avatar_path)}"
    bot_avatar = f"data:image/png;base64,{get_base64_of_bin_file(bot_avatar_path)}"
except FileNotFoundError:
    # Use default emojis if images are not found
    user_avatar = "👤"
    bot_avatar = "🤖"
    st.warning("Avatar images not found. Using default emojis. Please add 'user_avatar.png' and 'bot_avatar.png'.")


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
    if final_score is not None:
        prompt += f"\n !!!IMPORTANT!!!! The user recently completed a QUIZ and scored {final_score} out of {total_questions}."

        if highest_score is not None and highest_score > 0:
            prompt += f"The user's best score so far is {highest_score} out of {total_questions}."

        # 3. Failed Questions for Targeted Help
        if failed_questions and len(failed_questions) > 0:
            failed_q_summary = StringIO()
            failed_q_summary.write("The user had trouble with the following words/questions:\n")
            for i, q in enumerate(failed_questions):
                failed_q_summary.write(f"  - Question: '{q.get('question')}' (Correct answer: {q.get('correct')}).\n")
            
            prompt += "\n !!! IMPORTANT !!!! Tell the user you noticed they took a quiz and suggest helping them with the questions they got wrong! Important!"
            prompt += failed_q_summary.getvalue()
        else:
            prompt += "\nThe user got all the questions correct! Focus on building on their existing knowledge."
    else:
        prompt += "\nThe user has not taken the quiz yet. Focus on general conversation and encourage them to try the quiz."
    
    print(prompt.strip())
    return prompt.strip()

# --- Chat Initialization ---
system_prompt_text = build_system_prompt()
ss.system_prompt = system_prompt_text

if "messages" not in ss:
    print("Starting new chat session.")
    ss.messages = [] 
    initial_greeting = "Hello! I'm Harald, your personal Swedish tutor. Would you like to have a conversation with me in Swedish? Or if you prefer, we could start by practicing some Swedish words and phrases together. What sounds good to you?"
    ss.messages.append({"role": "harald", "content": initial_greeting})

# ✅ Rebuild chat session if not present OR quiz data is available
if "chat_session" not in ss or has_quiz_data:
    print("🔁 Rebuilding chat session with latest system prompt...")
    tools = Tool(function_declarations=[add_flashcard_function])
    config = GenerateContentConfig(
        system_instruction=ss.system_prompt,
        tools=[tools],
        temperature=0.3,
    )

    ss.chat_session = ss.client.chats.create(
        model=MODEL_NAME,
        config=config, 
        history=[
            {"role": "model" if msg["role"] == "harald" else "user", 
             "parts": [{"text": msg["content"]}]} 
            for msg in ss.messages
        ]
    )

    # Optional confirmation in console
    print("✅ ACTIVE SYSTEM PROMPT IN CHAT SESSION:")
    print(ss.system_prompt[:500], "...")


# --- UI Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanchenjunga:wght@400;500;600;700&family=Libre+Baskerville:wght@700&display=swap');

    .big-text {
        font-family: 'Libre Baskerville', serif;
        font-size: 100px;
        font-weight: 700;
        color: rgba(0,0,0,0.5);
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: -1;
        pointer-events: none;
        user-select: none;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Display Chat History ---
for message in ss.messages:
    role = message["role"]
    avatar = bot_avatar if role == "harald" else user_avatar
    display_role = "assistant" if role == "harald" else role
    with st.chat_message(display_role, avatar=avatar):
        st.markdown(message["content"])

# --- Chat Input and Response Logic (Non-streaming) ---
if prompt := st.chat_input("Vad vill du fråga Harald?"):
    
    # 1. Display user message and append to history
    st.chat_message("user", avatar=user_avatar).markdown(prompt)
    ss.messages.append({"role": "user", "content": prompt})
    
    try:
        with st.spinner("..."):
            response = ss.chat_session.send_message(prompt)
            print("Response content: ", response.candidates[0].content)
            
            if response.candidates[0].content.parts and (call := response.candidates[0].content.parts[0].function_call):
                add_flashcard(ss, **call.args)
                tool_reply = Part.from_function_response(
                    name=call.name,
                    response={"result": "Flashcard added successfully."},
                )
                response = ss.chat_session.send_message([tool_reply])
            full_response = response.text
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        full_response = f"Jag ber om ursäkt, ett fel uppstod vid kommunikationen: {e}"
        st.error(full_response)

    # 3. Display the full response from Harald
    with st.chat_message("assistant", avatar=bot_avatar):
        st.markdown(full_response)

    # 4. Add the model's final response to history
    ss.messages.append({"role": "harald", "content": full_response})

    # 5. Save session state to JSON storage
    json_storage.store_session_state(ss)
