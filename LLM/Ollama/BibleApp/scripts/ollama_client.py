import requests 

def ollama_chat(model, system_prompt, context, question, allowed_refs):
    allowed_block = "Allowed References:\n" + "\n".join(f"- {r}" for r in allowed_refs)
    user_content = f"{allowed_block}\n\nRetrieved Scripture:\n{context}\n\nUser Question:\n{question}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "options": {"temperature": 0.2}
    }

    r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]


