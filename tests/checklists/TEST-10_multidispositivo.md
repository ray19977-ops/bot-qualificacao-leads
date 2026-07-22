# TEST-10 — Teste de acesso multi-dispositivo/navegador

> Reconstruído a partir de `05_BACKLOG_TECNICO.md` (linha 94) e `02_PRD.md` (RF-07).
> Status no backlog: pendente. Dependências: UI-01, UI-03 (concluídas).

## Critério de aceite (backlog)

Interface carrega em até 3 segundos e mantém o histórico da conversa durante a
sessão ativa, nos 3 ambientes testados (RF-07).

**Interpretação documentada (política de QA):** o RF-07 completo menciona "link
web público", mas o deploy público é ENTREGA-03 (bloqueada por todos os TEST-XX).
Este teste valida carregamento e histórico via **rede local**; a parte "link
público carrega em até 3s" será revalidada na ENTREGA-03.

## Setup

- [ ] Servidor no ar: `uvicorn app.main:app --host 0.0.0.0 --port 8123`
      (a partir da raiz do repo, venv ativa, `.env` com `ANTHROPIC_API_KEY`)
- [ ] IP local anotado (`ipconfig` → IPv4 da rede Wi-Fi): `http://<IP>:8123`
- [ ] Firewall do Windows liberado para o Python na porta 8123 (testar acesso
      de um segundo dispositivo antes de começar a medir)
- [ ] `TEST_LOG_MODE=true` no `.env` se quiser guardar transcrições (desligar depois)

## Matriz de ambientes (3 distintos)

| # | Dispositivo | Navegador |
|---|---|---|
| A | PC Windows (host) | Edge |
| B | PC Windows (host) | Brave |
| C | Celular (via ngrok) | navegador padrão |

## Roteiro por ambiente (repetir em A, B e C)

1. [ ] Abrir `http://<IP>:8123` e **medir o tempo de carregamento** até a
       interface utilizável (cronômetro ou aba Network do DevTools).
       Registrar o valor. **Aceite: ≤ 3s.**
2. [ ] Enviar uma mensagem inicial e receber resposta do bot.
3. [ ] Trocar pelo menos 5 turnos de conversa. Verificar:
       - [ ] Histórico visível completo, em ordem, sem mensagens sumindo
       - [ ] Bot mantém contexto (não repergunta o que já foi respondido)
4. [ ] Verificar isolamento de sessão: a conversa deste ambiente **não**
       aparece nem mistura com a dos outros dispositivos abertos em paralelo.
5. [ ] Recarregar a página: nova sessão (histórico zera) — comportamento
       esperado conforme UI-03 ("reload gera novo session_id").
6. [ ] Nos ambientes B e C (acesso via IP, contexto não-seguro): observar que o
       fallback de `crypto.randomUUID` (`static/app.js:13`) funciona — a sessão
       acumula histórico normalmente e não há erro no console.

## Registro de resultados

| Ambiente | Tempo de carga | ≤ 3s? | Histórico mantido? | Isolamento OK? | Reload zera corretamente? |
|---|---|---|---|---|---|
| A — Edge (PC) | 2,12s (DevTools/Network) | ✅ | ✅ | ✅ | ✅ |
| B — Brave (PC) | 1,70s (DevTools/Network) | ✅ | ✅ | ✅ | ✅ |
| C — Celular (via ngrok) | 2–3s (cronometrado) | ✅ | ✅ | ✅ | ✅ |

### Detalhes por critério

- **Tempo de carga:** os 3 ambientes dentro do limite de 3s. Edge e Brave
  medidos via DevTools (2,12s e 1,70s); celular cronometrado manualmente em
  2–3s (acesso remoto via ngrok, latência de rede adicional em relação ao
  PC na rede local).
- **Histórico mantido:** confirmado nos 3 — mensagens visíveis em ordem,
  sem sumiço, bot mantendo contexto da conversa.
- **Isolamento entre sessões:** teste com os 3 ambientes abertos
  simultaneamente (Edge + Brave no PC + celular via ngrok), conversas em
  paralelo sem mistura de histórico entre eles.
- **Reload zerando corretamente:** testado nos 3 ambientes — nova sessão
  (`session_id` novo, histórico zerado) ao recarregar, conforme UI-03, sem
  falhas.

## Aprovação

- **Veredito: aprovado** (21/07/2026). Todos os 4 critérios (carga ≤3s,
  histórico mantido, isolamento entre sessões, reload zerando corretamente)
  confirmados nos 3 ambientes distintos exigidos pelo RF-07 (via rede
  local/ngrok — validação do link público fica para ENTREGA-03).
