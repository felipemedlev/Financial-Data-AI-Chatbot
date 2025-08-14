from google import genai
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

def generate_pandas_code(model_client, schema_docs: str, user_question: str,
                        company_list: list, date_range: str, business_units: list,
                        temperature: float = 0.7) -> str:
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
    prompt = f"""
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
    Always comment your code to explain the logic.
    """

    try:
        # Using the recommended approach from documentation
        response = model_client.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            generation_config={'temperature': temperature}
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
    Validate and execute the generated pandas code safely.

    Parameters:
    code (str): Python code to execute
    df: DataFrame containing financial data

    Returns:
    Any: Result of code execution
    """
    try:
        # Parse the code to check for potentially unsafe operations
        tree = ast.parse(code)

        # Check for unsafe operations (basic security check)
        unsafe_nodes = [node for node in ast.walk(tree)
                       if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call))
                       and hasattr(node, 'func') and hasattr(node.func, 'id')
                       and node.func.id in ['open', 'exec', 'eval']]

        if unsafe_nodes:
            raise ValueError("Code contains unsafe operations")

        # Create a safe execution environment
        safe_dict = {
            'df': df,
            'pd': __import__('pandas'),
        }

        # Execute the code
        exec(code, {"__builtins__": {}}, safe_dict)

        # Try to get the result (assuming it's stored in a variable named 'result')
        return safe_dict.get('result', 'No result variable found')
    except Exception as e:
        return f"Error executing code: {str(e)}"