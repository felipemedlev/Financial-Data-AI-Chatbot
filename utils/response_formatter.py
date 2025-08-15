from google import genai
from google.genai import types
import os
from typing import Any

def configure_gemini():
    """Configure the Gemini API with the API key."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Using the recommended approach from documentation
    client = genai.Client(api_key=api_key)
    return client.models

def format_results_as_natural_language(model_client, model_name, results: Any, user_question: str,
                                       temperature: float = 0.7) -> str:
    """
    Format the results as natural language using Gemini.

    Parameters:
    model_client: Configured Gemini model client
    results (Any): Results from pandas code execution
    user_question (str): Original user question

    Returns:
    str: Natural language response
    """
    # Convert results to string for the prompt
    results_str = str(results)

    prompt = f"""
    You are a financial data analyst. Given the results of a data analysis and the original question,
    create a clear, concise natural language response that answers the user's question.

    ORIGINAL QUESTION: {user_question}

    RESULTS:
    {results_str}

    Please provide a clear, concise answer to the original question based on the results.
    Include specific numbers and trends where relevant.
    Format the response in a professional, easy-to-understand manner.
    If the results don't directly answer the question, explain why.
    """

    try:
        # Using the recommended approach from documentation
        response = model_client.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature)
        )
        print(f"Generated response: {response}")
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
        # If results is a pandas DataFrame, convert to markdown
        if hasattr(results, 'to_markdown'):
            return results.to_markdown(index=False)
        # If results is a dict, try to format as table
        elif isinstance(results, dict):
            lines = ["| Key | Value |", "| --- | ----- |"]
            for key, value in results.items():
                lines.append(f"| {key} | {value} |")
            return "\n".join(lines)
        # For other types, just return string representation
        else:
            return str(results)
    except Exception as e:
        return f"Error formatting results as table: {str(e)}"