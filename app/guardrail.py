"""Verificação de guardrail pós-resposta (Arquitetura Seção 9, risco 2).

Segunda camada de proteção do RF-06, independente do prompt: inspeciona
a resposta do LLM antes do envio ao lead e intercepta vazamentos de
preço/prazo. Valor monetário só é violação quando o número não foi dito
pelo próprio lead (o bot pode ecoar o orçamento informado ao
recapitular); promessa de prazo de entrega é violação sempre — o único
prazo permitido, o retorno "em até 2 dias úteis", não casa com os
padrões de promessa abaixo.
"""

import re

# A resposta substituta quando um vazamento é interceptado vive em
# config/identidade.json ("guardrail_segura") — este módulo só detecta.

_DINHEIRO = re.compile(
    r"R\$\s*\d[\d.,]*|\b\d[\d.,]*\s*(?:mil\s+)?(?:reais|conto)\b",
    re.IGNORECASE,
)

_PROMESSA_PRAZO = re.compile(
    r"\bfica(?:rá|ria)?\s+pronto\s+em\b"
    r"|\bconsigo\s+(?:fazer|entregar|terminar)\s+em\b"
    r"|\bte\s+entrego\s+em\b"
    r"|\bentregamos\s+em\b"
    r"|\bleva\s+(?:s[óo]\s+|apenas\s+|uns\s+|cerca\s+de\s+)?\d+\s*(?:dias?|semanas?|m[eê]s(?:es)?)\b"
    r"|\bem\s+\d+\s*(?:dias?|semanas?|m[eê]s(?:es)?)\s+(?:fica|est[áa]|estar[áa]|t[áa])\s+pronto\b",
    re.IGNORECASE,
)


def _nucleos_numericos(texto: str) -> set[str]:
    return {re.sub(r"\D", "", trecho) for trecho in re.findall(r"\d[\d.,]*", texto)}


def detectar_vazamento(resposta: str, historico: list[dict]) -> str | None:
    """Retorna o trecho que viola o guardrail, ou None se a resposta é segura."""
    promessa = _PROMESSA_PRAZO.search(resposta)
    if promessa:
        return promessa.group(0)

    numeros_do_lead: set[str] = set()
    for mensagem in historico:
        if mensagem["role"] == "user":
            numeros_do_lead |= _nucleos_numericos(mensagem["content"])

    for valor in _DINHEIRO.finditer(resposta):
        nucleo = re.sub(r"\D", "", valor.group(0))
        if nucleo and nucleo not in numeros_do_lead:
            return valor.group(0)
    return None
