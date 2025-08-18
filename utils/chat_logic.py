# Chat logic for the Streamlit app
from utils.query_generator import generate_pandas_code, validate_and_execute_code
from utils.response_formatter import format_results_as_natural_language, format_results_as_table
import pandas as pd
import plotly.express as px
import streamlit as st

def process_user_prompt(prompt, df, schema_docs, unique_values, query_model_client, response_model_client, model_name, temperature, chat_history):
    generated_code = generate_pandas_code(
        query_model_client,
        model_name,
        schema_docs,
        prompt,
        unique_values["companies"],
        unique_values["date_range"],
        unique_values["accounts"],
        temperature,
        chat_history=chat_history
    )
    with st.expander("🔍 View Generated Code", expanded=False):
        st.code(generated_code, language="python")
    execution_result = validate_and_execute_code(generated_code, df)
    if isinstance(execution_result, dict):
        output_content = execution_result.get('output', '')
        result_content = execution_result.get('result', '')
        formatter_input = f"Output:\n{output_content}\n\nResult:\n{result_content}"
    else:
        formatter_input = execution_result
    natural_language_response = format_results_as_natural_language(
        response_model_client,
        model_name,
        formatter_input,
        prompt,
        temperature,
        chat_history=chat_history
    )
    st.markdown(natural_language_response)
    if isinstance(execution_result, dict):
        table_data = execution_result.get('result')
        if table_data is None:
            table_data = execution_result.get('output', '')
    else:
        table_data = execution_result
    if table_data is not None and (not isinstance(table_data, str) or (isinstance(table_data, str) and not table_data.startswith("Error"))):
        with st.expander("📋 View Results Table", expanded=False):
            table_format = format_results_as_table(table_data)
            st.markdown(table_format)
    try:
        chart_data = execution_result.get('result', '') if isinstance(execution_result, dict) else execution_result
        if hasattr(chart_data, 'plot'):
            st.subheader("📊 Visualization")
            st.line_chart(chart_data)
        elif isinstance(chart_data, pd.DataFrame) and len(chart_data) > 0:
            numeric_columns = chart_data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                st.subheader("📊 Visualization")
                if len(chart_data) <= 20:
                    fig = px.bar(chart_data, x=chart_data.index, y=numeric_columns[0])
                    st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass
    return natural_language_response
