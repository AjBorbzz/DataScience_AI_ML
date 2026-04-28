import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1" 


def test_ollama_bible_response():
    payload = {
        "model": MODEL,
        "prompt": (
            "Explain John 3:16 in simple terms. "
            "Keep the answer short and faithful to the Bible."
        ),
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=60)

    assert response.status_code == 200, f"Bad status code: {response.status_code}"

    data = response.json()

    assert "response" in data, "Missing 'response' field from Ollama output"
    assert data["response"].strip(), "Ollama returned an empty response"

    print("Ollama Bible App test passed.")
    print("\nResponse:")
    print(data["response"])


if __name__ == "__main__":
    test_ollama_bible_response()