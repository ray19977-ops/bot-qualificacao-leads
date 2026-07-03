from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app

app = FastAPI(title="Rai Bot")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    # Stub — a integração com o LLM entra na INFRA-04
    return ChatResponse(
        session_id=request.session_id,
        reply="[stub] Recebi sua mensagem. A lógica conversacional ainda não foi conectada.",
    )


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
