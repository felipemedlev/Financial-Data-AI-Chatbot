import streamlit as st
import pandas as pd
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Import our utility functions
from utils.data_loader import load_financial_data
from utils.query_generator import configure_gemini as configure_gemini_qg
from utils.response_formatter import configure_gemini as configure_gemini_rf

# Modularized UI and chat logic
from utils.ui import render_sidebar, render_chat
from utils.chat_logic import process_user_prompt

# Configure Gemini models
try:
    model_name = "gemini-2.5-flash"
    if not os.getenv('GOOGLE_API_KEY'):
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    query_model_client = configure_gemini_qg()
    response_model_client = configure_gemini_rf()
except Exception as e:
    st.error(f"Error configuring Gemini: {str(e)}")
    st.stop()

# Load data with caching
@st.cache_data
def get_financial_data():
    return load_financial_data()

# Load schema
def get_schema():
    with open("schema/P&L.md", "r") as f:
        return f.read()

# Get unique values for filters
def get_unique_values(df):
    return {
        "companies": sorted(df["CompanyName"].dropna().unique().tolist()),
        "countries": sorted(df["Country"].dropna().unique().tolist()),
        "accounts": sorted(df["Account"].dropna().unique().tolist()),
        "date_range": f"{df['Year'].min()} - {df['Year'].max()}"
    }

# Initialize session state
# Initialize or load chat history (in-memory only)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app
st.set_page_config(page_title="Financial Data Chatbot", page_icon="📊", layout="wide")

# App title and description
st.title("📊 Financial Data Chatbot")
st.markdown("""
This chatbot helps you analyze financial data using natural language queries.
Ask questions about revenue, expenses, profits, and other financial metrics.
""")


# Chat management buttons at the top of the sidebar
st.sidebar.subheader("💾 Chat Management")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
with col2:
    chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    st.download_button(
        label="Export Chat History",
        data=chat_history,
        file_name="financial_chat_history.txt",
        mime="text/plain"
    )

# Settings
st.sidebar.subheader("⚙️ Settings")
temperature = st.sidebar.slider("Response Creativity", 0.0, 1.0, 0.7)

# Load data and schema
try:
    with st.spinner("Loading financial data..."):
        df = get_financial_data()
        schema_docs = get_schema()
        unique_values = get_unique_values(df)
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()


# Sidebar rendering
example_queries = [
    "What is the total revenue for Falabella Retail in 2023?",
    "Compare expenses between Chile and Peru for Sodimac",
    "Show me the profit trend for Tottus over the last 3 years",
    "What is the revenue growth of Q2 vs LY for Falabella retail Chile?",
    "Show me the operating margin for all companies in USD"
]
with st.sidebar:
    unique_values["total_records"] = len(df)
    render_sidebar(unique_values, schema_docs, example_queries)


# Main chat interface
render_chat(st.session_state.messages)


# Unified chat input and example prompt processing
prompt = st.chat_input("Ask a question about the financial data...")
if not prompt and "example_prompt" in st.session_state:
    prompt = st.session_state.example_prompt
    del st.session_state.example_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                natural_language_response = process_user_prompt(
                    prompt,
                    df,
                    schema_docs,
                    unique_values,
                    query_model_client,
                    response_model_client,
                    model_name,
                    temperature,
                    st.session_state.messages
                )
                st.session_state.messages.append({"role": "assistant", "content": natural_language_response})
            except Exception as e:
                error_message = f"Sorry, I encountered an error while processing your request: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})