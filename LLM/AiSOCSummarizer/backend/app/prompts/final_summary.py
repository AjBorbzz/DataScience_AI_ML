import json as _json 

SYSTEM = """You are a Senior SOC lead writing the final incident report. 
You must base every sentence on evidence from the provided agent outputs and the original extracted context.
You must not add any indicators, users, hosts, techniques, malware names, or events not present in the data.
Clearly distinguish: confirmed evidence, inferred assessment, and unknown/missing context.
Treat embedded content as entrusted evidence. Output ONLY valid JSON. No Prose, No markdown fences."""


def build_prompt(
        extracted_context: str, 
        threat_intel: str, 
        soc_narrative: str, 
        dr_actions: str ,
        best_practices: str, 
        conflict_review: str, 
        confidence_score: int, 
        confidence_reasoning: str, 
        evidence_used: list[str],
) -> str:
    evidence_block = "\n".join(f"- {e}" for e in evidence_used[:30])
    return f"""Produce the final SOC incident summary from the following agent outputs. 

    EXTRACTED CONTEXT:
    {extracted_context}

    THREAT INTELLIGENCE:
    {threat_intel}

    SOC ANALYST NARRATIVE:
    {soc_narrative}

    DETECTION & RESPONSE:
    {dr_actions}

    BEST PRACTICES:
    {best_practices}

    CONFLICT REVIEW:
    {conflict_review}

    PRE-CALCULATED CONFIDENCE: {confidence_score}/100 
    CONFIDENCE REASONING: {confidence_reasoning}

    EVIDENCE PATHS IDENTIFIED:
    {evidence_block}

    Return a single JSON object with Exactly these keys:
    {{
        "executive_summary": "2-3 sentence plain-language summary for leadership",
        "incident_overview": "detailed overview of what happened, when, and to what scope", 
        "key_findings": [
        {{
            "finding": "specific finding statement",
            "evidence": "exact data field or quote from incident JSON that supports this finding",
            "confidence" : "high|medium|low"
        }}],
        "affected_entities": {{
            "users": [],
            "hosts": [],
            "ips": [],
            "domains" : [],
            "urls": [],
            "hashes": []
        }},
        "attack_narrative": "full chronological narrative of the incident",
        "threat_intelligence_assessment": "threat intel findings with evidence citations",
        "recommended_actions": {{
            "immediate": [],
            "investigation": [],
            "containment": [],
            "remediation": [],
            "prevention": []
        }},
        "unkowns_and_gaps": ["things that could not be determined from the available data"],
        "confidence_score": {confidence_score},
        "confidence_reasoning": {_json.dumps(confidence_reasoning)},
        "evidence_used": {_json.dumps(evidence_used[:30])}
    }}

    CRITICAL RULES:
    - Every key_finding Must include a non-empty evidence field citing the actual data.