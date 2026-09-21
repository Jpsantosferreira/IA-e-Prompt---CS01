# IA-e-Prompt---Challenge_Sprint
# ChargeGrid Assistant

## ✦ Integrantes ✦

| Nome | RM |
|---|---|
| Ana Julia Yumi Inoue | 569430 |
| João Pedro Santos Ferreira | 569202 |
| Maria Fernanda Dias Ribeiro | 569999 |
| Ulysses Gomes Soares de Souza | 573826 |
| Yasmin Cristina Carvalho Mayer | 573964 |

##  Problema Abordado 

O crescimento acelerado da frota de veículos elétricos no setor comercial expõe uma lacuna crítica na infraestrutura atual de recarga: a ausência de mecanismos integrados para gestão inteligente dos eletropostos. Olhando mais a fundo, os desafios desse problema são: ausência de controle de demanda; falta de registro estruturado de sessão; tarifação estática ou inexistente; silos entre hardware e software; e falta de orquestração centralizada.

##  Contexto 

Eletropostos comerciais, em sua maioria, operam de forma isolada e reativa — sem visibilidade sobre consumo em tempo real, sem controle de demanda e sem qualquer integração com sistemas de cobrança ou gerenciamento de sessão. Isso gera ineficiência operacional, desperdício energético e uma experiência precária tanto para o operador quanto para o usuário final.

##  Proposta do Chatbot 

Em nosso projeto, a IA é utilizada para otimização energética, automação operacional e assistência inteligente aos usuários. Além disso, a IA tem aplicações como: previsão de demanda; identificação de horários críticos; redistribuição de carga; análise de consumo; dentre outras.

Com tudo isso, entramos na proposta do nosso chatbot, o **ChargeGrid Assistant**, um assistente inteligente ("Goody") integrado a um aplicativo e a um painel administrativo. Ele tem como objetivo auxiliar usuários e administradores em tempo real.

**Suas funcionalidades:**
- **Usuários:** status da recarga; tempo restante; pagamentos; histórico de pagamento por mês; carregadores disponíveis; dados do veículo cadastrado; condomínios parceiros.
- **Administradores** *(acesso restrito por senha — ver Sprint 03 abaixo)*: alertas; falhas; monitoramento energético; relatórios rápidos dos eletropostos.

---

##  Tecnologias Selecionadas — Sprints 1 e 2 

### OpenAI API (`openai`)

É o núcleo inteligente do chatbot, mas originalmente frágil e limitado. Para melhorar isso, utilizamos a API com o modelo **gpt-4o-mini**, que entende linguagem natural, facilitando a comunicação com o usuário. O gpt-4o-mini foi escolhido por ser rápido e mais barato.

### Tool Calling

O Tool Calling é a maneira de identificar dados reais e/ou com base legítima; sem ele, a IA se basearia em "achar" que os dados são aqueles, inventando valores. Com essa ferramenta, o modelo consegue identificar a intenção do usuário, chamando a função correta, tornando o chatbot lógico e confiável.

### Roles do Chat

Temos 4 roles que estruturam o modelo com a API:
- **system**: define que é o chatbot (Goody), seu escopo e seu comportamento com o usuário.
- **user**: mensagem digitada pelo usuário.
- **assistant**: resposta gerada pelo modelo.
- **tool**: a resolução das funções chamadas, que em sua devolução auxiliam o modelo a formular respostas.

### Multi-turn

Relacionado à lista `historico`, que acumula todas as mensagens da sessão — enviada inteira a cada solicitação à API. Isso funciona como memória para o modelo, criando contexto em sua interação com os usuários.

### Base de Dados Simulada

`dados_usuario` e `dados_admin` simulam um banco de dados ou uma API de telemetria dos eletropostos. É a forma de testarmos o comportamento do chatbot sem depender de um sistema real por trás.

---

##  Evolução — Sprint 03 

Na Sprint 03, o núcleo conversacional foi refatorado para usar um **framework de agentes de IA**, mantendo a finalidade original do projeto. Resumo do que mudou (documentação técnica completa em `relatorio_sprint03.md`):

### Framework escolhido: OpenAI Agents SDK

Evolução natural do SDK `openai` já usado nas Sprints 1-2 — reaproveita as mesmas ferramentas (tools) e resolve nativamente memória, orquestração e guardrails, que antes eram feitos manualmente.

| Antes (Sprints 1-2) | Depois (Sprint 03) |
|---|---|
| Loop manual de tool calling (`processar_mensagem`) | `Runner.run()` orquestra tudo sozinho |
| Lista Python `historico` (memória perdida ao fechar o programa) | `SQLiteSession` (memória por sessão, persistente em disco) |
| Nenhum guardrail — só texto no system prompt | `input_guardrail` / `output_guardrail` (Prompt Injection, dados sensíveis, vazamento de instruções) |
| Um único conjunto de tools para todo mundo | Dois `Agent`s distintos (`goody_usuario` / `goody_admin`), com acesso administrativo protegido por senha |
| Só o `gpt-4o-mini` foi testado | Comparação sistemática entre modelos (`comparar_modelos.py`) |

### Memória conversacional

Implementada com `SQLiteSession`. Demonstração com 3+ turnos (exemplo do enunciado, condomínio Solar Park) disponível em `chatbot_agents_sdk.py::demo_memoria()`.

### Segurança e Guardrails

8 casos de teste, incluindo Prompt Injection, tentativa de sair do escopo GoodWe, pedido de aconselhamento jurídico/financeiro, orientação de segurança elétrica perigosa, invenção de especificação técnica, dado sensível no chat e tentativa de acesso administrativo sem autenticação. Ver `casos_teste_funcionais.md`.

### Controle de acesso usuário × administrador

Implementado em código (função `login()`), não no modelo: dois `Agent`s com toolsets diferentes, escolhidos **antes** de qualquer chamada à API, a partir de uma senha (`SENHA_ADMIN`, no `.env`). O modelo nunca "decide" quem é administrador.

### Comparação entre modelos de linguagem

`comparar_modelos.py` roda o mesmo conjunto de testes em múltiplas configurações (modelo + temperature) e gera `relatorio_modelos.md` automaticamente com os resultados.

### Comparativo antes × depois

`comparar_antes_depois.py` roda o mesmo conjunto de testes na arquitetura legada e na nova, medindo latência e tokens reais, e gera `comparativo_antes_depois.md`.

---

##  Arquivos do projeto

| Arquivo | Descrição |
|---|---|
| `chatbot_teste.py` | Núcleo conversacional original (Sprints 1-2) |
| `chatbot_agents_sdk.py` | Núcleo conversacional novo (Sprint 03, OpenAI Agents SDK) |
| `testes_comuns.py` | Conjunto único de testes reutilizado pelos scripts de comparação |
| `comparar_modelos.py` | Gera `relatorio_modelos.md` |
| `comparar_antes_depois.py` | Gera `comparativo_antes_depois.md` |
| `casos_teste_funcionais.md` | Casos de teste funcionais, de memória e de segurança |
| `relatorio_sprint03.md` | Documentação técnica do framework (justificativa, componentes, trade-offs) |
| `relatorio_evolucao.pdf` | Relatório de evolução (comparativo, problemas encontrados, equipe) |
