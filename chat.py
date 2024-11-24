from openai import OpenAI
import streamlit as st

OPENAI_API_KEY = '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'

client = OpenAI(api_key=OPENAI_API_KEY)

def open_chat(chat_title, opening_message):
    st.title(chat_title)

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(opening_message):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})