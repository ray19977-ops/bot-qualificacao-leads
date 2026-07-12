from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app
from app import conversa, llm_client, session_store

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
    # Resumo estruturado do lead, enviado apenas ao final da conversa —
    # preenchido pela geração de resumo (CONV-19) e exibido no painel da UI-02
    resumo: dict | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    mensagem = request.message.strip()
    if not mensagem:
        if session_store.get_history(request.session_id):
            raise HTTPException(status_code=422, detail="mensagem vazia")
        # Sessão nova sem texto: o frontend está pedindo a abertura (INT-01)
        mensagem = conversa.GATILHO_ABERTURA

    session_store.append_message(request.session_id, "user", mensagem)

    try:
        reply = conversa.responder(session_store.get_history(request.session_id))
    except llm_client.LLMUnavailableError:
        reply = FALLBACK_MESSAGE

    session_store.append_message(request.session_id, "assistant", reply)
    return ChatResponse(session_id=request.session_id, reply=reply)


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
