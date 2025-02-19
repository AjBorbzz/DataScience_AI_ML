import os
from dotenv import load_dotenv, find_dotenv
import textwrap

def load_env():
    """Loads environment variables from a .env file."""
    load_dotenv(find_dotenv())  # No need to return anything, load_dotenv modifies os.environ

def get_api_key(key_name):
    """Retrieves an API key from environment variables."""
    load_env()  # Load env vars only once when an API key is needed.
    api_key = os.getenv(key_name)
    if api_key is None:
        raise ValueError(f"Environment variable '{key_name}' not found.") # Handle missing key
    return api_key

def get_gemini_api_key():
    return get_api_key("GEMINI_API_KEY")

def get_serper_api_key():
    return get_api_key("SERPER_API_KEY")


def pretty_print_result(result):
    """Wraps text to 80 characters per line."""
    wrapped_lines = []
    for line in result.splitlines(): #splitlines handles different newline characters
        wrapped_lines.extend(textwrap.wrap(line, width=80, break_long_words=False)) # Use textwrap
    return "\n".join(wrapped_lines)


# Example usage (demonstrates error handling):
# try:
#     claude_key = get_claude_api_key()
#     print("Claude API Key:", claude_key)

#     serper_key = get_serper_api_key()
#     print("Serper API Key:", serper_key)

# except ValueError as e:
#     print(f"Error: {e}")

# long_text = """This is a very long string that needs to be wrapped to a maximum of 80 characters per line.  This is a demonstration of the text wrapping functionality. It should handle long words gracefully and avoid breaking them in the middle."""

# pretty_printed_text = pretty_print_result(long_text)
# print(pretty_printed_text)