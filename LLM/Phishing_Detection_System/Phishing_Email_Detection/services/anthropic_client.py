import os
from dotenv import load_dotenv
import anthropic 
from sample_data import sample_email_data
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

claude_api = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic()


def process_phishing_detection(data):
    prompt_ = f"""
    You are a cybersecurity threat detection assistant. Analyze the email data below and decide if it's phishing or benign.

        Evaluate:
        - Subject and body content
        - Sender name and address
        - URLs, domains, attachments, hashes
        - QR codes or shortened links
        - Language cues (urgency, impersonation, fear)
        - Header anomalies (SPF, DKIM, DMARC issues)
        - Threat indicators (IPs, file hashes, domains)

        Tasks:
        1. Enrich indicators (URLs, hashes, QR codes, domains) with threat intelligence.
        2. Judge whether the email is phishing, suspicious, or benign.
        3. Justify the conclusion briefly based on the indicators.

        ### Email Data
        Subject: {data.get("email_subject")}  
        From: {data["from_name"]} <{data["from_address"]}>  
        To: {data["to_address"]}  
        Headers: {data["headers"]}  
        Body:  
        {data["email_body"]}

        Attachments: {data["attachment_names_and_hashes"]}  
        URLs: {data["list_of_urls"]}  
        QR Codes (decoded): {data["qr_data"]}

        ### Output
        - Verdict: [Phishing | Suspicious | Benign]  
        - Confidence (0–100%)  
        - Reasoning:  
        - (short_reason_1)  
        - (short_reason_2)  
        - IOC Enrichment:  
        - (indicator): (Context)

    """


    message = client.messages.create(model="claude-3-7-sonnet-20250219",
                                    max_tokens=1000,
                                    temperature=1,
                                    system="You are a Security Automation Engineer who will integrate this LLM.",
                                    messages=[{"role": "user","content": prompt_}],
                                    stream=False,
                                        )
    
    print(type(message))
    response = message.content[0].text
    return response