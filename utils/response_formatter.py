from google import genai
from google.genai import types
import os
from typing import Any
from datetime import datetime

def configure_gemini():
    """Configure the Gemini API with the API key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Using the recommended approach from documentation
    client = genai.Client(api_key=api_key)
    return client.models

def format_results_as_natural_language(
    client,
    model_name,
    formatter_input,
    prompt,
    temperature,
    chat_history=None
):
    """Format results with chat history context."""
    # Get current date dynamically
    current_date = datetime.now()

    system_prompt = f"""You are a financial analyst assistant. Today's date is {current_date.strftime('%B %d, %Y')}.
    Any data from before this date should be treated as historical data, not forecasts.
    Only treat data after {current_date.strftime('%B %Y')} as forecasts/budgets.
    If no currency is specified, assume the default currency is Dolares (USD).
    If you don't have enough information to answer the question, ask for clarifications.
    """

    # Create context from chat history
    context = ""
    if chat_history:
        context = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-3:]])  # Last 3 messages

    # Add context to your existing prompt
    enhanced_prompt = f"""
    System: {system_prompt}

    Previous conversation:
    {context}

    Current question: {prompt}

    Given these results:
    {formatter_input}

    Please provide a natural language response explaining the results. Remember that any data
    from before {current_date.strftime('%B %Y')} is historical data, not forecasts.
    """

    try:
        # Using the recommended approach from documentation
        response = client.generate_content(
            model=model_name,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(temperature=temperature)
        )
        if response.text:
            return response.text.strip()
        else:
            return "I couldn't generate a response based on the results."
    except Exception as e:
        return f"Error generating natural language response: {str(e)}"

def format_results_as_table(results: Any) -> str:
    """
    Format the results as a markdown table when appropriate.

    Parameters:
    results (Any): Results from pandas code execution

    Returns:
    str: Markdown table representation of results
    """
    try:
        import pandas as pd
        # If results is a pandas DataFrame, format numbers and convert to markdown
        if hasattr(results, 'to_markdown'):
            df = results.copy()
            # Format all float/int columns with thousands separator and 2 decimals
            for col in df.select_dtypes(include=['float', 'int']).columns:
                df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "")
            return df.to_markdown(index=False)
        # If results is a dict, check if values are dicts (expand to columns)
        elif isinstance(results, dict):
            # If all values are dicts, treat as table with columns
            if all(isinstance(v, dict) for v in results.values()):
                # Collect all possible subkeys
                all_subkeys = set()
                for v in results.values():
                    all_subkeys.update(v.keys())
                all_subkeys = list(all_subkeys)
                # Header
                header = '| Key | ' + ' | '.join(all_subkeys) + ' |'
                sep = '| --- ' * (len(all_subkeys)+1) + '|'
                lines = [header, sep]
                for key, subdict in results.items():
                    row = [str(key)]
                    for subkey in all_subkeys:
                        value = subdict.get(subkey, "")
                        if isinstance(value, (int, float)):
                            value_str = f"{value:,.2f}"
                        else:
                            value_str = str(value)
                        row.append(value_str)
                    lines.append('| ' + ' | '.join(row) + ' |')
                return '\n'.join(lines)
            else:
                # Fallback: simple key-value table
                lines = ["| Key | Value |", "| --- | ----- |"]
                for key, value in results.items():
                    if isinstance(value, (int, float)):
                        value_str = f"{value:,.2f}"
                    else:
                        value_str = str(value)
                    lines.append(f"| {key} | {value_str} |")
                return "\n".join(lines)
        # For other types, just return string representation
        else:
            return str(results)
    except Exception as e:
        return f"Error formatting results as table: {str(e)}"