import re

def expand_ref(ref: str) -> list[str]:
    # "Book 3:16-18" -> ["Book 3:16-18","Book 3:16","Book 3:17","Book 3:18"]
    m = re.match(r"^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$", ref.strip())
    if not m:
        return [ref]
    book = m.group(1).strip()
    ch = int(m.group(2))
    a = int(m.group(3))
    b = int(m.group(4)) if m.group(4) else a
    out = [f"{book} {ch}:{a}" + (f"-{b}" if b != a else "")]
    for v in range(a, b + 1):
        out.append(f"{book} {ch}:{v}")
    return out

def ref_str(r):
    vs, ve = r["verse_start"], r["verse_end"]
    base = f'{r["book"]} {r["chapter"]}:{vs}'
    return base if vs == ve else f"{base}-{ve}"

def format_passage(r):
    return f'{ref_str(r)} ({r["translation"]})\n{r["text"]}'

def build_context(passages, max_passages=10):
    selected = passages[:max_passages]
    allowed = [ref_str(p) for p in selected]
    context = "\n\n".join(format_passage(p) for p in selected)
    return context, allowed

