# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Seção A - Análise Manual

Análise manual do código-fonte dos 3 projetos, realizada antes da construção da skill `refactor-arch`. Para cada projeto foram documentados 5 problemas: 1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW, com arquivo e linha exatos.

### Projeto 1 — code-smells-project (Python/Flask)

#### [CRITICAL] SQL Injection generalizado + endpoint de execução de SQL arbitrário
- **Arquivo:** `database.py:28,48-50,58-60,68,92,110-111,127-128,140,148-151,158-161,163-166,174,188,220,279-280,291-297` e `app.py:59-78`
- **Descrição:** Todas as queries são montadas por concatenação de strings com dados do usuário (`"SELECT * FROM produtos WHERE id = " + str(id)`), sem parâmetros preparados. Além disso, o endpoint `/admin/query` (`app.py:59-78`) recebe SQL bruto no corpo da requisição e executa diretamente no banco (`cursor.execute(query)`), sem autenticação nem sanitização.
- **Justificativa:** É a falha mais grave do projeto — permite a qualquer cliente ler, alterar ou apagar todo o banco de dados (incluindo a tabela `usuarios`, que guarda senhas em texto puro). Se enquadra exatamente no exemplo de CRITICAL do enunciado ("SQL Injection").

#### [MEDIUM] Duplicação de código na validação de produtos
- **Arquivo:** `controllers.py:24-96` (`criar_produto` e `atualizar_produto`)
- **Descrição:** Os blocos de validação de `nome`, `preco` e `estoque` são copiados quase identicamente entre as duas funções, em vez de extraídos para uma função/validador compartilhado.
- **Justificativa:** Qualquer nova regra de validação precisa ser replicada em múltiplos lugares, aumentando o risco de inconsistência entre criação e atualização — problema clássico de padronização/duplicação (exemplo MEDIUM do enunciado).

#### [MEDIUM] Queries N+1 ao montar pedidos
- **Arquivo:** `database.py:171-233` (`get_pedidos_usuario` e `get_todos_pedidos`)
- **Descrição:** Para cada pedido, o código abre um novo cursor e consulta `itens_pedido`, e para cada item abre outro cursor para buscar o nome do produto — tudo dentro de loops aninhados, em vez de um `JOIN` único.
- **Justificativa:** Gera dezenas de idas ao banco para listar poucos pedidos, degradando performance à medida que o volume de dados cresce — gargalo de performance moderada citado como exemplo MEDIUM.

#### [LOW] Uso de `print()` como mecanismo de log
- **Arquivo:** `controllers.py:8,11,57,61,106,161,179,182,208-210,219` e `app.py:56,83-86`
- **Descrição:** Toda a aplicação usa `print()` para registrar eventos e erros (inclusive "ENVIANDO EMAIL/SMS/PUSH" simulados), sem níveis de log, timestamps ou possibilidade de configurar destino/formato.
- **Justificativa:** Prejudica observabilidade em produção e mistura logs de negócio com debug — problema de legibilidade/manutenibilidade típico de LOW.

#### [LOW] Magic numbers no cálculo de desconto
- **Arquivo:** `database.py:256-262`
- **Descrição:** Os percentuais de desconto (`0.1`, `0.05`, `0.02`) e os limiares de faturamento (`10000`, `5000`, `1000`) estão soltos no meio da lógica, sem nomes ou constantes.
- **Justificativa:** Regra de negócio fica implícita no código, dificultando entendimento e alteração seguros — exemplo clássico de LOW ("magic numbers") citado no enunciado.

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

#### [CRITICAL] Credenciais hardcoded e criptografia de senha quebrada
- **Arquivo:** `src/utils.js:1-7` e `src/utils.js:17-23`
- **Descrição:** `config` expõe `dbPass`, `paymentGatewayKey` e `smtpUser` hardcoded no código-fonte. A função `badCrypto()` (usada para "hashear" a senha do usuário em `AppManager.js:68`) apenas repete o base64 do texto em claro 10 mil vezes e corta os 10 primeiros caracteres — não é um hash criptográfico, é reversível/previsível e nem sequer usa a senha inteira.
- **Justificativa:** Combina dois problemas CRITICAL do enunciado: segredos hardcoded e uma falha grave de segurança que expõe dados sensíveis (senhas de usuários armazenadas de forma essencialmente em texto claro).

#### [MEDIUM] Callback hell com queries N+1 no relatório financeiro
- **Arquivo:** `src/AppManager.js:80-129` (`/api/admin/financial-report`)
- **Descrição:** Para cada curso, busca matrículas; para cada matrícula, busca usuário e pagamento — tudo em callbacks aninhados (4 níveis), sem `JOIN`, `Promise.all` ou `async/await`.
- **Justificativa:** Multiplica o número de queries ao banco proporcionalmente a cursos × matrículas, e o código aninhado é difícil de testar e manter — gargalo de performance moderada (MEDIUM).

#### [MEDIUM] Exclusão de usuário sem integridade referencial
- **Arquivo:** `src/AppManager.js:131-137` (`DELETE /api/users/:id`)
- **Descrição:** O endpoint apaga o usuário mas deixa `enrollments` e `payments` órfãos — o próprio comentário da resposta admite: *"as matrículas e pagamentos ficaram sujos no banco"*.
- **Justificativa:** Ausência de validação/cascata na exclusão gera inconsistência de dados persistente, um problema de padronização/qualidade de dados enquadrado como MEDIUM.

#### [LOW] Nomes de variáveis não descritivos no checkout
- **Arquivo:** `src/AppManager.js:29-33`
- **Descrição:** Os dados da requisição de checkout são atribuídos a variáveis de uma letra (`u`, `e`, `p`, `cid`, `cc`) em vez de nomes descritivos (`usuario`, `email`, `senha`, `cursoId`, `cartaoCredito`).
- **Justificativa:** Reduz legibilidade do fluxo mais crítico do sistema (pagamento), exemplo direto de LOW ("nomenclatura de variáveis ruins").

#### [LOW] Estado global mutável e código morto em `utils.js`
- **Arquivo:** `src/utils.js:9-10,25`
- **Descrição:** `globalCache` e `totalRevenue` são exportados como estado mutável no nível do módulo; `totalRevenue` nunca é incrementado ou lido em lugar nenhum do projeto.
- **Justificativa:** Estado global solto favorece bugs sutis de concorrência/consistência e há código morto sem propósito — problema de qualidade/legibilidade classificado como LOW.

### Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

#### [CRITICAL] Autenticação quebrada: MD5 sem salt e token falso previsível
- **Arquivo:** `models/user.py:27-32` e `routes/user_routes.py:185-211`
- **Descrição:** Senhas são "hasheadas" com `hashlib.md5` sem salt (algoritmo quebrado, reversível por rainbow tables). O login bem-sucedido retorna `'fake-jwt-token-' + str(user.id)` (`user_routes.py:210`) — qualquer pessoa pode montar esse token para qualquer `user_id` sem nunca ter feito login, e não existe middleware validando token algum nas rotas protegidas.
- **Justificativa:** Apesar do projeto já ter camadas (models/routes/services), a autenticação inteira é forjável — qualquer atacante se passa por qualquer usuário (inclusive admin) só sabendo o ID. É uma falha de segurança grave, mesmo nível do exemplo CRITICAL do enunciado.

#### [MEDIUM] Queries N+1 ao montar listagens e relatórios
- **Arquivo:** `routes/task_routes.py:12-63` (`get_tasks`) e `routes/report_routes.py:53-68` (`summary_report`)
- **Descrição:** `get_tasks` chama `User.query.get()` e `Category.query.get()` dentro do loop para cada task; `summary_report` chama `Task.query.filter_by(user_id=u.id)` dentro de um loop sobre todos os usuários — em vez de `join`/eager loading.
- **Justificativa:** Escala mal com o número de tasks/usuários; é o exemplo textual de MEDIUM do enunciado ("Queries N+1 no banco de dados").

#### [MEDIUM] Configuração de segredos duplicada e divergente do `.env`
- **Arquivo:** `app.py:13`, `services/notification_service.py:7-10`, `.env:1,10-12`
- **Descrição:** `app.py` hardcoda `SECRET_KEY = 'super-secret-key-123'` mesmo havendo uma `SECRET_KEY` diferente definida em `.env`, que nunca é lida. `NotificationService` hardcoda host/usuário/senha de SMTP na classe, embora `SMTP_HOST/SMTP_USER/SMTP_PASSWORD` já existam (não usados) no `.env`.
- **Justificativa:** Configuração espalhada e inconsistente entre arquivo de ambiente e código-fonte é uso inadequado de configuração/middleware de infraestrutura — padronização deficiente (MEDIUM), com risco de vazar segredo de produção junto ao código.

#### [LOW] Imports não utilizados espalhados pelo projeto
- **Arquivo:** `app.py:7` (`os, sys, json`), `routes/task_routes.py:7` (`json, os, sys, time`), `utils/helpers.py:2-7` (`os, sys, math, hashlib`)
- **Descrição:** Diversos módulos importam bibliotecas que nunca são referenciadas no corpo do arquivo.
- **Justificativa:** Sinaliza ausência de lint/limpeza de código; não quebra a aplicação, mas é ruído que dificulta leitura — problema de legibilidade (LOW).

#### [LOW] Lógica de "atrasado" duplicada em vez de reutilizar `Task.is_overdue()`
- **Arquivo:** `models/task.py:50-60`, `routes/task_routes.py:30-39,71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-43`
- **Descrição:** O mesmo bloco de `if due_date: if due_date < utcnow(): if status not in (...)` é reescrito manualmente em 5 lugares diferentes, apesar do model já expor o método `is_overdue()` para esse fim.
- **Justificativa:** Duplicação evitável que já tem solução pronta no próprio código; qualquer mudança na regra de "atraso" precisa ser replicada em vários pontos — problema de legibilidade/manutenção (LOW).

## Seção B - Construção da Skill

> Escrita após a execução completa da skill nos 3 projetos: Projeto 1 (`code-smells-project`, Python/Flask monolítico), Projeto 2 (`ecommerce-api-legacy`, Node/Express) e Projeto 3 (`task-manager-api`, Flask parcialmente organizado). Em nenhum dos três casos foi preciso alterar o `SKILL.md` ou os arquivos de `references/` — `md5sum`/`diff -rq` entre as três pastas `.claude/skills/refactor-arch/` confirma que são cópias byte-idênticas, evidência direta de que a skill é agnóstica de tecnologia na prática, não só na intenção.

### Decisões de design

O `SKILL.md` funciona como um roteiro de 3 fases **sequenciais e obrigatórias** (Análise → Auditoria → Refatoração), com um gate humano explícito entre a Fase 2 e a Fase 3 (`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`) — nenhum arquivo pode ser modificado antes dessa confirmação. Cada fase só carrega os arquivos de referência de que precisa naquele momento (tabela fase → arquivo no topo do `SKILL.md`), em vez de carregar o catálogo inteiro, o playbook e as guidelines de uma vez — isso mantém o contexto de cada fase focado e faz o agente gastar atenção só no que é relevante para o passo atual.

Os arquivos de referência foram separados por responsabilidade, seguindo exatamente as 5 áreas de conhecimento exigidas pelo desafio:

- `project-analysis.md` — heurísticas de detecção (Fase 1)
- `antipattern-catalog.md` + `report-template.md` — o que procurar e como reportar (Fase 2)
- `architecture-guidelines.md` + `refactoring-playbook.md` — para onde migrar e como transformar cada padrão (Fase 3)

As Fases 1 e 3 exigem formatos de saída **fixos e literais** (blocos `================================`), o que reduz variância entre execuções e facilita comparar o resultado em stacks diferentes. A Fase 2 segue um template com regras de preenchimento explícitas (ordenação por severidade, `arquivo:linha` sempre exato, contagem real no `## Summary`) para o relatório não virar prosa solta.

### Anti-patterns incluídos no catálogo e por quê

O catálogo tem 16 anti-patterns (mínimo exigido: 8), cobrindo as 4 severidades:

- **CRITICAL (4):** SQL Injection, Credenciais Hardcoded, God Class/Module, Endpoint de Execução Arbitrária — falhas que comprometem o banco inteiro ou vazam segredos de produção.
- **HIGH (4):** Lógica de negócio em controllers, Autenticação quebrada, Acoplamento forte/ausência de DI, Estado global mutável — violações de MVC/SOLID que inviabilizam testes e manutenção segura.
- **MEDIUM (4):** Queries N+1, Duplicação de código, Tratamento de erro genérico/validação ausente, Uso de APIs deprecated — problemas de padronização/performance que não quebram a aplicação mas degradam ela com o tempo.
- **LOW (4):** Nomenclatura ruim, Magic numbers/strings, `print`/`console.log` como log, Imports mortos — legibilidade.

Cada item foi escolhido por aparecer de forma real e recorrente em pelo menos um dos 3 projetos-alvo durante a análise manual (Seção A) — não é uma lista teórica de boas práticas, é o inverso: primeiro os problemas foram encontrados lendo o código, depois generalizados em um catálogo. O item de **APIs Deprecated** (severidade MEDIUM) tem uma tabela por stack (Python, Node) mapeando API obsoleta → equivalente moderno, porque o enunciado exige essa verificação explicitamente — mesmo sabendo que nem todo projeto vai ter ocorrências: o Projeto 1 não teve nenhuma (Flask 3.1.1 e flask-cors 5.0.1 já são versões atuais), e o Projeto 2 também não (o Node/Express já usava `Buffer.from` e `express.json()` nativo, sem `body-parser` standalone) — a skill checou ativamente e reportou "nada encontrado" em vez de inventar um finding para preencher a categoria.

### Como garanti que a skill é agnóstica de tecnologia

Nenhum arquivo de referência assume uma linguagem específica como padrão — as heurísticas de `project-analysis.md` são tabelas de correspondência (extensão de arquivo → linguagem, manifest → framework) cobrindo Python, JS/TS, Ruby, PHP, Java e Go, e o catálogo/playbook descrevem o **padrão do anti-pattern** (ex: "query montada por concatenação") com exemplos concretos em mais de uma stack (Python/sqlite3 e Node/Express), deixando explícito que "o princípio de transformação é o mesmo em qualquer linguagem — adapte a sintaxe, preserve a ideia".

O maior risco de acoplamento não é a stack, é o **nível de organização prévio** do projeto — por isso `architecture-guidelines.md` tem uma seção de "Princípio de adaptação" só para isso: se o projeto já tem `models/`/`routes/`/`services/`, a skill deve corrigir violações dentro da estrutura existente em vez de recriar tudo do zero. Isso importa especialmente para o Projeto 3 (`task-manager-api`), que já tem alguma separação de camadas, ao contrário do Projeto 1 (monólito com 4 arquivos na raiz).

### Desafios encontrados e como resolvi

- **Preservar contrato vs. corrigir falha de segurança:** a instrução era manter 100% do comportamento observável, mas o próprio relatório da Fase 2 exigia remover o endpoint `/admin/query` (executava SQL arbitrário) e proteger `/admin/reset-db` com autenticação — ambos quebram o contrato original por definição. Resolvido tratando essas mudanças como exceções explícitas e documentando cada uma no resumo final da Fase 3, em vez de escondê-las ou de recusar a correção por medo de "quebrar contrato".
- **Seed de dados ficou inconsistente com o hashing:** ao migrar de senha em texto plano para hash (`werkzeug.security`), o `loja.db` já existente no repositório continha os usuários de exemplo com senha em texto plano, o que quebraria o login pós-refactor. Como o próprio `README.md` original do projeto já documentava o banco como "criado automaticamente no primeiro boot" (dado semente, não dado de usuário real) e o arquivo está no `.gitignore`, foi seguro apagá-lo e deixar a aplicação recriá-lo já com os hashes corretos.
- **Token assinado sem adicionar dependência nova:** o `requirements.txt` original só tinha `flask` e `flask-cors`. Em vez de adicionar `PyJWT` só para gerar um token de sessão real (como o playbook sugere como exemplo), usei `itsdangerous` — que já é dependência transitiva do próprio Flask — para gerar tokens assinados com expiração real via `URLSafeTimedSerializer`.
- **Handler de erro genérico capturando `HTTPException`:** ao centralizar o tratamento de erro com `@app.errorhandler(Exception)`, descobri que isso também intercepta exceções HTTP do próprio Flask/Werkzeug (404 de rota inexistente, por exemplo), convertendo-as erroneamente em 500. Corrigido checando `isinstance(e, HTTPException)` no início do handler e deixando essas exceções seguirem seu fluxo normal — só exceções verdadeiramente inesperadas viram o 500 genérico.
- **O catálogo não cobre tudo — validei isso na prática:** depois de declarar a Fase 3 concluída, pedi uma segunda revisão independente do código refatorado. Ela encontrou 2 bugs reais que **não correspondem a nenhum dos 16 anti-patterns do catálogo**: overselling de estoque quando o mesmo produto aparece duas vezes no mesmo pedido (a validação comparava cada item contra o estoque original, sem somar a demanda acumulada) e ausência de validação de tipo/sinal em `quantidade`/`preço` (permitia número negativo ou string, gerando comportamento incorreto silencioso). Também achou uma violação de camada que a própria refatoração introduziu (SQL cru dentro de `admin_controller.py` e `main_controller.py`, driblando a regra "Controllers nunca executam SQL cru"). Todos foram corrigidos manualmente após a Fase 3. Isso deixou claro que o catálogo audita bem os padrões que conhece, mas bugs de lógica de negócio específicos do domínio (ex: regras de estoque) exigem revisão humana ou de agente adicional — é um candidato a novo item de catálogo para as próximas iterações.
- **Corrigir um bug de integridade que o próprio código admitia, no Projeto 2:** o `DELETE /api/users/:id` original apagava o usuário mas deixava `enrollments`/`payments` órfãos, e a própria resposta de sucesso confessava isso em texto ("...mas as matrículas e pagamentos ficaram sujos no banco"). A skill tratou isso como o finding MEDIUM "Tratamento de Erros Genérico/Validação Ausente" exige — implementou exclusão em cascata e corrigiu o texto da resposta — e documentou a mudança de contrato no resumo da Fase 3, seguindo a mesma regra de exceção já usada no Projeto 1.
- **Proteger rotas administrativas sem inventar um novo segredo:** `/api/admin/financial-report` e `DELETE /api/users/:id` não tinham nenhuma autenticação (finding HIGH "Autenticação Quebrada/Fraca"). Em vez de criar uma variável de ambiente nova, a skill reaproveitou `ADMIN_API_KEY`, que já existia no `.env` do boilerplate mas nunca era lida em nenhum lugar do código — sinal de que o próprio projeto já antecipava essa necessidade.
- **Callback hell do driver `sqlite3` sem trocar de dependência:** o driver `sqlite3` do Node só expõe API por callback (ao contrário de `better-sqlite3`, não tem um modo Promise nativo), e era a causa raiz tanto do finding de Queries N+1 quanto da pirâmide de callbacks no checkout. Trocar de driver mudaria o comportamento de concorrência da conexão em memória, então a skill envolveu `get`/`all`/`run` numa classe `Database` com métodos que retornam Promises — permitindo controllers com `async/await` e uma única query com `JOIN` no relatório financeiro, sem alterar o driver subjacente.
- **Evitar dependência nativa para hashing de senha:** o playbook sugere bcrypt/scrypt/argon2 para substituir hashes quebrados; o `bcrypt` nativo do Node exige compilação (`node-gyp`), que pode falhar em sandboxes sem toolchain de build. A skill usou `bcryptjs` (implementação pura em JS, mesma API) — a mesma lógica de decisão do `itsdangerous` no Projeto 1: preferir a biblioteca sem dependência nativa quando o resultado de segurança é equivalente.
- **Projeto 3 já tinha camadas — o risco era recriar em vez de corrigir:** ao contrário dos Projetos 1 e 2 (monólitos), o `task-manager-api` já tinha `models/`, `routes/`, `services/`, `utils/`. Seguindo o "Princípio de adaptação" do `architecture-guidelines.md`, a Fase 3 não recriou nada disso — apenas adicionou as camadas que realmente faltavam (`config/`, `controllers/`, `middlewares/`) e corrigiu as violações dentro da estrutura existente (rotas com SQL/lógica de negócio embutidos viraram controllers finos; `services/notification_service.py` e `utils/helpers.py`, que existiam mas nunca eram chamados por nada, foram efetivamente conectados ou tiveram o código morto removido).
- **`datetime.utcnow()` deprecated sem trocar a semântica de comparação:** a correção óbvia (`datetime.now(datetime.UTC)`) gera datetimes *timezone-aware*, mas o projeto 3 compara `due_date`/`created_at` (naive, vindos de `strptime` e de colunas SQLite) o tempo todo — misturar aware e naive quebra a comparação em runtime (`TypeError`). A skill centralizou um helper único `utils.helpers.utcnow()` que usa `datetime.now(timezone.utc).replace(tzinfo=None)`, eliminando a API deprecated sem tocar na semântica naive usada em todo o resto do código.
- **Corrigir autenticação sem quebrar o contrato de toda a API:** o finding HIGH de autenticação quebrada (MD5 sem salt + token previsível) foi corrigido trocando para `werkzeug.security` e JWT real assinado (`PyJWT`) com expiração. A skill **não** adicionou um middleware de autenticação obrigatória em todas as rotas de escrita, porque isso mudaria o contrato de toda a API (exigiria que todo cliente passasse a enviar token) — uma decisão de produto, não uma correção pontual do finding. Essa lacuna foi documentada explicitamente no resumo da Fase 3 em vez de escondida.

## Seção C - Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack | Arquivos (antes) | LOC (antes) | CRITICAL | HIGH | MEDIUM | LOW | Total findings |
|---|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask 3.1.1 | 4 | ~780 | 4 | 4 | 3 | 4 | **15** |
| 2 — ecommerce-api-legacy | Node.js/Express ^4.18.2 | 3 | ~180 | 2 | 4 | 2 | 4 | **12** |
| 3 — task-manager-api | Python/Flask 3.0.0 | 15 | ~1160 | 2 | 2 | 4 | 4 | **12** |

Os relatórios completos (saída literal da Fase 2, findings com `arquivo:linha` exatos) estão em `reports/audit-project-{1,2,3}.md`. Todos os 3 projetos atingiram o mínimo de 5 findings e pelo menos 1 CRITICAL/HIGH exigido pelos critérios de aceite.

Observação sobre o Projeto 3: apesar de ter menos findings CRITICAL que o Projeto 1 (2 vs. 4), o total de findings (12) foi puxado por MEDIUM/LOW — reflexo direto de já ter alguma organização de camadas: não há mais "God Class" nem SQL Injection generalizado, mas restam problemas de qualidade (duplicação, N+1, tratamento de erro, código morto) espalhados pelas camadas existentes.

### Comparação antes/depois da estrutura

**Projeto 1 — code-smells-project**

```
Antes (monólito, 4 arquivos)          Depois (MVC, 24 arquivos)
app.py           (rotas + SQL cru)    config/{settings,database}.py
controllers.py   (validação + print)  controllers/{admin,main,pedido,produto,usuario}_controller.py
models.py        (3 domínios juntos)  middlewares/{auth,error_handler}.py
database.py      (conexão global)     models/{pedido,produto,usuario}_model.py
                                       routes/{admin,main,pedido,produto,relatorio,usuario}_routes.py
                                       app.py (composition root)
~780 LOC                              ~934 LOC
```

Mudanças de contrato documentadas: endpoint `POST /admin/query` (execução de SQL arbitrário) foi **removido**; `/admin/reset-db` passou a exigir autenticação; `GET /health` parou de expor `SECRET_KEY`/`db_path` em texto plano.

**Projeto 2 — ecommerce-api-legacy**

```
Antes (God Class, 3 arquivos)         Depois (MVC, 20 arquivos)
src/app.js        (bootstrap)         src/config/index.js
src/AppManager.js (rotas+SQL+regra    src/controllers/{admin,checkout,user}Controller.js
                   de negócio p/ 5    src/middlewares/{errorHandler,requireAdminAuth}.js
                   entidades)         src/models/{auditLog,course,enrollment,payment,user}Model.js + database.js
src/utils.js       (config+cache+     src/routes/{admin,checkout,user}Routes.js
                    crypto quebrado)  src/utils/{cache,logger,security}.js
~180 LOC                              ~447 LOC
```

Mudanças de contrato documentadas: `DELETE /api/users/:id` e `GET /api/admin/financial-report` passaram a exigir header `x-api-key` (reaproveitando `ADMIN_API_KEY`, já presente no `.env` mas nunca lido); a exclusão de usuário passou a ser em cascata (antes deixava `enrollments`/`payments` órfãos, o que a própria resposta do endpoint admitia em texto).

**Projeto 3 — task-manager-api**

```
Antes (parcialmente organizado,       Depois (MVC completo, 23 arquivos)
15 arquivos)                          config/settings.py                    [NOVO]
models/, routes/, services/,          controllers/{task,user,report}_controller.py [NOVO]
utils/ já existiam, mas com           middlewares/error_handler.py          [NOVO]
SQL/lógica de negócio dentro          models/, routes/, services/, utils/   [AJUSTADOS in-place]
das rotas, secrets hardcoded          app.py (composition root)             [AJUSTADO]
ignorando o .env já existente
~1160 LOC                             ~1136 LOC (menos, apesar das 3 camadas novas — código morto de
                                       utils/helpers.py e services/ removido/conectado)
```

Mudanças de contrato documentadas: mensagens de erro 500 passaram a ser genéricas (`"Erro interno do servidor"`, antes cada rota tinha uma frase própria); `PUT /categories/<id>` com corpo vazio passou a responder 400 em vez de um no-op silencioso 200; `token` do login continua uma string, mas agora é um JWT assinado com expiração em vez de `'fake-jwt-token-' + id`.

### Checklist de validação

**Projeto 1 — code-smells-project**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1, via requirements.txt)
- [x] Domínio da aplicação descrito corretamente (E-commerce: produtos, usuários, pedidos)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (15 findings)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada — Flask 3.1.1/flask-cors 5.0.1 já atuais; reportado explicitamente como "nada encontrado")
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (config/controllers/middlewares/models/routes)
- [x] Configuração extraída para módulo de config (sem hardcoded) — config/settings.py lê .env
- [x] Models criados para abstrair dados (models/produto_model.py, usuario_model.py, pedido_model.py)
- [x] Views/Routes separadas (routes/*_routes.py, sem lógica de negócio nem SQL)
- [x] Controllers concentram o fluxo (controllers/*_controller.py)
- [x] Error handling centralizado (middlewares/error_handler.py)
- [x] Entry point claro (app.py como composition root)
- [x] Aplicação inicia sem erros (validado via `python3 app.py`, boot log limpo)
- [x] Endpoints originais respondem corretamente (/, /health, /produtos*, /usuarios, /login, /pedidos, /relatorios/vendas testados via curl)
```

**Projeto 2 — ecommerce-api-legacy**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express ^4.18.2, via package.json)
- [x] Domínio da aplicação descrito corretamente (LMS com fluxo de checkout: cursos, matrículas, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos: app.js, AppManager.js, utils.js)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (12 findings)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada — já usa Buffer.from e express.json() nativo; reportado explicitamente)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (src/config/controllers/middlewares/models/routes/utils)
- [x] Configuração extraída para módulo de config (sem hardcoded) — src/config/index.js lê .env via dotenv
- [x] Models criados para abstrair dados (userModel, courseModel, enrollmentModel, paymentModel, auditLogModel)
- [x] Views/Routes separadas (src/routes/*.js)
- [x] Controllers concentram o fluxo (src/controllers/{admin,checkout,user}Controller.js)
- [x] Error handling centralizado (src/middlewares/errorHandler.js)
- [x] Entry point claro (src/app.js)
- [x] Aplicação inicia sem erros (validado via `node src/app.js`, log "Frankenstein LMS rodando na porta 3000")
- [x] Endpoints originais respondem corretamente (/api/checkout, /api/admin/financial-report, DELETE /api/users/:id testados via curl, incluindo os novos 401 esperados sem x-api-key)
```

**Projeto 3 — task-manager-api**

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + flask-sqlalchemy, via requirements.txt)
- [x] Domínio da aplicação descrito corretamente (Task Manager: tasks, usuários, categorias, relatórios)
- [x] Número de arquivos analisados condiz com a realidade (15 arquivos)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (12 findings)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow() encontrado em 9 arquivos, finding MEDIUM próprio)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (config/controllers/middlewares adicionados; models/routes/services/utils ajustados in-place, sem recriar do zero)
- [x] Configuração extraída para módulo de config (sem hardcoded) — config/settings.py lê .env (SECRET_KEY, DATABASE_URL, SMTP_*, TOKEN_TTL_SECONDS)
- [x] Models criados/ajustados para abstrair dados (Task.validate_status/validate_priority/is_overdue/search/stats, User com hashing seguro)
- [x] Views/Routes separadas (routes/*_routes.py reduzidas a request → controller → jsonify)
- [x] Controllers concentram o fluxo (controllers/{task,user,report}_controller.py)
- [x] Error handling centralizado (middlewares/error_handler.py, com passthrough de HTTPException)
- [x] Entry point claro (app.py como composition root)
- [x] Aplicação inicia sem erros (validado via `python seed.py` + `python app.py`, boot log limpo, debug off)
- [x] Endpoints originais respondem corretamente (/, /health, /tasks*, /users*, /login, /reports/*, /categories* testados via curl, incluindo os erros esperados 400/401/403/404/409/415)
```

### Logs das aplicações rodando após a refatoração

**Projeto 1 — code-smells-project** (`python3 app.py`, depois `curl`):

```
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'app'
 * Debug mode: on
2026-07-30 08:53:25 INFO werkzeug: * Running on http://127.0.0.1:5000
2026-07-30 08:53:35 INFO controllers.produto_controller: Listando 10 produtos
2026-07-30 08:53:35 INFO werkzeug: 127.0.0.1 - - "GET /produtos HTTP/1.1" 200 -
2026-07-30 08:53:35 INFO controllers.produto_controller: Produto criado com ID: 21
2026-07-30 08:53:35 INFO werkzeug: 127.0.0.1 - - "POST /produtos HTTP/1.1" 201 -
2026-07-30 08:53:35 INFO controllers.usuario_controller: Login falhou: x@x.com
2026-07-30 08:53:35 INFO werkzeug: 127.0.0.1 - - "POST /login HTTP/1.1" 401 -
2026-07-30 08:53:47 INFO werkzeug: 127.0.0.1 - - "POST /admin/query HTTP/1.1" 404 -   ← endpoint removido, contrato documentado
2026-07-30 08:53:47 INFO werkzeug: 127.0.0.1 - - "GET /produtos/busca?nome=Notebook'-- HTTP/1.1" 200 -  ← tentativa de SQLi neutralizada
```

**Projeto 2 — ecommerce-api-legacy** (`node src/app.js`, depois `curl`):

```
[INFO] Frankenstein LMS rodando na porta 3000...

$ curl -X POST /api/checkout {...cartão "4111..."}   → 200 {"msg":"Sucesso","enrollment_id":2}
$ curl -X POST /api/checkout {...cartão "5111..."}   → 400 "Pagamento recusado"
$ curl /api/admin/financial-report (sem x-api-key)   → 401 {"error":"Não autorizado"}
$ curl /api/admin/financial-report (com x-api-key)   → 200 [{"course":"Clean Architecture","revenue":997,...}]
$ curl -X DELETE /api/users/1 (sem x-api-key)         → 401 {"error":"Não autorizado"}
$ curl -X DELETE /api/users/1 (com x-api-key)         → 200 "Usuário deletado com sucesso, incluindo matrículas e pagamentos associados."
```

**Projeto 3 — task-manager-api** (`python seed.py` + `python app.py`, depois `curl`):

```
Seed concluído com sucesso!
  3 usuários / 4 categorias / 10 tasks
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000

$ curl /tasks/stats                         → 200 {"cancelled":1,"completion_rate":10.0,"done":1,"in_progress":2,"overdue":2,"pending":6,"total":10}
$ curl -X POST /login {"email":"joao@email.com","password":"1234"}
  → 200 {"token":"eyJhbGciOiJIUzI1NiIs...", "user":{...,"password":"scrypt:32768:8:1$..."}}   ← JWT real + hash seguro (era MD5 + token previsível)
$ curl -X PUT /categories/1 -d '{}'          → 400 {"error":"Dados inválidos"}                ← bug de validação ausente corrigido
$ curl /nao-existe                           → 404 default do Flask (middleware de erro não interfere em HTTPException)
```

### Observações sobre o comportamento da skill em stacks diferentes

- A mesma pasta `.claude/skills/refactor-arch/` (SKILL.md + 5 arquivos de referência), copiada byte-a-byte entre os 3 projetos, produziu as 3 fases corretamente em Python/Flask monolítico, Node/Express "God Class" com callbacks, e Python/Flask parcialmente organizado — sem nenhum ajuste nos arquivos de referência entre uma execução e outra.
- A maior diferença de comportamento não veio da linguagem, e sim do **nível de organização prévio**: no Projeto 3, a Fase 3 respeitou o "Princípio de adaptação" e ajustou a estrutura existente em vez de recriá-la, enquanto nos Projetos 1 e 2 (monólitos) ela criou a árvore MVC do zero — confirmando que a heurística de `architecture-guidelines.md` generaliza bem para os dois cenários.
- No Node.js, a skill lidou corretamente com um paradigma diferente do Python (callbacks em vez de exceções síncronas): o playbook de "Queries N+1" e "Erro genérico" foi aplicado convertendo callbacks aninhados em `async/await` sobre uma camada de Promises, sem que isso estivesse explicitamente detalhado nos exemplos do catálogo além do princípio geral ("adapte a sintaxe, preserve a ideia").
- Em nenhum dos 3 projetos a skill inventou um finding de "API deprecated" só para preencher a categoria obrigatória: reportou corretamente "nada encontrado" nos Projetos 1 e 2, e encontrou uma ocorrência real e recorrente (`datetime.utcnow()`) no Projeto 3 — evidência de que a verificação é ativa, não um checklist decorativo.
- A auditoria (Fase 2) do Projeto 3 teve o dobro de findings LOW/MEDIUM em relação a CRITICAL, o oposto do Projeto 1 — condizente com a hipótese inicial de que projetos já organizados trocam falhas estruturais graves por dívida técnica mais sutil (duplicação, N+1, código morto), exigindo que o catálogo cubra bem as duas pontas da escala de severidade.

## Seção D - Como Executar

### Pré-requisitos

- **Claude Code** instalado e autenticado (`npm install -g @anthropic-ai/claude-code` ou conforme a documentação oficial) — ferramenta usada em todas as execuções deste desafio.
- **Python 3.10+** com `pip`, para os Projetos 1 (`code-smells-project`) e 3 (`task-manager-api`).
- **Node.js 18+** com `npm`, para o Projeto 2 (`ecommerce-api-legacy`).
- Repositório clonado localmente, com os 3 projetos e suas respectivas pastas `.claude/skills/refactor-arch/` já commitadas (a skill não precisa ser reinstalada — já está em cada projeto).

### Comandos para executar a skill em cada projeto

```bash
# Projeto 1 — code-smells-project (Python/Flask, monólito)
cd code-smells-project
claude "/refactor-arch"
# → Fase 1 imprime o resumo da stack; Fase 2 imprime o relatório e pergunta
#   "Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]"; responda "y"
#   para a Fase 3 refatorar e validar automaticamente.

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)
cd ../task-manager-api
claude "/refactor-arch"
```

Cada execução gera a saída da Fase 2 no terminal — copie/cole (ou redirecione) esse conteúdo para `reports/audit-project-{1,2,3}.md`, conforme a numeração do projeto.

### Como validar que a refatoração funcionou

**Projeto 1 e 3 (Python/Flask):**

```bash
cd code-smells-project   # ou task-manager-api
python3 -m venv .venv && source .venv/bin/activate   # se ainda não existir um venv
pip install -r requirements.txt
python seed.py            # apenas task-manager-api — popula o banco SQLite de exemplo
python app.py              # sobe o servidor em http://localhost:5000
```

Em outro terminal:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/produtos       # code-smells-project
curl http://localhost:5000/tasks          # task-manager-api
```

Status `200` e JSON de resposta confirmam que a aplicação subiu e os endpoints originais continuam funcionando. Confira também o log de boot: nenhuma exception deve aparecer entre o "Serving Flask app" e a primeira requisição.

**Projeto 2 (Node.js/Express):**

```bash
cd ecommerce-api-legacy
npm install
node src/app.js            # sobe o servidor em http://localhost:3000
```

Em outro terminal:

```bash
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Teste","eml":"teste@email.com","pwd":"123456","c_id":1,"card":"4111222233334444"}'

curl http://localhost:3000/api/admin/financial-report \
  -H "x-api-key: <valor de ADMIN_API_KEY no .env>"
```

Status `200` no checkout e no relatório administrativo (com a `x-api-key` correta) confirma que a aplicação e as rotas protegidas continuam funcionando após a refatoração. Testar a mesma rota administrativa sem o header deve retornar `401`, confirmando que a correção do finding de autenticação quebrada está em vigor.

Em todos os 3 projetos, encerre o processo do servidor (`Ctrl+C` ou `kill <pid>`) ao final da validação.

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.