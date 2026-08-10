from fastapi import FastAPI, HTTPException

from app.models import ChatRequest, ChatResponse
from app.runtime import JarvisRuntime
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="JARVIS Developer API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = JarvisRuntime()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "jarvis",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = runtime.run(request.message)

        plan = response["plan"]

        return ChatResponse(
            message=request.message,
            plan=plan.model_dump() if plan else None,
            results=response["results"],
            context=response["context"].debug()
            if response["context"]
            else None,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
        
@app.post("/api/chat/events")
def chat_events(request: ChatRequest):
    try:
        response, events = runtime.run_with_events(request.message)
        return {
            "response": response,
            "events": [
                event.model_dump()
                for event in events
            ],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
        