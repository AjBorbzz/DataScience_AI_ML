REQUIRED_HEADERS = [
    "Biblical Summary:",
    "Key Scriptures:",
    "Explanation:",
    "Wisdom Applications:",
]

def missing_headers(answer: str):
    return [h for h in REQUIRED_HEADERS if h not in answer]
