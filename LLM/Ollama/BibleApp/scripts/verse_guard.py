import re

# Handles: "Proverbs 22:7", "Matthew 6:19-21", "1 Timothy 6:10"
REF_RE = re.compile(
    r'\b((?:[1-3]\s)?[A-Za-z]+(?:\s[A-Za-z]+)*)\s(\d+):(\d+)(?:-(\d+))?\b'
)

def normalize_book(book: str) -> str:
    return " ".join(book.split()).strip()

def extract_refs(text: str):
    refs = []
    for m in REF_RE.finditer(text):
        book = normalize_book(m.group(1))
        ch = int(m.group(2))
        vs = int(m.group(3))
        ve = int(m.group(4)) if m.group(4) else vs
        if vs > ve:
            vs, ve = ve, vs
        if vs == ve:
            refs.append(f"{book} {ch}:{vs}")
        else:
            refs.append(f"{book} {ch}:{vs}-{ve}")
    return refs

def validate_refs(found_refs, allowed_refs):
    allowed = set(allowed_refs)
    invalid = [r for r in found_refs if r not in allowed]
    return invalid
