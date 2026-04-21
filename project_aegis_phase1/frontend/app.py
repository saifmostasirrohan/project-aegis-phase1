import streamlit as st
import api_client

st.set_page_config(page_title="Aegis Crop Intel", page_icon="🌱")

st.title("Project Aegis: Agronomy Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Session Management")
    if st.button("Start New Session"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    if st.session_state.session_id:
        st.caption(f"Active Session:\n{st.session_state.session_id}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Describe the crop symptoms..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response_data = api_client.send_chat_message(prompt, st.session_state.session_id)

            if "error" in response_data:
                st.error(response_data["error"])
            else:
                st.session_state.session_id = response_data["session_id"]
                assistant_response = response_data["response"]
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
