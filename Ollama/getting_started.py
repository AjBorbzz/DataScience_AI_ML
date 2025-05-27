from pathlib import Path
import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

def get_claude_api():
    return os.getenv("ANTHROPIC_API_KEY")

claude_api = get_claude_api()
print(claude_api)


response = completion(
  model="anthropic/claude-3-sonnet-20240229",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)