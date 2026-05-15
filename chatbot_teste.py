"""
╔══════════════════════════════════════════════════════════════════╗
║           ChargeGrid Assistant — Goody Chatbot (GoodWe)          ║
╚══════════════════════════════════════════════════════════════════╝

"""

# ──────────────────────────────────────────────
import json
from openai import OpenAI
from google.colab import userdata   

client = OpenAI(api_key=userdata.get("OPENAI_API_KEY"))


# ──────────────────────────────────────────────
# BASE DE DADOS SIMULADA
# ──────────────────────────────────────────────

dados_usuario = {
    "status_recarga": "75%",
    "tempo_restante": "20 minutos",
    "pagamento_atual": "R$ 40,00",
    "historico_pagamentos": {
        "abril": "R$ 55,00",
        "maio": "R$ 40,00",
    },
    "carregadores_disponiveis": 2,
}

dados_admin = {
    "alertas": ["SOBRECARGA NO ELETROPOSTO 05"],
    "falhas": ["FALHA NO PAGAMENTO — CLIENTE_X | ELETROPOSTO_04"],
    "monitoramento_energetico": "STATUS GERAL: NORMAL",
    "relatorio_eletropostos": {
        "ELETROPOSTO_01": "EM USO",
        "ELETROPOSTO_02": "VAZIO",
        "ELETROPOSTO_03": "FINALIZANDO PAGAMENTO",
        "ELETROPOSTO_04": "FALHA",
        "ELETROPOSTO_05": "SOBRECARGA",
    },
}


# ──────────────────────────────────────────────
#  FUNÇÕES DE FERRAMENTA (TOOLS)
# ──────────────────────────────────────────────

def status_recarga() -> str:
    return (
        f"🔋 Status atual da recarga: {dados_usuario['status_recarga']}\n"
        f"⏱️  Tempo estimado para conclusão: {dados_usuario['tempo_restante']}"
    )


def info_pagamento() -> str:
    historico = "\n".join(
        f"   • {mes.capitalize()}: {valor}"
        for mes, valor in dados_usuario["historico_pagamentos"].items()
    )
    return (
        f"💳 Cobrança da sessão atual: {dados_usuario['pagamento_atual']}\n"
        f"📋 Histórico de pagamentos:\n{historico}"
    )


def carregadores_disponiveis() -> str:
    qtd = dados_usuario["carregadores_disponiveis"]
    emoji = "✅" if qtd > 0 else "❌"
    return (
        f"{emoji} Carregadores disponíveis no momento: {qtd}\n"
        f"   Localize o mais próximo pelo mapa do aplicativo."
    )


def listar_alertas() -> str:
    if dados_admin["alertas"]:
        lista = "\n".join(f"   ⚠️  {a}" for a in dados_admin["alertas"])
        return f"🚨 Alertas ativos:\n{lista}"
    return "✅ Nenhum alerta ativo no momento."


def listar_falhas() -> str:
    if dados_admin["falhas"]:
        lista = "\n".join(f"   ❌ {f}" for f in dados_admin["falhas"])
        return f"🔧 Falhas registradas:\n{lista}"
    return "✅ Nenhuma falha registrada no momento."


def monitoramento_energetico() -> str:
    return f"⚡ Monitoramento energético:\n   {dados_admin['monitoramento_energetico']}"


def relatorio_eletropostos() -> str:
    def icone(status):
        if status == "EM USO":
            return "🟢"
        if status == "VAZIO":
            return "⚫"
        if "FINAL" in status:
            return "🟡"
        return "🔴"

    linhas = "\n".join(
        f"   {icone(s)} {ep}: {s}"
        for ep, s in dados_admin["relatorio_eletropostos"].items()
    )
    return f"📊 Relatório rápido dos eletropostos:\n{linhas}"


# ──────────────────────────────────────────────
# MAPA DE FERRAMENTAS
# ──────────────────────────────────────────────

FERRAMENTAS_DISPONIVEIS = {
    "status_recarga":          status_recarga,
    "info_pagamento":          info_pagamento,
    "carregadores_disponiveis": carregadores_disponiveis,
    "listar_alertas":          listar_alertas,
    "listar_falhas":           listar_falhas,
    "monitoramento_energetico": monitoramento_energetico,
    "relatorio_eletropostos":  relatorio_eletropostos,
}


# ──────────────────────────────────────────────
# DEFINIÇÃO DAS TOOLS PARA A API
# ──────────────────────────────────────────────

def _tool(nome: str, descricao: str) -> dict:
    """Helper que monta uma tool sem parâmetros."""
    return {
        "type": "function",
        "function": {
            "name": nome,
            "description": descricao,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }


tools = [
    _tool("status_recarga",
          "Retorna o status atual da recarga do veículo e o tempo restante."),
    _tool("info_pagamento",
          "Retorna o valor da sessão atual e o histórico de pagamentos do usuário."),
    _tool("carregadores_disponiveis",
          "Informa quantos carregadores estão disponíveis no momento."),
    _tool("listar_alertas",
          "Lista todos os alertas ativos no sistema (uso exclusivo do administrador)."),
    _tool("listar_falhas",
          "Lista todas as falhas registradas nos eletropostos (uso exclusivo do administrador)."),
    _tool("monitoramento_energetico",
          "Retorna o status geral do monitoramento energético da rede."),
    _tool("relatorio_eletropostos",
          "Exibe o relatório completo com o status de cada eletroposto."),
]


# ──────────────────────────────────────────────
# SYSTEM PROMPT
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """
Você é o Goody, assistente virtual da ChargeGrid (GoodWe).
Seu papel é ajudar usuários e administradores de eletropostos.

Para USUÁRIOS você pode:
  - Consultar o status da recarga em andamento
  - Informar o pagamento e histórico de cobranças
  - Verificar carregadores disponíveis

Para ADMINISTRADORES você pode:
  - Listar alertas ativos
  - Listar falhas registradas
  - Exibir o monitoramento energético
  - Gerar o relatório dos eletropostos

Use SEMPRE as ferramentas disponíveis para buscar os dados reais —
nunca invente valores. Responda de forma clara, amigável e em português.
"""


# ──────────────────────────────────────────────
# PROCESSAMENTO DA MENSAGEM
# ──────────────────────────────────────────────

def processar_mensagem(historico: list) -> str:
    """
    Recebe o histórico de mensagens (incluindo a última do usuário)
    e retorna a resposta final do assistente como string.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico,
        tools=tools,
        temperature=0,
        max_tokens=1000,
    )

    msg = completion.choices[0].message

    if not msg.tool_calls:
        return msg.content

    historico.append(msg)  

    for tool_call in msg.tool_calls:
        nome_funcao = tool_call.function.name
        funcao = FERRAMENTAS_DISPONIVEIS.get(nome_funcao)

        if funcao:
            resultado = funcao()
        else:
            resultado = f"Ferramenta '{nome_funcao}' não encontrada."

        historico.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": resultado,
        })

    completion_final = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico,
        tools=tools,
        temperature=0,
        max_tokens=1000,
    )

    return completion_final.choices[0].message.content


# ──────────────────────────────────────────────
# LOOP PRINCIPAL (INTERFACE NO TERMINAL)
# ──────────────────────────────────────────────

def iniciar_chatbot():
    banner = """
╔══════════════════════════════════════════════════╗
║   ⚡  ChargeGrid Assistant — Goody  ⚡           ║
║       Assistente Virtual GoodWe (OpenAI API)     ║
║  Digite 'sair' ou 'tchau' para encerrar          ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)


    historico = [{"role": "system", "content": SYSTEM_PROMPT}]

    DESPEDIDAS = ("tchau", "até", "ate", "bye", "sair", "exit", "fim", "encerrar")

    while True:
        try:
            entrada = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoody: Sessão encerrada. Até logo! ⚡")
            break

        if not entrada:
            continue

        if any(d in entrada.lower() for d in DESPEDIDAS):
            print("\nGoody: 👋 Até logo! Qualquer dúvida é só chamar. Boa recarga! ⚡\n")
            break

        historico.append({"role": "user", "content": entrada})

        resposta = processar_mensagem(historico)

        historico.append({"role": "assistant", "content": resposta})

        print(f"\nGoody: {resposta}\n")


# ──────────────────────────────────────────────
# START - COMEÇO!
# ──────────────────────────────────────────────

if __name__ == "__main__":
    iniciar_chatbot()