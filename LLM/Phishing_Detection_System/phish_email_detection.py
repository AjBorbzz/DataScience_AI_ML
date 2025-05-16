import os
from dotenv import load_dotenv
import anthropic 
from sample_data import sample_email_data

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
    return message

# print(sample_email_data[0])


phishing_detection_message = process_phishing_detection(sample_email_data[0])

print(phishing_detection_message)


### Example output
"""
Message(id='msg_01KPefmuQTE9G3ncMPZHxQ8r', 
        content=[TextBlock(
                citations=None, 
                text='I\'ll analyze this email carefully using the structured threat detection approach.\n\n
                ## Analysis\n\n
                ### Email Data Assessment\n
                - **Subject**: "Urgent: Your Account Has Been Locked!" uses urgency tactics common in phishing\n
                - **Sender**: Claims to be Chase Bank but uses a suspicious domain (chase-verification.com)\n
                - **Authentication**: All email authentication mechanisms failed (SPF, DKIM, DMARC)\n
                - **Content**: Brief message with urgent call to action and suspicious link\n
                - **URL**: Domain "chase-verification-login.com" is not an official Chase Bank domain\n\n
                ### IOC Enrichment\n
                - **Domain analysis**: "chase-verification.com" \n
                   - Not a legitimate Chase domain (legitimate would be chase.com)\n 
                 - Uses hyphenated domain naming pattern common in phishing\n
                 - **URL analysis**: "http://chase-verification-login.com"\n
                   - Uses HTTP instead of HTTPS (lacks encryption)\n  - Domain mimics Chase Bank but is not authentic\n
                   - Likely a credential harvesting page\n\n## Output\n\n
                 - **Verdict**: Phishing\n
                 - **Confidence**: 95%\n- **Reasoning**:\n
                   - Email fails all authentication checks (SPF, DKIM, DMARC)\n
                   - Sender domain "chase-verification.com" is not an official Chase domain\n
                   - Uses classic phishing tactics: urgency, fear, and impersonation of a financial institution\n
                   - Contains suspicious URL that mimics the bank\'s name but on an unofficial domain\n
                   - Lacks specific customer information that would be in legitimate communications\n\n
                 - **IOC Enrichment**:\n
                   - chase-verification.com: Suspicious domain mimicking Chase Bank, not affiliated with legitimate financial institution\n
                   - chase-verification-login.com: Likely credential harvesting site, not an official Chase domain\n
                   - SPF/DKIM/DMARC failures: Indicates the email is not actually from the claimed sender\n\n
                 This is a clear phishing attempt designed to trick users into believing their Chase account has security issues requiring immediate action, with the goal of stealing login credentials.', 
                type='text')],
                model='claude-3-7-sonnet-20250219', 
                role='assistant',
                stop_reason='end_turn', 
                stop_sequence=None, 
                type='message', 
                usage=Usage(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=432, output_tokens=471, server_tool_use=None)
        )
"""

sample_output = """
            I\'ll analyze this email carefully using the structured threat detection approach.\n\n
                ## Analysis\n\n
                ### Email Data Assessment\n
                - **Subject**: "Urgent: Your Account Has Been Locked!" uses urgency tactics common in phishing\n
                - **Sender**: Claims to be Chase Bank but uses a suspicious domain (chase-verification.com)\n
                - **Authentication**: All email authentication mechanisms failed (SPF, DKIM, DMARC)\n
                - **Content**: Brief message with urgent call to action and suspicious link\n
                - **URL**: Domain "chase-verification-login.com" is not an official Chase Bank domain\n\n
                ### IOC Enrichment\n
                - **Domain analysis**: "chase-verification.com" \n
                   - Not a legitimate Chase domain (legitimate would be chase.com)\n 
                 - Uses hyphenated domain naming pattern common in phishing\n
                 - **URL analysis**: "http://chase-verification-login.com"\n
                   - Uses HTTP instead of HTTPS (lacks encryption)\n  - Domain mimics Chase Bank but is not authentic\n
                   - Likely a credential harvesting page\n\n## Output\n\n
                 - **Verdict**: Phishing\n
                 - **Confidence**: 95%\n- **Reasoning**:\n
                   - Email fails all authentication checks (SPF, DKIM, DMARC)\n
                   - Sender domain "chase-verification.com" is not an official Chase domain\n
                   - Uses classic phishing tactics: urgency, fear, and impersonation of a financial institution\n
                   - Contains suspicious URL that mimics the bank\'s name but on an unofficial domain\n
                   - Lacks specific customer information that would be in legitimate communications\n\n
                 - **IOC Enrichment**:\n
                   - chase-verification.com: Suspicious domain mimicking Chase Bank, not affiliated with legitimate financial institution\n
                   - chase-verification-login.com: Likely credential harvesting site, not an official Chase domain\n
                   - SPF/DKIM/DMARC failures: Indicates the email is not actually from the claimed sender\n\n
                 This is a clear phishing attempt designed to trick users into believing their Chase account has security issues requiring immediate action, with the goal of stealing login credentials.

"""