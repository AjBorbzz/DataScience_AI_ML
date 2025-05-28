from crewai import Agent, Task, Crew, LLM
import litellm
from litellm import AnthropicChatCompletion

from utils import get_serper_api_key, get_gemini_api_key, pretty_print_result

# Retrieve the API keys
serper_api_key = get_serper_api_key()
gemini_api_key = get_gemini_api_key()
file_path = '/resume/sample_resume.docx'

from langchain_community.llms import Bedrock