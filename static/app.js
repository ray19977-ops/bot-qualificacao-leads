"use strict";

// Identidade/comportamento configuráveis por cliente (Arquitetura Seção 10)
const CONFIG = {
  nomeBot: "Rai Bot",
  mensagemErroRede:
    "Não consegui enviar sua mensagem agora. Confira sua conexão e tente de novo.",
  // Placeholder — a UI-03 passa a gerar um session_id novo a cada
  // carregamento da página (Arquitetura Seção 4, passos 1–3)
  sessionId: "ui-01-placeholder",
};

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
    body: JSON.stringify({ session_id: CONFIG.sessionId, message: texto }),
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

campo.focus();
