import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.app import ask


st.title("📚 Chatbot for IZTECH Library")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! How can I assist you with the IZTECH Library today?"}]

# Display chat messages for the user interface
for message in st.session_state.messages:
    # For user messages, display the original query if available
    if message["role"] == "user" and "original_query" in message:
        st.chat_message("user").markdown(message["original_query"])
    else:
        st.chat_message(message["role"]).markdown(message["content"])

# Get user input
user_input = st.chat_input("Ask your question about the IZTECH Library...")

if user_input:
    # Display the original user message
    st.chat_message("user").markdown(user_input)
    
    with st.spinner("Thinking..."):
        # Pass current chat history to the model
        response, preprocessed_query = ask(user_input, st.session_state.messages)
        
        # Store the preprocessed query in history, but keep original for display
        st.session_state.messages.append({
            "role": "user", 
            "content": preprocessed_query,  # This will be used by the LLM
            "original_query": user_input    # This is for UI display
        })

    # Display and store assistant response
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
