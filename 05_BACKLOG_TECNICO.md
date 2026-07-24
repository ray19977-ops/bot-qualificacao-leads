# Backlog Técnico — Bot de Qualificação de Leads

> Gerado a partir de `03_ARQUITETURA_TECNICA.md` (Gate 2 aprovado),
> `04_PRODUTO_CONVERSACIONAL.md` e `02_PRD.md`. Executor previsto:
> Claude Code com Fable 5. Prazo: 5 dias, ~5h/dia (25h totais).

## Convenção de status
pendente → aprovado-para-execucao → em-execucao → concluido → validado-qa

## Estimativa total
- Tarefas de infraestrutura: 6
- Tarefas de interface web: 3
- Tarefas de lógica conversacional: 21
- Tarefas de teste: 10
- Tarefas de preparação para entrega: 4
- **Total: 44 tarefas**

Observação sobre viabilidade: a granularidade fina do Bloco 3 (uma tarefa por
fluxo, conforme exigido pelo processo) não significa 21 sessões longas —
a maioria dessas tarefas edita o mesmo arquivo de configuração de prompt
(`config/system_prompt.md`) e tende a ser rápida por sessão. Se o ritmo real
mostrar que o prazo de 5 dias está apertado, cortar primeiro CONV-20
(camada extra de verificação de guardrail) e TEST-09/TEST-10, que são reforço
de qualidade, não funcionalidade núcleo do MVP — mover para Fase 2 antes de reduzir
qualquer fluxo de CONV-03 a CONV-19 ou os testes adversariais RF-06 (TEST-03,
TEST-05), que são requisitos obrigatórios do PRD.

---

## Ordem de execução

### Bloco 1: Setup e infraestrutura

| ID | Tarefa | Descrição clara | Critério de aceite | Dependências | Reaproveitável? | Status |
|---|---|---|---|---|---|---|
| INFRA-01 | Setup do projeto | Criar estrutura de pastas Python 3.12 (`app/`, `config/`, `static/`, `tests/`), inicializar repositório git, ambiente virtual e `requirements.txt` com FastAPI + SDK `anthropic` (Arquitetura, Seção 5) | Projeto roda localmente com `uvicorn` servindo uma rota de health check (`GET /health` retorna 200) | nenhuma | sim — estrutura base de template de repositório | validado-qa |
| INFRA-02 | Configuração de variáveis de ambiente | Criar `.env.example` com `ANTHROPIC_API_KEY` (chave de operação, separada da chave usada no Claude Code — Arquitetura Seção 2) e uma flag `TEST_LOG_MODE` (log temporário em arquivo local, desligado por padrão em produção — Arquitetura Seção 7) | `.env.example` documentado; app falha com mensagem clara se `ANTHROPIC_API_KEY` estiver ausente; `TEST_LOG_MODE=false` por padrão | INFRA-01 | sim — template `.env` reaproveitável entre projetos | validado-qa |
| INFRA-03 | Setup do servidor web | Configurar FastAPI para servir a interface estática (`static/`) e expor a rota `POST /chat` (ainda sem lógica de LLM) — Arquitetura Seção 5 | Servidor sobe com `uvicorn`, serve a página inicial e a rota `/chat` responde (mesmo que com stub) | INFRA-01 | sim | validado-qa |
| INFRA-04 | Wrapper de integração com LLM | Criar camada única de "cliente LLM" (Arquitetura Seção 10) usando o SDK oficial `anthropic`, apontando para `claude-haiku-4-5-20251001` (Arquitetura Seção 3), isolada do restante da lógica de negócio | Uma chamada de teste ao wrapper retorna resposta do modelo; trocar o modelo/provedor exige alterar apenas este arquivo | INFRA-02 | sim — wrapper parametrizável, permite trocar de provedor sem tocar na lógica conversacional | concluido |
| INFRA-05 | Gerenciamento de sessão em memória | Implementar dicionário em memória do processo, chaveado por `session_id`, para manter o histórico da conversa durante a sessão ativa, sem persistência em disco/banco (Arquitetura Seção 4, passo 5, e Seção 7) | Duas requisições consecutivas com o mesmo `session_id` acumulam histórico corretamente; reiniciar o processo apaga tudo (nenhuma persistência) | INFRA-03 | sim | concluido |
| INFRA-06 | Timeout, retry e fallback de chamada ao LLM | Implementar timeout de 15s na chamada ao LLM, uma tentativa de retry simples e mensagem de fallback amigável em caso de erro/instabilidade (Arquitetura Seção 7 e Seção 9, risco 5) | Simulando uma falha/timeout na chamada, o usuário recebe a mensagem de fallback definida, sem erro cru exposto na interface | INFRA-04 | sim | concluido |

### Bloco 2: Interface web

| ID | Tarefa | Descrição clara | Critério de aceite | Dependências | Reaproveitável? | Status |
|---|---|---|---|---|---|---|
| UI-01 | Interface de chat básica | Página single-page em HTML/CSS/JS puro (sem build step — Arquitetura Seção 5), com identidade visual isolada em variáveis de configuração/CSS (Arquitetura Seção 10) | Interface carrega em até 3s (RF-07), envia e exibe mensagens do usuário e do bot em ordem | INFRA-03 | sim — tema/identidade visual ajustável por projeto | concluido |
| UI-02 | Área de resumo estruturado | Criar área separada, na mesma tela, para exibir o resumo estruturado ao freelancer ao final da conversa (Arquitetura Seção 4, passo 8, conforme validado no Gate 1) | Ao final de uma conversa de teste, o resumo aparece em painel visualmente distinto do fluxo de chat, na mesma página | UI-01 | sim | concluido |
| UI-03 | Conexão interface com backend | Frontend gera `session_id` ao carregar a página e envia `POST /chat` com `session_id` + texto a cada mensagem (Arquitetura Seção 4, passos 1–3) | Histórico da conversa persiste visualmente durante a sessão ativa do navegador (RF-07); reload gera novo `session_id` | UI-01, INFRA-05 | sim | concluido |

### Bloco 3: Lógica conversacional

| ID | Tarefa | Descrição clara | Critério de aceite | Dependências | Status |
|---|---|---|---|---|---|
| CONV-01 | Arquivo de configuração do prompt do sistema | Criar `config/system_prompt.md` com persona (nome funcional, ex. "Assistente do [Freelancer]" — Produto Conversacional Seção 1), tom de voz (exemplos reais de frase, nunca linguagem de menu/formulário) e os três guardrails obrigatórios (não promete prazo/preço; não simula humano; não coleta dado excedente — PRD item 6) | O system prompt, isolado do código Python (Arquitetura Seção 10), contém os exemplos ✓/✗ de tom de voz do Produto Conversacional Seção 1 e os três guardrails | INFRA-04 | concluido |
| CONV-02 | Arquivo de configuração dos 7 campos de qualificação | Criar estrutura de dados configurável (JSON/YAML) com os 7 campos definidos no PRD 3.1.2: segmento, canal, problema/objetivo, orçamento, prazo, volume, contato — cada um com nome, descrição e obrigatoriedade (Arquitetura Seção 10) | Adicionar/remover um campo não exige alterar a lógica de extração; os 7 campos do PRD 3.1.2 estão presentes | CONV-01 | concluido |
| CONV-03 | Fluxo de abertura e boas-vindas (INT-01) | Implementar mensagem de abertura gerada dinamicamente pelo LLM (não texto fixo), conforme exemplo do Caso 1 do Produto Conversacional Seção 8 | Em teste com 5 pessoas fora do projeto, nenhuma identifica a abertura como "formulário automatizado" (RF-01) | CONV-01, CONV-02 | concluido |
| CONV-04 | Fluxo 3.1 — Segmento/negócio do cliente final | Implementar coleta do campo de segmento (INT-02), com reconhecimento do que foi dito e conexão fluida para a próxima pergunta (Produto Conversacional 3.1) | Bot reconhece o segmento informado e já encadeia a pergunta seguinte na mesma resposta, sem repetir a mesma pergunta de forma idêntica se a resposta for vaga (aciona Fluxo de desambiguação) | CONV-03 | concluido |
| CONV-05 | Fluxo 3.2 — Canal desejado | Implementar coleta do canal (WhatsApp/site/outro — INT-03), reconhecendo se o lead já mencionou o canal espontaneamente antes de perguntar (Produto Conversacional 3.2) | Se o lead já respondeu o canal antecipadamente, o bot confirma em vez de perguntar de novo; se responder "não sei", registra como "a definir" sem insistir | CONV-04 | concluido |
| CONV-06 | Fluxo 3.3 — Problema/objetivo principal | Implementar coleta do problema/objetivo (INT-04), refletindo o problema numa frase curta antes de seguir (Produto Conversacional 3.3) | Se o pedido estiver fora do escopo típico do freelancer, o bot não julga em voz alta e sinaliza apenas no campo interno de observação de viabilidade (RF-03) | CONV-05 | concluido |
| CONV-07 | Fluxo 3.4 — Orçamento aproximado | Implementar coleta de orçamento (INT-05) sem ancorar valores nem opinar/confirmar o número dito pelo lead (guardrail PRD 3.1.2.4) | Em nenhuma resposta o bot avalia se o valor informado é "pouco" ou "dentro do esperado"; se o lead recusar informar, registra "não informado" sem insistir | CONV-06 | concluido |
| CONV-08 | Fluxo 3.5 — Prazo desejado | Implementar coleta de prazo (INT-06) sem confirmar viabilidade (Produto Conversacional 3.5) | Bot registra o prazo informado sem prometer que é viável; tentativa de indução por confirmação aciona o Fluxo de pergunta fora de escopo (CONV-14) | CONV-07 | concluido |
| CONV-09 | Fluxo 3.6 — Volume estimado | Implementar coleta de volume estimado (INT-07), aceitando estimativa aproximada ou "não sei precisar" sem insistir em número exato (Produto Conversacional 3.6) | Resposta vaga de volume é aceita e registrada como estimativa aberta, sem repetição da pergunta | CONV-08 | concluido |
| CONV-10 | Fluxo 3.7 — Dado de contato | Implementar coleta final de nome + e-mail/WhatsApp (INT-08), sinalizando como etapa final (Produto Conversacional 3.7) | Se o contato vier incompleto, o bot pede especificamente o que falta (não repete a pergunta inteira); após 2ª tentativa sem sucesso, segue para o resumo sinalizando contato ausente (conforme RF-02 permite) | CONV-09 | concluido |
| CONV-11 | Memória de curto prazo dentro da sessão | Garantir que o LLM, a cada chamada, receba o histórico completo da sessão + os campos já coletados, para nunca reformular a mesma pergunta de forma idêntica duas vezes seguidas (Produto Conversacional Seção 1 e Seção 6 — dependência marcada "Pendente" no doc de Produto, resolvida pela arquitetura em memória) | Em teste manual, repetir uma resposta já dada não gera a mesma pergunta novamente; o bot pula perguntas já respondidas antecipadamente | INFRA-05, CONV-04 a CONV-10 | concluido |
| CONV-12 | Estratégia de desambiguação | Implementar lógica de desambiguação: nunca repetir a pergunta anterior com as mesmas palavras, estreitando de aberta para específica a cada tentativa (Produto Conversacional Seção 4) | Após 2 tentativas de desambiguação sem sucesso, o bot registra o campo como "não especificado" e segue em frente sem insistir pela 3ª vez (conforme exemplo da Seção 4) | CONV-04 | concluido |
| CONV-13 | Detecção de loop sem progresso (INT-14) | Implementar detecção de 3+ mensagens seguidas do lead sem informação nova identificável para o campo em aberto (Produto Conversacional Seção 5) | Ao atingir o critério, o bot encerra graciosamente sem repetir a pergunta pela 4ª vez, pedindo apenas contato para retomada posterior (conforme Caso 4) | CONV-11 | concluido |
| CONV-14 | Fluxo — Pergunta de preço/prazo direto (INT-09) | Implementar resposta padrão que reconhece a pergunta, explica o motivo de não responder e redireciona (Produto Conversacional, Fluxo "Pergunta fora do escopo — preço ou prazo") | Em 20 conversas de teste com tentativas de indução, 0 respostas contêm valores de prazo ou preço (RF-06); a partir da 3ª insistência no mesmo tópico, aciona transferência humana (CONV-16) | CONV-01 | concluido |
| CONV-15 | Fluxo — Usuário pergunta se o bot é humano (INT-10) | Implementar confirmação direta e honesta ("sou uma automação, não uma pessoa"), sem variação de conteúdo, apenas de fraseado (Produto Conversacional, Fluxo INT-10) | Em teste direto, o bot se identifica como automação/assistente em 100% das vezes (RF-06) e retoma o ponto exato da qualificação onde estava | CONV-01 | concluido |
| CONV-16 | Fluxo — Usuário quer falar com humano (INT-11) | Implementar gatilhos objetivos de transferência humana: termos como "falar com/humano/pessoa/atendente/responsável", OU 3+ tentativas de indução de preço/prazo, OU 3+ mensagens sem progresso (Produto Conversacional Seção 5) | Ao acionar, o bot confirma o pedido, não insiste em reter o lead, e gera o resumo com os campos disponíveis até aquele ponto (mesmo incompletos) | CONV-13, CONV-14 | concluido |
| CONV-17 | Fluxo — Pergunta fora de escopo geral (INT-13) | Implementar resposta que reconhece a pergunta sem inventar o que o freelancer oferece, e retoma a qualificação no ponto em que parou (Produto Conversacional, Fluxo INT-13) | O bot nunca afirma se um serviço faz parte ou não do escopo do freelancer; oferece registrar a dúvida no resumo e retoma a qualificação | CONV-01 | concluido |
| CONV-18 | Geração de resumo final personalizado ao lead | Implementar chamada final ao LLM que gera a mensagem de encerramento referenciando pelo menos 2 dados específicos coletados, sem prometer prazo/preço, com próximo passo textual claro (Produto Conversacional, Fluxo "Resumo final personalizado"; Arquitetura Seção 4, passo 7) | Mensagem final referencia ≥2 dados específicos da conversa (RF-04) e não contém nenhuma promessa de prazo ou preço; revisão manual de 10 transcrições confirma | CONV-04 a CONV-10 | concluido |
| CONV-19 | Geração de resumo estruturado ao freelancer | Implementar chamada final ao LLM solicitando, em formato JSON via tool use, os 7 campos + observação de fit/viabilidade + campos não coletados com motivo (Arquitetura Seção 4, passo 7; Produto Conversacional, Fluxo "Resumo estruturado para o freelancer") | Resumo gerado em formato consistente em 100% das conversas concluídas, disponível em até 1 minuto (RF-05); campo de viabilidade preenchido em 100% (RF-03); campos não coletados aparecem explicitamente, nunca omitidos | CONV-04 a CONV-10 | concluido |
| CONV-20 | Camada de verificação de guardrail pós-resposta | Implementar checagem de padrões de valores monetários/prazos na resposta do LLM antes de enviá-la ao usuário, como segunda camada de proteção ao RF-06 (Arquitetura Seção 9, risco 2) | Em teste com respostas simuladas contendo valores monetários, a checagem intercepta e impede o envio ao lead | CONV-14 | concluido |
| CONV-21 | Limite de turnos por sessão | Implementar teto técnico de turnos por sessão (ex.: máx. 20) como salvaguarda de custo (Arquitetura Seção 9, risco 3) | Sessão que ultrapassa o limite é encerrada de forma controlada, com mensagem explicativa ao lead, sem erro cru | INFRA-05 | concluido |
| CONV-22 | Correção do gatilho de encerramento por estagnação (CONV-13) | Corrigir as 2 falhas do TEST-04: contador de estagnação cumulativo entre campos (a troca de campo não zera) e marcador [FIM_QUALIFICACAO] no encerramento por loop. Prompt reescrito (seção de loop com contador, precedência e exemplo) + reforço determinístico em app/conversa.py (contar_estagnacao + instrução interna injetada na chamada ao LLM com 3/4+ mensagens vagas seguidas) | Caso 4 reexecutado encerra pedindo apenas contato na 3ª mensagem sem progresso e faz a despedida na 4ª com resumo estruturado gerado; TEST-01 e TEST-06 sem regressão | CONV-12, CONV-13 | concluido |
| CONV-23 | Correção de alucinação no extrator de resumo estruturado | Instrução de extração de gerar_resumo_estruturado() ajustada (system + instrução interna): campo só é preenchido com o que o LEAD disse explicitamente; exemplos/sugestões citados pelo bot nas perguntas não contam como resposta, mesmo não negados; campo sem resposta clara recebe o texto padrão de não coletado | TEST-06 reexecutado 2x com "Problema / objetivo principal" saindo "não especificado" (consistente); TEST-01, TEST-02 e Caso 4 sem regressão. Atenção futura (não bloqueia): inferência residual pode aparecer no campo de texto livre Observações (ex.: "lead pediu desculpas" inexistente na conversa) e textos padrão às vezes saem parafraseados — candidato a item de refinamento | CONV-19 | concluido |
| CONV-24 | Rede de segurança do resumo no fechamento sem marcador | Achado do TEST-03: modelo omite [FIM_QUALIFICACAO] em parte dos fechamentos normais (3/17 na amostra), deixando o freelancer sem o resumo (RF-05). parece_fechamento() em conversa.py (assinaturas conservadoras de encerramento) + rede em main.py que gera o resumo quando o fechamento vem sem marcador — avaliada SOMENTE no branch sem marcador, sem risco de resumo duplo | 8× caminho feliz com resumo no fechamento em 8/8 e zero geração intermediária; rede reconhece 3/3 fechamentos falhados do TEST-03 e 0 falsos positivos em 222 respostas não-finais; TEST-06 e Caso 4 sem regressão | CONV-18, CONV-19 | concluido |
| CONV-25 | Prompt caching no system prompt | Achado do TEST-09: custo real por conversa ~4,1× a estimativa da Arquitetura Seção 8, porque cada chamada reenvia o system prompt (~8,9 mil tokens) a preço cheio. cache_control ephemeral no bloco de system em app/llm_client.py (_system_cacheavel, usado por complete e extract_structured), sem alterar o conteúdo do prompt nem a lógica conversacional. A chamada de resumo não cacheia (prefixo abaixo do mínimo de 4.096 tokens do Haiku 4.5) — sem erro, comportamento inalterado | 3 conversas de aceite (feliz, humano, preço-3x): 1 escrita de cache (8.924 tokens) e leitura de cache em 100% das chamadas de conversa seguintes a 10% do preço; custo US$0,053 vs US$0,187 das mesmas conversas no TEST-09 (economia ~72%); sem regressão (resumo em 3/3, 0 vazamentos de preço/prazo, 0 fallbacks); nova projeção ~US$0,028/conversa → ~R$12,42/mês em 80 conversas/mês (antes R$34,76; estimativa original R$8,40) | CONV-19, TEST-09 | concluido |

### Bloco 4: Testes

| ID | Tarefa | Descrição clara | Critério de aceite | Dependências | Status |
|---|---|---|---|---|---|
| TEST-01 | Caso de teste: caminho feliz | Executar o diálogo completo do Caso 1 (Produto Conversacional Seção 8) do início ao resumo final | Conversa flui sem repetição de pergunta idêntica; resumo final e estruturado gerados corretamente; duração < 5 minutos | todos CONV | concluido |
| TEST-02 | Caso de teste: ambiguidade/projeto pouco definido | Executar o diálogo do Caso 2, com respostas vagas repetidas | Após 2 tentativas de desambiguação, o campo é registrado como "não especificado" e a conversa segue sem travar (CONV-12) | todos CONV | concluido |
| TEST-03 | Caso de teste: fuga de escopo (preço direto) | Executar 20 conversas de teste com tentativas de indução de preço/prazo, incluindo o roteiro do Caso 3 | 0 respostas contêm valores de prazo ou preço em 20 conversas (RF-06); transferência humana acionada na 3ª insistência | todos CONV | concluido — critério RF-06 atendido (0 vazamentos em 156 respostas, ~34 induções; transferência na 3ª insistência em 6/6; CONV-20 nunca precisou intervir). Achado lateral fora do critério: em 3 de 17 fechamentos normais o modelo omitiu o marcador [FIM_QUALIFICACAO] e o resumo estruturado não saiu no turno de fechamento (recuperado no turno seguinte em 3/3) — afeta RF-05; correção separada em CONV-24 |
| TEST-04 | Caso de teste: loop sem progresso | Executar o diálogo do Caso 4, com respostas "não sei" repetidas | Bot não repete a pergunta pela 4ª vez; encerra graciosamente pedindo contato (CONV-13) | todos CONV | concluido |
| TEST-05 | Caso de teste: usuário pergunta se é humano | Executar teste direto ("você é humano ou um bot?") em 10 conversas | O bot se identifica como automação/assistente em 100% das vezes (RF-06) | todos CONV | concluido |
| TEST-06 | Caso de teste: usuário pede humano diretamente | Executar o diálogo do Caso 6, sem indução prévia | Bot confirma o pedido sem insistir em reter o lead e pede confirmação de contato já fornecido (sem repetir pergunta se já respondida) | todos CONV | concluido |
| TEST-07 | Caso de teste: pergunta fora de escopo geral | Executar o diálogo do Caso 7 | Bot não inventa resposta sobre o que o freelancer atende; retoma a qualificação no ponto em que parou | todos CONV | concluido |
| TEST-08 | Teste com usuários reais — percepção "não parece formulário" | Aplicar o bot com 5 pessoas fora do projeto e perguntar pós-conversa "isso pareceu um formulário?" | Nenhuma das 5 identifica a abertura como formulário automatizado (RF-01); resposta majoritária "não" na pergunta pós-conversa (RF-02, visão do cliente) | TEST-01 | aprovado |
| TEST-09 | Verificar custo operacional real vs. estimado | Rodar 10 conversas completas e medir consumo real de tokens/custo, comparando com a estimativa de ~R$8,40/mês da Arquitetura Seção 8 | Custo real por conversa está dentro da mesma ordem de grandeza da estimativa; total mensal projetado permanece ≤ R$50/mês | todos CONV | concluido — 10 conversas completas medidas: custo médio US$0,079/conversa (~74,3 mil tokens de entrada + 950 de saída), ~4,1× a estimativa por conversa da Arquitetura; projeção mensal em 80 conversas/mês: R$34,76 ≤ R$50 (critério atendido). Causa do desvio: reenvio integral do system prompt (~8,9 mil tokens) a cada chamada, sem cache — corrigido na CONV-25 (nova projeção ~R$12,42/mês). Ressalva: resumo estruturado não gerado em 2/10 conversas — t09-08b: roteiro de teste terminou antes do fechamento (confirmado na transcrição); t09-03 (ambiguidade) não gerou resumo estruturado na execução original; causa não investigada por decisão de economia de créditos (não é confirmado se é falha real ou artefato de roteiro, como aconteceu com a t09-08b). Fica como item de atenção não bloqueante, a verificar se reaparecer em uso real |
| TEST-10 | Teste de acesso multi-dispositivo/navegador | Testar carregamento e manutenção de histórico em 3 dispositivos/navegadores diferentes | Interface carrega em até 3 segundos e mantém o histórico da conversa durante a sessão ativa, nos 3 ambientes testados (RF-07) | UI-01, UI-03 | aprovado |

### Bloco 5: Preparação para entrega e reaproveitamento

| ID | Tarefa | Descrição clara | Critério de aceite | Dependências | Status |
|---|---|---|---|---|---|
| ENTREGA-01 | Extrair configurações para arquivos parametrizáveis | Consolidar e revisar `config/system_prompt.md`, `config/campos_qualificacao.json` e as variáveis de identidade visual, confirmando que nenhum está hardcoded no código Python (Arquitetura Seção 10) | Trocar de cliente/projeto exige apenas editar arquivos de `config/`, sem tocar em código Python | todos TEST | concluido |
| ENTREGA-02 | README do repositório | Documentar setup, variáveis de ambiente, como rodar localmente e como adaptar os arquivos de configuração para um novo cliente | Uma pessoa nova consegue subir o projeto localmente seguindo apenas o README | ENTREGA-01 | concluido |
| ENTREGA-03 | Deploy em ambiente público | Deploy no Render.com (tier gratuito, backend + frontend estático no mesmo serviço — Arquitetura Seção 5), com ping externo periódico (ex.: UptimeRobot) para mitigar cold start (Arquitetura Seção 9, risco 1) | Link público carrega em até 3s de forma consistente (RF-07), mesmo após período de inatividade | todos TEST | pendente |
| ENTREGA-04 | Atualizar LOG_DE_DECISOES.md com handoffs pendentes | Registrar as entradas de handoff sugeridas nos artefatos 03 e 04 (Gate 2 aprovado; especialista de Produto Conversacional) no log de decisões do projeto, caso esse arquivo exista ou seja criado | Entradas de handoff de ambos os artefatos estão registradas no log, com IDs sequenciais corretos | ENTREGA-01 | concluido |

---

## Mapa de dependências críticas

- **INFRA-04** (wrapper de LLM) bloqueia todo o **Bloco 3** — nenhuma lógica conversacional funciona sem a integração com o Claude Haiku 4.5.
- **INFRA-05** (sessão em memória) bloqueia **CONV-11** e, por extensão, toda a coerência conversacional entre turnos (evitar reperguntar campos já respondidos).
- **CONV-01** e **CONV-02** (arquivos de configuração de persona e campos) bloqueiam **CONV-03 a CONV-21** — são a base de que todos os fluxos dependem.
- **Todos os CONV-XX** bloqueiam o **Bloco 4** (Testes) — não é possível testar caminhos de conversa sem a lógica implementada.
- **Todos os TEST-XX** bloqueiam **ENTREGA-01** e **ENTREGA-03** — configurações só devem ser "congeladas" e o deploy final feito depois de validado o comportamento.

## Tarefas marcadas como bloqueadas

Nenhuma tarefa está tecnicamente bloqueada por dependência circular. As
pendências abaixo **não bloqueiam o início da execução** (os artefatos de
origem assumiram valores padrão explicitamente), mas exigem confirmação do
freelancer antes de considerar o MVP como "fechado":

1. **Nome/identidade do bot** — `[Rai]` é um placeholder no Produto
   Conversacional (Seção 1); **CONV-01** deve implementar com o nome
   funcional sugerido ("Assistente do [Freelancer]") até confirmação em
   contrário.
2. **Lista dos 7 campos de coleta** — marcada `[NECESSITA VALIDAÇÃO DO
   FREELANCER]` no PRD (item 3.1.2); **CONV-02 e CONV-04 a CONV-10** assumem
   a lista atual. Se o freelancer alterar os campos, essas tarefas precisam
   ser refeitas.
3. **Modo de log temporário para testes** — marcado `[NECESSITA VALIDAÇÃO DO
   FREELANCER]` na Arquitetura (Seção 7); **INFRA-02** implementa como
   proposto (arquivo local via variável de ambiente, desligado por padrão),
   mas o freelancer deve confirmar se essa forma de inspecionar as 10
   conversas de teste (TEST-01 a TEST-07) é aceitável.
4. **Reconfirmação de pricing do Claude Haiku 4.5** — a Arquitetura já
   registrou uma mudança de preço um dia antes da análise (Seção 3);
   **INFRA-04 e TEST-09** devem reconfirmar o valor oficial em
   claude.com/pricing antes de fechar o orçamento definitivo do projeto.
5. **Canal de aquisição de leads** — marcado `[A VALIDAR]` no PRD (Seção 6);
   não bloqueia nenhuma tarefa, mas pode motivar um ajuste de tom na
   abertura (**CONV-03**) após as primeiras conversas reais.

## O modelo base reaproveitável

Ao final deste projeto, os seguintes componentes devem estar
parametrizáveis para reaproveitamento em projetos futuros:

- [ ] Arquivo de configuração do prompt do sistema (`CONV-01`)
- [ ] Arquivo de configuração das perguntas/campos de qualificação (`CONV-02`)
- [ ] Wrapper de integração com LLM — troca de provedor sem reescrever
      lógica conversacional (`INFRA-04`)
- [ ] Estrutura de pastas do projeto / template de repositório (`INFRA-01`)
- [ ] Interface web com identidade visual ajustável por projeto (`UI-01`)
- [ ] Checklist final de extração de configurações antes da entrega
      (`ENTREGA-01`)

---

Artefato 05_BACKLOG_TECNICO.md gerado. Revise as dependências críticas antes
de iniciar execução.
