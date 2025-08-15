from google import genai
from google.genai import types
import os
from typing import Dict, Any
import ast
import sys

def configure_gemini():
    """Configure the Gemini API with the API key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Using the recommended approach from documentation
    client = genai.Client(api_key=api_key)
    return client.models

def generate_pandas_code(model_client, model_name, schema_docs: str, user_question: str,
                        company_list: list, date_range: str, business_units: list,
                        temperature: float = 0.7, chat_history=None) -> str:
    """
    Generate pandas code using Gemini based on the user question and schema.

    Parameters:
    model_client: Configured Gemini model client
    schema_docs (str): Schema documentation
    user_question (str): User's question
    company_list (list): List of available companies
    date_range (str): Available date range
    business_units (list): List of business units

    Returns:
    str: Generated pandas code
    """
    # Create context from chat history
    context = ""
    if chat_history:
        context = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-3:]])  # Last 3 messages

    # Add context to your existing prompt
    prompt = f"""Previous conversation:\n{context}\n\nCurrent question: {user_question}
    Based on this context and the current question, generate Python pandas code that...

    You are a financial data analyst. Given this schema and user question, generate pandas code.

    SCHEMA:
    {schema_docs}

    AVAILABLE DATA:
    - Companies: {', '.join(company_list) if company_list else 'Not specified'}
    - Date Range: {date_range}
    - Business Units: {', '.join(business_units) if business_units else 'Not specified'}

    USER QUESTION: {user_question}

    Generate only valid pandas code that answers the question. Return code between ```python and ```.
    The code should work with a DataFrame named 'df' that contains the financial data.
    Make sure to handle potential errors and edge cases.
    Dont comment your code to explain the logic.
    Always assign the main result to a variable named result.
    """

    try:
        # Using the recommended approach from documentation
        response = model_client.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature)
        )
        if response.text:
            # Extract code from markdown code block
            code = response.text
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            return code.strip()
        else:
            return "# No code generated"
    except Exception as e:
        return f"# Error generating code: {str(e)}"

def validate_and_execute_code(code: str, df) -> Any:
    """
    Execute the generated pandas code without safety restrictions.

    Parameters:
    code (str): Python code to execute
    df: DataFrame containing financial data

    Returns:
    Any: Result of code execution
    """
    try:
        import pandas as pd
        import numpy as np
        import io
        from contextlib import redirect_stdout

        local_namespace = {
            'df': df,
            'pd': pd,
            'np': np,
        }

        f = io.StringIO()
        globals_with_pd = globals().copy()
        globals_with_pd['pd'] = pd
        globals_with_pd['np'] = np
        with redirect_stdout(f):
            exec(code, globals_with_pd, local_namespace)

        output = f.getvalue()
        if output:
            print(output)

        result = local_namespace.get('result', 'No result variable found')
        return {'output': output, 'result': result}

    except Exception as e:
        return f"Error executing code: {str(e)}"