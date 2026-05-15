# IA-e-Prompt---CS01
**ChargeGrid Assistant**

✦ Integrantes ✦ 

João Pedro Santos Ferreira - RM: 569202   
Maria Beatriz Braga de Lima - RM: 570501   
Ulysses Gomes Soares de Souza - RM: 573826   
Yasmin Cristina Carvalho Mayer - RM: 573964  

⚡ Problema Abordado ⚡    

O crescimento acelerado da frota de veículos elétricos no setor comercial expõe uma lacuna crítica na infraestrutura atual de recarga: a ausência de mecanismos integrados para gestão inteligente dos eletropostos. Olhando mais afundo, os desafios desse problema são: Ausência de controle de demanda; Falta de registro estruturado de sessão; Tarifação estática ou inexistente; Silos entre hardware e software e Falta de orquestração centralizada.

📁 Contexto 📁

Eletropostos comerciais, em sua maioria, operam de forma isolada e reativa — sem visibilidade sobre consumo em tempo real, sem controle de demanda e sem qualquer integração com sistemas de cobrança ou gerenciamento de sessão. Isso gera ineficiência operacional, desperdício energético e uma experiência precária tanto para o operador quanto para o usuário final.

🤖 Proposta do Chatbot 🤖  

Em nosso projeto, a IA será utilizada para otimização energética, automação operacional e assistência inteligente aos usuários. Além disso, a IA terá aplicações como: previsão de demanda; identificação de horários críticos; redistribuição de carga; análise de consumo; dentre outras.       
Com tudo isso, entramos na proposta do nosso Chatbot, o "ChargeGrid Assistant", um chatbot inteligente integrado à um aplicativo e ao painel administrativo. Ele terá como objetivo auxiliar usuários e administradores em tempo real.        
Suas Funcionalidades:         
- Usuários: Status da recarga; tempo restante; pagamentos e carregadores disponíveis.

- Administradores: Alertas; falhas; monitoramento energético e relatórios rápidos.


💾 Tecnologias Selecionadas 💾

OPENAI API - (openai)     

É o núcleo inteligente do chatbot, mas originalmente frágil e limitado. Para melhorar isso, utilizamos a API (gpt-4o-mini), que entende linguagem natural, facilitando a comunicação natural com o usuário.
O gpt-4o-mini foi escolhido por ser rápido e mais barato. 

TOOL CALLING     

O Tool calling é a maneira de identifica dados reais e/ou com base legítima; sem ele, a IA iria se basear em "achar" que os dados são aqueles, inventando valores. Com essa ferramenta, o modelo consegue identificar a intenção do usuário, chamando pela função correta, tornando o chatbot lógico.

ROLES DO CHAT     

Temos 4 roles que estruturam o modelo com a API: 
- system: define que é o chatbot (GOODY), seu escopo e seu comportamento com o usuário.

- user: mensagem digitada pelo usuário.

- assistant: resposta gerada pelo modelo.

- tool: a resolução das funções chamadas, que em sua devolução, auxiliam para que o modelo formule respostas.

MULTI-TURN        

Relacionado com a lista "histórico", que acumula todas as mensagens da sessão e a mesma é enviada inteira a cada vez que ocorre uma solicitação à API. Isso serve como memória para o modelo, criando um contexto em sua interação com usuários.

BASE DE DADOS SIMULADA       

"dados_usuario" e "dados_admin" simulam um banco de dados ou API de telemetria dos eletropostos. Essa é a maneira para testarmos o modelo do chatbot.
