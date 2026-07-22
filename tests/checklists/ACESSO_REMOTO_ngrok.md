# Acesso remoto via ngrok — apoio ao TEST-08

Alternativa ao acesso por Wi-Fi local para voluntários fora da rede.
Estado desta máquina (verificado em 18/07/2026): ngrok **já instalado**
(v3.39.8, via Microsoft Store) e **authtoken já configurado** em
`C:\Users\ray19\AppData\Local\ngrok\ngrok.yml` — nada a instalar.

## Como subir o túnel (passo a passo)

1. **Subir o servidor** (terminal 1, raiz do repo, venv ativa):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8123
   ```
   (Com ngrok o `--host 0.0.0.0` não é obrigatório — o túnel entra por
   `localhost` — mas manter o mesmo comando de sempre não atrapalha.)

2. **Criar o túnel** (terminal 2):
   ```
   ngrok http 8123
   ```

3. **Obter a URL pública:** aparece no próprio terminal do ngrok, na linha
   `Forwarding`:
   ```
   Forwarding  https://<algo-aleatorio>.ngrok-free.app -> http://localhost:8123
   ```
   Essa URL `https://...ngrok-free.app` é o link a enviar ao voluntário.
   Alternativa: abrir o painel local em `http://127.0.0.1:4040`, que mostra a
   URL e o tráfego de cada requisição em tempo real.

4. **Encerrar:** `Ctrl+C` no terminal do ngrok. O link morre na hora.

## Instalação e token (só se precisar refazer em outra máquina)

1. Instalar: `winget install ngrok.ngrok` (ou baixar de ngrok.com/download).
2. Criar conta gratuita em https://dashboard.ngrok.com e copiar o authtoken
   em "Your Authtoken".
3. Registrar o token (uma única vez):
   ```
   ngrok config add-authtoken <SEU_TOKEN>
   ```

## Avisos importantes para os testes

- **A URL muda a cada execução** do `ngrok http` no plano gratuito. Enviar o
  link ao voluntário só depois de subir o túnel. (Opcional: o plano gratuito
  permite reivindicar **1 domínio estático** no dashboard — Domains → New
  Domain; aí o comando vira
  `ngrok http --url=<seu-dominio>.ngrok-free.app 8123` e o link passa a ser
  sempre o mesmo.)
- **Página interstitial:** no plano gratuito, o primeiro acesso mostra uma
  página do ngrok com um botão "Visit Site". Avisar o voluntário no briefing
  que essa tela é da ferramenta de acesso, **antes** da conversa começar —
  para não contaminar a percepção avaliada no TEST-08.
- **Custo/exposição:** com o túnel aberto, qualquer pessoa com o link conversa
  com o bot e consome créditos da API Anthropic. Compartilhar o link apenas
  com o voluntário da vez e fechar o túnel (`Ctrl+C`) ao terminar cada
  sessão de teste.
- **Contexto seguro:** via ngrok o acesso é HTTPS, então o navegador usa o
  `crypto.randomUUID` nativo (não o fallback exercitado no TEST-10 via IP) —
  os dois caminhos ficam cobertos entre os dois modos de acesso.
