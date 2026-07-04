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

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def complete(
    messages: list[dict],
    system: str | None = None,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """Envia o histórico da conversa ao modelo e retorna o texto da resposta.

    `messages` segue o formato do Messages API:
    [{"role": "user"|"assistant", "content": "..."}, ...]
    """
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system is not None:
        kwargs["system"] = system

    response = _client.messages.create(**kwargs)
    return "".join(
        block.text for block in response.content if block.type == "text"
    )
