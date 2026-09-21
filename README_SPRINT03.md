# Sprint 03 — GoodWe / Goody — Guia de execução

Este pacote contém tudo que falta pra fechar a Sprint 03. Como o ambiente
usado para preparar isso não tem acesso à API da OpenAI, os itens que
dependem de rodar o modelo de verdade (memória, segurança, comparação de
modelos, comparativo antes×depois) vêm como **scripts prontos**, que geram
os relatórios automaticamente quando o grupo rodar com a própria
`OPENAI_API_KEY`.

## ⚠️ Antes de tudo

Se vocês já usaram alguma `OPENAI_API_KEY` em texto puro em algum chat,
mensagem ou repositório público, **revoguem essa chave em
platform.openai.com/api-keys e gerem uma nova**. Guardem só no `.env`
(que já deve estar no `.gitignore`, conforme o item 10 do enunciado).

## 1. Preparar o ambiente

```bash
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install openai-agents python-dotenv reportlab
```

Crie um arquivo `.env` na mesma pasta com:

```
OPENAI_API_KEY=sua-chave-aqui
SENHA_ADMIN=escolha-uma-senha-de-admin
```

## 2. Rodar o chatbot (memória + segurança + modo interativo)

```bash
python chatbot_agents_sdk.py
```

Isso roda automaticamente `demo_memoria()` (3 turnos, exemplo do Solar
Park) e `demo_seguranca()` (8 casos, incluindo Prompt Injection), imprime
tudo no terminal, e depois abre o modo interativo — onde dá pra escolher
"Usuário" ou "Administrador" (com senha) e testar na prática.

**Copiem as saídas impressas para `casos_teste_funcionais.md`.**

## 3. Comparar modelos de linguagem (Seção 5 do enunciado)

```bash
python comparar_modelos.py
```

Roda o mesmo conjunto de testes em 3 configurações (`gpt-4o-mini` e
Roda o mesmo conjunto de testes em 3 configurações. Por padrão:
`gpt-4o-mini` e `gpt-5-nano` (dois modelos diferentes — ajuste os nomes em
`CONFIGURACOES`, no topo do script, conforme os modelos disponíveis no seu
projeto OpenAI: rode `client.models.list()` pra ver quais você tem acesso),
mais uma variação de `temperature`. Mede tokens e latência, e
gera **`relatorio_modelos.md`** já com as tabelas preenchidas. Vocês só
precisam completar as seções "Diferenças percebidas", "Vantagens e
limitações" e "Modelo escolhido / justificativa" com a análise do grupo.

Isso faz chamadas reais à API (custa um pouco de dinheiro). Se quiserem
economizar, editem `CONFIGURACOES` no topo do script.

## 4. Comparar arquitetura antiga × nova (Seção 6 do enunciado)

```bash
python comparar_antes_depois.py
```

Precisa que `chatbot_teste.py` (Sprint 2) e `chatbot_agents_sdk.py`
(Sprint 03) estejam na mesma pasta. Roda o mesmo conjunto de testes nas
duas arquiteturas e gera **`comparativo_antes_depois.md`** com uma tabela
de métricas reais (latência, tokens, memória, guardrails).

## 5. Gerar o relatório de evolução em PDF (Seção 7 do enunciado)

```bash
python gerar_relatorio_evolucao.py
```

Gera `relatorio_evolucao.pdf` (3 páginas, dentro do limite de 5). Se vocês
já rodaram o passo 4 antes, este script **lê `comparativo_antes_depois.md`
automaticamente** e preenche a tabela da seção 7.3 com os números reais —
então a ordem recomendada é: passo 4 primeiro, depois este.

As seções 7.1, 7.2 e 7.4 já vêm redigidas com o conteúdo técnico real
desta sprint. A seção 7.5 (equipe) puxa de `equipe.txt` — editem esse
arquivo com nomes/RM/turma reais antes de rodar este script pela última
vez (ou editem direto o PDF/script, como preferirem).

## 6. Preencher a identificação da equipe

Editem `equipe.txt` com nomes, RM e turma reais. As responsabilidades já
estão distribuídas (uma por pessoa) — ajustem se não refletir quem
trabalhou em cada parte.

## 7. Checklist final de entregáveis (Seção 8 do enunciado)

- [x] Código-fonte (`chatbot_teste.py` legado + `chatbot_agents_sdk.py` novo)
- [ ] `relatorio_modelos.md` (rodar passo 3)
- [ ] Casos de teste preenchidos (`casos_teste_funcionais.md`, passo 2)
- [ ] `relatorio_evolucao.pdf` com números reais (passos 4 e 5)
- [ ] Repositório Git com histórico de commits de todos os integrantes
- [x] `equipe.txt` (preencher nomes/RM/turma reais)

## Arquivos deste pacote

| Arquivo | O que é |
|---|---|
| `chatbot_agents_sdk.py` | Núcleo conversacional novo (Sprint 03) |
| `testes_comuns.py` | Conjunto único de testes reusado pelos scripts de comparação |
| `comparar_modelos.py` | Gera `relatorio_modelos.md` |
| `comparar_antes_depois.py` | Gera `comparativo_antes_depois.md` |
| `gerar_relatorio_evolucao.py` | Gera `relatorio_evolucao.pdf` |
| `casos_teste_funcionais.md` | Tabelas de teste (funcionais/memória/segurança) a preencher |
| `equipe.txt` | Identificação da equipe (a preencher) |
| `relatorio_sprint03.md` | Documentação técnica do framework (seção 3.1) já preenchida |
| `relatorio_evolucao.pdf` | Relatório de evolução (seção 7) — gerado, com placeholders na 7.3/7.5 |
