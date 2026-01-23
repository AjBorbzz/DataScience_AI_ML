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

