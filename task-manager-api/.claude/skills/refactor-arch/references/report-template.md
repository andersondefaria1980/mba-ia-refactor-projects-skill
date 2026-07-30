# Template do Relatório de Auditoria (Fase 2)

Use exatamente esta estrutura para o relatório impresso ao final da Fase 2. Preencha os placeholders `<...>` com os dados reais do projeto analisado na Fase 1 e os findings encontrados.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório/projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Nome do anti-pattern>
File: <arquivo.ext>:<linha ou faixa de linhas>
Description: <o que foi encontrado, em 1-2 frases objetivas>
Impact: <consequência concreta se não for corrigido>
Recommendation: <ação de correção recomendada>

### [CRITICAL] <próximo finding CRITICAL, se houver>
...

### [HIGH] <Nome do anti-pattern>
File: <arquivo.ext>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Nome do anti-pattern>
File: <arquivo.ext>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <Nome do anti-pattern>
File: <arquivo.ext>:<linha>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

1. **Ordem obrigatória:** os findings devem aparecer agrupados e ordenados por severidade, sempre `CRITICAL → HIGH → MEDIUM → LOW`. Dentro da mesma severidade, ordene pela ordem em que os anti-patterns aparecem no catálogo (`references/antipattern-catalog.md`).
2. **`File:` sempre com linha exata** — nunca "arquivo inteiro" sem número de linha; se o anti-pattern ocorre em várias linhas do mesmo arquivo, liste todas (ex: `models.py:28,48-50,68`) ou uma faixa (`models.py:1-350`) quando for um God Module.
3. **Um finding por anti-pattern detectado**, mesmo que o mesmo anti-pattern se repita em arquivos diferentes — nesse caso, crie um finding por arquivo (ou agrupe citando todos os arquivos, se fizer mais sentido para leitura), nunca oculte ocorrências.
4. **`## Summary`** deve refletir a contagem real de findings por severidade — some antes de escrever o relatório, não estime.
5. **`Files: <N> analyzed | ~<LOC> lines of code`** deve usar os mesmos números detectados na Fase 1 (arquivos de código-fonte, ignorando dependências/build/cache).
6. **Nunca omita a pergunta final** `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` — é o gate obrigatório de confirmação humana antes de qualquer modificação de arquivo na Fase 3. Pare e aguarde a resposta do usuário; não assuma "sim".
7. Se nenhum finding de uma severidade for encontrado, omita a seção dela nos Findings mas mantenha o contador em `0` no Summary (ex: `LOW: 0`).
