"""
╔══════════════════════════════════════════════════════════════════╗
║           ChargeGrid Assistant — Goody Chatbot (GoodWe)         ║
╚══════════════════════════════════════════════════════════════════╝

Chatbot de teste para auxiliar usuários e administradores de
eletropostos GoodWe com status de recarga, pagamentos e alertas.
"""

# ──────────────────────────────────────────────
# PASSO 1: BASE DE DADOS SIMULADA
# Dicionários que simulam os dados em tempo real
# do sistema (usuários e administradores).
# ──────────────────────────────────────────────

dados_usuario = {
    "status_recarga": "75%",
    "tempo_restante": "20 minutos",
    "pagamento_atual": "R$ 40,00",
    "historico_pagamentos": {
        "abril": "R$ 55,00",
        "maio": "R$ 40,00"
    },
    "carregadores_disponiveis": 2
}

dados_admin = {
    "alertas": ["SOBRECARGA NO ELETROPOSTO 05"],
    "falhas": [
        "FALHA NO PAGAMENTO — CLIENTE_X | ELETROPOSTO_04"
    ],
    "monitoramento_energetico": "STATUS GERAL: NORMAL",
    "relatorio_eletropostos": {
        "ELETROPOSTO_01": "EM USO",
        "ELETROPOSTO_02": "VAZIO",
        "ELETROPOSTO_03": "FINALIZANDO PAGAMENTO",
        "ELETROPOSTO_04": "FALHA",
        "ELETROPOSTO_05": "SOBRECARGA"
    }
}


# ──────────────────────────────────────────────
# PASSO 2: FUNÇÕES DE RESPOSTA
# Cada função é responsável por montar e
# retornar uma resposta específica para o usuário.
# ──────────────────────────────────────────────

def resposta_status_recarga():
    return (
        f"🔋 Status atual da sua recarga: {dados_usuario['status_recarga']}\n"
        f"⏱️  Tempo estimado para conclusão: {dados_usuario['tempo_restante']}"
    )


def resposta_pagamento():
    historico = "\n".join(
        f"   • {mes.capitalize()}: {valor}"
        for mes, valor in dados_usuario["historico_pagamentos"].items()
    )
    return (
        f"💳 Cobrança da sessão atual: {dados_usuario['pagamento_atual']}\n"
        f"📋 Histórico de pagamentos:\n{historico}"
    )


def resposta_carregadores():
    qtd = dados_usuario["carregadores_disponiveis"]
    emoji = "✅" if qtd > 0 else "❌"
    return (
        f"{emoji} Carregadores disponíveis no momento: {qtd}\n"
        f"   Localize o mais próximo pelo mapa do aplicativo."
    )


def resposta_alertas():
    if dados_admin["alertas"]:
        lista = "\n".join(f"   ⚠️  {a}" for a in dados_admin["alertas"])
        return f"🚨 Alertas ativos:\n{lista}"
    return "✅ Nenhum alerta ativo no momento."


def resposta_falhas():
    if dados_admin["falhas"]:
        lista = "\n".join(f"   ❌ {f}" for f in dados_admin["falhas"])
        return f"🔧 Falhas registradas:\n{lista}"
    return "✅ Nenhuma falha registrada no momento."


def resposta_monitoramento():
    return f"⚡ Monitoramento energético:\n   {dados_admin['monitoramento_energetico']}"


def resposta_relatorio():
    linhas = "\n".join(
        f"   {'🟢' if s == 'EM USO' else '⚫' if s == 'VAZIO' else '🟡' if 'FINAL' in s else '🔴'} {ep}: {s}"
        for ep, s in dados_admin["relatorio_eletropostos"].items()
    )
    return f"📊 Relatório rápido dos eletropostos:\n{linhas}"


# ──────────────────────────────────────────────
# PASSO 3: MAPA DE INTENÇÕES
# Liga palavras-chave às funções de resposta.
# O chatbot percorre este dicionário para
# encontrar qual resposta acionar.
# ──────────────────────────────────────────────

intencoes = {
    # Usuário
    ("status", "recarga", "carregando", "bateria", "carga"):
        resposta_status_recarga,

    ("pagamento", "pagar", "cobrança", "valor", "histórico", "historico", "fatura"):
        resposta_pagamento,

    ("carregador", "disponível", "disponivel", "vaga", "livre", "disponibilidade"):
        resposta_carregadores,

    # Administrador
    ("alerta", "alertas", "atenção", "atenção", "urgente"):
        resposta_alertas,

    ("falha", "falhas", "erro", "problema", "quebrado"):
        resposta_falhas,

    ("energia", "energético", "energetico", "monitoramento", "consumo", "carga geral"):
        resposta_monitoramento,

    ("relatório", "relatorio", "relatório", "eletroposto", "eletropostos", "status geral"):
        resposta_relatorio,
}

SAUDACOES = ("oi", "olá", "ola", "hello", "boa", "bom", "hi", "hey")
DESPEDIDAS = ("tchau", "até", "ate", "bye", "sair", "exit", "fim", "encerrar")
AJUDA      = ("ajuda", "help", "menu", "opções", "opcoes", "comandos", "o que")


# ──────────────────────────────────────────────
# PASSO 4: FUNÇÕES AUXILIARES
# Normalização do texto e roteamento central.
# ──────────────────────────────────────────────

def normalizar(texto: str) -> str:
    """Remove espaços extras e converte para minúsculas."""
    return texto.strip().lower()


def menu_ajuda() -> str:
    return (
        "📋 Posso te ajudar com:\n"
        "  👤 Para USUÁRIOS:\n"
        "     • status da recarga\n"
        "     • pagamento / histórico\n"
        "     • carregadores disponíveis\n\n"
        "  🔧 Para ADMINISTRADORES:\n"
        "     • alertas\n"
        "     • falhas\n"
        "     • monitoramento energético\n"
        "     • relatório dos eletropostos\n\n"
        "  Digite sua pergunta ou escolha um dos tópicos acima."
    )


def processar_mensagem(mensagem: str) -> str:
    """
    Recebe a mensagem do usuário e retorna a resposta adequada.
    Fluxo:
      1. Normaliza o texto
      2. Verifica saudações / despedidas / ajuda
      3. Percorre o mapa de intenções procurando palavras-chave
      4. Se nada casar, retorna mensagem de não entendimento
    """
    texto = normalizar(mensagem)

    # Saudação
    if any(s in texto for s in SAUDACOES):
        return (
            "👋 Olá! Eu sou o **Goody**, assistente virtual da GoodWe.\n"
            "Estou aqui para ajudar com recargas, pagamentos, alertas e muito mais.\n\n"
            + menu_ajuda()
        )

    # Despedida
    if any(d in texto for d in DESPEDIDAS):
        return "👋 Até logo! Qualquer dúvida é só chamar. Boa recarga! ⚡"

    # Ajuda / menu
    if any(a in texto for a in AJUDA):
        return menu_ajuda()

    # Percorre intenções
    for palavras_chave, funcao_resposta in intencoes.items():
        if any(palavra in texto for palavra in palavras_chave):
            return funcao_resposta()

    # Fallback
    return (
        "🤔 Não entendi muito bem. Pode reformular?\n\n"
        + menu_ajuda()
    )


# ──────────────────────────────────────────────
# PASSO 5: LOOP PRINCIPAL (INTERFACE NO TERMINAL)
# Exibe o banner, inicia o loop de conversa e
# chama processar_mensagem() a cada entrada.
# ──────────────────────────────────────────────

def iniciar_chatbot():
    banner = """
╔══════════════════════════════════════════════════╗
║   ⚡  ChargeGrid Assistant — Goody  ⚡           ║
║       Assistente Virtual GoodWe                  ║
║  Digite 'ajuda' para ver os comandos disponíveis ║
║  Digite 'sair' para encerrar                     ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)

    while True:
        try:
            entrada = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoody: Sessão encerrada. Até logo! ⚡")
            break

        if not entrada:
            continue

        resposta = processar_mensagem(entrada)
        print(f"\nGoody: {resposta}\n")

        # Encerra o loop se o usuário se despedir
        if any(d in normalizar(entrada) for d in DESPEDIDAS):
            break


# ──────────────────────────────────────────────
# PASSO 6: PONTO DE ENTRADA
# Só executa se o arquivo for rodado diretamente.
# ──────────────────────────────────────────────

if __name__ == "__main__":
    iniciar_chatbot()