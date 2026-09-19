"""
relatorio_evolucao.pdf (Sprint 03, seção 7 — Relatório de evolução).
"""

import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontSize=15, spaceAfter=8, spaceBefore=4))
styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontSize=12, spaceAfter=6, spaceBefore=10))
styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontSize=9.5, leading=13, spaceAfter=6))
styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=8, leading=11, textColor=colors.grey))

story = []


def h1(texto):
    story.append(Paragraph(texto, styles["H1"]))


def h2(texto):
    story.append(Paragraph(texto, styles["H2"]))


def p(texto):
    story.append(Paragraph(texto, styles["Body"]))


def bullets(itens):
    story.append(
        ListFlowable(
            [ListItem(Paragraph(i, styles["Body"])) for i in itens],
            bulletType="bullet",
            leftIndent=14,
        )
    )


def tabela(dados, col_widths=None):
    t = Table(dados, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b57")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 8))



# Cabeçalho

story.append(Paragraph("Relatório de Evolução — Sprint 03", styles["Title"]))
story.append(Paragraph("EV Challenge — GoodWe · Chatbot Goody", styles["Heading3"]))
story.append(Spacer(1, 10))


# 7.1 Resumo da evolução

h1("7.1 Resumo da evolução (Sprints 1-2 → Sprint 03)")
p(
    "Nas Sprints 1 e 2, o chatbot Goody foi implementado em "
    "<b>chatbot_teste.py</b> com chamadas diretas ao SDK <b>openai</b> "
    "(client.chat.completions.create), tool calling controlado manualmente "
    "por um dicionário de funções (FERRAMENTAS_DISPONIVEIS) e memória de "
    "conversa mantida em uma lista Python (historico), sem persistência "
    "entre execuções e sem nenhum mecanismo de guardrail dedicado."
)
p(
    "Na Sprint 03, o núcleo conversacional foi refatorado para "
    "<b>chatbot_agents_sdk.py</b>, usando o <b>OpenAI Agents SDK</b> "
    "(pacote openai-agents). O que era um loop manual de tool calling virou "
    "uma única chamada a Runner.run(); a memória passou a ser gerenciada "
    "por SQLiteSession (persistente em disco, por sessão); e foram "
    "adicionados guardrails de entrada e saída, além de dois agentes "
    "separados (goody_usuario / goody_admin) para impor de verdade a "
    "separação de perfis que antes existia só como texto no system prompt."
)
p(
    "Também foram adicionados: uma tool parametrizada "
    "(consultar_historico_mes), novos dados simulados (veículo do usuário, "
    "condomínios parceiros, mais meses de histórico, mais eletropostos), e "
    "os scripts comparar_modelos.py / comparar_antes_depois.py, que rodam o "
    "mesmo conjunto de testes contra diferentes modelos/configurações e "
    "contra a arquitetura antiga, respectivamente, gerando relatorio_"
    "modelos.md e comparativo_antes_depois.md automaticamente."
)


# 7.2 Refatoração

h1("7.2 Refatoração — principais decisões técnicas")
bullets(
    [
        "<b>Agent + Runner</b> no lugar do loop manual: cada função de ferramenta virou uma "
        "@function_tool (schema gerado a partir de type hints/docstring), e o Runner decide "
        "sozinho quando chamar uma tool e quando responder diretamente.",
        "<b>SQLiteSession</b> no lugar da lista historico: memória por sessão/usuário, "
        "persistida em disco, sem precisar mais de .append() manual a cada turno.",
        "<b>input_guardrail / output_guardrail</b>: dois guardrails de entrada "
        "(prompt injection e dados sensíveis) e um de saída (vazamento de instruções internas), "
        "cada um interrompendo a execução via exceção própria do SDK "
        "(InputGuardrailTripwireTriggered / OutputGuardrailTripwireTriggered).",
        "<b>Dois Agents (usuário/admin)</b> com toolsets diferentes, escolhidos em código "
        "(função login(), com senha via getpass e .env) antes de qualquer chamada ao modelo — "
        "o controle de acesso não depende de o modelo \"decidir\" recusar um pedido.",
    ]
)
p(
    "<b>Trade-offs identificados:</b> o SDK é assíncrono por padrão (exige asyncio mesmo em um "
    "chatbot simples de terminal); o projeto fica mais acoplado especificamente ao pacote "
    "openai-agents (menos portátil entre provedores do que LangChain/LangGraph); e os guardrails "
    "aqui são baseados em palavras-chave — um ponto de partida didático, não um substituto para "
    "um classificador de moderação dedicado em produção."
)

# 7.3 Comparativo antes × depois

h1("7.3 Comparativo antes × depois")


def carregar_comparativo_md(caminho="comparativo_antes_depois.md"):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        conteudo = f.read()
    bloco = conteudo.split("## Tabela-resumo")
    if len(bloco) < 2:
        return None
    linhas_tabela = [l for l in bloco[1].splitlines() if l.strip().startswith("|")]
    linhas_tabela = [l for l in linhas_tabela if not re.match(r"^\|[\s\-\|]+\|$", l.strip())]
    dados = []
    for linha in linhas_tabela:
        celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
        dados.append(celulas)
    return dados if len(dados) > 1 else None


dados_reais = carregar_comparativo_md()

if dados_reais:
    p(
        "Tabela gerada automaticamente a partir da execução real de "
        "comparar_antes_depois.py (mesmo conjunto de testes rodado nas duas "
        "arquiteturas):"
    )
    tabela(dados_reais, col_widths=[6.5 * cm, 5 * cm, 5 * cm])
else:
    p(
        "<b>Tabela ainda não preenchida com dados reais.</b> Rode "
        "<b>comparar_antes_depois.py</b> com a OPENAI_API_KEY do grupo (ele "
        "roda o mesmo conjunto de testes na arquitetura legada e na nova, "
        "mede tokens e latência, e gera comparativo_antes_depois.md — depois "
        "é só rodar este script de novo, que ele preenche a tabela sozinho)."
    )
    tabela(
        [
            ["Métrica", "Legado (Sprints 1-2)", "Novo (Sprint 03)"],
            ["Latência média por turno (s)", "A preencher", "A preencher"],
            ["Tokens médios por turno", "A preencher", "A preencher"],
            ["Casos de segurança bloqueados", "0 (sem guardrails)", "A preencher"],
            ["Memória entre turnos", "Lista Python (perdida ao fechar)", "SQLiteSession (persiste em disco)"],
            ["Controle de acesso admin", "Nenhum (apenas texto no prompt)", "Dois Agents distintos, decidido em código"],
        ],
        col_widths=[6.5 * cm, 5 * cm, 5 * cm],
    )

p(
    "<b>Leitura qualitativa (independente dos números):</b> a nova arquitetura já é "
    "superior em dois pontos que não dependem de execução — memória persistente "
    "(vs. perdida a cada reinício) e controle de acesso real (vs. inexistente). "
    "Em latência/tokens, a expectativa é que a Sprint 03 gaste um pouco mais por "
    "turno complexo (o Runner pode fazer chamadas extra de guardrail/orquestração), "
    "o que deve ser confirmado ou refutado pelos números reais acima."
)


# 7.4 Problemas encontrados e soluções

h1("7.4 Problemas encontrados e soluções")

h2("Problema 1 — SDK assíncrono em um chatbot originalmente síncrono")
p(
    "<b>Problema:</b> chatbot_teste.py era 100% síncrono; o Agents SDK expõe "
    "Runner.run() como uma coroutine (await), o que quebra a compatibilidade "
    "direta com o loop de terminal original (input() bloqueante dentro de "
    "while True)."
)
p(
    "<b>Alternativas consideradas:</b> (a) chamar asyncio.run(Runner.run(...)) "
    "a cada mensagem, dentro do loop síncrono original; (b) reescrever o "
    "programa inteiro como uma função async, usando asyncio.run() só uma vez "
    "no entrypoint."
)
p(
    "<b>Solução adotada:</b> opção (b) — todo o núcleo interativo "
    "(iniciar_chatbot, demo_memoria, demo_seguranca) virou async, com um "
    "único asyncio.run(main()) no final do arquivo."
)
p(
    "<b>Justificativa:</b> a opção (a) recriaria um novo event loop a cada "
    "mensagem, o que é ineficiente e pode gerar erros quando o SDK já mantém "
    "estado assíncrono internamente (ex.: sessões, streaming). Escrever o "
    "programa como async de ponta a ponta é o padrão recomendado pelo "
    "próprio SDK e evita essa armadilha."
)

h2("Problema 2 — separação usuário/administrador era apenas texto, não controle de acesso")
p(
    "<b>Problema:</b> na primeira versão migrada, existia um único Agent com "
    "todas as tools (inclusive as administrativas); a diferenciação entre "
    "usuário comum e administrador estava só na redação do system prompt "
    "(\"uso exclusivo do administrador\"). Isso não impede nada de verdade: "
    "qualquer pessoa podia pedir \"liste os alertas ativos\" e o modelo "
    "chamava a tool normalmente."
)
p(
    "<b>Alternativas consideradas:</b> (a) manter um único Agent e confiar "
    "apenas em reforçar o texto do system prompt; (b) adicionar um "
    "input_guardrail que tenta detectar \"pedidos de administrador\" vindos "
    "de um usuário comum; (c) criar dois Agents distintos (goody_usuario / "
    "goody_admin), cada um com seu próprio toolset, escolhidos em código "
    "após uma etapa de login com senha."
)
p(
    "<b>Solução adotada:</b> opção (c)."
)
p(
    "<b>Justificativa:</b> a opção (a) é frágil — texto de system prompt "
    "pode ser contornado por prompt injection. A opção (b) ainda depende do "
    "guardrail \"adivinhar\" corretamente a intenção, o que é uma heurística "
    "sujeita a falso negativo. A opção (c) é a única que remove fisicamente "
    "a capacidade (as tools administrativas simplesmente não existem para o "
    "agente de usuário comum), então nenhuma manipulação de prompt consegue "
    "reverter essa restrição — a decisão de acesso é feita fora do modelo, "
    "em código determinístico."
)


# 7.5 Divisão da equipe

h1("7.5 Divisão da equipe")


def carregar_equipe_txt(caminho="equipe.txt"):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        conteudo = f.read()

    blocos = re.split(r"\nIntegrante \d+\n", "\n" + conteudo)[1:]
    linhas = []
    for i, bloco in enumerate(blocos, start=1):
        nome = re.search(r"Nome:\s*(.+)", bloco)
        rm = re.search(r"RM:\s*(.+)", bloco)
        resp = re.search(r"Responsabilidade principal:\s*(.+)", bloco)
        nome = nome.group(1).strip() if nome else "A preencher"
        rm = rm.group(1).strip() if rm else "A preencher"
        resp = resp.group(1).strip() if resp else "A preencher"
        linhas.append([str(i), f"{nome} / {rm}", resp])

    if not linhas:
        return None
    return [["Integrante", "Nome / RM", "Responsabilidade principal"]] + linhas


dados_equipe = carregar_equipe_txt()

if dados_equipe:
    algum_preenchido = any("[PREENCHER]" not in linha[1] for linha in dados_equipe[1:])
    if algum_preenchido:
        p("Equipe lida automaticamente de equipe.txt:")
    else:
        p(
            "Estrutura lida de equipe.txt (nomes e RM ainda não preenchidos pelo "
            "grupo — edite equipe.txt e rode este script de novo):"
        )
    tabela(dados_equipe, col_widths=[2 * cm, 5.5 * cm, 9 * cm])
else:
    p(
        "equipe.txt não encontrado ou fora do formato esperado — usando uma "
        "distribuição padrão de 5 integrantes como referência:"
    )
    tabela(
        [
            ["Integrante", "Nome / RM", "Responsabilidade principal"],
            ["1", "João Pedro Santos Ferreira / RM569202", "Framework de agentes e orquestração (Agent, Runner, function_tools)"],
            ["2", "Ana Julia Yumi Inoue / RM569430 ", "Memória conversacional e controle de acesso (SQLiteSession, login usuário/admin)"],
            ["3", "Maria Fernanda Dias  / RM569999", "Segurança e guardrails (Prompt Injection e demais casos de teste)"],
            ["4", "Ulysses Gomes Soares / RM573826", "Comparação entre modelos de linguagem (comparar_modelos.py, relatorio_modelos.md)"],
            ["5", "Yasmin Cristina Mayer / RM573964", "Comparativo antes×depois e relatório de evolução (comparar_antes_depois.py, este PDF)"],
        ],
        col_widths=[2 * cm, 5.5 * cm, 9 * cm],
    )

story.append(Spacer(1, 6))
story.append(
    Paragraph(
        "Arquivos-fonte: chatbot_teste.py, chatbot_agents_sdk.py, "
        "testes_comuns.py, comparar_modelos.py, comparar_antes_depois.py.",
        styles["Small"],
    )
)

doc = SimpleDocTemplate(
    "relatorio_evolucao.pdf",
    pagesize=A4,
    topMargin=1.6 * cm,
    bottomMargin=1.6 * cm,
    leftMargin=1.8 * cm,
    rightMargin=1.8 * cm,
    title="Relatório de Evolução — Sprint 03 — GoodWe",
)
doc.build(story)
print("relatorio_evolucao.pdf gerado.")
