# RULES — Constituição operacional do projeto

## 1. Identidade do projeto

| Campo | Valor |
|---|---|
| Nome do projeto | Bot de Qualificação de Leads Freelancer |
| Cliente | Próprio freelancer (projeto de portfólio) |
| Freelancer responsável | Rai |
| Data de início | 2026-07-03 |
| Versão deste documento | v1.0 |
| Última atualização | 2026-07-03 por Coordenador |

## 2. Contexto de negócio

Freelancer de tecnologia iniciando no mercado de automação de
chatbots perde tempo em triagens manuais repetitivas com clientes
potenciais. O bot qualifica leads em até 5 minutos via interface
web, coleta 7 campos essenciais do projeto e entrega resposta
personalizada ao lead e resumo estruturado ao freelancer.

**Stakeholders:**
- Decisor final do projeto: Rai (freelancer)
- Quem vai operar o bot no dia a dia: Rai
- Canal do MVP: Interface web de demonstração
- Canal futuro (Fase 2): WhatsApp Business
- Canal de aquisição de leads atual: Workana

## 3. Stack técnica mandatória

| Componente | Escolha |
|---|---|
| LLM de construção | Claude Code + Fable 5 |
| LLM de operação do bot | Claude Haiku 4.5 (claude-haiku-4-5-20251001) |
| Linguagem | Python 3.14 |
| Backend | FastAPI |
| Interface web | HTML/CSS/JS puro (single-page) |
| Armazenamento | Sem banco — histórico em memória de sessão |
| Deploy | Render.com tier gratuito |
| Nome do bot | Rai Bot |

## 4. Regras de engenharia

- Responsabilidade única por módulo
- Nenhuma chave de API em código-fonte — tudo via .env
- Chave de operação (ANTHROPIC_API_KEY) separada da chave
  de construção usada no Claude Code
- Commits no padrão: feat/fix/docs/test/refactor/chore
- Branches para cada bloco do backlog

## 5. Regras de execução do Fable 5 via Claude Code

1. Executar apenas tarefas com status
   "aprovado-para-execucao" no 05_BACKLOG_TECNICO.md
2. Uma tarefa por sessão — parar e reportar ao concluir
3. Reportar ao concluir: arquivos alterados + como validar
4. Parar e perguntar se encontrar ambiguidade não coberta
   por este RULES.md
5. Nunca deletar arquivos sem confirmação explícita
6. Nunca adicionar dependências fora do requirements.txt
   definido na arquitetura sem consultar o freelancer

## 6. Regras de qualidade

- Custo operacional máximo: R$ 50/mês
- Custo estimado real: R$ 8,40/mês (80 conversas)
- Tempo de resposta do bot: menos de 15s (timeout definido)
- Carregamento da interface: menos de 3s (RF-07)
- Zero violações dos 3 guardrails comportamentais por
  100 conversas (RF-06)

## 7. Campos obrigatórios de qualificação (os 7 do PRD)

1. Tipo de negócio / segmento do cliente final
2. Canal desejado (WhatsApp, site, outro)
3. Problema ou objetivo principal
4. Faixa de orçamento aproximada
5. Prazo desejado pelo lead
6. Volume estimado de atendimentos
7. Dado de contato (nome + e-mail ou WhatsApp)

## 8. Registro de decisões relevantes

| Data | Decisão | Aprovado por |
|---|---|---|
| 2026-07-03 | Gate 1 aprovado — PRD v1.0 | Rai |
| 2026-07-03 | Gate 2 aprovado — Arquitetura v1.0 | Coordenador |
| 2026-07-03 | Nome do bot: Rai Bot | Rai |
| 2026-07-03 | LLM operação: Claude Haiku 4.5 | Coordenador |
| 2026-07-03 | Deploy: Render.com tier gratuito | Coordenador |
| 2026-07-03 | Modo log testes: TEST_LOG_MODE via .env | Coordenador |
| 2026-07-03 | Python 3.14 no lugar de 3.12 (única versão na máquina; stack compatível) | Rai |