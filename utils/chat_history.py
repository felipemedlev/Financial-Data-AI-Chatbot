import json
import streamlit as st
import os
from datetime import datetime

CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    """Load chat history from session state."""
    return st.session_state.get("messages", [])

def save_chat_history(messages):
    """Save chat history to session state."""
    st.session_state["messages"] = messages

def clear_chat_history():
    """Clear chat history from session state."""
    st.session_state["messages"] = []