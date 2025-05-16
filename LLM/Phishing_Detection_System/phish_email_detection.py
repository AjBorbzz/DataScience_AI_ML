import os
from dotenv import load_dotenv
import anthropic 


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
        Subject: {email_subject}  
        From: {from_name} <{from_address}>  
        To: {to_address}  
        Headers: {headers}  
        Body:  
        {email_body}

        Attachments: {attachment_names_and_hashes}  
        URLs: {list_of_urls}  
        QR Codes (decoded): {qr_data}

        ### Output
        - Verdict: [Phishing | Suspicious | Benign]  
        - Confidence (0–100%)  
        - Reasoning:  
        - {short_reason_1}  
        - {short_reason_2}  
        - IOC Enrichment:  
        - {indicator}: {context}

    """


    message = client.messages.create(model="claude-3-7-sonnet-20250219",
                                    max_tokens=1000,
                                    temperature=1,
                                    system="You are a Security Automation Engineer who will integrate this LLM.",
                                    messages=[{"role": "user","content": prompt_}],
                                    stream=False,
                                        )
    print(message)
