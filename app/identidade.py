"""Identidade, mensagens fixas e parâmetros configuráveis por cliente.

O conteúdo vive em config/identidade.json (Arquitetura Seção 10):
trocar de cliente não exige tocar em código Python. Carregado uma vez
na subida do servidor — editar o JSON exige reiniciar. Os textos de
mensagens aceitam placeholders com as chaves da seção "identidade"
(ex.: {nome_freelancer}).
"""

import json
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent
_CAMINHO = _RAIZ / "config" / "identidade.json"

_dados = json.loads(_CAMINHO.read_text(encoding="utf-8"))

IDENTIDADE: dict = _dados["identidade"]
PARAMETROS: dict = _dados["parametros"]

MENSAGENS: dict = {
    chave: texto.format(**IDENTIDADE)
    for chave, texto in _dados["mensagens"].items()
}


def config_publica() -> dict:
    """Parte da configuração exposta ao frontend via GET /config."""
    return {
        "nome_bot": IDENTIDADE["nome_bot"],
        "subtitulo": IDENTIDADE["subtitulo"],
        "letra_avatar": IDENTIDADE["letra_avatar"],
        "erro_rede": MENSAGENS["erro_rede"],
    }
