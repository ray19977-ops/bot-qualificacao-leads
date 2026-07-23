# Bot de Qualificação de Leads

Automação de qualificação de leads via chat web: conversa com potenciais
clientes, coleta os dados essenciais do projeto em poucos minutos e entrega
um resumo estruturado para o freelancer dar continuidade. O bot nunca finge
ser humano e nunca informa preço ou prazo — isso fica sempre a cargo do
freelancer.

**Stack:** Python 3.14 · FastAPI · HTML/CSS/JS puro (frontend estático,
sem framework) · Claude Haiku 4.5 (LLM de operação) · sem banco de dados —
o histórico de cada conversa vive em memória, por sessão.

## Pré-requisitos

- Python 3.14
- Uma chave de API da Anthropic (console.anthropic.com) para o Claude
  Haiku 4.5 — **use uma chave separada** de qualquer chave usada em
  ferramentas de construção/desenvolvimento (Claude Code, etc.)

## Setup local

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd bot-qualificacao-leads

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar as variáveis de ambiente
cp .env.example .env
# Editar .env e preencher ANTHROPIC_API_KEY com sua chave

# 5. Rodar o servidor
uvicorn app.main:app --reload
```

O servidor sobe em `http://127.0.0.1:8000`. Abra essa URL no navegador
para conversar com o bot.

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `ANTHROPIC_API_KEY` | Sim | Chave de operação do bot (chamadas ao Claude Haiku 4.5). Sem ela o servidor não sobe. |
| `TEST_LOG_MODE` | Não (default `false`) | `true` grava um log local temporário das conversas, para inspeção durante testes. Manter `false` em produção. |

## Adaptando para um novo cliente

Trocar o bot de cliente/projeto é só editar os arquivos em `config/` —
**nenhum código Python precisa ser tocado.** Depois de editar, reinicie o
servidor (exceto `system_prompt.md` e `campos_qualificacao.json`, que são
lidos a cada resposta e não exigem reinício).

| Arquivo | O que controla |
|---|---|
| `config/identidade.json` | Nome do bot, nome do freelancer, subtítulo, letra do avatar, descrição do serviço, e os textos fixos de fallback/limite de turnos/sessão encerrada/guardrail. Os textos aceitam os placeholders `{nome_bot}`, `{nome_freelancer}`, `{subtitulo}`, `{letra_avatar}` e `{descricao_servico}`. Também define o teto de turnos por sessão (`parametros.limite_turnos`). |
| `config/system_prompt.md` | A persona do bot, o tom de voz, os guardrails de conversa e as instruções de abertura/encerramento — o system prompt enviado ao LLM. |
| `config/campos_qualificacao.json` | Os campos que o bot coleta do lead (o que é, como coletar, o que registrar se o lead não responder). Adicionar ou remover um campo aqui já atualiza automaticamente o prompt e o schema do resumo estruturado — sem editar código. |

## Estrutura de pastas

```
app/             Backend FastAPI
  main.py          Rotas HTTP (/health, /config, /chat) e orquestração do fluxo
  conversa.py       Monta o system prompt e gera as respostas do bot
  guardrail.py      Segunda camada de proteção: intercepta vazamento de preço/prazo
  identidade.py     Carrega config/identidade.json na subida do servidor
  llm_client.py     Wrapper das chamadas ao Claude Haiku 4.5
  session_store.py  Histórico de conversa em memória, por sessão
  config.py         Carrega e valida as variáveis de ambiente (.env)
config/          Arquivos editáveis por cliente (ver seção acima)
static/          Frontend: HTML/CSS/JS puro, servido pelo próprio FastAPI
tests/checklists/  Protocolos de teste manual (ver seção abaixo)
```

## Testes

O projeto não tem uma suíte automatizada — a validação é feita por
checklists manuais em `tests/checklists/`, um arquivo por rodada de teste
(ex.: `TEST-08_usuarios_reais.md`, `TEST-10_multidispositivo.md`). Cada
checklist documenta o critério de aceite, o roteiro de execução e o
resultado da rodada. Para validar uma mudança, abra o checklist relevante
e siga o roteiro descrito nele com o servidor local rodando.

## Deploy

Ver ENTREGA-03 no backlog técnico (`05_BACKLOG_TECNICO.md`).
