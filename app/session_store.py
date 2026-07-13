"""Gerenciamento de sessão em memória (Arquitetura Seção 4, passo 5, e Seção 7).

Histórico de conversa por `session_id`, mantido apenas na memória do
processo — sem disco nem banco. Reiniciar o servidor apaga todas as
sessões, por decisão de arquitetura (RULES.md, Seção 3: "Sem banco").
"""

_sessions: dict[str, list[dict]] = {}

# Sessões encerradas pelo teto de turnos (CONV-21) — mensagens novas
# nessas sessões recebem a resposta padrão de encerramento, sem reabrir
_encerradas: set[str] = set()


def append_message(session_id: str, role: str, content: str) -> None:
    """Acrescenta uma mensagem ao histórico da sessão, criando-a se necessário.

    `role` segue o formato do Messages API: "user" ou "assistant".
    """
    _sessions.setdefault(session_id, []).append(
        {"role": role, "content": content}
    )


def get_history(session_id: str) -> list[dict]:
    """Retorna uma cópia do histórico da sessão, pronta para o llm_client.

    Sessão inexistente retorna lista vazia — primeira mensagem da conversa.
    """
    return list(_sessions.get(session_id, []))


def marcar_encerrada(session_id: str) -> None:
    """Marca a sessão como encerrada — novas mensagens não a reabrem."""
    _encerradas.add(session_id)


def esta_encerrada(session_id: str) -> bool:
    return session_id in _encerradas


def clear_session(session_id: str) -> None:
    """Descarta o histórico e o estado de uma sessão encerrada."""
    _sessions.pop(session_id, None)
    _encerradas.discard(session_id)
