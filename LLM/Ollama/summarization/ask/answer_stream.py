import argparse
import asyncio
from typing import AsyncIterator

import httpx


async def stream_answer(
    question: str,
    model: str = "llama3",
    base_url: str = "http://localhost:8000",
    timeout_seconds: float = 300.0,
) -> None:
    """
    Stream an answer from a FastAPI endpoint.

    Expected server endpoint:
        POST /ask/stream

    Expected streaming format:
        plain text chunks
    """

    base_url = base_url.rstrip("/")

    timeout = httpx.Timeout(
        connect=5.0,
        read=timeout_seconds,
        write=10.0,
        pool=5.0,
    )

    payload = {
        "question": question,
        "model": model,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            f"{base_url}/ask/stream",
            json=payload,
        ) as response:
            response.raise_for_status()

            print("\nAnswer:\n", end="", flush=True)

            async for chunk in response.aiter_text():
                if chunk:
                    print(chunk, end="", flush=True)

            print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Streaming FastAPI Ollama Client")

    parser.add_argument(
        "--question",
        "-q",
        required=True,
        help="Question to ask",
    )

    parser.add_argument(
        "--model",
        "-m",
        default="llama3",
        help="Model to use",
    )

    parser.add_argument(
        "--url",
        "-u",
        default="http://localhost:8000",
        help="FastAPI server URL",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Read timeout in seconds",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        asyncio.run(
            stream_answer(
                question=args.question,
                model=args.model,
                base_url=args.url,
                timeout_seconds=args.timeout,
            )
        )
        return 0

    except httpx.HTTPStatusError as exc:
        print(f"\nHTTP error {exc.response.status_code}: {exc.response.text}")
        return 1

    except httpx.HTTPError as exc:
        print(f"\nHTTP client error: {exc}")
        return 1

    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())