"""Camada única de integração com o LLM (Arquitetura Seção 10).

Todo acesso ao modelo passa por este módulo. Trocar de modelo ou de
provedor exige alterar apenas este arquivo — a lógica conversacional
nunca importa o SDK diretamente.
"""

import anthropic

from app import config

# LLM de operação definido no RULES.md (Seção 3)
MODEL = "claude-haiku-4-5-20251001"

# Teto de tokens de saída por resposta do bot
MAX_TOKENS = 1024

# Timeout por chamada — RULES.md Seção 6: resposta do bot em menos de 15s
TIMEOUT_SECONDS = 15.0

# Uma tentativa extra em caso de instabilidade (Arquitetura Seção 7)
MAX_RETRIES = 1


class LLMUnavailableError(Exception):
    """Chamada ao LLM falhou mesmo após o retry — o chamador deve
    responder com a mensagem de fallback, nunca expor o erro cru."""


_client = anthropic.Anthropic(
    api_key=config.ANTHROPIC_API_KEY,
    timeout=TIMEOUT_SECONDS,
    max_retries=MAX_RETRIES,
)


def complete(
    messages: list[dict],
    system: str | None = None,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """Envia o histórico da conversa ao modelo e retorna o texto da resposta.

    `messages` segue o formato do Messages API:
    [{"role": "user"|"assistant", "content": "..."}, ...]

    Levanta LLMUnavailableError se a chamada falhar após timeout/retry.
    """
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system is not None:
        kwargs["system"] = system

    try:
        response = _client.messages.create(**kwargs)
    except anthropic.APIError as exc:
        raise LLMUnavailableError(str(exc)) from exc
    return "".join(
        block.text for block in response.content if block.type == "text"
    )


def extract_structured(
    messages: list[dict],
    tool: dict,
    system: str | None = None,
    max_tokens: int = MAX_TOKENS,
) -> dict:
    """Extrai dados estruturados da conversa via tool use forçado.

    `tool` é uma definição de ferramenta do Messages API (name,
    description, input_schema). O modelo é obrigado a respondê-la, o que
    garante retorno no formato do schema em 100% das chamadas.

    Levanta LLMUnavailableError se a chamada falhar após timeout/retry.
    """
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
        "tools": [tool],
        "tool_choice": {"type": "tool", "name": tool["name"]},
    }
    if system is not None:
        kwargs["system"] = system

    try:
        response = _client.messages.create(**kwargs)
    except anthropic.APIError as exc:
        raise LLMUnavailableError(str(exc)) from exc

    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise LLMUnavailableError("resposta sem bloco tool_use")
