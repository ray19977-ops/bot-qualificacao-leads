"use strict";

// Identidade/comportamento configuráveis por cliente (Arquitetura Seção 10)
const CONFIG = {
  nomeBot: "Rai Bot",
  mensagemErroRede:
    "Não consegui enviar sua mensagem agora. Confira sua conexão e tente de novo.",
};

// Um session_id novo a cada carregamento da página (Arquitetura Seção 4,
// passos 1–3): recarregar inicia conversa nova; o histórico vive só no
// backend em memória (INFRA-05) e no DOM durante a sessão ativa.
// crypto.randomUUID exige contexto seguro (https/localhost); o fallback
// cobre acesso via IP da rede local, ex. teste multi-dispositivo.
function gerarSessionId() {
  if (window.crypto && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `sessao-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

const sessionId = gerarSessionId();

const mensagens = document.getElementById("mensagens");
const form = document.getElementById("form-chat");
const campo = document.getElementById("campo-mensagem");
const botaoEnviar = document.getElementById("botao-enviar");
const painelResumo = document.getElementById("painel-resumo");
const camposResumo = document.getElementById("resumo-campos");

// Exibe o resumo estruturado do lead no painel lateral (UI-02).
// `resumo` é um objeto {campo: valor} enviado pelo backend ao final
// da conversa (CONV-19); valores em array são exibidos em linhas.
function exibirResumo(resumo) {
  camposResumo.replaceChildren();
  for (const [nomeCampo, valor] of Object.entries(resumo)) {
    const termo = document.createElement("dt");
    termo.textContent = nomeCampo;
    const definicao = document.createElement("dd");
    definicao.textContent = Array.isArray(valor)
      ? valor.join("\n")
      : String(valor);
    camposResumo.append(termo, definicao);
  }
  painelResumo.hidden = false;
}

function adicionarMensagem(autor, texto) {
  const balao = document.createElement("div");
  balao.className = `mensagem mensagem-${autor}`;
  balao.textContent = texto;
  mensagens.appendChild(balao);
  mensagens.scrollTop = mensagens.scrollHeight;
  return balao;
}

async function enviarMensagem(texto) {
  const resposta = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message: texto }),
  });
  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status}`);
  }
  return resposta.json();
}

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const texto = campo.value.trim();
  if (!texto) {
    return;
  }

  adicionarMensagem("usuario", texto);
  campo.value = "";
  campo.disabled = true;
  botaoEnviar.disabled = true;

  const digitando = adicionarMensagem("bot", "digitando…");
  digitando.classList.add("mensagem-digitando");

  try {
    const dados = await enviarMensagem(texto);
    digitando.classList.remove("mensagem-digitando");
    digitando.textContent = dados.reply;
    if (dados.resumo) {
      exibirResumo(dados.resumo);
    }
  } catch {
    digitando.classList.remove("mensagem-digitando");
    digitando.textContent = CONFIG.mensagemErroRede;
  } finally {
    campo.disabled = false;
    botaoEnviar.disabled = false;
    campo.focus();
    mensagens.scrollTop = mensagens.scrollHeight;
  }
});

// Ao carregar a página, pede a mensagem de abertura ao backend (INT-01):
// enviar texto vazio numa sessão nova dispara a abertura gerada pelo LLM
async function solicitarAbertura() {
  const digitando = adicionarMensagem("bot", "digitando…");
  digitando.classList.add("mensagem-digitando");
  try {
    const dados = await enviarMensagem("");
    digitando.textContent = dados.reply;
  } catch {
    digitando.textContent = CONFIG.mensagemErroRede;
  } finally {
    digitando.classList.remove("mensagem-digitando");
  }
}

solicitarAbertura();
campo.focus();
