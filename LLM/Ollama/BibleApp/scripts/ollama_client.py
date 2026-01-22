import requests
from scripts.answer_template import ANSWER_TEMPLATE

def ollama_chat(model, system_prompt, context, question, allowed_refs):
    allowed_block = "Allowed References (you must cite ONLY these; include at least one in EVERY section):\n" + \
                    "\n".join(f"- {r}" for r in allowed_refs)

    user_content = (
        f"{allowed_block}\n\n"
        f"Retrieved Scripture (use as the ONLY source):\n{context}\n\n"
        f"User Question:\n{question}\n\n"
        f"{ANSWER_TEMPLATE}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
        "options": {"temperature": 0.0}
    }

    r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"]
