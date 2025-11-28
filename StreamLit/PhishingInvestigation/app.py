import streamlit as st
import re
import json
from datetime import datetime
from email import policy
from email.parser import BytesParser
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
    {
        "type": "url",
        "value": "",
        "source": "extracted",
        "vt_score": "",
        "reputation": "unknown",
        "notes": "",
    }
]

DEFAULT_TIMELINE = [
    {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "actor": "analyst",
        "event": "Investigation created",
    }
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
        body_joined = "\n\n".join(
            [t if isinstance(t, str) else str(t) for t in body_texts]
        )
        urls = extract_urls(body_joined)
        return {"headers": headers, "body_preview": body_joined[:4000], "urls": urls}
    except Exception as e:
        return {"error": str(e)}


def to_markdown(payload: Dict[str, Any]) -> str:
    md = []
    add = md.append

    add("# Phishing Investigation Report\n")
    add(f"_Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n")

    meta = payload.get("meta", {})
    add("\n## Case Metadata")
    for k in ["case_id", "analyst", "severity", "status", "environment", "business_unit"]:
        add(f"- **{k.replace('_', ' ').title()}**: {meta.get(k, '')}")

    email = payload.get("email", {})
    add("\n## Email Details")
    for k in ["from", "to", "cc", "subject", "date", "message_id", "return_path"]:
        add(f"- **{k.replace('_', ' ').title()}**: {email.get(k, '')}")

    add("\n### Authentication")
    for k in ["spf", "dkim", "dmarc", "auth_results"]:
        label = "Authentication-Results" if k == "auth_results" else k.upper()
        add(f"- **{label}**: {email.get(k, '')}")

    add("\n## Indicators")
    inds = payload.get("indicators", [])
    if inds:
        add("| Type | Value | Source | VT Score | Reputation | Notes |")
        add("|---|---|---|---:|---|---|")
        for ind in inds:
            add(
                f"| {ind.get('type','')} | {ind.get('value','')} | {ind.get('source','')} | "
                f"{ind.get('vt_score','')} | {ind.get('reputation','')} | {ind.get('notes','')} |"
            )
    else:
        add("_None_")

    add("\n## Analysis Flags")
    flags = payload.get("flags", {})
    for k, v in flags.items():
        add(f"- {k.replace('_', ' ').title()}: {'Yes' if v else 'No'}")

    vr = payload.get("verdict", {})
    add("\n## Verdict")
    add(f"- **Risk Score**: {vr.get('score', '')}")
    add(f"- **Verdict**: {vr.get('verdict', '')}")

    add("\n## Actions Taken")
    acts = payload.get("actions", [])
    if acts:
        for a in acts:
            add(f"- {a}")
    else:
        add("- (none)")

    add("\n## Timeline")
    tline = payload.get("timeline", [])
    if tline:
        for t in tline:
            add(
                f"- {t.get('ts', '')} — **{t.get('actor', '')}**: {t.get('event', '')}"
            )
    else:
        add("- (no events recorded)")

    notes = payload.get("notes", "")
    if notes:
        add("\n## Analyst Notes\n")
        add(notes)

    img_names = payload.get("images", [])
    if img_names:
        add("\n## Evidence Screenshots (filenames)\n")
        for n in img_names:
            add(f"- {n}")

    return "\n".join(md)


# Session scaffolding
if "indicators" not in st.session_state:
    st.session_state.indicators = DEFAULT_INDICATORS.copy()
if "timeline" not in st.session_state:
    st.session_state.timeline = DEFAULT_TIMELINE.copy()
if "flags" not in st.session_state:
    st.session_state.flags = DEFAULT_FLAGS.copy()
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "report_payload" not in st.session_state:
    st.session_state.report_payload = {}


# Sidebar
st.sidebar.header("Case Controls")
with st.sidebar:
    st.markdown("Manage case-level details and export your report.")
    case_id = st.text_input("Case ID", value="PHISH-0001")
    analyst = st.text_input("Analyst", value="")
    severity = st.select_slider(
        "Severity", options=["Low", "Medium", "High", "Critical"], value="Medium"
    )
    status = st.selectbox(
        "Status",
        ["Open", "Under Review", "Containment", "Eradication", "Closed"],
        index=0,
    )
    environment = st.text_input("Environment / Tenant", value="Production")
    business_unit = st.text_input("Business Unit", value="")

    st.divider()
    st.caption("Export controls are in the Export tab.")


st.title("Phishing Investigation Report")
st.caption(
    "Streamlit UI for analysts to capture evidence, enrichment, and a defensible verdict."
)

meta_tab, email_tab, ind_tab, enrich_tab, actions_tab, timeline_tab, notes_tab, export_tab = st.tabs(
    [
        "Case Metadata",
        "Email",
        "Indicators",
        "Enrichment",
        "Actions",
        "Timeline",
        "Notes",
        "Export",
    ]
)

# --- Case Metadata ---
with meta_tab:
    st.subheader("Case Metadata")
    col1, col2, col3 = st.columns(3)
    with col1:
        report_date = st.date_input(
            "Report Date", value=datetime.utcnow().date()
        )
        detection_source = st.selectbox(
            "Detection Source",
            ["User Report", "SIEM Alert", "Email Gateway", "Hunting", "Other"],
            index=1,
        )
    with col2:
        campaign = st.text_input("Campaign / Cluster Tag", value="")
        mitre = st.multiselect(
            "MITRE ATT&CK (Suspected)",
            [
                "TA0001 - Initial Access",
                "TA0002 - Execution",
                "TA0009 - Collection",
                "TA0011 - Command and Control",
                "TA0013 - Test",
            ],
        )
    with col3:
        customer = st.text_input("Customer / Stakeholder", value="Internal")
        sensitivity = st.selectbox(
            "Report Sensitivity", ["Public", "Internal", "Confidential"], index=1
        )

# --- Email ---
with email_tab:
    st.subheader("Email Artifacts")
    st.caption("Upload a .eml to auto-extract headers and URLs, or fill manually.")
    eml = st.file_uploader(".eml file", type=["eml"])
    parsed = {}

    if eml is not None:
        parsed = parse_eml(eml.read())
        if parsed.get("error"):
            st.error(f"Failed to parse EML: {parsed['error']}")
        else:
            with st.expander("Parsed Headers"):
                st.json(parsed.get("headers", {}))
            with st.expander("Body Preview (truncated)"):
                st.code(parsed.get("body_preview", ""))

            urls = parsed.get("urls", [])
            if urls:
                for u in urls:
                    st.session_state.indicators.append(
                        {
                            "type": "url",
                            "value": u,
                            "source": "email_body",
                            "vt_score": "",
                            "reputation": "unknown",
                            "notes": "extracted from body",
                        }
                    )
                st.info(
                    f"Extracted {len(urls)} URL(s) and appended to Indicators."
                )

    col1, col2 = st.columns(2)
    with col1:
        email_from = st.text_input(
            "From",
            value=(parsed.get("headers", {}).get("From", "") if parsed else ""),
        )
        email_to = st.text_input(
            "To",
            value=(parsed.get("headers", {}).get("To", "") if parsed else ""),
        )
        email_cc = st.text_input(
            "Cc",
            value=(parsed.get("headers", {}).get("Cc", "") if parsed else ""),
        )
        subject = st.text_input(
            "Subject",
            value=(parsed.get("headers", {}).get("Subject", "") if parsed else ""),
        )
    with col2:
        email_date = st.text_input(
            "Date",
            value=(parsed.get("headers", {}).get("Date", "") if parsed else ""),
        )
        message_id = st.text_input(
            "Message-ID",
            value=(parsed.get("headers", {}).get("Message-ID", "") if parsed else ""),
        )
        return_path = st.text_input(
            "Return-Path",
            value=(parsed.get("headers", {}).get("Return-Path", "") if parsed else ""),
        )
        auth_results = st.text_area(
            "Authentication-Results",
            value=(
                parsed.get("headers", {}).get("Authentication-Results", "")
                if parsed
                else ""
            ),
            height=80,
        )

    st.markdown("### Authentication Summary")
    a1, a2, a3 = st.columns(3)
    with a1:
        spf = st.selectbox(
            "SPF", ["pass", "fail", "softfail", "neutral", "none", "unknown"], index=0
        )
    with a2:
        dkim = st.selectbox(
            "DKIM", ["pass", "fail", "none", "unknown"], index=0
        )
    with a3:
        dmarc = st.selectbox(
            "DMARC", ["pass", "fail", "none", "unknown"], index=0
        )

# --- Indicators ---
with ind_tab:
    st.subheader("Indicators of Compromise (IoCs)")
    st.caption(
        "Edit in place. Add URLs, IPs, domains, hashes, emails. Fill reputation as enrichment completes."
    )

    st.session_state.indicators = st.data_editor(
        st.session_state.indicators,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "type": st.column_config.SelectboxColumn(
                options=["url", "domain", "ip", "hash", "email"], width="small"
            ),
            "value": st.column_config.TextColumn(width="large"),
            "source": st.column_config.SelectboxColumn(
                options=[
                    "extracted",
                    "email_body",
                    "header",
                    "gateway",
                    "siem",
                    "manual",
                ],
                width="small",
            ),
            "vt_score": st.column_config.TextColumn(
                label="VT Score", width="small"
            ),
            "reputation": st.column_config.SelectboxColumn(
                options=REPUTATION_ORDER, width="small"
            ),
            "notes": st.column_config.TextColumn(width="medium"),
        },
        hide_index=True,
    )

# --- Enrichment / Flags + Risk ---
with enrich_tab:
    st.subheader("Enrichment & Heuristic Flags")
    st.caption("Toggle signals used for heuristic risk scoring.")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.session_state.flags["spoofed_display_name"] = st.checkbox(
            "Spoofed Display Name",
            value=st.session_state.flags["spoofed_display_name"],
        )
        st.session_state.flags["suspicious_links"] = st.checkbox(
            "Suspicious Links",
            value=st.session_state.flags["suspicious_links"],
        )
        st.session_state.flags["attachment_macros"] = st.checkbox(
            "Attachment Macros / Executables",
            value=st.session_state.flags["attachment_macros"],
        )
    with f2:
        st.session_state.flags["auth_failures"] = st.checkbox(
            "Authentication Failures (SPF/DKIM/DMARC)",
            value=st.session_state.flags["auth_failures"],
        )
        st.session_state.flags["brand_impersonation"] = st.checkbox(
            "Brand Impersonation",
            value=st.session_state.flags["brand_impersonation"],
        )
        st.session_state.flags["urgent_language"] = st.checkbox(
            "Urgent / Coercive Language",
            value=st.session_state.flags["urgent_language"],
        )
    with f3:
        st.session_state.flags["sender_mismatch"] = st.checkbox(
            "Display Name vs Address Mismatch",
            value=st.session_state.flags["sender_mismatch"],
        )
        st.session_state.flags["new_sender"] = st.checkbox(
            "First-Time Sender to Recipient",
            value=st.session_state.flags["new_sender"],
        )

    verdict = calc_risk(st.session_state.flags, st.session_state.indicators)

    st.markdown("---")
    st.markdown("### Heuristic Verdict")
    vcol1, vcol2 = st.columns([1, 3])
    with vcol1:
        st.metric("Risk Score", verdict["score"])
    with vcol2:
        st.markdown(
            f"<span class='badge {verdict['tone']}'>Verdict: {verdict['verdict']}</span>",
            unsafe_allow_html=True,
        )

# --- Actions ---
with actions_tab:
    st.subheader("Actions Taken")
    st.caption("Track containment/eradication steps for auditability.")
    actions_df = st.data_editor(
        getattr(st.session_state, "actions_editor", [{"action": ""}]),
        key="actions_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "action": st.column_config.TextColumn(
                width="large", help="Describe the action you performed"
            )
        },
        hide_index=True,
    )

# --- Timeline ---
with timeline_tab:
    st.subheader("Timeline")
    st.caption("Chronological sequence of events in the investigation.")

    st.session_state.timeline = st.data_editor(
        st.session_state.timeline,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "ts": st.column_config.TextColumn(
                label="Timestamp (UTC ISO8601)",
                width="large",
                help="e.g. 2025-11-28T10:15:00Z",
            ),
            "actor": st.column_config.TextColumn(
                width="medium", help="Who performed the action"
            ),
            "event": st.column_config.TextColumn(
                width="large", help="What happened"
            ),
        },
        hide_index=True,
    )

# --- Notes ---
with notes_tab:
    st.subheader("Analyst Notes")
    st.caption("Free-form notes, rationale, and narrative for the case.")
    st.session_state.notes = st.text_area(
        "Notes",
        value=st.session_state.notes,
        height=200,
        placeholder="Document your reasoning, escalation notes, approvals, etc.",
    )

# --- Export ---
with export_tab:
    st.subheader("Export Report")
    st.caption("Generate a structured payload and download as Markdown or JSON.")

    # Build payload
    actions_list = [
        row["action"].strip()
        for row in st.session_state.actions_editor
        if row.get("action", "").strip()
    ]

    payload = {
        "meta": {
            "case_id": case_id,
            "analyst": analyst,
            "severity": severity,
            "status": status,
            "environment": environment,
            "business_unit": business_unit,
            "report_date": report_date.isoformat(),
            "detection_source": detection_source,
            "campaign": campaign,
            "mitre": mitre,
            "customer": customer,
            "sensitivity": sensitivity,
        },
        "email": {
            "from": email_from,
            "to": email_to,
            "cc": email_cc,
            "subject": subject,
            "date": email_date,
            "message_id": message_id,
            "return_path": return_path,
            "spf": spf,
            "dkim": dkim,
            "dmarc": dmarc,
            "auth_results": auth_results,
        },
        "indicators": st.session_state.indicators,
        "flags": st.session_state.flags,
        "verdict": verdict,
        "actions": actions_list,
        "timeline": st.session_state.timeline,
        "notes": st.session_state.notes,
        "images": [],
    }

    st.session_state.report_payload = payload

    with st.expander("Raw Payload Preview"):
        st.json(payload)

    markdown_report = to_markdown(payload)
    json_report = json.dumps(payload, indent=2)

    st.download_button(
        "Download Markdown Report",
        data=markdown_report,
        file_name=f"{case_id}_report.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download JSON Payload",
        data=json_report,
        file_name=f"{case_id}_payload.json",
        mime="application/json",
    )
