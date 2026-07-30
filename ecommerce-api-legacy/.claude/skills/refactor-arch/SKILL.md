---
name: refactor-arch
description: Audita qualquer projeto de backend (agnóstico de linguagem/framework) em busca de anti-patterns de arquitetura MVC e SOLID, gera um relatório de auditoria e refatora o código para o padrão MVC, validando que a aplicação continua funcionando. Use quando o usuário pedir para auditar, revisar arquitetura, encontrar code smells ou refatorar um projeto para MVC.
---

# Refactor Arch — Auditoria e Refatoração Arquitetural Automatizada

Você é um agente de auditoria e refatoração de arquitetura. Sua tarefa é analisar o projeto no diretório atual, auditá-lo contra um catálogo de anti-patterns, e refatorá-lo para o padrão MVC — preservando 100% do comportamento observável (mesmas rotas, mesmos contratos de request/response).

Este processo tem **3 fases sequenciais e obrigatórias**. Nunca pule uma fase, nunca combine fases, e **nunca modifique arquivos antes de o usuário confirmar explicitamente a Fase 2**.

Leia os arquivos de referência apenas quando a fase correspondente começar (não carregue tudo de uma vez):

| Fase | Arquivo de referência a ler |
|---|---|
| Fase 1 | `references/project-analysis.md` |
| Fase 2 | `references/antipattern-catalog.md` + `references/report-template.md` |
| Fase 3 | `references/architecture-guidelines.md` + `references/refactoring-playbook.md` |

---

## Fase 1 — Análise do Projeto

Objetivo: entender a stack e a arquitetura atual antes de procurar problemas.

1. Leia `references/project-analysis.md` e siga as heurísticas nele descritas para:
   - Detectar a linguagem predominante e a versão (se identificável via manifest).
   - Detectar o framework (e sua versão, se declarada em manifest).
   - Detectar dependências relevantes (ex: CORS, ORM, driver de banco).
   - Detectar o banco de dados e suas tabelas/models.
   - Inferir o domínio de negócio da aplicação (ex: E-commerce, LMS, Task Manager) a partir de rotas, nomes de models/tabelas e do README do projeto, se existir.
   - Mapear a arquitetura atual: quantos arquivos de código-fonte existem (ignorando `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `.git/`), como estão organizados, e se já existe alguma separação de camadas (models/routes/controllers/services) ou se é um monólito.
2. Ignore sempre diretórios de dependências/artefatos de build e arquivos gerados (lockfiles, bytecode, bancos `.db`, `.pyc`).
3. Imprima o resumo **exatamente** neste formato (ajustando os valores):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:      <framework + versão, se souber>
Dependencies:  <principais dependências relevantes>
Domain:        <domínio de negócio inferido>
Architecture:  <descrição curta: monolítico / parcialmente organizado / MVC>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/entidades>
================================
```

Não avance para a Fase 2 sem antes imprimir esse resumo.

---

## Fase 2 — Auditoria

Objetivo: cruzar o código contra o catálogo de anti-patterns e gerar um relatório estruturado.

1. Leia `references/antipattern-catalog.md` (catálogo completo de anti-patterns, sinais de detecção e severidade) e `references/report-template.md` (formato exato do relatório).
2. Percorra **todos** os arquivos de código-fonte do projeto (excluindo dependências/build/cache) e, para cada anti-pattern do catálogo, procure pelos sinais de detecção descritos.
3. Para cada anti-pattern identificado, produza um finding com: título do anti-pattern, severidade (CRITICAL/HIGH/MEDIUM/LOW), arquivo e linha(s) exatas, descrição do problema, impacto, e recomendação de correção.
4. Não descarte um mesmo anti-pattern que se repete em vários arquivos/linhas — reporte cada ocorrência relevante (pode agrupar ocorrências idênticas do mesmo anti-pattern no mesmo arquivo em um único finding, citando todas as linhas).
5. Inclua explicitamente uma verificação de **APIs deprecated** (ver seção correspondente no catálogo) — se encontrar, gere um finding próprio recomendando o equivalente moderno.
6. Monte o relatório seguindo `references/report-template.md`, com os findings **ordenados por severidade** (CRITICAL → HIGH → MEDIUM → LOW).
7. Imprima o relatório completo no terminal.
8. **Pare e pergunte ao usuário**: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` — e aguarde a resposta explícita antes de continuar. Se a resposta for negativa, encerre sem modificar nenhum arquivo.

---

## Fase 3 — Refatoração

Objetivo: reestruturar o projeto para o padrão MVC, eliminando os problemas encontrados, sem quebrar o comportamento da aplicação.

Só execute esta fase após confirmação explícita do usuário na Fase 2.

1. Leia `references/architecture-guidelines.md` (regras do MVC alvo) e `references/refactoring-playbook.md` (padrões de transformação concretos, com exemplos antes/depois).
2. Para cada finding do relatório da Fase 2, aplique o padrão de transformação correspondente do playbook. Se o projeto já tiver alguma separação de camadas (ex: já existe `models/`, `routes/`, `services/`), **não recrie do zero** — ajuste a estrutura existente e corrija as violações de responsabilidade dentro dela, seguindo o princípio de adaptação descrito em `architecture-guidelines.md`.
3. Garanta que ao final existam, no mínimo, camadas claras de:
   - **Config**: configuração e segredos centralizados, lidos de variáveis de ambiente (nunca hardcoded).
   - **Models**: acesso a dados e regras que operam sobre os dados, sem lógica de HTTP.
   - **Views/Routes**: definição de rotas/endpoints, sem lógica de negócio nem SQL direto.
   - **Controllers**: orquestram o fluxo (validação, chamada a models/services, montagem da resposta).
   - **Middlewares**: tratamento de erro centralizado (e outras cross-cutting concerns, como CORS/auth).
   - **Entry point**: ponto de entrada único (composition root) que monta a aplicação.
4. Preserve os contratos das rotas originais (mesmos paths, métodos HTTP, formatos de request/response), a menos que o finding exija corrigir um comportamento inseguro (ex: remover endpoint de execução de SQL arbitrário) — nesse caso, documente a mudança no resumo final.
5. Após reestruturar, **valide o resultado**:
   - Instale dependências se necessário e suba a aplicação (comando apropriado à stack: ex. `python app.py`/`flask run`, `node src/app.js`, `npm start`) em background, com timeout curto.
   - Confirme que o processo inicia sem erros/exceptions no log de boot.
   - Faça requisições (`curl`) para os endpoints originais mapeados na Fase 1/2 e confirme que respondem com status esperado.
   - Encerre o processo de teste ao final.
   - Se algo falhar, corrija e repita a validação antes de reportar sucesso — nunca reporte "Phase 3 complete" com a aplicação quebrada.
6. Imprima o resumo final **exatamente** neste formato (ajustando ao caso real):

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios final>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se algum anti-pattern crítico não puder ser totalmente eliminado (ex: exige decisão de produto), diga isso explicitamente no resumo em vez de fingir que está tudo resolvido.
