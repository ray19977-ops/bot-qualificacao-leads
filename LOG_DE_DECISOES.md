# LOG DE DECISÕES — Bot de Qualificação de Leads

> **Nota desta reconstrução (2026-07-23):** este log foi reconstruído a
> partir do chat original do projeto e começa na entrada LOG-003. As
> entradas LOG-001 e LOG-002, existentes no processo original, não foram
> recuperadas nesta sessão — se localizadas, devem ser inseridas acima
> da LOG-003 mantendo a numeração.

---

### LOG-003 — 2026-07-03 — Gate 2 — Aprovado

**Resumo:** Arquitetura técnica validada e aprovada para
seguir para execução do backlog.

**O que foi validado:**

- LLM de operação escolhido: Claude Haiku 4.5
  (claude-haiku-4-5-20251001)
- Stack completa: Python 3.14 + FastAPI + HTML/JS puro
- Armazenamento: sem banco — histórico em memória de sessão
- Deploy: Render.com tier gratuito
- Custo estimado: R$8,40/mês (83% de folga do limite de R$50)
- Viabilidade dentro de orçamento e prazo (5 dias) confirmada
- Todos os requisitos do PRD com solução técnica correspondente
- Pontos de extensão para reaproveitamento identificados

**Critérios cumpridos antes da aprovação:**

- Comparação honesta de provedores de LLM (Haiku 4.5 vs
  Gemini 2.5 Flash) com justificativa documentada
- Custo operacional calculado com premissa explícita
- Stack factível para desenvolvedor iniciante no prazo definido
- Distinção entre LLM de construção (Fable 5 via Claude Code)
  e LLM de operação (Haiku 4.5) documentada

**Artefato aprovado:** 03_ARQUITETURA_TECNICA.md v1.0

---

### LOG-004 — 2026-07-03 — Produto Conversacional — handoff

**Resumo:** PRD aprovado (Gate 1) entregue ao Especialista 04
para desenho da experiência conversacional, em paralelo ao
Especialista 03 de Arquitetura.

**O que foi entregue no handoff:**

- 02_PRD.md aprovado (Gate 1 com validação do cliente/decisor)
- 01_CONTEXTO_NEGOCIO.md para referência de tom de marca e
  perfil do usuário final
- Informação adicional validada no Gate 1: resumo para o
  freelancer exibido na interface web em área separada
- Canal de aquisição de leads: Workana

**O que marcou essa transição:**

Saída da fase de especificação técnica (infraestrutura, backend,
stack) para o desenho da experiência de conversa — fluxos de
qualificação, casos de teste, tom de voz, estratégia de
desambiguação, guardrails comportamentais e critérios de
transferência humana.

**Conteúdo formal entregue (04_PRODUTO_CONVERSACIONAL.md):**

- Persona do bot: "Rai Bot", automação de qualificação do Rai
- 15 intents mapeados com fluxos completos
- Estratégia de desambiguação (2 tentativas por campo,
  sem 3ª insistência)
- 5 casos de teste cobrindo caminho feliz, ambiguidade,
  fora de escopo, loop e transferência humana
- Dependências técnicas identificadas para o Arquiteto validar
- 3 guardrails obrigatórios: não prometer prazo/preço,
  não simular humano, não coletar dado excedente

**Artefato gerado:** 04_PRODUTO_CONVERSACIONAL.md
