SECTIONS = {
    "Biblical Summary:": ["Key Scriptures:"],
    "Key Scriptures:": ["Explanation:"],
    "Explanation:": ["Wisdom Applications:"],
    "Wisdom Applications:": ["(Optional) Closing Prayer:"],
}

def split_sections(answer: str):
    # very simple parser based on known headers
    parts = {}
    for header in SECTIONS.keys():
        parts[header] = ""

    lines = answer.splitlines()
    current = None
    for line in lines:
        line_stripped = line.strip()
        if line_stripped in SECTIONS:
            current = line_stripped
            continue
        if current:
            parts[current] += line + "\n"
    return {k: v.strip() for k, v in parts.items()}

def section_ref_coverage(answer: str, allowed_refs: list[str]):
    allowed = set(allowed_refs)
    sections = split_sections(answer)
    missing = []
    for header, body in sections.items():
        if header == "(Optional) Closing Prayer:" and not body:
            continue  # optional section can be empty
        hit = any(r in body for r in allowed) or any(r in header for r in allowed)
        if not hit:
            missing.append(header)
    return missing
