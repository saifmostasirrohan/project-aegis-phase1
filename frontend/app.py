import streamlit as st
import json
import api_client

st.set_page_config(page_title="Aegis Crop Intel", page_icon="🌱")

st.title("Project Aegis: Agronomy Assistant")

# 1. Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for session control
with st.sidebar:
    st.header("Session Management")
    if st.button("Start New Session", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    if st.session_state.session_id:
        st.caption(f"Active Session: {st.session_state.session_id[:8]}...")

        # EXPORT FEATURE
        chat_history_str = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="⬇️ Export Conversation log",
            data=chat_history_str,
            file_name=f"aegis_log_{st.session_state.session_id[:8]}.json",
            mime="application/json",
            use_container_width=True,
        )

# 2. Render existing messages in the UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. Handle new user input
if prompt := st.chat_input("Describe the crop symptoms..."):
    # Immediately display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response_data = api_client.send_chat_message(prompt, st.session_state.session_id)

            if "error" in response_data:
                st.error(response_data["error"])
            else:
                # Update session_id if this was the first message
                st.session_state.session_id = response_data["session_id"]
                assistant_response = response_data["response"]

                # Display response
                st.markdown(assistant_response)

                # Save to UI history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
