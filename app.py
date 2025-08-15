import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our utility functions
from utils.data_loader import load_financial_data
from utils.query_generator import configure_gemini as configure_gemini_qg, generate_pandas_code, validate_and_execute_code
from utils.response_formatter import configure_gemini as configure_gemini_rf, format_results_as_natural_language, format_results_as_table
from utils.chat_history import load_chat_history, save_chat_history, clear_chat_history

# Configure Gemini models
try:
    model_name = "gemini-2.5-flash-lite"
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
# Initialize or load chat history
st.session_state.messages = load_chat_history()

# Streamlit app
st.set_page_config(page_title="Financial Data Chatbot", page_icon="📊", layout="wide")

# App title and description
st.title("📊 Financial Data Chatbot")
st.markdown("""
This chatbot helps you analyze financial data using natural language queries.
Ask questions about revenue, expenses, profits, and other financial metrics.
""")

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

# Sidebar
with st.sidebar:
    st.header("📈 Data Overview")
    st.write(f"**Companies:** {len(unique_values['companies'])}")
    st.write(f"**Countries:** {len(unique_values['countries'])}")
    st.write(f"**Date Range:** {unique_values['date_range']}")
    st.write(f"**Total Records:** {len(df):,}")

    st.subheader("🏢 Companies")
    st.write(", ".join(unique_values["companies"][:10]) + ("..." if len(unique_values["companies"]) > 10 else ""))

    st.subheader("🌍 Countries")
    st.write(", ".join(unique_values["countries"]))

    st.subheader("📋 Account Categories")
    st.write(", ".join(unique_values["accounts"][:10]) + ("..." if len(unique_values["accounts"]) > 10 else ""))

    st.subheader("📚 Schema")
    with st.expander("View Schema"):
        st.markdown(schema_docs)

    st.subheader("💡 Example Queries")
    example_queries = [
        "What is the total revenue for Falabella Retail in 2023?",
        "Compare expenses between Chile and Peru for Sodimac",
        "Show me the profit trend for Tottus over the last 3 years",
        "What is the revenue growth of Q2 vs LY for Falabella retail Chile?",
        "Show me the operating margin for all companies in USD"
    ]
    for i, query in enumerate(example_queries):
        if st.button(query, key=f"example_{i}"):
            st.session_state.messages.append({"role": "user", "content": query})
            st.rerun()

# Main chat interface
st.subheader("💬 Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the financial data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the user's query
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Generate pandas code using Gemini
                generated_code = generate_pandas_code(
                    query_model_client,
                    model_name,
                    schema_docs,
                    prompt,
                    unique_values["companies"],
                    unique_values["date_range"],
                    unique_values["accounts"],
                    temperature
                )

                # Show generated code in an expander
                with st.expander("🔍 View Generated Code", expanded=False):
                    st.code(generated_code, language="python")

                # Execute the generated code
                execution_result = validate_and_execute_code(generated_code, df)

                # Handle the new return format from validate_and_execute_code
                if isinstance(execution_result, dict):
                    # If we have a dict with output and result, use the output for natural language processing
                    # and pass both to the formatter
                    output_content = execution_result.get('output', '')
                    result_content = execution_result.get('result', '')
                    # Combine output and result for the formatter
                    formatter_input = f"Output:\n{output_content}\n\nResult:\n{result_content}"
                else:
                    # If it's not a dict, use the original behavior
                    formatter_input = execution_result

                # Format results as natural language
                natural_language_response = format_results_as_natural_language(
                    response_model_client,
                    model_name,
                    formatter_input,
                    prompt,
                    temperature
                )

                # Display the natural language response
                st.markdown(natural_language_response)

                # Display results as table if possible
                # Extract the appropriate data for table formatting
                table_data = execution_result.get('result', '') if isinstance(execution_result, dict) else execution_result
                if table_data is not None and not isinstance(table_data, str) or (isinstance(table_data, str) and not table_data.startswith("Error")):
                    with st.expander("📋 View Results Table", expanded=False):
                        table_format = format_results_as_table(table_data)
                        st.markdown(table_format)

                # Try to create a chart if the data is suitable
                try:
                    # Extract the appropriate data for charting
                    chart_data = execution_result.get('result', '') if isinstance(execution_result, dict) else execution_result
                    if hasattr(chart_data, 'plot'):
                        st.subheader("📊 Visualization")
                        st.line_chart(chart_data)
                    elif isinstance(chart_data, pd.DataFrame) and len(chart_data) > 0:
                        # If we have a DataFrame with data, try to create a chart
                        numeric_columns = chart_data.select_dtypes(include=['number']).columns
                        if len(numeric_columns) > 0:
                            st.subheader("📊 Visualization")
                            if len(chart_data) <= 20:  # Only show chart if not too many data points
                                fig = px.bar(chart_data, x=chart_data.index, y=numeric_columns[0])
                                st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    # Silently ignore chart creation errors to avoid disrupting the user experience
                    # In a production environment, you might want to log this error for debugging
                    pass

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": natural_language_response})

            except Exception as e:
                error_message = f"Sorry, I encountered an error while processing your request: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

    # Save chat history after each interaction
    save_chat_history(st.session_state.messages)

# Export and management functionality
st.sidebar.subheader("💾 Chat Management")
if st.sidebar.button("Export Chat History"):
    chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    st.sidebar.download_button(
        label="Download Chat History",
        data=chat_history,
        file_name="financial_chat_history.txt",
        mime="text/plain"
    )

if st.sidebar.button("Clear Chat History"):
    clear_chat_history()
    st.rerun()