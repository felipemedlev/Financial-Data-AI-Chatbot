import json
import streamlit as st
import os
from datetime import datetime

CHAT_HISTORY_FILE = "chat_history.json"

@st.cache_resource
def load_chat_history():
    """Load chat history from JSON file with error handling"""
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        return []

def save_chat_history(messages):
    """Save chat history to JSON file with atomic write"""
    try:
        # Create a temporary file first
        temp_file = f"{CHAT_HISTORY_FILE}.tmp"
        with open(temp_file, "w") as f:
            json.dump(messages, f, indent=2)

        # Replace original file after successful write
        os.replace(temp_file, CHAT_HISTORY_FILE)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def clear_chat_history():
    """Clear chat history from disk and session state"""
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            os.remove(CHAT_HISTORY_FILE)
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Error clearing chat history: {str(e)}")