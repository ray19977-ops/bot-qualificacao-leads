"""Lógica conversacional: monta o system prompt e gera as respostas do bot.

O conteúdo do prompt vive em config/system_prompt.md (Arquitetura Seção
10) — este módulo só o carrega e repassa o histórico ao llm_client.
"""

import json
import re
import unicodedata
from pathlib import Path

from app import identidade, llm_client

_NOME_FREELANCER = identidade.IDENTIDADE["nome_freelancer"]
_DESCRICAO_SERVICO = identidade.IDENTIDADE["descricao_servico"]

_RAIZ = Path(__file__).resolve().parent.parent
_CAMINHO_SYSTEM_PROMPT = _RAIZ / "config" / "system_prompt.md"
_CAMINHO_CAMPOS = _RAIZ / "config" / "campos_qualificacao.json"

# Marcador no system_prompt.md substituído pela lista renderizada dos
# campos de campos_qualificacao.json — adicionar/remover campo é só
# editar o JSON, sem tocar em código nem no texto do prompt
_MARCADOR_CAMPOS = "{{CAMPOS_QUALIFICACAO}}"

# Primeira mensagem "user" de toda sessão (INT-01): o frontend pede a
# abertura ao carregar a página e o lead nunca vê este texto. O system
# prompt instrui o bot a gerar a mensagem de boas-vindas ao recebê-lo.
GATILHO_ABERTURA = "[INICIAR_CONVERSA]"

# O system prompt instrui o bot a terminar com este marcador a resposta
# que encerra a qualificação. O backend o remove do texto exibido e o
# usa como gatilho da geração do resumo estruturado (CONV-19).
MARCADOR_FIM = "[FIM_QUALIFICACAO]"

# Reforço determinístico da CONV-13 (CONV-22): o Haiku 4.5 não sustenta
# a contagem de estagnação entre turnos só pela regra do prompt, então o
# código conta as mensagens finais consecutivas do lead sem informação
# nova e injeta a instrução de encerramento na chamada ao LLM. Cobre as
# formas comuns de estagnação; variações fora do padrão continuam sob a
# regra do system prompt.
_PADRAO_SEM_PROGRESSO = re.compile(
    r"^(nao sei( dizer| precisar| mesmo| ainda| nao)?|sei la|"
    r"nao tenho ideia|nao faco ideia|tanto faz|qualquer coisa|"
    r"nem sei|hu?m+)[.!?…\s]*$"
)

_INSTRUCAO_LOOP_CONTATO = (
    "[INSTRUÇÃO INTERNA — o lead não vê esta mensagem] Loop sem "
    "progresso detectado: as últimas 3 mensagens do lead não trouxeram "
    "informação nova. Pare de qualificar agora: não pergunte por nenhum "
    "outro campo. Encerre graciosamente, sem fazer o lead se sentir "
    f"mal, pedindo APENAS um e-mail ou WhatsApp para o {_NOME_FREELANCER} "
    "retomar depois. Se o lead já tiver dado o contato antes, confirme o que "
    "você tem, encerre de vez e termine a resposta com o marcador "
    "[FIM_QUALIFICACAO] sozinho na última linha."
)

_INSTRUCAO_LOOP_ENCERRAR = (
    "[INSTRUÇÃO INTERNA — o lead não vê esta mensagem] O lead segue sem "
    "trazer informação nova mesmo após o pedido de contato. Encerre a "
    "conversa de vez, educadamente, sem pedir mais nada, e OBRIGATORIAMENTE "
    "termine a resposta com o marcador [FIM_QUALIFICACAO] sozinho na "
    "última linha."
)


# Rede de segurança do RF-05 (CONV-24): o modelo omite o marcador de fim
# em parte dos fechamentos (~18% na amostra do TEST-03). Assinaturas
# conservadoras das mensagens de encerramento; fraseados fora do padrão
# continuam cobertos pela regra do marcador no system prompt.
_PADRAO_FECHAMENTO = re.compile(
    r"recapitulando"
    r"|obrigad[oa] pelo (?:seu )?tempo"
    r"|acrescentar antes de (?:eu )?(?:fechar|encerrar)",
    re.IGNORECASE,
)


def parece_fechamento(resposta: str) -> bool:
    """Reconhece uma mensagem de encerramento que veio sem o marcador."""
    return bool(_PADRAO_FECHAMENTO.search(resposta))


def _sem_informacao_nova(texto: str) -> bool:
    normalizado = unicodedata.normalize("NFD", texto.strip().lower())
    normalizado = "".join(
        c for c in normalizado if unicodedata.category(c) != "Mn"
    )
    return bool(_PADRAO_SEM_PROGRESSO.match(normalizado))


def contar_estagnacao(historico: list[dict]) -> int:
    """Conta as mensagens finais consecutivas do lead sem informação nova.

    Percorre o histórico do fim para o início considerando apenas as
    mensagens do lead; a primeira que trouxer informação real (ou o
    gatilho de abertura) zera a sequência.
    """
    contagem = 0
    for mensagem in reversed(historico):
        if mensagem["role"] != "user":
            continue
        if mensagem["content"] == GATILHO_ABERTURA:
            break
        if not _sem_informacao_nova(mensagem["content"]):
            break
        contagem += 1
    return contagem


def _renderizar_campos() -> str:
    dados = json.loads(_CAMINHO_CAMPOS.read_text(encoding="utf-8"))
    linhas = []
    for numero, campo in enumerate(dados["campos"], start=1):
        linhas.append(
            f"{numero}. **{campo['nome']}** — {campo['descricao']}\n"
            f"   Como coletar: {campo['orientacao_coleta']}\n"
            f"   Se não coletado, registre como: \"{campo['registro_se_nao_coletado']}\""
        )
    return "\n".join(linhas)


def carregar_system_prompt() -> str:
    # Lido a cada resposta: editar o prompt não exige reiniciar o servidor
    prompt = _CAMINHO_SYSTEM_PROMPT.read_text(encoding="utf-8")
    return prompt.replace(_MARCADOR_CAMPOS, _renderizar_campos())


def responder(historico: list[dict]) -> str:
    """Gera a próxima resposta do bot para o histórico da sessão.

    Levanta LLMUnavailableError (via llm_client) se o modelo estiver
    indisponível — o chamador responde com a mensagem de fallback.
    """
    mensagens = historico
    estagnacao = contar_estagnacao(historico)
    if estagnacao == 3:
        # A instrução interna não é persistida na sessão: só entra na
        # chamada ao LLM, como já faz gerar_resumo_estruturado
        mensagens = historico + [
            {"role": "user", "content": _INSTRUCAO_LOOP_CONTATO}
        ]
    elif estagnacao >= 4:
        mensagens = historico + [
            {"role": "user", "content": _INSTRUCAO_LOOP_ENCERRAR}
        ]
    return llm_client.complete(mensagens, system=carregar_system_prompt())


def _tool_resumo() -> dict:
    """Monta a tool de resumo estruturado a partir do JSON de campos.

    Schema dinâmico: adicionar/remover campo em campos_qualificacao.json
    muda o resumo sem tocar em código (critério da CONV-02).
    """
    campos = json.loads(_CAMINHO_CAMPOS.read_text(encoding="utf-8"))["campos"]
    properties = {
        campo["id"]: {
            "type": "string",
            "description": (
                f"{campo['nome']}: {campo['descricao']} "
                f"Se não coletado, use exatamente: \"{campo['registro_se_nao_coletado']}\""
            ),
        }
        for campo in campos
    }
    properties["observacao_viabilidade"] = {
        "type": "string",
        "description": (
            "Observação interna de fit/viabilidade (RF-03), SEMPRE "
            "preenchida: o pedido parece dentro do escopo típico de "
            f"{_DESCRICAO_SERVICO} do freelancer? Sinalize pedidos fora "
            "do escopo, urgência extrema ou qualquer alerta útil à "
            "decisão humana."
        ),
    }
    properties["campos_nao_coletados"] = {
        "type": "array",
        "description": (
            "OBRIGATÓRIO: um item para CADA campo acima cujo valor "
            "ficou com o texto padrão de não coletado (ex.: 'não "
            "informado', 'a definir', 'não especificado'), repetindo o "
            "campo e o motivo (ex.: 'lead não quis informar', 'conversa "
            "encerrada antes desta etapa'). Lista vazia SOMENTE se todos "
            "os campos foram efetivamente coletados."
        ),
        "items": {
            "type": "object",
            "properties": {
                "campo": {"type": "string"},
                "motivo": {"type": "string"},
            },
            "required": ["campo", "motivo"],
        },
    }
    properties["observacoes_livres"] = {
        "type": "string",
        "description": (
            "Observações úteis ao freelancer: lead insistiu em "
            "preço/prazo, pediu atendimento humano, dúvidas fora de "
            "escopo a responder no retorno etc. String vazia se nada."
        ),
    }
    ids_campos = [campo["id"] for campo in campos]
    return {
        "name": "registrar_resumo_lead",
        "description": (
            "Registra o resumo estruturado interno da qualificação para "
            "o freelancer. Nunca é mostrado ao lead."
        ),
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": ids_campos + ["observacao_viabilidade", "campos_nao_coletados"],
        },
    }, campos


def gerar_resumo_estruturado(historico: list[dict]) -> dict:
    """Chamada final ao LLM (Arquitetura Seção 4, passo 7): extrai o
    resumo estruturado da transcrição via tool use e o devolve pronto
    para exibição no painel do freelancer (UI-02).
    """
    tool, campos = _tool_resumo()
    mensagens = historico + [
        {
            "role": "user",
            "content": (
                "[INSTRUÇÃO INTERNA] Gere agora o resumo estruturado da "
                "conversa acima usando a ferramenta registrar_resumo_lead. "
                "Preencha cada campo SOMENTE com o que o lead disse "
                "explicitamente: exemplos ou sugestões que o assistente "
                "citou nas próprias perguntas NÃO contam como resposta do "
                "lead. Campo sem resposta clara do lead (resposta vaga, "
                "mudança de assunto, pedido de humano antes de responder) "
                "recebe o texto padrão de não coletado e entra em "
                "campos_nao_coletados com motivo."
            ),
        }
    ]
    dados = llm_client.extract_structured(
        mensagens,
        tool=tool,
        system=(
            f"Você é o registrador interno de leads do freelancer "
            f"{_NOME_FREELANCER}. "
            "Extraia da transcrição os dados pedidos pela ferramenta com "
            "fidelidade literal ao que o LEAD disse. Regra crítica: "
            "exemplos, sugestões ou hipóteses que o assistente citou nas "
            "próprias perguntas (ex.: 'seria reduzir perguntas repetidas, "
            "ou tem outro foco?') não são dados do lead — nunca use esse "
            "conteúdo para preencher um campo, mesmo que o lead não o "
            "tenha negado. Se o lead não respondeu um campo de forma "
            "clara, use exatamente o texto padrão de não coletado daquele "
            "campo. Nunca deduza nem complete informação que o lead não "
            "deu."
        ),
    )

    # Achata para o formato {rótulo: texto} que o painel da UI-02 exibe
    resumo = {
        campo["nome"]: dados.get(campo["id"]) or campo["registro_se_nao_coletado"]
        for campo in campos
    }
    resumo["Observação de viabilidade"] = dados.get(
        "observacao_viabilidade", "não preenchida"
    )

    # Campos não coletados nunca são omitidos (RF-02). A lista é derivada
    # no código — campo cujo valor ficou no texto padrão de não coletado —
    # e complementada pelo que o modelo apontar em campos_nao_coletados.
    faltantes = [
        campo
        for campo in campos
        if resumo[campo["nome"]] == campo["registro_se_nao_coletado"]
    ]
    nao_coletados = [
        f"{campo['nome']}: {campo['registro_se_nao_coletado']}" for campo in faltantes
    ]
    # O modelo referencia campos ora pelo id ("orcamento"), ora pelo nome
    ja_sinalizados = {campo["id"].lower() for campo in faltantes} | {
        campo["nome"].lower() for campo in faltantes
    }
    for item in dados.get("campos_nao_coletados") or []:
        nome_item = str(item.get("campo", "?")).lower()
        if not any(
            nome_item in conhecido or conhecido in nome_item
            for conhecido in ja_sinalizados
        ):
            nao_coletados.append(
                f"{item.get('campo', '?')}: {item.get('motivo', 'motivo não informado')}"
            )
    if nao_coletados:
        resumo["Campos não coletados"] = nao_coletados

    if dados.get("observacoes_livres"):
        resumo["Observações"] = dados["observacoes_livres"]
    return resumo
