"""
╔══════════════════════════════════════════════════════════════════╗
║  Sprint 03 — Seção 5: Comparação entre modelos de linguagem      ║
╚══════════════════════════════════════════════════════════════════╝

"""

import asyncio
import json
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from agents import (
    Agent,
    InputGuardrailTripwireTriggered,
    ModelSettings,
    OutputGuardrailTripwireTriggered,
    Runner,
    SQLiteSession,
)

from chatbot_agents_sdk import (
    INSTRUCOES_USUARIO,
    TOOLS_USUARIO,
    bloquear_dados_sensiveis,
    bloquear_prompt_injection,
    bloquear_vazamento_de_instrucoes,
)
from testes_comuns import CASOS_SEGURANCA, TESTES_FUNCIONAIS, TURNOS_MEMORIA

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Defina OPENAI_API_KEY no seu .env antes de rodar este script.")



# Configurações a comparar:  2 modelos + 1 variação de parâmetro


CONFIGURACOES = [
    {"id": "gpt-4o-mini (temperature=0)", "model": "gpt-4o-mini", "temperature": 0.0},
    {"id": "gpt-5-nano (padrão)", "model": "gpt-5-nano", "temperature": None},
    {"id": "gpt-4o-mini (temperature=0.8)", "model": "gpt-4o-mini", "temperature": 0.8},
]


def montar_agente(model: str, temperature: float | None) -> Agent:
    kwargs = dict(
        name=f"Goody ({model}, t={temperature if temperature is not None else 'padrão'})",
        instructions=INSTRUCOES_USUARIO,
        model=model,
        tools=TOOLS_USUARIO,
        input_guardrails=[bloquear_prompt_injection, bloquear_dados_sensiveis],
        output_guardrails=[bloquear_vazamento_de_instrucoes],
    )
    if temperature is not None:
        kwargs["model_settings"] = ModelSettings(temperature=temperature)
    return Agent(**kwargs)


async def rodar_mensagem(agente: Agent, mensagem: str, sessao: SQLiteSession) -> dict:
    inicio = time.perf_counter()
    try:
        resultado = await Runner.run(agente, mensagem, session=sessao)
        latencia = time.perf_counter() - inicio
        uso = resultado.context_wrapper.usage
        return {
            "bloqueado": False,
            "resposta": resultado.final_output,
            "latencia_s": round(latencia, 2),
            "tokens_entrada": uso.input_tokens,
            "tokens_saida": uso.output_tokens,
            "tokens_total": uso.total_tokens,
        }
    except InputGuardrailTripwireTriggered:
        latencia = time.perf_counter() - inicio
        return {
            "bloqueado": True,
            "resposta": "[bloqueado - input guardrail]",
            "latencia_s": round(latencia, 2),
            "tokens_entrada": None,
            "tokens_saida": None,
            "tokens_total": None,
        }
    except OutputGuardrailTripwireTriggered:
        latencia = time.perf_counter() - inicio
        return {
            "bloqueado": True,
            "resposta": "[bloqueado - output guardrail]",
            "latencia_s": round(latencia, 2),
            "tokens_entrada": None,
            "tokens_saida": None,
            "tokens_total": None,
        }


async def rodar_configuracao(config: dict) -> dict:
    agente = montar_agente(config["model"], config["temperature"])
    resultados = {"funcionais": [], "memoria": [], "seguranca": []}

    # Testes funcionais — cada um em uma sessão nova (não dependem de contexto)
    for caso in TESTES_FUNCIONAIS:
        sessao = SQLiteSession(f"cmp_{config['id']}_{caso['nome']}")
        r = await rodar_mensagem(agente, caso["mensagem"], sessao)
        resultados["funcionais"].append({"nome": caso["nome"], **r})

    # Teste de memória — mesma sessão nos 3 turnos
    sessao_memoria = SQLiteSession(f"cmp_{config['id']}_memoria")
    for i, mensagem in enumerate(TURNOS_MEMORIA, start=1):
        r = await rodar_mensagem(agente, mensagem, sessao_memoria)
        resultados["memoria"].append({"turno": i, "mensagem": mensagem, **r})

    # Casos de segurança — cada um em uma sessão nova (isolados)
    for caso in CASOS_SEGURANCA:
        sessao = SQLiteSession(f"cmp_{config['id']}_seg_{caso['nome']}")
        r = await rodar_mensagem(agente, caso["mensagem"], sessao)
        resultados["seguranca"].append({"nome": caso["nome"], **r})

    return resultados


async def main():
    print("Rodando comparação entre modelos... isso faz chamadas reais à API.")
    todos_resultados = {}
    for config in CONFIGURACOES:
        print(f"\n▶ Configuração: {config['id']}")
        todos_resultados[config["id"]] = await rodar_configuracao(config)
        print(f"  ✅ concluído.")

    with open("resultados_modelos.json", "w", encoding="utf-8") as f:
        json.dump(todos_resultados, f, ensure_ascii=False, indent=2)
    print("\nResultados brutos salvos em resultados_modelos.json")

    gerar_relatorio_markdown(todos_resultados)
    print("relatorio_modelos.md gerado com sucesso.")


def _media(valores):
    valores = [v for v in valores if v is not None]
    return round(sum(valores) / len(valores), 2) if valores else None


def gerar_relatorio_markdown(resultados: dict) -> None:
    linhas = []
    linhas.append("# relatorio_modelos.md — Comparação entre modelos de linguagem\n")
    linhas.append(
        f"_Gerado automaticamente por `comparar_modelos.py` em "
        f"{datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}._\n"
    )

    linhas.append("## 1. Modelos e configurações avaliados\n")
    linhas.append("| Configuração | Modelo | Temperature |")
    linhas.append("|---|---|---|")
    for c in CONFIGURACOES:
        temp_exibida = c["temperature"] if c["temperature"] is not None else "padrão (sem override)"
        linhas.append(f"| {c['id']} | {c['model']} | {temp_exibida} |")
    linhas.append("")

    linhas.append("## 2. Conjunto de testes utilizado\n")
    linhas.append(
        f"Mesmo conjunto para todas as configurações (`testes_comuns.py`): "
        f"{len(TESTES_FUNCIONAIS)} testes funcionais, "
        f"{len(TURNOS_MEMORIA)} turnos de memória, "
        f"{len(CASOS_SEGURANCA)} casos de segurança.\n"
    )

    linhas.append("## 3. Resultados quantitativos\n")
    linhas.append(
        "| Configuração | Latência média (s) | Tokens médios/turno | "
        "Testes de segurança bloqueados | Total de chamadas ao modelo |"
    )
    linhas.append("|---|---|---|---|---|")
    for config in CONFIGURACOES:
        cid = config["id"]
        r = resultados[cid]
        todas_interacoes = r["funcionais"] + r["memoria"] + r["seguranca"]
        latencias = [x["latencia_s"] for x in todas_interacoes]
        tokens = [x["tokens_total"] for x in todas_interacoes]
        bloqueados = sum(1 for x in r["seguranca"] if x["bloqueado"])
        linhas.append(
            f"| {cid} | {_media(latencias)} | {_media(tokens)} | "
            f"{bloqueados}/{len(r['seguranca'])} | {len(todas_interacoes)} |"
        )
    linhas.append("")

    linhas.append("## 4. Resultados detalhados por configuração\n")
    for config in CONFIGURACOES:
        cid = config["id"]
        r = resultados[cid]
        linhas.append(f"### {cid}\n")

        linhas.append("**Testes funcionais**\n")
        linhas.append("| Teste | Bloqueado | Latência (s) | Tokens | Resposta (resumo) |")
        linhas.append("|---|---|---|---|---|")
        for x in r["funcionais"]:
            resumo = (x["resposta"] or "")[:120].replace("\n", " ")
            linhas.append(
                f"| {x['nome']} | {x['bloqueado']} | {x['latencia_s']} | "
                f"{x['tokens_total']} | {resumo} |"
            )
        linhas.append("")

        linhas.append("**Memória (3 turnos)**\n")
        for x in r["memoria"]:
            linhas.append(f"- Turno {x['turno']} — \"{x['mensagem']}\"")
            linhas.append(f"  - Resposta: {x['resposta']}")
        linhas.append("")

        linhas.append("**Segurança**\n")
        linhas.append("| Caso | Bloqueado pelo guardrail | Resposta (resumo) |")
        linhas.append("|---|---|---|")
        for x in r["seguranca"]:
            resumo = (x["resposta"] or "")[:120].replace("\n", " ")
            linhas.append(f"| {x['nome']} | {x['bloqueado']} | {resumo} |")
        linhas.append("")

    linhas.append("## 5. Diferenças percebidas entre os modelos\n")
    linhas.append(
        "_(preencher com base nas tabelas acima — ex.: algum modelo respondeu "
        "com mais detalhes? algum foi mais rápido? algum resistiu melhor aos "
        "casos de segurança? o aumento de temperature mudou o comportamento "
        "nos casos de segurança ou só no tom das respostas funcionais?)_\n"
    )

    linhas.append("## 6. Vantagens e limitações de cada modelo\n")
    linhas.append("_(preencher — considerar custo, velocidade e qualidade percebida)_\n")

    linhas.append("## 7. Modelo escolhido para a versão final e justificativa\n")
    linhas.append(
        "_(preencher — a decisão deve se basear nos números da seção 3 e nas "
        "observações da seção 5/6, não apenas em preferência do grupo)_\n"
    )

    with open("relatorio_modelos.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


if __name__ == "__main__":
    asyncio.run(main())
