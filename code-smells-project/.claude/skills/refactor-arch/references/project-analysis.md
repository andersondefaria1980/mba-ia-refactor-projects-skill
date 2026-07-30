# Heurísticas de Análise de Projeto (Fase 1)

Estas heurísticas são deliberadamente agnósticas de tecnologia: baseiam-se em manifests, extensões de arquivo e padrões textuais que existem (com pequenas variações) em praticamente qualquer stack de backend.

## 0. Diretórios e arquivos a sempre ignorar

Nunca conte, liste ou analise conteúdo dentro de:

- `node_modules/`, `.venv/`, `venv/`, `env/`, `__pycache__/`, `.git/`, `dist/`, `build/`, `.next/`, `target/`, `vendor/`
- Lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`), bytecode (`*.pyc`, `*.class`), binários de banco (`*.db`, `*.sqlite`), e arquivos de ambiente sensíveis (`.env` — pode ler para checar *nomes* de variáveis, mas nunca exponha valores de segredo real no relatório).

"Source files analyzed" = contagem de arquivos de código-fonte fora dessas pastas.

## 1. Detectar a linguagem

Conte a extensão predominante entre os arquivos de código-fonte:

| Extensão | Linguagem |
|---|---|
| `.py` | Python |
| `.js`, `.mjs`, `.cjs` | JavaScript |
| `.ts` | TypeScript |
| `.rb` | Ruby |
| `.php` | PHP |
| `.java` | Java |
| `.go` | Go |

Se houver manifest (ver seção 2), ele confirma a linguagem com mais certeza que a contagem de extensões.

## 2. Detectar o framework e a versão

Procure primeiro em arquivos de manifest de dependências — eles são a fonte mais confiável:

| Manifest | O que procurar |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | `flask`, `Flask`, `django`, `Django`, `fastapi`, `FastAPI` (com versão ao lado, ex: `flask==3.1.1`) |
| `package.json` (`dependencies`) | `express`, `koa`, `fastify`, `@nestjs/core` |
| `Gemfile` | `rails`, `sinatra` |
| `composer.json` | `laravel/framework`, `slim/slim` |
| `go.mod` | `gin-gonic/gin`, `labstack/echo` |

Se não houver manifest ou a versão não estiver pinada, confirme via import/require no código e reporte apenas o nome do framework (sem inventar versão):

- Python/Flask: `from flask import Flask`, `app = Flask(__name__)`
- Python/Django: `manage.py`, `django.conf.urls`, `settings.py` com `INSTALLED_APPS`
- Python/FastAPI: `from fastapi import FastAPI`
- Node/Express: `require('express')` ou `import express from 'express'`, `app.listen(...)`

Liste também 2–3 dependências relevantes além do framework (ex: driver de banco, CORS, validação) — não a lista inteira do manifest.

## 3. Detectar o banco de dados

Sinais, em ordem de confiabilidade:

1. Variáveis de ambiente / config: `DATABASE_URL`, `SQLALCHEMY_DATABASE_URI`, `DB_PATH`, string de conexão em `.env` ou em um módulo de config.
2. Driver/ORM importado: `sqlite3`, `psycopg2`/`pg`, `mysql2`/`pymysql`, `sqlalchemy`/`flask_sqlalchemy`, `sequelize`, `mongoose`, `sqlite3` (Node).
3. Definições de schema/tabela no código: `CREATE TABLE ...`, classes de model de ORM (`class X(db.Model)`, `sequelize.define(...)`).

Liste as tabelas/entidades encontradas (nomes de tabela ou de classes de model) — isso também ajuda a inferir o domínio (seção 4).

## 4. Inferir o domínio de negócio

Combine estes sinais (não dependa de um único):

- Nomes de rotas/endpoints (ex: `/produtos`, `/pedidos`, `/checkout`, `/tasks`, `/courses`).
- Nomes de tabelas/models (ex: `produtos`, `pedidos`, `enrollments`, `payments`, `tasks`, `categories`).
- Título/descrição no `README.md` do projeto, se existir.
- Mensagens de log ou comentários que descrevam o propósito do sistema.

Descreva o domínio em uma frase curta e concreta (ex: "E-commerce API (produtos, pedidos, usuários)", "LMS API com fluxo de checkout", "Task Manager API").

## 5. Mapear a arquitetura atual

Classifique o projeto em uma destas categorias (e explique em uma linha por quê):

- **Monolítico** — toda a lógica (rotas, acesso a dados, regras de negócio) concentrada em 1–4 arquivos na raiz, sem pastas por responsabilidade.
- **Parcialmente organizado** — já existem pastas como `models/`, `routes/`, `services/`, `utils/`, mas com violações de responsabilidade dentro delas (ex: rota fazendo query direta, model com lógica de e-mail, config espalhada).
- **MVC/organização adequada** — separação clara e consistente de camadas, sem violações relevantes (raro nos projetos-alvo desta skill, mas a heurística deve prever esse caso para não forçar refatoração desnecessária).

Para chegar a essa classificação, olhe rapidamente:

- Existe um único arquivo que mistura conexão com banco, query SQL, validação e definição de rota? → monolítico.
- Existem pastas por camada, mas alguma delas (ex: `routes/`) contém lógica que deveria estar em outra (ex: cálculo de negócio, envio de e-mail, SQL cru)? → parcialmente organizado.
- Config/segredos estão centralizados em um único módulo lido de variáveis de ambiente, sem hardcode? Isso é um sinal positivo a favor de "MVC/organização adequada" — mas não é suficiente sozinho.

## 6. Formato de saída da Fase 1

Sempre gere o resumo com estes 7 campos, nesta ordem, mesmo que algum valor seja "não identificado":

```
Language:      ...
Framework:      ...
Dependencies:  ...
Domain:        ...
Architecture:  ...
Source files:  <N> files analyzed
DB tables:     ...
```
