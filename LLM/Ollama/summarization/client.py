import argparse
import asyncio
from typing import Any
from urllib.parse import urlparse

import httpx


DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_MODEL = "llama3"


class ClientError(Exception):
    """Raised when the client receives an invalid or failed response."""


def normalize_base_url(base_url: str) -> str:
    """Validate and normalize the server base URL."""
    parsed = urlparse(base_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Base URL must start with http:// or https://")

    if not parsed.netloc:
        raise ValueError("Base URL must include a hostname and optional port")

    return base_url.rstrip("/")


def build_headers(token: str | None = None) -> dict[str, str]:
    """Build optional authorization headers."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


async def parse_json_response(response: httpx.Response) -> dict[str, Any]:
    """Safely parse JSON from an HTTP response."""
    try:
        return response.json()
    except ValueError as exc:
        raise ClientError(
            f"Server returned non-JSON response: {response.text[:500]}"
        ) from exc


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send an HTTP request and return validated JSON."""
    try:
        response = await client.request(method, path, json=json_body)
        response.raise_for_status()
        return await parse_json_response(response)

    except httpx.TimeoutException as exc:
        raise ClientError("Request timed out. Server or model may be overloaded.") from exc

    except httpx.ConnectError as exc:
        raise ClientError("Cannot connect to server. Check if FastAPI is running.") from exc

    except httpx.HTTPStatusError as exc:
        error_text = exc.response.text[:500]
        raise ClientError(
            f"HTTP {exc.response.status_code}: {error_text}"
        ) from exc

    except httpx.HTTPError as exc:
        raise ClientError(f"HTTP client error: {exc}") from exc


async def check_health(client: httpx.AsyncClient) -> dict[str, Any]:
    """Call the health endpoint."""
    return await request_json(client, "GET", "/health")


async def list_models(client: httpx.AsyncClient) -> dict[str, Any]:
    """Call the models endpoint."""
    return await request_json(client, "GET", "/models")


async def ask_question(
    client: httpx.AsyncClient,
    question: str,
    model: str,
) -> str:
    """Send a question to the server and return the answer."""
    payload = {
        "question": question,
        "model": model,
    }

    result = await request_json(client, "POST", "/ask", json_body=payload)

    answer = result.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise ClientError("Server response does not contain a valid 'answer' field.")

    return answer


async def test_client(
    question: str,
    model: str,
    base_url: str,
    token: str | None = None,
    timeout_seconds: float = 120.0,
) -> str | None:
    """Run a health check, then ask one question."""
    base_url = normalize_base_url(base_url)

    timeout = httpx.Timeout(
        connect=5.0,
        read=timeout_seconds,
        write=10.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        base_url=base_url,
        headers=build_headers(token),
        timeout=timeout,
    ) as client:
        try:
            print("Testing health check...")
            health = await check_health(client)
            print(f"Health: {health}")

            print(f"\nAsking question: {question!r}")
            answer = await ask_question(client, question, model)

            print(f"\nAnswer:\n{answer}")
            return answer

        except ClientError as exc:
            print(f"Error: {exc}")
            return None


async def read_input(prompt: str) -> str:
    """Read terminal input without blocking the event loop directly."""
    return await asyncio.to_thread(input, prompt)


async def interactive_client(
    base_url: str,
    model: str,
    token: str | None = None,
    timeout_seconds: float = 120.0,
) -> None:
    """Run an interactive CLI client."""
    base_url = normalize_base_url(base_url)

    timeout = httpx.Timeout(
        connect=5.0,
        read=timeout_seconds,
        write=10.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        base_url=base_url,
        headers=build_headers(token),
        timeout=timeout,
    ) as client:
        print("=== Interactive Ollama Client ===")
        print("Commands: quit | exit | q | health | models")
        print("-" * 40)

        while True:
            try:
                question = (await read_input(f"\n[{model}] Enter your question: ")).strip()

                if question.lower() in {"quit", "exit", "q"}:
                    print("Goodbye.")
                    return

                if question.lower() == "health":
                    health = await check_health(client)
                    print(f"Health: {health}")
                    continue

                if question.lower() == "models":
                    models = await list_models(client)
                    print(f"Available models: {models}")
                    continue

                if not question:
                    print("Question cannot be empty.")
                    continue

                print("\nThinking...")

                answer = await ask_question(client, question, model)
                print(f"\nAnswer:\n{answer}")

            except KeyboardInterrupt:
                print("\nGoodbye.")
                return

            except ClientError as exc:
                print(f"Error: {exc}")

            except Exception as exc:
                print(f"Unexpected error: {type(exc).__name__}: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FastAPI Ollama Client")

    parser.add_argument(
        "--question",
        "-q",
        type=str,
        help="Question to ask",
    )

    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use. Default: {DEFAULT_MODEL}",
    )

    parser.add_argument(
        "--url",
        "-u",
        type=str,
        default=DEFAULT_BASE_URL,
        help=f"Server URL. Default: {DEFAULT_BASE_URL}",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Optional bearer token for authenticated APIs",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Read timeout in seconds. Default: 120",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.interactive:
            asyncio.run(
                interactive_client(
                    base_url=args.url,
                    model=args.model,
                    token=args.token,
                    timeout_seconds=args.timeout,
                )
            )
            return 0

        if args.question:
            answer = asyncio.run(
                test_client(
                    question=args.question,
                    model=args.model,
                    base_url=args.url,
                    token=args.token,
                    timeout_seconds=args.timeout,
                )
            )
            return 0 if answer else 1

        question = input("Enter your question: ").strip()
        if not question:
            print("No question provided. Use --help for usage info.")
            return 1

        answer = asyncio.run(
            test_client(
                question=question,
                model=args.model,
                base_url=args.url,
                token=args.token,
                timeout_seconds=args.timeout,
            )
        )

        return 0 if answer else 1

    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())