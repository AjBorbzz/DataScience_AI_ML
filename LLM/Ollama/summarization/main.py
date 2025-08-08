from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    model: str = "llama3"  # Default model
    stream: bool = False
    
class QuestionResponse(BaseModel):
    answer: str
    model: str
    tokens_used: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    ollama_available: bool
    available_models: list

# Global HTTP client
http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global http_client
    http_client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout for long responses
    logger.info("FastAPI server started with Ollama integration")
    yield
    # Shutdown
    await http_client.aclose()
    logger.info("FastAPI server shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Ollama API Server",
    description="A FastAPI server that interfaces with Ollama for AI model interactions",
    version="1.0.0",
    lifespan=lifespan
)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"

async def check_ollama_health():
    """Check if Ollama is running and accessible"""
    try:
        response = await http_client.get(f"{OLLAMA_BASE_URL}/api/tags")
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return False, None

async def get_ollama_response(question: str, model: str = "llama3", stream: bool = False):
    """Send question to Ollama and get response"""
    try:
        payload = {
            "model": model,
            "prompt": question,
            "stream": stream
        }
        
        response = await http_client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", ""), result.get("total_duration", 0)
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        logger.error(f"Error calling Ollama API: {e}")
        return None, None

# API Routes
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Ollama FastAPI Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ask": "/ask",
            "models": "/models"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    is_healthy, models_data = await check_ollama_health()
    available_models = []
    
    if is_healthy and models_data:
        available_models = [model["name"] for model in models_data.get("models", [])]
    
    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        ollama_available=is_healthy,
        available_models=available_models
    )

@app.get("/models")
async def get_available_models():
    """Get list of available Ollama models"""
    is_healthy, models_data = await check_ollama_health()
    
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Ollama service is not available")
    
    return models_data

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Main endpoint to ask questions to Ollama model"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Check if Ollama is available
    is_healthy, _ = await check_ollama_health()
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Ollama service is not available")
    
    # Get response from Ollama
    answer, duration = await get_ollama_response(
        request.question, 
        request.model, 
        request.stream
    )
    
    if answer is None:
        raise HTTPException(status_code=500, detail="Failed to get response from Ollama")
    
    return QuestionResponse(
        answer=answer,
        model=request.model,
        tokens_used=duration  # Using duration as a proxy for complexity
    )

@app.post("/ask-stream")
async def ask_question_stream(request: QuestionRequest):
    """Streaming endpoint for real-time responses"""
    from fastapi.responses import StreamingResponse
    import json
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    async def generate_stream():
        try:
            payload = {
                "model": request.model,
                "prompt": request.question,
                "stream": True
            }
            
            async with http_client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield f"data: {json.dumps({'text': data['response']})}\n\n"
                                if data.get("done", False):
                                    yield f"data: {json.dumps({'done': True})}\n\n"
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    yield f"data: {json.dumps({'error': 'Ollama API error'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error on {request.url}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error on {request.url}: {str(exc)}")
    return {"error": "Internal server error", "status_code": 500}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )