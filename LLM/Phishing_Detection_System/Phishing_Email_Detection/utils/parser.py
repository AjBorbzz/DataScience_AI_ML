import re

def extract_message_output(text):
    verdict = re.search(r"### Verdict:\s*(.+)", text).group(1)
    confidence = re.search(r"### Confidence:\s*(\d+)%", text).group(1)
    reasoning = re.findall(r"- (.*?)\n", re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL).group(1))

    domain = re.search(r"- Domain:\s*(.*?)\s*-", text).group(1).strip()
    auth = re.search(r"- Email authentication:\s*(.*?)\s*-", text).group(1).strip()
    attachment = re.search(r"- Attachment:\s*(.*?)\s*-", text).group(1).strip()
    sha256 = re.search(r"- SHA256 hash:\s*(.*?)\s*-", text).group(1).strip()

    return {
        "Verdict": verdict,
        "Confidence": int(confidence),
        "Reasoning": reasoning,
        "IOC Enrichment": {
            "Domain": domain,
            "Email Authentication": auth,
            "Attachment": attachment,
            "SHA256 Hash": sha256
        }
    }
