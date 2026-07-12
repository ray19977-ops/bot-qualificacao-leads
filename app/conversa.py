"""Lógica conversacional: monta o system prompt e gera as respostas do bot.

O conteúdo do prompt vive em config/system_prompt.md (Arquitetura Seção
10) — este módulo só o carrega e repassa o histórico ao llm_client.
"""

import json
from pathlib import Path

from app import llm_client

_RAIZ = Path(__file__).resolve().parent.parent
_CAMINHO_SYSTEM_PROMPT = _RAIZ / "config" / "system_prompt.md"
_CAMINHO_CAMPOS = _RAIZ / "config" / "campos_qualificacao.json"

# Marcador no system_prompt.md substituído pela lista renderizada dos
# campos de campos_qualificacao.json — adicionar/remover campo é só
# editar o JSON, sem tocar em código nem no texto do prompt
_MARCADOR_CAMPOS = "{{CAMPOS_QUALIFICACAO}}"

# Primeira mensagem "user" de toda sessão (INT-01): o frontend pede a
# abertura ao carregar a página e o lead nunca vê este texto. O system
# prompt instrui o bot a gerar a mensagem de boas-vindas ao recebê-lo.
GATILHO_ABERTURA = "[INICIAR_CONVERSA]"


def _renderizar_campos() -> str:
    dados = json.loads(_CAMINHO_CAMPOS.read_text(encoding="utf-8"))
    linhas = []
    for numero, campo in enumerate(dados["campos"], start=1):
        linhas.append(
            f"{numero}. **{campo['nome']}** — {campo['descricao']}\n"
            f"   Como coletar: {campo['orientacao_coleta']}\n"
            f"   Se não coletado, registre como: \"{campo['registro_se_nao_coletado']}\""
        )
    return "\n".join(linhas)


def carregar_system_prompt() -> str:
    # Lido a cada resposta: editar o prompt não exige reiniciar o servidor
    prompt = _CAMINHO_SYSTEM_PROMPT.read_text(encoding="utf-8")
    return prompt.replace(_MARCADOR_CAMPOS, _renderizar_campos())


def responder(historico: list[dict]) -> str:
    """Gera a próxima resposta do bot para o histórico da sessão.

    Levanta LLMUnavailableError (via llm_client) se o modelo estiver
    indisponível — o chamador responde com a mensagem de fallback.
    """
    return llm_client.complete(historico, system=carregar_system_prompt())
