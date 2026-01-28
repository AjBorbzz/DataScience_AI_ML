import re

# Handles: "Proverbs 22:7", "Matthew 6:19-21", "1 Timothy 6:10"
_REF_RE = re.compile(
    r"\(?"                               # optional "("
    r"(?P<book>(?:[1-3]\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*)"  # book name, supports "1 John", "Song of Solomon"
    r"\s+"
    r"(?P<ch>\d+)"
    r":"
    r"(?P<v1>\d+)"
    r"(?:-(?P<v2>\d+))?"
    r"\)?"
)

def normalize_book(book: str) -> str:
    return " ".join(book.split()).strip()

def extract_refs(text: str) -> list[str]:
    out = []
    for m in _REF_RE.finditer(text or ""):
        book = " ".join(m.group("book").split())
        ch = m.group("ch")
        v1 = m.group("v1")
        v2 = m.group("v2")
        ref = f"{book} {ch}:{v1}" + (f"-{v2}" if v2 else "")
        out.append(ref)
    return out

def validate_refs(found_refs, allowed_refs):
    allowed = set(allowed_refs)
    invalid = [r for r in found_refs if r not in allowed]
    return invalid
