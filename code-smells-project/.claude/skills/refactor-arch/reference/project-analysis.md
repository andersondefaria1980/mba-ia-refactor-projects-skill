# Heurísticas de Análise de Projeto (Fase 1)

Objetivo da Fase 1: em poucos minutos, sem assumir nada sobre a stack de antemão, produzir um resumo confiável de linguagem, framework, dependências, domínio, arquitetura atual e banco de dados. Este documento é agnóstico de tecnologia — as heurísticas abaixo servem tanto para Python quanto para Node.js (ou qualquer outra stack de backend web) e devem ser aplicadas na ordem descrita.

## 1. Detecção de linguagem

Olhe para arquivos de manifesto de dependências na raiz do projeto, em ordem de prioridade:

| Arquivo encontrado | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python |
| `package.json` | JavaScript/TypeScript (Node.js) |
| `go.mod` | Go |
| `pom.xml`, `build.gradle` | Java/Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |

Se nenhum manifesto existir, use a extensão predominante dos arquivos-fonte (`find . -name "*.py" | wc -l` vs `*.js` etc.) como fallback.

## 2. Detecção de framework e versão

- **Python**: leia o manifesto de dependências e procure por `flask`, `django`, `fastapi`, `bottle`. Extraia a versão exata pinada (`flask==3.1.1`). Se não houver pin, rode `pip show <pacote>` no ambiente ativo, ou informe "versão não pinada".
- **Node.js**: leia `package.json` → `dependencies`. Procure `express`, `koa`, `fastify`, `nestjs`. Para a versão *resolvida* (não apenas o range do `package.json`), prefira `package-lock.json` (`packages["node_modules/<pkg>"].version`) quando existir.
- Liste também dependências relevantes para a auditoria (ORMs, drivers de banco, libs de auth, `cors`, etc.) — elas entram no resumo da Fase 1 e ajudam a prever quais anti-patterns procurar (ex: presença de `flask-cors`/`cors` sem config de origem sinaliza possível CORS aberto).

## 3. Detecção de banco de dados

Procure, nesta ordem:
1. Import/require de driver de banco no código (`sqlite3`, `psycopg2`, `pymysql`, `mysql`, `pg`, `mongoose`, `sqlalchemy`).
2. String de conexão (mesmo hardcoded) — ex: `sqlite:///arquivo.db`, `postgresql://...`.
3. Arquivo `.db`/`.sqlite` presente na raiz do projeto.
4. Definições de schema/tabela — em SQL puro (`CREATE TABLE ...`) ou em classes de ORM (`class Produto(db.Model)`, `sequelize.define(...)`).

Para cada tabela/entidade encontrada, anote o nome e, se possível, as colunas — isso alimenta a seção "DB tables" do resumo e ajuda a nomear os Models na Fase 3.

## 4. Mapeamento de domínio da aplicação

Não adivinhe o domínio pelo nome da pasta do projeto — ele pode estar errado (ex: uma pasta chamada `ecommerce-*` pode na verdade implementar um LMS). Infira o domínio real a partir de:
- Nomes de rotas/endpoints (`/produtos`, `/cursos`, `/matriculas`, `/tasks`).
- Nomes de tabelas/entidades no banco.
- Textos de resposta, comentários e nomes de variáveis em português/inglês no código.

Descreva o domínio em uma frase objetiva (ex: "API de Task Manager (tarefas, categorias, usuários)").

## 5. Mapeamento da arquitetura atual

Classifique a organização atual em uma das categorias:

- **Monolítica de arquivo único ou poucos arquivos**: toda a lógica (rotas + regra de negócio + acesso a dados) concentrada em 1-4 arquivos na raiz, sem pastas por responsabilidade.
- **Camadas parciais/cosméticas**: existem pastas como `models/`, `routes/`, `services/`, `utils/`, mas isso por si só **não significa que a arquitetura está correta**. Confirme se cada camada é de fato usada:
  - As rotas chamam `services`/`models`, ou fazem query direta ao banco e reimplementam lógica que já existe em outro lugar?
  - Alguma pasta existe mas nunca é importada por ninguém (camada morta)? Rode uma busca (`grep -r "from services" .` / `grep -r "require.*services" .`) para confirmar uso real, não apenas presença da pasta.
- **MVC real**: Models, Views/Routes e Controllers claramente separados, cada um com responsabilidade única, sem lógica de negócio vazando para fora dos Controllers/Services e sem acesso a dados fora dos Models.

Conte o número de arquivos-fonte analisados (exclua dependências instaladas, ex: `node_modules/`, `venv/`, `__pycache__/`) para a linha "Source files: N files analyzed".

## 6. Formato do resumo da Fase 1

Ao final, imprima um bloco assim (adaptando os valores):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework> <versão>
Dependencies:  <libs relevantes, separadas por vírgula>
Domain:        <descrição objetiva do domínio>
Architecture:  <classificação da seção 5 + justificativa curta>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/entidades>
================================
```
