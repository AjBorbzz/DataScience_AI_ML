import StreamLit as st
import re
import json
from datetime import datetime
from email import policy
from email.parser import BytesParser
from io import BytesIO
from typing import List, Dict, Any


st.set_page_config(
page_title="Phishing Investigation Report",
page_icon="🕵️‍♂️",
layout="wide",
)

st.markdown(
"""
<style>
.small { font-size: 0.85rem; opacity: 0.85; }
.muted { color: #6b7280; }
.badge { display:inline-block; padding:2px 8px; border-radius:9999px; background:#eef2ff; }
.ok { background:#ecfdf5; }
.warn { background:#fffbeb; }
.crit { background:#fef2f2; }
.rule-header{ font-weight:600; margin-top:0.5rem; }
.section-card{ padding:1rem; border-radius:0.75rem; border:1px solid #e5e7eb; background:white; }
</style>
""",
unsafe_allow_html=True,
)


DEFAULT_INDICATORS = [
{"type": "url", "value": "", "source": "extracted", "vt_score": "", "reputation": "unknown", "notes": ""}
]


DEFAULT_TIMELINE = [
{"ts": datetime.utcnow().isoformat(timespec="seconds") + "Z", "actor": "analyst", "event": "Investigation created"}
]


DEFAULT_FLAGS = {
"spoofed_display_name": False,
"suspicious_links": True,
"attachment_macros": False,
"auth_failures": False,
"brand_impersonation": True,
"urgent_language": True,
"sender_mismatch": False,
"new_sender": True,
}


WEIGHTS = {
"spoofed_display_name": 10,
"suspicious_links": 25,
"attachment_macros": 20,
"auth_failures": 15,
"brand_impersonation": 15,
"urgent_language": 5,
"sender_mismatch": 20,
"new_sender": 5,
}


REPUTATION_ORDER = ["malicious", "suspicious", "unknown", "benign"]


def calc_risk(flags: Dict[str, bool], indicators: List[Dict[str, Any]]) -> Dict[str, Any]:
    base = sum(WEIGHTS[k] for k, v in flags.items() if v)
    # Indicator-based adjustments
    ind_boost = 0
    for ind in indicators:
        rep = (ind.get("reputation") or "").lower()
        if rep == "malicious":
            ind_boost += 25
        elif rep == "suspicious":
            ind_boost += 10
        elif rep == "benign":
            ind_boost -= 5
    total = max(0, min(100, base + ind_boost))
    if total >= 70:
        verdict = "Malicious"
        tone = "crit"
    elif total >= 40:
        verdict = "Suspicious"
        tone = "warn"
    else:
        verdict = "Benign / No Action"
        tone = "ok"
    return {"score": total, "verdict": verdict, "tone": tone}

def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    url_pattern = r"(https?://[\w\-\._~:/%\?#\[\]@!$&'()*+,;=]+)"
    return list(sorted(set(re.findall(url_pattern, text, flags=re.IGNORECASE))))


def parse_eml(file_bytes: bytes) -> Dict[str, Any]:
    try:
        msg = BytesParser(policy=policy.default).parsebytes(file_bytes)
        headers = {
            "From": str(msg.get("From", "")),
            "To": str(msg.get("To", "")),
            "Cc": str(msg.get("Cc", "")),
            "Subject": str(msg.get("Subject", "")),
            "Date": str(msg.get("Date", "")),
            "Message-ID": str(msg.get("Message-ID", "")),
            "Return-Path": str(msg.get("Return-Path", "")),
            "Received": "\n".join(msg.get_all("Received", []))[:5000],
            "Authentication-Results": str(msg.get("Authentication-Results", "")),
        }
        # Walk body and collect text parts
        body_texts = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    try:
                        body_texts.append(part.get_content())
                    except Exception:
                        pass
                elif ctype == "text/html":
                    try:
                        body_texts.append(part.get_content())
                    except Exception:
                        pass
        else:
            try:
                body_texts.append(msg.get_content())
            except Exception:
                pass
        body_joined = "\n\n".join([t if isinstance(t, str) else str(t) for t in body_texts])
        urls = extract_urls(body_joined)
        return {"headers": headers, "body_preview": body_joined[:4000], "urls": urls}
    except Exception as e:
        return {"error": str(e)}