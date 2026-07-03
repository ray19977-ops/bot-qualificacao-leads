"""Carrega e valida as variáveis de ambiente do projeto (.env)."""

import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

TEST_LOG_MODE = os.getenv("TEST_LOG_MODE", "false").strip().lower() == "true"

if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "ANTHROPIC_API_KEY ausente. Copie o arquivo .env.example para .env "
        "na raiz do projeto e preencha a chave de operação do bot "
        "(chave separada da usada no Claude Code — ver RULES.md, Seção 4)."
    )
