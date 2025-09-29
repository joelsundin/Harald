import streamlit as st

st.markdown(
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



if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "harald", "content": "Harald: Hej <namn>! Hur mår du idag?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    user_input = prompt
    #TODO: Pass user_input into LLM for inference EXCHANGING THIS FOR CHAT CLASS instead
    response = f"Harald: {prompt}"
    """
    response = requests.post("http://localhost:8000/generate", json={"prompt": prompt}).json()
    answer = response["response"]

    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    """
    with st.chat_message("harald"):
        st.markdown(response)

    # add haralds response to history
    st.session_state.messages.append({"role": "harald", "content": response})
    