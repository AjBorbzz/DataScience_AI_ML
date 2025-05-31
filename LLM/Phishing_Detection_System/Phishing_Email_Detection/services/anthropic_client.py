import os
import anthropic 
import sys
from utils.logging_config import log_duration
from utils.ioc_utils import get_api_key


claude_api = get_api_key("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=claude_api)

@log_duration
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

        Here is a sample output (text): 
        ```
        I'll analyze this email for threat indicators as requested.

        ## Analysis of Email Data

        After reviewing the provided email data, I can provide the following threat assessment:

        ### Verdict: Phishing
        ### Confidence: 90%

        ### Reasoning:
        - The sender domain "paypal-secure.com" is suspicious - legitimate PayPal emails come from paypal.com, not variants with hyphens or additional words
        - Complete authentication failure (SPF softfail, DKIM fail, DMARC fail) indicates the sender is not authorized
        - Urgent language about penalties within 24 hours is a classic pressure tactic used in phishing
        - Generic greeting and vague content about an invoice without specific details is typical of phishing attempts

        ### IOC Enrichment:
        - Domain: paypal-secure.com - This appears to be a typosquat domain designed to impersonate PayPal
        - Email authentication: 
          - SPF: "Failed"
          - DKIM: "Passed"
          - DMARC: "Failed"
          - Conclusion: All three email authentication mechanisms (SPF, DKIM, DMARC) failed, strongly suggesting the email is not from a legitimate sender
        - Attachment: invoice_1245.pdf - The provided hash appears to be incomplete, but PDF attachments are common vectors for malware delivery
        - SHA256 hash: e3b0c44298fc1c14...ffb6c1 (truncated) - Without the complete hash, proper enrichment is limited, but this should be scanned in a sandbox environment

        This email contains multiple indicators of a phishing attempt impersonating PayPal with the goal of delivering potentially malicious content via the PDF attachment.
        ```
    """


    message = client.messages.create(model="claude-sonnet-4-20250514",
                                    max_tokens=1000,
                                    temperature=1,
                                    system="You are a Security Automation Engineer who will integrate this LLM.",
                                    messages=[{"role": "user","content": prompt_}],
                                    stream=False,
                                        )
    
    print("\nYour message is read!\n")
    response = message.content[0].text

    return response, data