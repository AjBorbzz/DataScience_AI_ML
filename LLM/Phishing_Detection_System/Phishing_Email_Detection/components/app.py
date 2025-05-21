import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import anthropic_client
from utils import ioc_utils, parser

print("Claude API Key:", anthropic_client.get_claude_api())


# client = anthropic.Anthropic()

# def extract_message_output(text):
#     verdict = re.search(r"### Verdict:\s*(.+)", text).group(1)
#     confidence = re.search(r"### Confidence:\s*(\d+)%", text).group(1)
#     reasoning = re.findall(r"- (.*?)\n", re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL).group(1))

#     domain = re.search(r"- Domain:\s*(.*?)\s*-", text).group(1).strip()
#     auth = re.search(r"- Email authentication:\s*(.*?)\s*-", text).group(1).strip()
#     attachment = re.search(r"- Attachment:\s*(.*?)\s*-", text).group(1).strip()
#     sha256 = re.search(r"- SHA256 hash:\s*(.*?)\s*-", text).group(1).strip()

#     return {
#         "Verdict": verdict,
#         "Confidence": int(confidence),
#         "Reasoning": reasoning,
#         "IOC Enrichment": {
#             "Domain": domain,
#             "Email Authentication": auth,
#             "Attachment": attachment,
#             "SHA256 Hash": sha256
#         }
#     }


sample_output_2 = """
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
- Email authentication: All three email authentication mechanisms (SPF, DKIM, DMARC) failed, strongly suggesting the email is not from a legitimate sender
- Attachment: invoice_1245.pdf - The provided hash appears to be incomplete, but PDF attachments are common vectors for malware delivery
- SHA256 hash: e3b0c44298fc1c14...ffb6c1 (truncated) - Without the complete hash, proper enrichment is limited, but this should be scanned in a sandbox environment

This email contains multiple indicators of a phishing attempt impersonating PayPal with the goal of delivering potentially malicious content via the PDF attachment.

"""


# def process_phishing_detection(data):
#     prompt_ = f"""
#     You are a cybersecurity threat detection assistant. Analyze the email data below and decide if it's phishing or benign.

#         Evaluate:
#         - Subject and body content
#         - Sender name and address
#         - URLs, domains, attachments, hashes
#         - QR codes or shortened links
#         - Language cues (urgency, impersonation, fear)
#         - Header anomalies (SPF, DKIM, DMARC issues)
#         - Threat indicators (IPs, file hashes, domains)

#         Tasks:
#         1. Enrich indicators (URLs, hashes, QR codes, domains) with threat intelligence.
#         2. Judge whether the email is phishing, suspicious, or benign.
#         3. Justify the conclusion briefly based on the indicators.

#         ### Email Data
#         Subject: {data.get("email_subject")}  
#         From: {data["from_name"]} <{data["from_address"]}>  
#         To: {data["to_address"]}  
#         Headers: {data["headers"]}  
#         Body:  
#         {data["email_body"]}

#         Attachments: {data["attachment_names_and_hashes"]}  
#         URLs: {data["list_of_urls"]}  
#         QR Codes (decoded): {data["qr_data"]}

#         ### Output
#         - Verdict: [Phishing | Suspicious | Benign]  
#         - Confidence (0–100%)  
#         - Reasoning:  
#         - (short_reason_1)  
#         - (short_reason_2)  
#         - IOC Enrichment:  
#         - (indicator): (Context)

#     """


#     message = client.messages.create(model="claude-3-7-sonnet-20250219",
#                                     max_tokens=1000,
#                                     temperature=1,
#                                     system="You are a Security Automation Engineer who will integrate this LLM.",
#                                     messages=[{"role": "user","content": prompt_}],
#                                     stream=False,
#                                         )
    
#     print(type(message))
#     response = message.content[0].text
#     return response

# phishing_detection_message = process_phishing_detection(sample_email_data[1])
# print(phishing_detection_message)

# def main():
#     # run sample
#     print(extract_message_output(sample_output_2))


# if __name__ == '__main__':
#     main()

# Sample return statement (Complete) - Sample 2:
"""
Message(id='msg_01VpHmSLFc3jzt5wdbQH3QKW', 
        content=[TextBlock(citations=None, 
        text='I\'ll analyze this email for phishing indicators:\n\n## Analysis Process\n\n
        First, I need to evaluate all the provided data points for potential phishing indicators and enrich any threat indicators with intelligence.\n\n
        ### Email Data Analysis:\n\n1. **Sender:**\n   - Domain "paypal-secure.com" is suspicious - legitimate PayPal emails come from paypal.com\n
        - This appears to be a typosquat or lookalike domain\n\n2. **Email Headers:**\n   
        - SPF: softfail - indicates the sender IP is not authorized to send from this domain\n   
        - DKIM: fail - email was altered in transit or signature is invalid\n   
        - DMARC: fail - email fails authentication policies\n\n3. **Subject/Body:**\n   
        - Creates urgency ("within 24 hours")\n   - Threatens penalties\n   
        - Lacks specific details about the invoice\n   
        - Generic greeting without recipient personalization\n\n4. **Attachment:**\n   
        - invoice_1245.pdf with SHA256 hash starting with e3b0c44298fc1c14...ffb6c1\n   
        - The partial hash shown matches the SHA256 of an empty file (e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)\n   
        - This is suspicious as a legitimate invoice would not be an empty file\n\n
        ### Output\n\n
        - **Verdict: Phishing**\n
        - **Confidence: 95%**\n
        - **Reasoning:**\n  
        - Email originates from a lookalike domain (paypal-secure.com) not the legitimate PayPal domain\n
        - All email authentication mechanisms (SPF, DKIM, DMARC) have failed\n  
        - Uses urgent language and threats to motivate immediate action\n  
        - Attachment hash appears to be for an empty file, likely malicious\n  \n
        - **IOC Enrichment:**\n  
        - Domain "paypal-secure.com": Typosquat of legitimate PayPal domain, likely created for phishing\n  
        - Attachment SHA256 (e3b0c44298fc1c14...): Matches hash of empty file, suspicious for malware payload\n\n
        This email exhibits multiple strong indicators of a phishing attempt designed to appear as if it\'s from PayPal to trick the recipient into opening a potentially malicious attachment.', 
        type='text')], 
        model='claude-3-7-sonnet-20250219', 
        role='assistant', 
        stop_reason='end_turn', 
        stop_sequence=None, 
        type='message', 
        usage=Usage(cache_creation_input_tokens=0, 
        cache_read_input_tokens=0, input_tokens=437, output_tokens=533, server_tool_use=None))
"""

# Sample Return Statement from Sample 2
