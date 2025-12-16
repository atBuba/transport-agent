from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- ИМПОРТ 1
from pydantic import BaseModel
import uvicorn
from agent_service import AgentService

# --- Инициализация сервиса ---
agent_service = AgentService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте сервера"""
    await agent_service.initialize()
    yield

app = FastAPI(title="MCP Agent API", lifespan=lifespan)

# --- НАСТРОЙКА CORS (ОБЯЗАТЕЛЬНО ДЛЯ БРАУЗЕРА) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить всем (для локальной разработки ок)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Модели ---
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

# --- Маршруты ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = await agent_service.chat(request.message, request.session_id)
        return ChatResponse(response=answer, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    agent_service.clear_history(session_id)
    return {"status": "ok", "message": f"История сессии {session_id} очищена"}

@app.get("/health")
async def health():
    is_ready = agent_service.agent_executor is not None
    return {"status": "ok", "agent_ready": is_ready}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)
