# ENTREGA-03 — Deploy em ambiente público (Render.com)

## Critério de aceite (backlog / RF-07)

Link público carrega em até 3s de forma consistente, mesmo após
período de inatividade.

## Configuração do deploy (23/07/2026)

- **Serviço:** Web Service no Render.com, tier gratuito, criado
  manualmente pelo painel (backend FastAPI + frontend estático no
  mesmo serviço, como previsto na Arquitetura Seção 5). O repositório
  também contém um `render.yaml` equivalente, utilizável como
  Blueprint em recriações futuras do serviço.
- **Repositório conectado:** github.com/ray19977-ops/bot-qualificacao-leads,
  branch `main` (deploy automático a cada push).
- **URL pública:** https://bot-qualificacao-leads.onrender.com
- **`ANTHROPIC_API_KEY`:** configurada como variável de ambiente
  segura no painel do Render — nunca commitada nem exposta no frontend.
- **Mitigação de cold start (Arquitetura Seção 9, risco 1):** monitor
  do UptimeRobot pingando `GET /health` a cada 5 minutos, mantendo o
  serviço acordado no free tier (que hiberna após ~15 min de
  inatividade, com cold start de 30–60s).

## Medições (23/07/2026)

### Serviço acordado (verificação independente via curl)

| Checagem | Resultado |
|---|---|
| `GET /health` | HTTP 200 em 0,29s |
| `GET /` (página do chat) | HTTP 200 em 0,199s / 0,203s / 0,201s (3 medições) |
| `GET /config` | Identidade correta servida de `config/identidade.json` |
| `POST /chat` (abertura real) | Resposta do Haiku 4.5 em 1,79s — API key do painel validada ponta a ponta |

### Após período de inatividade (teste final do critério)

Acesso pelo navegador com o serviço em descanso e o UptimeRobot
ativo: **carregamento em 2,55s, com resposta correta do bot** —
dentro do teto de 3s. Primeira medição do dia (deploy recém-criado)
havia registrado 2,5s, consistente com o resultado final.

## Resultado

**APROVADO.** Todas as medições ficaram dentro do critério de ≤3s
(RF-07): ~0,2s com o serviço acordado e 2,55s no pior caso medido
(pós-inatividade, com o ping do UptimeRobot ativo).

Observação de operação: a consistência do tempo de resposta ao longo
do tempo pode ser acompanhada pelo gráfico de response time do
próprio monitor no painel do UptimeRobot.
