from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app
from app import conversa, guardrail, llm_client, session_store

app = FastAPI(title="Rai Bot")

# Mensagem amigável quando o LLM falha após timeout/retry (Arquitetura
# Seção 7 e Seção 9, risco 5) — o lead nunca vê o erro cru
FALLBACK_MESSAGE = (
    "Tive uma instabilidade técnica aqui do meu lado. Pode reenviar sua "
    "última mensagem em alguns instantes? Se preferir, deixe seu nome e "
    "e-mail ou WhatsApp que o Rai entra em contato com você."
)

# Teto de turnos por sessão — salvaguarda de custo (CONV-21, Arquitetura
# Seção 9, risco 3). 1 turno = 1 mensagem do lead + 1 resposta do bot;
# o gatilho interno de abertura não conta.
LIMITE_TURNOS = 20

MENSAGEM_LIMITE_TURNOS = (
    "A gente já trocou bastante mensagem por aqui, então vou fechar esta "
    "conversa pra não tomar mais o seu tempo. Tudo o que você me contou "
    "já vai organizado pro Rai dar continuidade — se você deixou um "
    "contato, ele te retorna por lá; se não, é só voltar aqui pra "
    "retomar numa nova conversa. Obrigado pelo papo!"
)

MENSAGEM_SESSAO_ENCERRADA = (
    "Esta conversa já foi encerrada e o que você me contou seguiu pro "
    "Rai. Pra começar uma conversa nova, é só recarregar a página. "
    "Obrigado!"
)


def _turnos_do_lead(session_id: str) -> int:
    return sum(
        1
        for mensagem in session_store.get_history(session_id)
        if mensagem["role"] == "user"
        and mensagem["content"] != conversa.GATILHO_ABERTURA
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
    # Sessão encerrada pelo teto de turnos não reabre (CONV-21)
    if session_store.esta_encerrada(request.session_id):
        return ChatResponse(
            session_id=request.session_id, reply=MENSAGEM_SESSAO_ENCERRADA
        )

    mensagem = request.message.strip()
    if not mensagem:
        if session_store.get_history(request.session_id):
            raise HTTPException(status_code=422, detail="mensagem vazia")
        # Sessão nova sem texto: o frontend está pedindo a abertura (INT-01)
        mensagem = conversa.GATILHO_ABERTURA

    session_store.append_message(request.session_id, "user", mensagem)

    # Teto de turnos atingido: encerramento controlado, sem chamada ao
    # LLM de conversa — gera o resumo com o que foi coletado até aqui
    if _turnos_do_lead(request.session_id) >= LIMITE_TURNOS:
        session_store.marcar_encerrada(request.session_id)
        reply = MENSAGEM_LIMITE_TURNOS
        # Consistência com a CONV-20: texto fixo também passa pelo guardrail
        if guardrail.detectar_vazamento(
            reply, session_store.get_history(request.session_id)
        ):
            reply = guardrail.MENSAGEM_SEGURA
        session_store.append_message(request.session_id, "assistant", reply)
        try:
            resumo = conversa.gerar_resumo_estruturado(
                session_store.get_history(request.session_id)
            )
        except llm_client.LLMUnavailableError:
            resumo = None
        return ChatResponse(
            session_id=request.session_id, reply=reply, resumo=resumo
        )

    try:
        reply = conversa.responder(session_store.get_history(request.session_id))
        # Segunda camada do RF-06 (CONV-20): intercepta vazamento de
        # preço/prazo antes que a resposta chegue ao lead
        vazamento = guardrail.detectar_vazamento(
            reply, session_store.get_history(request.session_id)
        )
        if vazamento is not None:
            reply = guardrail.MENSAGEM_SEGURA
    except llm_client.LLMUnavailableError:
        reply = FALLBACK_MESSAGE

    # Fim da qualificação: remove o marcador técnico do texto exibido e
    # gera o resumo estruturado ao freelancer (CONV-19 / RF-03 / RF-05)
    resumo = None
    if conversa.MARCADOR_FIM in reply:
        reply = reply.replace(conversa.MARCADOR_FIM, "").strip()
        session_store.append_message(request.session_id, "assistant", reply)
        try:
            resumo = conversa.gerar_resumo_estruturado(
                session_store.get_history(request.session_id)
            )
        except llm_client.LLMUnavailableError:
            resumo = None  # o lead não é afetado; o resumo fica indisponível
    else:
        session_store.append_message(request.session_id, "assistant", reply)

    return ChatResponse(session_id=request.session_id, reply=reply, resumo=resumo)


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
