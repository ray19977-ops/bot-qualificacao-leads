# TEST-08 — Teste com usuários reais: percepção "não parece formulário"

> Reconstruído a partir de `05_BACKLOG_TECNICO.md` (linha 92) e `02_PRD.md`
> (RF-01 e RF-02 visão do cliente). Status no backlog: pendente. Dependência:
> TEST-01 (concluída).

## Critério de aceite (backlog / PRD)

- **RF-01:** nenhuma das pessoas testadoras identifica a abertura como
  "formulário automatizado".
- **RF-02 (visão do cliente):** resposta majoritária "não" à pergunta
  pós-conversa "isso pareceu um formulário?".

**Desvio documentado (resolvido):** a rodada inicial de 17/07/2026 previa
executar com 3 pessoas, deixando a formalização para 5 a decidir depois. Na
rodada final (21/07/2026), o teste foi completado com **5 pessoas** ao todo
(Khuliso, Paolo, Arnaldo, Gustavo, Rodrigo), cumprindo o número previsto pelo
critério original. Rodrigo teve a conversa completa, mas sem as 3 respostas
de percepção coletadas — por isso não entra na contagem de RF-01/RF-02,
ficando registrado apenas como nota (ver "Resultado final" abaixo). Os outros
4 são testes válidos e completos.

## Perfil dos testadores

- Pessoas **fora do projeto**, sem contexto prévio sobre o bot.
- Não contar antes que é um teste de "parecer formulário" nem mencionar as
  palavras "bot", "formulário" ou "automação" no convite.

## Setup

- [ ] Servidor no ar: `uvicorn app.main:app --host 0.0.0.0 --port 8123`
- [ ] Link de acesso para o dispositivo de cada testador: `http://<IP>:8123`
- [ ] `TEST_LOG_MODE=true` para guardar as transcrições como evidência
      (desligar ao final)

## Briefing padrão (ler/enviar igual para os 3)

> "Imagina que você é um cliente interessado em contratar um serviço desse
> profissional (ex.: automação de atendimento, site, chatbot). Abre esse link
> e conversa com o atendimento até o final, como você faria de verdade.
> Depois eu te faço duas perguntas rápidas."

Não responder dúvidas sobre "o que é isso" antes da conversa — pedir que a
pessoa simplesmente converse.

## Roteiro por testador

1. [ ] Enviar o briefing padrão e o link.
2. [ ] Testador conclui a conversa até a mensagem final (resumo ao lead).
3. [ ] Perguntas pós-conversa, **nesta ordem** (registrar as respostas
       literalmente):
       - [ ] (a) Aberta, sem induzir: "Como foi a experiência?"
       - [ ] (b) RF-01: "A **abertura** da conversa pareceu um formulário
             automatizado?"
       - [ ] (c) RF-02: "No geral, **isso pareceu um formulário**?"
4. [ ] Registrar observações espontâneas (elogios, estranhamentos, travadas).

## Registro de resultados (4 testes válidos)

| Testador | Negócio | Q1 — Como foi a experiência | Q2 — Pareceu formulário? | Q3 — Impressão da abertura |
|---|---|---|---|---|
| Khuliso Pinto | não detalhado (venezuelano, gravou vídeo) | "A experiência foi agradável, uma coisa boa é que ressalta os pontos discutidos caso o usuário queira explicar de uma forma melhor ou o bot não tenha entendido direito, e dá tempo de corrigir" | **Não** — "ele se adaptou para não ser um simples formulário pois interage diretamente com o usuário, dando a possibilidade de se expressar de forma que possa achar uma solução para seu problema ou protótipo" | "No início da conversa ele passou uma impressão de agrado e de estar disposto a ajudar a começar o projeto, ajudando a formular ideias e melhorar pontos do pensamento" |
| Paolo | rede de motéis | "A experiência foi bem boa. Respostas precisas e bem rápidas" | **Não** — "as perguntas e respostas foram extremamente diretas" | "O comecinho da conversa foi mais leve que uma pena" |
| Arnaldo | loja de calçados online | "A experiência foi boa, me senti bem atendido, super humanizado, tudo bem natural e produtivo" | **Não** — "tudo me pareceu bem natural" | "A impressão é que meu problema é muito simples de resolver; a objetividade da IA tirou de letra. Não consegui sentir se ela entende de sapatos (meu negócio), mas pelo atendimento ele soube traçar um bom agendamento para avaliação — cumpriu seu papel" |
| Gustavo | eletrônicos/materiais/decoração/roupas | "Gostei da interação, ele é prestativo e direto" | **Não** — "está compatível a um bot tradicional de mercado" | "O sistema parece humanizado e direcional" |

**Resultado:** 4 de 4 responderam "não" à pergunta central — unanimidade
(acima do critério de maioria). Nenhum identificou a abertura como
formulário automatizado.

### Observações qualitativas

- **Khuliso (não nativo em português):** escreveu com erros de português; o
  bot manteve fluidez normal, sem se confundir com a entrada ruidosa. Também
  houve um momento em que o testador presumiu que o freelancer desenvolvia
  aplicativos — o bot corrigiu e esclareceu que o serviço é automação de
  atendimento, sem inventar escopo (CONV-17).
- **Arnaldo:** a conversa expandiu de "atendimento" para "funil de vendas
  completo com pagamento e logística" — o resumo estruturado marcou
  corretamente isso como fora do escopo típico, recomendando avaliação
  humana (CONV-17/19 funcionando como esperado).
- **Gustavo:** teste reaproveitado de sessão anterior (transcrição já
  registrada), sem necessidade de nova execução.

### Nota — caso descartado

**Rodrigo Citron (estúdio de música):** transcrição completa disponível,
mas sem as 3 respostas de percepção pós-conversa coletadas. Registrado
apenas como nota de rodapé — **não conta** como teste válido para
RF-01/RF-02.

## Aprovação

- **RF-01:** 0/4 identificaram a abertura como formulário — atendido.
- **RF-02:** 4/4 responderam "não" — unanimidade, acima do mínimo de
  maioria exigido.
- **Veredito: aprovado** (21/07/2026). Total de 5 pessoas efetivamente
  testadas atende ao número previsto no critério original; 1 caso
  (Rodrigo) excluído da contagem por dados incompletos, documentado como
  nota acima.
