# comprehension.py
import streamlit as st
import random
from urls import urls  
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
MODEL_NAME = 'gemini-2.5-flash'

# --- Streamlit session state ---
ss = st.session_state
ss.setdefault("selected_article", None)
ss.setdefault("task_type", None)
ss.setdefault("generated_questions", [])
ss.setdefault("user_answers", [])
ss.setdefault("feedback", None)
ss.setdefault("followup_history", [])

st.header("Reading & Writing Comprehension")
st.markdown("Read the article and choose a task: summarize it or answer comprehension questions.")


if "selected_article" not in ss or ss.selected_article is None:
    ss.selected_article = random.choice(urls)
selected_article = ss.selected_article

if st.button("🔄 Refresh Article"):
    ss.selected_article = random.choice(urls)
    ss.generated_questions = []
    ss.user_answers = []
    ss.feedback = None
    ss.followup_history = []
    st.rerun()

st.markdown(f"### Article: {selected_article['title']}")
st.markdown(selected_article["content"])


task_type = st.radio("Choose your task:", ["Summarize the text", "Answer comprehension questions"])
ss.task_type = task_type

if task_type == "Summarize the text":
    user_summary = st.text_area("Write your summary in Swedish here:")
    if st.button("Submit Summary"):
        system_prompt = f"""
You are Harald, a friendly Swedish tutor specialized in reading comprehension.

Evaluate the user's answers or summary based on grammar, vocabulary, coherence, and comprehension.
- Provide overall feedback in English.
- When correcting grammar, vocabulary, or sentence structure, include the corrections in Swedish.
- Be constructive and clear.


Article: {selected_article['content']}
User summary: {user_summary}
"""
        with st.spinner("Harald is reviewing your summary..."):
            config = GenerateContentConfig(system_instruction=system_prompt)
            chat_session = client.chats.create(model=MODEL_NAME, config=config)
            response = chat_session.send_message(user_summary)
            ss.feedback = response.text
        st.markdown("### Feedback from Harald:")
        st.markdown(ss.feedback)

elif task_type == "Answer comprehension questions":
   
    if not ss.generated_questions or ss.selected_article != selected_article:
        ss.generated_questions = []
        ss.user_answers = []
        question_prompt = f"""
You are Harald, a friendly Swedish tutor.

Generate 3-5 clear and relevant comprehension questions from the following article.
- Only output the questions. Do NOT include greetings, introductions, or explanations.
- Format each question as a single line.
- Beginner/intermediate level suitable for someone learning Swedish.
Article: {selected_article['content']}
"""
        with st.spinner("Harald is generating questions..."):
            config = GenerateContentConfig(system_instruction=question_prompt)
            chat_session = client.chats.create(model=MODEL_NAME, config=config)
            response = chat_session.send_message(selected_article["content"])
            questions = [q.strip() for q in response.text.split("\n") if q.strip()]
            ss.generated_questions = questions

    st.markdown("### Answer the following questions:")
    user_answers = []
    for i, q in enumerate(ss.generated_questions):
        ans = st.text_input(f"{i+1}. {q}", key=f"answer_{i}")
        user_answers.append(ans)
    ss.user_answers = user_answers

    if st.button("Submit Answers"):
        answer_eval_prompt = f"""
You are Harald, a friendly Swedish tutor.


Evaluate the user's answers based on grammar, vocabulary, coherence, and comprehension.
- Provide overall feedback in English.
- When correcting grammar, vocabulary, or sentence structure, include the corrections in Swedish.
- Be constructive and clear.


Article: {selected_article['content']}
Questions: {ss.generated_questions}
User answers: {ss.user_answers}
"""
        with st.spinner("Harald is reviewing your answers..."):
            config = GenerateContentConfig(system_instruction=answer_eval_prompt)
            chat_session = client.chats.create(model=MODEL_NAME, config=config)
            response = chat_session.send_message("\n".join(ss.user_answers))
            ss.feedback = response.text
        st.markdown("### Feedback from Harald:")
        st.markdown(ss.feedback)


st.markdown("### Ask follow-up questions about this article")
followup_question = st.text_input("Type your question here and press Enter", key="followup_input")

if followup_question:
    
    if "followup_history" not in ss:
        ss.followup_history = []
    ss.followup_history.append({"role": "user", "content": followup_question})

 
    conversation_context = f"Article: {selected_article['content']}\n"

    if ss.task_type == "Summarize the text" and st.session_state.get("user_summary"):
        conversation_context += f"\nUser submitted summary: {ss.user_summary}\n"
        if ss.feedback:
            conversation_context += f"Feedback given: {ss.feedback}\n"

    elif ss.task_type == "Answer comprehension questions" and ss.generated_questions:
        conversation_context += "\nGenerated questions and user's answers:\n"
        for i, q in enumerate(ss.generated_questions):
            user_ans = ss.user_answers[i] if i < len(ss.user_answers) else "No answer"
            conversation_context += f"{i+1}. Q: {q}\n   User answer: {user_ans}\n"
        if ss.feedback:
            conversation_context += f"Feedback given: {ss.feedback}\n"

    
    for msg in ss.followup_history:
        conversation_context += f"{msg['role']}: {msg['content']}\n"

    
    system_prompt = f"""
You are Harald, a friendly Swedish tutor.

You are aware of the user's reading comprehension activity and their submitted work.
Maintain the context of previous follow-up questions and answers.
Answer the user's current follow-up question in a helpful and concise manner.
Be aware of the user's task context (summary or comprehension questions) and feedback given.
"""
    with st.spinner("Harald is responding..."):
        config = GenerateContentConfig(system_instruction=system_prompt)
        chat_session = client.chats.create(model=MODEL_NAME, config=config)
        response = chat_session.send_message(conversation_context)
        answer = response.text

   
    st.markdown(f"**Harald:** {answer}")

  
    ss.followup_history.append({"role": "harald", "content": answer})
