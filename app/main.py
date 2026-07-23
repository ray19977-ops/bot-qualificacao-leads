from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config  # valida as variáveis de ambiente na subida do app
from app import conversa, guardrail, identidade, llm_client, session_store

app = FastAPI(title=identidade.IDENTIDADE["nome_bot"])

# Textos fixos e parâmetros por cliente vivem em config/identidade.json
# (ENTREGA-01): fallback de LLM indisponível (Arquitetura Seção 7 e
# Seção 9, risco 5), teto de turnos por sessão — salvaguarda de custo
# (CONV-21, Seção 9, risco 3; 1 turno = 1 mensagem do lead + 1 resposta
# do bot, o gatilho interno de abertura não conta) — e mensagens de
# encerramento.
FALLBACK_MESSAGE = identidade.MENSAGENS["fallback"]
LIMITE_TURNOS = identidade.PARAMETROS["limite_turnos"]
MENSAGEM_LIMITE_TURNOS = identidade.MENSAGENS["limite_turnos"]
MENSAGEM_SESSAO_ENCERRADA = identidade.MENSAGENS["sessao_encerrada"]


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


@app.get("/config")
def config_frontend() -> dict:
    # Identidade pública do bot para o frontend (nome, subtítulo, avatar)
    return identidade.config_publica()


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
            reply = identidade.MENSAGENS["guardrail_segura"]
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
            reply = identidade.MENSAGENS["guardrail_segura"]
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
        # Rede de segurança do RF-05 (CONV-24): fechamento em que o modelo
        # omitiu o marcador — gera o resumo estruturado mesmo assim
        if conversa.parece_fechamento(reply):
            try:
                resumo = conversa.gerar_resumo_estruturado(
                    session_store.get_history(request.session_id)
                )
            except llm_client.LLMUnavailableError:
                resumo = None

    return ChatResponse(session_id=request.session_id, reply=reply, resumo=resumo)


# Montado por último para não sobrepor /health e /chat
app.mount("/", StaticFiles(directory="static", html=True), name="static")
