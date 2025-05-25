import os
from dotenv import load_dotenv
import anthropic 
import sys
from utils.logging_config import log_duration

load_dotenv()



def get_claude_api():
    return os.getenv("ANTHROPIC_API_KEY")

claude_api = get_claude_api()
client = anthropic.Anthropic(api_key=claude_api)


def process_message_with_cache():
    response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            system=[
            {
                "type": "text",
                "text": "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.\n",
            },
            {
                "type": "text",
                "text": "<the entire contents of 'Pride and Prejudice'>",
                "cache_control": {"type": "ephemeral"}
            }
            ],
            messages=[{"role": "user", "content": "Analyze the major themes in 'Pride and Prejudice'."}],
        )
    print(f"response: {response}")
    
    return response.usage.model_dump_json()
    
print(response.usage.model_dump_json())