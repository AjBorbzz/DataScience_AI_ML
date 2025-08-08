import asyncio
import httpx
import json
import sys
import argparse

async def test_client(question="What is the capital of France?", model="llama3", base_url="http://localhost:8000"):
    """Test client for the FastAPI Ollama server"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test health check
        print("Testing health check...")
        health_response = await client.get(f"{base_url}/health")
        print(f"Health: {health_response.json()}")
        
        # Test asking a question
        print(f"\nAsking question: '{question}'")
        question_data = {
            "question": question,
            "model": model
        }
        
        response = await client.post(f"{base_url}/ask", json=question_data)
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            return result['answer']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

async def interactive_client(base_url="http://localhost:8000", model="llama3"):
    """Interactive client that keeps asking for questions"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=== Interactive Ollama Client ===")
        print("Type 'quit', 'exit', or 'q' to stop")
        print("Type 'health' to check server health")
        print("Type 'models' to see available models")
        print("-" * 40)
        
        while True:
            try:
                question = input(f"\n[{model}] Enter your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if question.lower() == 'health':
                    health_response = await client.get(f"{base_url}/health")
                    print(f"Health: {health_response.json()}")
                    continue
                
                if question.lower() == 'models':
                    try:
                        models_response = await client.get(f"{base_url}/models")
                        print(f"Available models: {models_response.json()}")
                    except Exception as e:
                        print(f"Error getting models: {e}")
                    continue
                
                if not question:
                    print("Please enter a question!")
                    continue
                
                print(f"\nAsking: '{question}'")
                print("Thinking... (this may take a while)")
                
                question_data = {
                    "question": question,
                    "model": model
                }
                
                response = await client.post(f"{base_url}/ask", json=question_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"\nAnswer:\n{result['answer']}")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="FastAPI Ollama Client")
    parser.add_argument("--question", "-q", type=str, help="Question to ask")
    parser.add_argument("--model", "-m", type=str, default="llama3", help="Model to use (default: llama3)")
    parser.add_argument("--url", "-u", type=str, default="http://localhost:8000", help="Server URL")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        # Interactive mode
        asyncio.run(interactive_client(args.url, args.model))
    elif args.question:
        # Single question mode
        asyncio.run(test_client(args.question, args.model, args.url))
    else:
        # Default mode - ask for question input
        question = input("Enter your question: ").strip()
        if question:
            asyncio.run(test_client(question, args.model, args.url))
        else:
            print("No question provided. Use --help for usage info.")

if __name__ == "__main__":
    main()