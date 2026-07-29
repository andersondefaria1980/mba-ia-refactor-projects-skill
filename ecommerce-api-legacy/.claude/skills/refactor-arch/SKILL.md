---
name: refactor-arch
description: "Analyzes, audits and refactors any backend project (any language/framework) toward the MVC pattern — detects stack and architecture, catalogs anti-patterns by severity with exact file:line, generates a structured audit report, pauses for human confirmation, then refactors and validates that the app still boots and endpoints still respond. Use when the user asks to audit, refactor, or fix the architecture of a codebase."
---

# /refactor-arch

Audita e refatora automaticamente qualquer projeto backend para o padrão MVC (Model-View-Controller), independente de linguagem/framework. Executa em 3 fases sequenciais e **obrigatoriamente pausa para confirmação humana entre a Fase 2 e a Fase 3**.

Este arquivo é o roteiro de execução. O conhecimento de domínio (heurísticas de detecção, catálogo de anti-patterns, template de relatório, regras de arquitetura alvo, padrões de transformação) está em `reference/`:

- `reference/project-analysis.md` — como executar a Fase 1
- `reference/anti-pattern-catalog.md` — o que procurar na Fase 2, com severidade
- `reference/audit-report-template.md` — formato exato do relatório da Fase 2
- `reference/mvc-guidelines.md` — arquitetura alvo da Fase 3
- `reference/refactoring-playbook.md` — como transformar cada anti-pattern na Fase 3

Leia os 5 arquivos de `reference/` antes de começar a Fase 1 — eles contêm as regras que governam as 3 fases abaixo.

## Fase 1 — Análise

1. Aplique as heurísticas de `reference/project-analysis.md` para detectar linguagem, framework (com versão), dependências relevantes, domínio da aplicação, banco de dados/tabelas, e classificar a arquitetura atual.
2. Conte os arquivos-fonte relevantes analisados (exclua dependências instaladas).
3. Imprima o bloco de resumo exatamente no formato definido em `reference/project-analysis.md` (seção 6).
4. Não avance para a Fase 2 automaticamente sem exibir esse resumo primeiro.

## Fase 2 — Auditoria

1. Leia todo o código-fonte relevante do projeto (todos os arquivos contados na Fase 1).
2. Cruze o código contra **cada item** de `reference/anti-pattern-catalog.md`, incluindo a seção de APIs deprecadas — não pule itens do catálogo sem verificar.
3. Para cada problema encontrado, registre: severidade, anti-pattern, arquivo:linha exato, descrição, impacto e recomendação — seguindo `reference/audit-report-template.md`.
4. Monte o relatório completo no formato exato do template, ordenado por severidade (CRITICAL → HIGH → MEDIUM → LOW).
5. Garanta o mínimo de 5 findings, incluindo ao menos 1 CRITICAL ou HIGH, 2 MEDIUM e 2 LOW — se não atingir isso, releia o código antes de fechar o relatório.
6. Exiba o relatório completo ao usuário.
7. **Pare aqui.** Pergunte explicitamente: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e aguarde a resposta do usuário antes de tocar em qualquer arquivo. Se a resposta for negativa, encerre sem modificar nada.
8. Salve o relatório completo (sem a pergunta y/n) em `reports/audit-project-N.md` na raiz do repositório (pergunte ao usuário o número N do projeto se não estiver óbvio pelo contexto, ou infira pela ordem de execução já registrada em `reports/`).

## Fase 3 — Refatoração

Só executar após confirmação explícita do usuário na Fase 2.

1. Siga `reference/mvc-guidelines.md` para definir a estrutura de diretórios alvo — adaptando ao caso do projeto:
   - Se a arquitetura atual é monolítica/poucos arquivos: crie a estrutura `src/{config,models,views (ou routes),controllers,middlewares}/` do zero.
   - Se o projeto já tem alguma separação em pastas (ex: `models/`, `routes/`, `services/`, `utils/`) mas com problemas (camadas mortas, rotas fazendo tudo): **não recrie do zero** — corrija a estrutura existente conforme a seção "Adaptação a projetos parcialmente organizados" de `reference/mvc-guidelines.md`.
2. Para cada finding do relatório da Fase 2, aplique a transformação correspondente de `reference/refactoring-playbook.md`.
3. Preserve o contrato observável da API: mesmos endpoints, mesmos métodos HTTP, mesmo formato de resposta em caso de sucesso (a menos que o próprio finding seja sobre o contrato estar errado, ex: senha vazando em uma resposta).
4. Depois de aplicar as mudanças, **valide de fato**, não apenas visualmente:
   - Instale dependências se necessário e suba a aplicação (ex: `python app.py` / `npm start`) em background.
   - Bata com `curl` em uma amostra representativa dos endpoints originais (pelo menos um de cada recurso principal) e confirme que respondem com o status/formato esperado.
   - Verifique os logs de boot em busca de erros/exceptions.
   - Encerre o processo de teste ao final.
5. Imprima o resumo final exatamente neste formato:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante, resumida>

## Validation
  <✓ ou ✗> Application boots without errors
  <✓ ou ✗> All endpoints respond correctly
  <✓ ou ✗> Zero anti-patterns remaining (ou liste os que ficaram, com justificativa)
================================
```

6. Se algum item de validação falhar, corrija antes de declarar a Fase 3 concluída — não reporte sucesso com uma aplicação que não sobe ou endpoint quebrado.

## Regras gerais (valem para as 3 fases)

- A skill deve funcionar sem nenhuma suposição hardcoded sobre um projeto específico — todas as heurísticas vêm de `reference/`, que são agnósticas de stack.
- Nunca modifique arquivos fora da Fase 3, e nunca na Fase 3 sem confirmação prévia obtida na Fase 2.
- Sempre prefira reaproveitar código/estrutura já existente no projeto a criar abstrações novas não solicitadas pelo relatório de auditoria.
- Se o projeto usa uma stack não coberta explicitamente nos exemplos de `reference/`, aplique os mesmos princípios (heurísticas de detecção, catálogo de anti-patterns, guidelines de MVC) de forma adaptada — a skill deve generalizar, não travar por falta de um exemplo exato.
