from crewai import Agent, Task, Crew, LLM
import litellm
from litellm import AnthropicChatCompletion

from utils import get_serper_api_key, get_gemini_api_key, pretty_print_result

# Retrieve the API keys
serper_api_key = get_serper_api_key()
gemini_api_key = get_gemini_api_key()
file_path = '/resume/sample_resume.docx'

from langchain_community.llms import Bedrock
import crewai_tools
from crewai_tools import DOCXSearchTool


llm = LLM(model="bedrock/anthropic.claude-3-5-haiku-20241022-v1:0", temperature=0.7)

semantic_search_resume = DOCXSearchTool(
    docx=file_path,
    config=dict(
        llm=dict(
            provider="aws_bedrock",  # Using Amazon Bedrock as the LLM provider
            config=dict(
                model="anthropic.claude-3-5-sonnet-20241022-v2:0",  # Specify the Bedrock-supported model
                # temperature=0.5,
                # top_p=1,
                # stream=True,
            ),
        ),
        embedder=dict(
            provider="aws_bedrock",  # Using Amazon Bedrock for embeddings
            config=dict(
                model="amazon.titan-embed-text-v1",  # Bedrock-supported embedding model
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)


from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileReadTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
read_resume = FileReadTool(file_path)


from docx import Document

def display_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])  # Extract text from all paragraphs
    return text

file_path = "resume/sample_resume.docx"  # Upload your resume or use a sample 
resume_text = display_docx(file_path)

from IPython.display import display, Markdown
display(Markdown(f"### Resume Preview\n\n{resume_text}"))


# Agent 1: Researcher
researcher = Agent(
    role="Tech Job Researcher",
    goal="Make sure to do amazing analysis on "
         "job posting to help job applicants",
    tools = [scrape_tool, search_tool],
    verbose=True,
    llm=llm,
    backstory=(
        "As a Job Researcher, your prowess in "
        "navigating and extracting critical "
        "information from job postings is unmatched."
        "Your skills help pinpoint the necessary "
        "qualifications and skills sought "
        "by employers, forming the foundation for "
        "effective application tailoring."
    )
)


# Agent 2: Profiler
profiler = Agent(
    role="Personal Profiler for Engineers",
    goal="Do increditble research on job applicants "
         "to help them stand out in the job market",
    tools = [scrape_tool, search_tool,
             read_resume, semantic_search_resume],
    verbose=True,
    llm=llm,
    backstory=(
        "Equipped with analytical prowess, you dissect "
        "and synthesize information "
        "from diverse sources to craft comprehensive "
        "personal and professional profiles, laying the "
        "groundwork for personalized resume enhancements."
    )
)