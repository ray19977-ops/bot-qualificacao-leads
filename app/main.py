from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app
from app import session_store

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
    session_store.append_message(request.session_id, "user", request.message)

    # Stub — a resposta passa a vir do llm_client com o histórico da
    # sessão quando a lógica conversacional (Bloco 3) for conectada
    reply = "[stub] Recebi sua mensagem. A lógica conversacional ainda não foi conectada."

    session_store.append_message(request.session_id, "assistant", reply)
    return ChatResponse(session_id=request.session_id, reply=reply)


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
