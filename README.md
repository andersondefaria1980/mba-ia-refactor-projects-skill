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
```

```
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

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

## Análise Manual

Análise realizada por leitura completa do código-fonte dos 3 projetos, antes da construção da skill. Os achados abaixo alimentaram diretamente o catálogo de anti-patterns em `reference/anti-pattern-catalog.md`.

### Projeto 1 — code-smells-project (Python/Flask, monólito em 4 arquivos)

Stack: Python 3 + Flask 3.1.1 + flask-cors 5.0.1, SQLite via `sqlite3` puro (sem ORM). Domínio: API de e-commerce (produtos, usuários, pedidos, itens de pedido).

| # | Severidade | Local | Problema | Por que importa |
|---|---|---|---|---|
| 1 | **CRITICAL** | `app.py:59-78` | `POST /admin/query` executa SQL arbitrário enviado pelo cliente (`cursor.execute(query)`), sem autenticação | Equivale a um shell SQL exposto na internet — permite drop de tabelas, exfiltração total do banco |
| 2 | **CRITICAL** | `models.py:109-111` | `login_usuario` monta a query de autenticação por concatenação de string, permitindo bypass de login via SQL Injection (`' OR '1'='1`) | Quebra completamente o mecanismo de autenticação, não é "só" um SQLi qualquer |
| 3 | **CRITICAL** | `app.py:7`, `controllers.py:288-289` | `SECRET_KEY` hardcoded e devolvida em texto puro pelo endpoint `/health`, junto com a flag de debug | Vaza o segredo usado para assinar sessões/tokens; qualquer um pode ler via `curl /health` |
| 4 | `models.py:122-131`, `database.py:76-79` | **CRITICAL** | Senhas armazenadas e comparadas em texto puro, inclusive na massa de seed (`admin123`, `123456`) | Nenhuma proteção em caso de vazamento do banco; viola o mínimo de segurança para credenciais |
| 5 | **HIGH** | `controllers.py:188-220` | Lógica de orquestração de pedido (checagem de estoque, cálculo de total, "envio" de notificação) embutida direto no controller, sem camada de serviço | Mistura HTTP handling com regra de negócio — impossível testar a regra isoladamente |
| 6 | **HIGH** | `database.py:4-11` | Conexão SQLite única compartilhada em variável global de módulo (`db_connection`) | Estado mutável global acessado por todas as requisições concorrentes, sem isolamento por request |
| 7 | **MEDIUM** | `models.py:171-233` | N+1 queries: para cada pedido, uma query de itens e, para cada item, uma query de produto — sem JOIN — duplicado em duas funções quase idênticas | Degrada performance conforme o volume de pedidos cresce; a duplicação dobra o custo de manutenção |
| 8 | **MEDIUM** | `controllers.py:24-62` vs `64-96` | Bloco de validação (campos obrigatórios, preço/estoque negativo) copiado e colado entre `criar_produto` e `atualizar_produto` | Qualquer mudança de regra precisa ser replicada manualmente em 2+ lugares — fonte de bugs de inconsistência |
| 9 | **LOW** | `app.py:11-30,32,47,59` | Registro de rotas inconsistente — mistura `add_url_rule` com `@app.route` sem critério | Reduz legibilidade e previsibilidade do roteamento |
| 10 | **LOW** | `controllers.py:8,11,57,61,106,...`, `app.py:56` | Uso de `print()` para logging em vez do módulo `logging` | Sem níveis de log, sem timestamps, impossível filtrar/desligar em produção |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS com checkout)

Stack: Node.js + Express ^4.18.2 + sqlite3 ^5.1.6 (banco em memória). Domínio real (apesar do nome da pasta): LMS — usuários, cursos, matrículas e pagamentos via checkout.

| # | Severidade | Local | Problema | Por que importa |
|---|---|---|---|---|
| 1 | **CRITICAL** | `src/utils.js:2-6` | Credenciais hardcoded no código-fonte, incluindo uma chave de gateway de pagamento com prefixo `pk_live_...` | Segredo de produção commitado no repositório — comprometimento imediato se o repo vazar |
| 2 | **CRITICAL** | `src/AppManager.js:45` | Número completo de cartão de crédito logado em texto puro via `console.log`, junto da chave do gateway | Violação direta de PCI-DSS; dado de cartão nunca deve ir para log |
| 3 | **CRITICAL** | `src/AppManager.js:46` | "Processamento" de pagamento aprova qualquer cartão cujo número comece com `"4"` (`cc.startsWith("4")`) | Não há validação real de pagamento — qualquer usuário "compra" qualquer curso de graça |
| 4 | **CRITICAL** | `src/utils.js:17-23` (`badCrypto`) | "Hash" de senha implementado como base64 repetido e truncado — reversível, sem salt | Não é criptografia; equivale a guardar a senha praticamente em claro |
| 5 | **HIGH** | `src/AppManager.js` (arquivo inteiro) | God Class: uma única classe cuida de conexão/schema do banco, todas as rotas HTTP e toda a regra de negócio (pagamento, matrícula, auditoria) | Impossível testar ou trocar qualquer parte isoladamente; qualquer mudança arrisca quebrar tudo |
| 6 | **HIGH** | `src/AppManager.js:80,131` | `GET /api/admin/financial-report` e `DELETE /api/users/:id` sem nenhuma autenticação/autorização | Qualquer pessoa lê o relatório financeiro completo ou apaga usuários à vontade |
| 7 | **MEDIUM** | `src/AppManager.js:83-127` | N+1 em pirâmide de callbacks: para cada curso, query de matrículas; para cada matrícula, query de usuário e de pagamento, com contadores manuais de pendência em vez de Promises | Performance ruim e propenso a bugs de concorrência (contadores que nunca fecham se uma query falha) |
| 8 | **MEDIUM** | `src/utils.js:9-10` | Cache mutável em variável de módulo (`globalCache`), sem expiração, populado a cada checkout | Estado global compartilhado entre requisições, cresce indefinidamente, não é thread/process-safe |
| 9 | **LOW** | `src/AppManager.js:29-33` | Nomes de variável de uma letra (`u`, `e`, `p`, `cid`, `cc`) para usuário, email, senha, curso e cartão | Dificulta entender o fluxo de checkout só de olhar o código |
| 10 | **LOW** | `src/AppManager.js:46`, `utils.js:19-22` | Magic numbers/strings soltos (`"4"` como prefixo de bandeira, `10000` no loop do hash falso, `"PAID"`/`"DENIED"` repetidos como literais) | Sem constantes/enum, qualquer alteração de regra exige caçar strings repetidas pelo código |

### Projeto 3 — task-manager-api (Python/Flask, com separação parcial em camadas)

Stack: Python 3 + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1, SQLite. Já possui pastas `models/`, `routes/`, `services/`, `utils/`, mas a separação é majoritariamente cosmética — o ponto central desta análise.

| # | Severidade | Local | Problema | Por que importa |
|---|---|---|---|---|
| 1 | **CRITICAL** | `app.py:13` | `SECRET_KEY` hardcoded, apesar de `python-dotenv` estar nas dependências e nunca ser usado | Segredo de sessão exposto no código-fonte, sem nenhuma tentativa real de externalizar config |
| 2 | **CRITICAL** | `models/user.py:29,32` | Senhas com hash MD5 sem salt | MD5 é criptograficamente quebrado para senhas — trivial de reverter via rainbow tables |
| 3 | **CRITICAL** | Toda a aplicação (grep confirma zero `login_required`/checagem de token) | Nenhuma rota exige autenticação, incluindo `DELETE /users/<id>` e `DELETE /tasks/<id>` | Qualquer cliente anônimo lê, altera ou apaga qualquer dado de qualquer usuário |
| 4 | **HIGH** | `routes/report_routes.py:12-101` | Lógica pesada de agregação/estatística implementada direto na rota, mesmo existindo uma pasta `services/` | A camada de serviço existe no projeto mas não é usada onde faria mais sentido — separação decorativa |
| 5 | **HIGH** | `services/notification_service.py` e `utils/helpers.py` | `NotificationService` e as funções de `helpers.py` nunca são importados/chamados por nenhuma rota (confirmado via grep) | Camadas "mortas": dão a impressão de arquitetura em camadas, mas o fluxo real ignora completamente essas pastas |
| 6 | **MEDIUM** | `routes/task_routes.py:41-57` | N+1 queries: para cada task, uma query separada de usuário e de categoria em vez de eager loading (`joinedload`) | Escala mal conforme o número de tasks cresce |
| 7 | **MEDIUM** | Lógica de "overdue" duplicada em 6 lugares (`models/task.py:50-60`, `routes/task_routes.py:30-39,71-80,283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-37,132-135`) | `Task.is_overdue()` já existe no model mas nunca é chamado — cada rota reimplementa o mesmo `if` | Seis pontos para manter sincronizados manualmente; risco alto de divergência de regra |
| 8 | **MEDIUM** | Todas as rotas de listagem (`task_routes.py:14`, `user_routes.py:12`, `report_routes.py:30,53,159`) | `Model.query.all()` sem paginação em nenhum endpoint | Endpoint fica O(n) em payload conforme a tabela cresce; a própria seed (`seed.py:70`) já sinaliza isso como pendência |
| 9 | **LOW** | `models/task.py:15-16,52`, `models/user.py:14`, várias rotas | Uso de `datetime.utcnow()`, depreciado desde Python 3.12 em favor de `datetime.now(timezone.utc)` | API deprecada — funciona hoje, mas gera warning e será removida em versões futuras do Python |
| 10 | **LOW** | `app.py:7`, `routes/task_routes.py:7` | Imports não utilizados (`os`, `sys`, `json` em `app.py`; `json`, `os`, `sys`, `time` em `task_routes.py`) | Ruído no código, sinaliza falta de lint/CI configurado |

---

## Construção da Skill

A skill vive em `code-smells-project/.claude/skills/refactor-arch/` e foi copiada, sem alterações, para os outros dois projetos.

### Decisões de design

- **`SKILL.md` como roteiro de execução, não como base de conhecimento.** Ele descreve as 3 fases, a ordem em que os 5 arquivos de `reference/` devem ser consultados e as regras que valem para todas as fases (nunca modificar fora da Fase 3, sempre pausar na Fase 2, sempre validar no fim da Fase 3). Todo o conhecimento de domínio — heurísticas, catálogo, template, guidelines, playbook — fica nos arquivos de referência, para que o `SKILL.md` continue pequeno e legível mesmo se o catálogo crescer.
- **Um arquivo por área de conhecimento**, em vez de um único documento monolítico: `project-analysis.md` (heurísticas da Fase 1), `anti-pattern-catalog.md` (o que procurar na Fase 2), `audit-report-template.md` (formato exato do relatório), `mvc-guidelines.md` (arquitetura alvo da Fase 3) e `refactoring-playbook.md` (como transformar cada anti-pattern, com código antes/depois). Essa separação deixou cada arquivo focado em uma responsabilidade e mais fácil de iterar isoladamente quando um projeto revelava um caso que a versão anterior do catálogo não cobria.
- **Sinais de detecção concretos, não julgamentos vagos.** Cada anti-pattern do catálogo diz exatamente o que procurar no código (ex: "montagem de query por f-string/concatenação interpolando input do usuário", "pastas como `services/`/`utils/` existem mas `grep -r "import nome_do_modulo"` não encontra nenhum uso real") em vez de "código mal escrito". Isso foi o que mais mudou entre iterações — a primeira versão do catálogo era mais genérica e a Fase 2 encontrava menos findings do que a análise manual já tinha revelado.

### Anti-patterns incluídos e por quê

O catálogo (`anti-pattern-catalog.md`) tem 18 entradas (5 CRITICAL, 5 HIGH, 5 MEDIUM, 3 LOW, mais uma seção dedicada a APIs deprecadas) — acima do mínimo de 8 pedido pelo desafio. Cada entrada nasceu de um problema real encontrado na análise manual dos 3 projetos, não de uma lista genérica copiada de um checklist de boas práticas:

- **Credenciais hardcoded, SQL Injection, God Class, endpoint destrutivo sem auth, senha insegura** (CRITICAL) — presentes nos 3 projetos, em formas diferentes (SQL Injection via concatenação em Python, "hash" de senha falso em Node, MD5 sem salt em Python com ORM).
- **Fat Controller, acoplamento forte, estado global mutável, camadas decorativas/mortas, auth ausente/falsa** (HIGH) — o item "camadas decorativas" foi adicionado especificamente por causa do `task-manager-api`, onde `services/` e `utils/` existem mas nunca são chamados; sem esse item explícito no catálogo, a Fase 2 teria elogiado a "boa organização em pastas" do projeto 3 sem perceber que ela é só aparência.
- **N+1, duplicação de código, validação ausente, middleware mal usado, ausência de paginação** (MEDIUM) — o N+1 apareceu nos 3 projetos com formas bem diferentes (JOIN ausente em SQL cru, pirâmide de callbacks em Node, loop Python sobre `Task.query` por usuário), então os sinais de detecção do catálogo descrevem o padrão geral ("loop que dispara uma query individual por item já carregado") em vez de um exemplo de uma stack só.
- **Nomenclatura ruim, logging via print/console.log, imports/código morto** (LOW).
- **Seção dedicada a APIs deprecadas**, com uma tabela de referência rápida por stack (Python: `datetime.utcnow()`, `Model.query.get()`, `@app.before_first_request`; Node: `new Buffer()`, `crypto.createCipher`) e instrução explícita para expandir a busca para a versão exata detectada na Fase 1 — a tabela é um ponto de partida, não uma lista fechada.

### Como garanti que a skill é agnóstica de tecnologia

- Nenhum arquivo de referência menciona um projeto específico por nome — todos os exemplos são ilustrativos ("Antes/Depois" em Python **e** em Node lado a lado no playbook, quando aplicável).
- As heurísticas de detecção (`project-analysis.md`) são organizadas por **o que perguntar ao código**, não por stack: "procure manifesto de dependências", "procure import/require de driver de banco", em vez de "se for Flask, faça X".
- O teste real de agnosticismo foi rodar a skill sem alterações nos 3 projetos: copiei a mesma pasta `refactor-arch/` para `ecommerce-api-legacy/` (Node/Express) e `task-manager-api/` (Python/Flask com camadas parciais) e só ajustei o *conteúdo* que a skill gerou (estrutura de pastas, código), nunca a skill em si.
- `mvc-guidelines.md` explicitamente instrui a adaptar nomes de pasta à convenção idiomática da stack (`views/` vira `routes/` em Express) sem abrir mão das 5 responsabilidades (config, models, views/routes, controllers, error handling centralizado).

### Desafios encontrados e como resolvi

- **Projeto 3 exigia uma Fase 3 qualitativamente diferente.** A primeira versão do `mvc-guidelines.md` só descrevia "criar a estrutura MVC do zero", o que não fazia sentido para um projeto que já tinha `models/routes/services/utils/`. Adicionei a seção "Adaptação a projetos parcialmente organizados" com uma regra explícita: não recriar a estrutura, e sim mover lógica para dentro dela, reconectar camadas mortas ou removê-las com justificativa, e preservar os endpoints existentes.
- **Risco de a Fase 3 travar em chamadas externas reais.** O `NotificationService` do projeto 3 faz uma conexão SMTP real; religá-lo ao fluxo sem cuidado faria `POST /tasks` tentar conectar em `smtp.gmail.com` durante a validação (e possivelmente travar num ambiente sem acesso à internet). A correção adicionou timeout explícito na chamada SMTP e uma flag `NOTIFICATIONS_ENABLED` (desligada por padrão) — o serviço volta a ser chamado de verdade pelo fluxo de criação de task, mas sem risco de travar a validação automatizada.
- **Preservar contrato de API sem preservar os bugs.** Em alguns casos a correção do finding muda a resposta por definição (ex: `DELETE /api/users/:id` no projeto 2 respondia com uma mensagem que admitia deixar dados órfãos — corrigir o bug exige mudar essa mensagem). O critério adotado, documentado no `SKILL.md`, foi: mesmo path/método/formato de sucesso sempre que possível; mudança de contrato só quando o próprio finding é sobre o contrato estar errado, e sempre citada na validação da Fase 3.
- **Padronizar quantos findings "bastam".** Nas primeiras execuções mentais do fluxo o número de findings variava bastante por severidade; fixei no `SKILL.md`/`audit-report-template.md` o mínimo de 5 findings com pelo menos 1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW, e a regra de "não fechar o relatório sem bater esse mínimo, releia o código". Na prática as 3 execuções ficaram bem acima do mínimo (18–21 findings).

## Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask (monólito) | 20 | 6 | 5 | 5 | 4 |
| 2 — ecommerce-api-legacy | Node.js/Express (God Class) | 18 | 5 | 5 | 4 | 4 |
| 3 — task-manager-api | Python/Flask (camadas cosméticas) | 21 | 6 | 5 | 6 | 4 |

Relatórios completos em [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md) e [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Antes/depois da estrutura de cada projeto

**Projeto 1** — de 4 arquivos planos (`app.py`, `controllers.py`, `models.py`, `database.py`, SQL concatenado, senha em texto puro) para:
```
src/{config,models,controllers,views,middlewares,services}/  (+ app.py como entry point)
```

**Projeto 2** — de 3 arquivos com uma God Class (`AppManager.js` fazendo DB + rotas + regra de negócio) para:
```
src/{config,models,controllers,routes,middlewares,services}/  (+ server.js como entry point)
```

**Projeto 3** — de uma separação em pastas cosmética (`models/routes/services/utils` já existiam, mas `services/`/`utils/` nunca eram chamados) para a mesma estrutura de pastas **com a camada `controllers/` que faltava adicionada**, e `services/`/`utils/` reconectados ao fluxo real — a mudança aqui é majoritariamente de comportamento, não de nomes de pasta.

### Checklist de validação (preenchido para os 3 projetos)

```markdown
### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python nos projetos 1 e 3, JavaScript/Node no 2)
- [x] Framework detectado corretamente (Flask 3.1.1 / Express ^4.18.2 / Flask 3.0.0 + Flask-SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (inclusive projeto 2, cujo domínio real — LMS — diverge do nome da pasta)
- [x] Número de arquivos analisados condiz com a realidade (4 / 3 / 15 arquivos)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido em reference/audit-report-template.md
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (20 / 18 / 21)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow(), Model.query.get(), sqlite3.verbose())
- [x] Skill pausa e pede confirmação antes da Fase 3 (confirmado explicitamente nos 3 projetos)

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC (criada do zero nos projetos 1/2; corrigida no 3)
- [x] Configuração extraída para módulo de config (sem hardcoded) — .env/.env.example nos 3 projetos
- [x] Models criados/corrigidos para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (handler único, sem vazar exceção crua ao cliente)
- [x] Entry point claro (app.py / server.js / app.py com create_app())
- [x] Aplicação inicia sem erros (validado com boot real em venv/node_modules limpos)
- [x] Endpoints originais respondem corretamente (validado com curl em todos os endpoints principais)
```

### Logs das aplicações rodando após a refatoração

**Projeto 1** (`python app.py`):
```
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```
`curl -X POST /admin/query` → `404` (endpoint removido); `curl -X POST /login` com payload de SQL Injection → `{"erro":"Email ou senha inválidos"}` (antes: bypass de autenticação).

**Projeto 2** (`npm start`):
```
Servidor rodando na porta 3000
```
`curl -X GET /api/admin/financial-report` sem header → `401 {"erro":"Acesso restrito a administradores"}`; com `x-admin-key` correto → relatório financeiro completo, sem N+1 (uma única query com JOIN).

**Projeto 3** (`python seed.py && python app.py`):
```
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
 * Serving Flask app 'app'
 * Debug mode: off
```
`curl -X DELETE /tasks/1` sem token → `401 {"error":"Autenticação necessária"}`; `curl /users` → lista de usuários sem o campo de senha/hash (antes vazava o hash MD5 de todos).

### Observações sobre o comportamento da skill em stacks diferentes

- A Fase 1 nunca assumiu a stack de antemão — em nenhum dos 3 projetos foi necessário editar `reference/project-analysis.md` entre execuções; as heurísticas baseadas em "qual manifesto de dependência existe" bastaram para Python e Node.
- O catálogo de anti-patterns generalizou bem: o mesmo item "N+1 queries" foi corretamente identificado em SQL cru (projeto 1), em callbacks aninhados (projeto 2) e em ORM (projeto 3), com a correção apropriada a cada caso vinda do playbook.
- A maior diferença de comportamento entre execuções foi na Fase 3: nos projetos 1 e 2 ela criou uma estrutura de diretórios inteiramente nova; no projeto 3 ela teve que decidir, arquivo por arquivo, o que preservar, o que mover e o que reconectar — exatamente o comportamento que `mvc-guidelines.md` pede na seção de adaptação a projetos parcialmente organizados.
- Nenhum dos 3 projetos exigiu alterar o catálogo/playbook depois da primeira versão para atingir os critérios de aceite — a análise manual prévia (que já tinha lido os 3 projetos a fundo) foi suficiente para escrever um catálogo genérico o bastante de primeira.

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado.
- Python 3.10+ (projetos 1 e 3) e Node.js 18+ (projeto 2).

### Rodando a skill em cada projeto

```bash
# Projeto 1 — Python/Flask
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — Node.js/Express (skill já copiada para .claude/skills/refactor-arch/)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — Python/Flask com camadas parciais (skill já copiada)
cd ../task-manager-api
claude "/refactor-arch"
```

Em cada execução: a Fase 1 imprime o resumo da stack, a Fase 2 imprime o relatório de auditoria e **pausa pedindo confirmação** (`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`) antes de tocar em qualquer arquivo, e a Fase 3 só roda após a confirmação.

### Rodando os projetos já refatorados

**Projeto 1:**
```bash
cd code-smells-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # e ajuste SECRET_KEY
python app.py          # http://localhost:5000
```

**Projeto 2:**
```bash
cd ecommerce-api-legacy
npm install
cp .env.example .env   # e ajuste PAYMENT_GATEWAY_KEY / ADMIN_API_KEY
npm start               # http://localhost:3000
```

**Projeto 3:**
```bash
cd task-manager-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # e ajuste SECRET_KEY
python seed.py          # popula o banco antes do primeiro boot
python app.py           # http://localhost:5000
```

### Como validar que a refatoração funcionou

- `curl http://localhost:<porta>/` e `/health` devem responder `200`.
- Os endpoints originais de cada projeto (documentados em cada `README.md`/`api.http`) devem continuar respondendo com o mesmo formato de sucesso.
- Endpoints antes inseguros devem recusar acesso sem credencial: `POST /admin/reset-db` (projeto 1), `GET /api/admin/financial-report`/`DELETE /api/users/:id` (projeto 2), `DELETE`/`PUT` em `/tasks`, `/users`, `/categories` (projeto 3) devem responder `401` sem um token/chave válido.
- Os relatórios de auditoria completos (achados que motivaram cada mudança) estão em `reports/audit-project-{1,2,3}.md`.
