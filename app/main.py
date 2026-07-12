from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app
from app import llm_client, session_store

app = FastAPI(title="Rai Bot")

# Mensagem amigável quando o LLM falha após timeout/retry (Arquitetura
# Seção 7 e Seção 9, risco 5) — o lead nunca vê o erro cru
FALLBACK_MESSAGE = (
    "Tive uma instabilidade técnica aqui do meu lado. Pode reenviar sua "
    "última mensagem em alguns instantes? Se preferir, deixe seu nome e "
    "e-mail ou WhatsApp que o Rai entra em contato com você."
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _generate_reply(history: list[dict]) -> str:
    # Stub — passa a chamar llm_client.complete(history) quando a
    # lógica conversacional (Bloco 3) for conectada
    return "[stub] Recebi sua mensagem. A lógica conversacional ainda não foi conectada."


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    session_store.append_message(request.session_id, "user", request.message)

    try:
        reply = _generate_reply(session_store.get_history(request.session_id))
    except llm_client.LLMUnavailableError:
        reply = FALLBACK_MESSAGE

    session_store.append_message(request.session_id, "assistant", reply)
    return ChatResponse(session_id=request.session_id, reply=reply)


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
