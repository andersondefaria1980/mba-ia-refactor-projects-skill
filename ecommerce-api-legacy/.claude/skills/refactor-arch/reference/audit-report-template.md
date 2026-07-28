# Template do Relatório de Auditoria (Fase 2)

A saída da Fase 2 deve seguir exatamente esta estrutura. É este texto que deve ser salvo em `reports/audit-project-N.md` e mostrado ao usuário antes de pedir a confirmação para avançar à Fase 3.

## Regras de formatação

- **Ordene os findings por severidade**: todos os `CRITICAL` primeiro, depois `HIGH`, depois `MEDIUM`, depois `LOW`. Dentro da mesma severidade, ordem de descoberta é aceitável.
- Todo finding **deve** ter arquivo e linha(s) exatos — nunca "em algum lugar do models.py". Se o problema abrange um intervalo, use `arquivo.py:10-45`.
- Use a nomenclatura de severidade em maiúsculas (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) exatamente como no catálogo de anti-patterns.
- O nome do anti-pattern no título de cada finding deve vir do catálogo (`reference/anti-pattern-catalog.md`) sempre que se aplicar; se for um problema específico do projeto que não se encaixa em nenhum item do catálogo, ainda assim classifique por severidade usando a rubrica de `SKILL.md`.
- Inclua **Impact** (consequência concreta se não for corrigido) e **Recommendation** (o que fazer, referenciando o playbook de refatoração quando aplicável) em todo finding.
- Ao final, sempre pausar com o prompt de confirmação exato mostrado abaixo — não prosseguir para a Fase 3 sem uma resposta afirmativa explícita do usuário.

## Estrutura exata

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto/pasta>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<N> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <Nome do Anti-Pattern>
File: <arquivo>:<linha ou intervalo>
Description: <o que foi encontrado, específico e concreto>
Impact: <consequência real se não corrigido>
Recommendation: <ação de correção, referenciando o playbook quando aplicável>

### [<SEVERIDADE>] <Nome do Anti-Pattern>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

<... um bloco por finding, na ordem de severidade ...>

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
>
```

## Observações

- O relatório completo (do cabeçalho `ARCHITECTURE AUDIT REPORT` até a linha `Total: N findings`, sem incluir a interação y/n) é o conteúdo a ser salvo em `reports/audit-project-N.md`.
- Se o número de findings for menor que 5, isso é um sinal de que a Fase 2 não foi minuciosa o suficiente — releia o código e o catálogo de anti-patterns antes de fechar o relatório. O mínimo aceitável é 5 findings, com pelo menos 1 CRITICAL ou HIGH, 2 MEDIUM e 2 LOW.
- Nunca modifique nenhum arquivo do projeto durante a Fase 2 — ela é somente leitura + geração do relatório.
