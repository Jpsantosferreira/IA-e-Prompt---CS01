"""
╔══════════════════════════════════════════════════════════════════╗
║  Sprint 03 — Seção 6: Comparativo antes × depois                 ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    Runner,
    SQLiteSession,
)

import chatbot_teste as legado
from chatbot_agents_sdk import goody_usuario
from testes_comuns import CASOS_SEGURANCA, TESTES_FUNCIONAIS, TURNOS_MEMORIA

load_dotenv()

_registro_uso_legado: list = []
_create_original = legado.client.chat.completions.create


def _create_instrumentado(*args, **kwargs):
    resposta = _create_original(*args, **kwargs)
    _registro_uso_legado.append(resposta.usage)
    return resposta


legado.client.chat.completions.create = _create_instrumentado


def rodar_legado(mensagem: str, historico: list) -> dict:
    inicio = time.perf_counter()
    historico.append({"role": "user", "content": mensagem})
    antes = len(_registro_uso_legado)
    resposta = legado.processar_mensagem(historico)
    depois = len(_registro_uso_legado)
    historico.append({"role": "assistant", "content": resposta})
    latencia = time.perf_counter() - inicio

    usos = [u for u in _registro_uso_legado[antes:depois] if u is not None]
    tokens_total = sum(u.total_tokens for u in usos) if usos else None
    return {
        "bloqueado": False,
        "resposta": resposta,
        "latencia_s": round(latencia, 2),
        "tokens_total": tokens_total,
        "chamadas_ao_modelo": len(usos),
    }


async def rodar_novo(mensagem: str, sessao: SQLiteSession) -> dict:
    inicio = time.perf_counter()
    try:
        resultado = await Runner.run(goody_usuario, mensagem, session=sessao)
        latencia = time.perf_counter() - inicio
        uso = resultado.context_wrapper.usage
        return {
            "bloqueado": False,
            "resposta": resultado.final_output,
            "latencia_s": round(latencia, 2),
            "tokens_total": uso.total_tokens,
            "chamadas_ao_modelo": uso.requests,
        }
    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered):
        latencia = time.perf_counter() - inicio
        return {
            "bloqueado": True,
            "resposta": "[bloqueado por guardrail]",
            "latencia_s": round(latencia, 2),
            "tokens_total": None,
            "chamadas_ao_modelo": None,
        }


async def rodar_tudo() -> dict:
    resultados = {"legado": {"funcionais": [], "memoria": [], "seguranca": []},
                  "novo": {"funcionais": [], "memoria": [], "seguranca": []}}

    # --- Testes funcionais (contexto novo a cada teste) ---
    for caso in TESTES_FUNCIONAIS:
        hist = [{"role": "system", "content": legado.SYSTEM_PROMPT}]
        r_legado = rodar_legado(caso["mensagem"], hist)
        resultados["legado"]["funcionais"].append({"nome": caso["nome"], **r_legado})

        sessao = SQLiteSession(f"antesdepois_novo_{caso['nome']}")
        r_novo = await rodar_novo(caso["mensagem"], sessao)
        resultados["novo"]["funcionais"].append({"nome": caso["nome"], **r_novo})


    hist_memoria = [{"role": "system", "content": legado.SYSTEM_PROMPT}]
    sessao_memoria = SQLiteSession("antesdepois_novo_memoria")
    for i, mensagem in enumerate(TURNOS_MEMORIA, start=1):
        r_legado = rodar_legado(mensagem, hist_memoria)
        resultados["legado"]["memoria"].append({"turno": i, "mensagem": mensagem, **r_legado})

        r_novo = await rodar_novo(mensagem, sessao_memoria)
        resultados["novo"]["memoria"].append({"turno": i, "mensagem": mensagem, **r_novo})


    for caso in CASOS_SEGURANCA:
        hist = [{"role": "system", "content": legado.SYSTEM_PROMPT}]
        r_legado = rodar_legado(caso["mensagem"], hist)
        resultados["legado"]["seguranca"].append({"nome": caso["nome"], **r_legado})

        sessao = SQLiteSession(f"antesdepois_novo_seg_{caso['nome']}")
        r_novo = await rodar_novo(caso["mensagem"], sessao)
        resultados["novo"]["seguranca"].append({"nome": caso["nome"], **r_novo})

    return resultados


def _media(valores):
    valores = [v for v in valores if v is not None]
    return round(sum(valores) / len(valores), 2) if valores else None


def gerar_relatorio(resultados: dict) -> None:
    linhas = []
    linhas.append("# comparativo_antes_depois.md\n")
    linhas.append(
        f"_Gerado automaticamente por `comparar_antes_depois.py` em "
        f"{datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}._\n"
    )

    linhas.append("## Tabela-resumo (para a seção 7.3 do relatório de evolução)\n")
    linhas.append(
        "| Métrica | Legado (Sprints 1-2) | Novo (Sprint 03) |"
    )
    linhas.append("|---|---|---|")

    for chave, label in [("funcionais", "Testes funcionais"), ("memoria", "Memória (3 turnos)"), ("seguranca", "Segurança")]:
        leg = resultados["legado"][chave]
        nov = resultados["novo"][chave]
        linhas.append(
            f"| Latência média — {label} (s) | {_media([x['latencia_s'] for x in leg])} "
            f"| {_media([x['latencia_s'] for x in nov])} |"
        )
        linhas.append(
            f"| Tokens médios — {label} | {_media([x['tokens_total'] for x in leg])} "
            f"| {_media([x['tokens_total'] for x in nov])} |"
        )

    bloqueados_legado = sum(1 for x in resultados["legado"]["seguranca"] if x["bloqueado"])
    bloqueados_novo = sum(1 for x in resultados["novo"]["seguranca"] if x["bloqueado"])
    linhas.append(
        f"| Casos de segurança bloqueados por guardrail | {bloqueados_legado}/"
        f"{len(resultados['legado']['seguranca'])} (sem guardrails) | {bloqueados_novo}/"
        f"{len(resultados['novo']['seguranca'])} |"
    )
    linhas.append(
        "| Memória entre turnos | Lista Python em memória (perdida ao fechar o programa) "
        "| SQLiteSession (persiste em disco) |"
    )
    linhas.append("")

    linhas.append("## Detalhes por caso\n")
    for chave, label in [("funcionais", "Testes funcionais"), ("memoria", "Memória"), ("seguranca", "Segurança")]:
        linhas.append(f"### {label}\n")
        linhas.append("| Caso | Legado — bloqueado | Legado — latência (s) | Legado — tokens | Novo — bloqueado | Novo — latência (s) | Novo — tokens |")
        linhas.append("|---|---|---|---|---|---|---|")
        leg = resultados["legado"][chave]
        nov = resultados["novo"][chave]
        for l, n in zip(leg, nov):
            nome = l.get("nome") or f"Turno {l.get('turno')}"
            linhas.append(
                f"| {nome} | {l['bloqueado']} | {l['latencia_s']} | {l['tokens_total']} | "
                f"{n['bloqueado']} | {n['latencia_s']} | {n['tokens_total']} |"
            )
        linhas.append("")

    with open("comparativo_antes_depois.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    with open("resultados_antes_depois.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)


async def main():
    print("Rodando o mesmo conjunto de testes na arquitetura legada e na nova...")
    resultados = await rodar_tudo()
    gerar_relatorio(resultados)
    print("Gerado: comparativo_antes_depois.md e resultados_antes_depois.json")


if __name__ == "__main__":
    asyncio.run(main())
