def format_passage(r):
    ref = f'{r["book"]} {r["chapter"]}:{r["verse_start"]}'
    if r["verse_start"] != r["verse_end"]:
        ref += f'-{r["verse_end"]}'
    return f'{ref} (KJV)\n{r["text"]}'

def build_context(passages, max_passages=6):
    selected = passages[:max_passages]
    return "\n\n".join(format_passage(p) for p in selected)
