"""
Optional feature: Grounding Guard for RAG answers.

Purpose:
    Run a second validation step after answer generation to check whether the
    answer is actually supported by the retrieved context.

How to integrate later:
    1. Import evaluate_grounding from this file.
    2. After calling generate_response(...), call evaluate_grounding(...).
    3. Display the verdict and issues in Streamlit.

Example integration:
    answer = generate_response(query, chunks)
    grounding_report = evaluate_grounding(
        query=query,
        answer=answer,
        context=format_context(chunks),
        api_key=get_secret("GEMINI_API"),
    )
    st.json(grounding_report)
"""

from __future__ import annotations

import json
from typing import Any

from litellm import completion


DEFAULT_GROUNDING_MODEL = "gemini/gemini-1.5-flash"


class GroundingGuardError(RuntimeError):
    """Raised when grounding validation fails unexpectedly."""



def _safe_json_loads(raw_text: str) -> dict[str, Any]:
    """Parse JSON safely from an LLM response that may contain markdown fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("JSON\n", "", 1)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GroundingGuardError(f"Grounding model returned invalid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise GroundingGuardError("Grounding model response must be a JSON object.")

    return parsed



def evaluate_grounding(
    *,
    query: str,
    answer: str,
    context: str,
    api_key: str | None,
    model: str = DEFAULT_GROUNDING_MODEL,
    timeout: int = 60,
) -> dict[str, Any]:
    """
    Validate whether a generated RAG answer is grounded in retrieved context.

    Returns a dictionary like:
        {
            "verdict": "supported" | "partially_supported" | "unsupported",
            "confidence": 0.0-1.0,
            "unsupported_claims": [...],
            "missing_context": [...],
            "recommended_action": "..."
        }
    """
    if not api_key:
        raise GroundingGuardError("Missing API key for grounding validation.")

    system_prompt = (
        "You are a strict RAG grounding validator. "
        "Check whether the answer is supported only by the retrieved context. "
        "Do not judge whether the answer is generally true. Judge only support from context. "
        "Return valid JSON only."
    )

    user_prompt = f"""
Question:
{query}

Retrieved context:
{context}

Generated answer:
{answer}

Return this exact JSON schema:
{{
  "verdict": "supported | partially_supported | unsupported",
  "confidence": 0.0,
  "unsupported_claims": [],
  "missing_context": [],
  "recommended_action": ""
}}
""".strip()

    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        api_key=api_key,
        temperature=0,
        timeout=timeout,
    )

    raw_content = str(response["choices"][0]["message"]["content"])
    report = _safe_json_loads(raw_content)

    verdict = str(report.get("verdict", "")).strip().lower()
    if verdict not in {"supported", "partially_supported", "unsupported"}:
        raise GroundingGuardError(f"Invalid grounding verdict: {verdict}")

    try:
        confidence = float(report.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    report["confidence"] = max(0.0, min(1.0, confidence))
    report.setdefault("unsupported_claims", [])
    report.setdefault("missing_context", [])
    report.setdefault("recommended_action", "")

    return report
