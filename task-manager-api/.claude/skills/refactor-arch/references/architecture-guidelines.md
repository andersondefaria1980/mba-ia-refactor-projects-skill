# Guidelines de Arquitetura MVC Alvo (Fase 3)

Estas regras definem o "padrão MVC" que a refatoração deve produzir, independente da linguagem/framework. Os nomes de pasta abaixo são a convenção padrão desta skill — adapte apenas o necessário para a convenção idiomática da stack (ex: em Node é comum `routes/` no lugar de `views/`), mas **mantenha sempre a separação de responsabilidades descrita**, não apenas os nomes de pasta.

## As camadas

### Models
- Representam dados e acesso a dados (queries/ORM), e regras que operam puramente sobre esses dados (ex: `is_overdue()`, `validate_priority()`).
- **Não conhecem HTTP**: nunca recebem `request`/`response`, nunca retornam JSON formatado para o cliente, nunca leem query string.
- Toda query a banco deve usar parâmetros/prepared statements ou API do ORM — nunca concatenação de string.
- Um arquivo/módulo de model por entidade de domínio (ex: `produto_model.py`, `user.py`), nunca um único arquivo com todas as entidades.

### Views / Routes
- Definem os endpoints (path + método HTTP) e fazem o roteamento para o controller correspondente.
- **Não contêm lógica de negócio nem SQL direto** — apenas: receber request → chamar controller → repassar a resposta.
- Se o framework não distinguir fisicamente "view" de "rota" (comum em APIs REST sem template engine), esta camada é o arquivo de definição de rotas (`routes.py`, `*_routes.js`) — não é necessário inventar uma camada de "view" HTML onde não existe.

### Controllers
- Orquestram o fluxo de uma requisição: validam entrada (ou delegam a um validador), chamam o model/service necessário, tratam erros esperados do domínio, montam a resposta.
- São a única camada que "conversa" tanto com Views/Routes quanto com Models — mas nunca contêm SQL cru nem regras de negócio complexas de longo prazo (essas ficam no model/service).
- Idealmente finos: se um controller começa a acumular cálculo de negócio extenso, extraia para uma camada de `services/`.

### Config
- Único ponto de leitura de configuração e segredos (`SECRET_KEY`, string de conexão, chaves de API, credenciais de SMTP/pagamento), sempre a partir de variáveis de ambiente (`.env` + `os.environ`/`process.env`), nunca hardcoded no código-fonte.
- Se o projeto já tiver um `.env` com variáveis não utilizadas, o config deve efetivamente lê-las (não deixar duplicidade entre valor hardcoded e valor do `.env`).

### Middlewares
- Concerns transversais: tratamento de erro centralizado (um único handler que padroniza respostas de erro), CORS, autenticação/autorização, logging de requisições.
- Tratamento de erro **não deve ser duplicado** em cada controller com blocos `try/except`/`try/catch` genéricos — controllers tratam erros de negócio esperados (ex: "não encontrado"), o middleware trata o inesperado (exceções não previstas → resposta 500 padronizada, sem vazar stack trace/detalhes internos ao cliente).

### Entry point (composition root)
- Um único arquivo (`app.py`, `src/app.js`) responsável por: instanciar a aplicação, carregar config, registrar middlewares, registrar rotas, e iniciar o servidor.
- **Não contém lógica de negócio nem definição de rota inline** (além, no máximo, de rotas triviais de health-check).

## Estrutura de diretórios de referência

```
<raiz do projeto>/
├── config/         # configuração e segredos (lidos de env)
├── models/         # uma entidade de domínio por arquivo
├── views/          # ou routes/ — definição de endpoints
│   └── routes.py (ou *_routes.js)
├── controllers/     # orquestração por domínio
├── middlewares/     # tratamento de erro, auth, CORS, logging
└── app.py (ou src/app.js)   # entry point / composition root
```

Ajuste os nomes para o idioma da stack (ex.: em projetos Node é aceitável `src/routes/`, `src/controllers/`, `src/config/`), mas preserve a intenção de cada camada.

## Regra de dependência

A direção de dependência é sempre:

```
Views/Routes → Controllers → Models / Services
```

- Views/Routes nunca chamam Models diretamente, pulando o Controller.
- Controllers nunca executam SQL cru — sempre via Model.
- Models nunca importam nada de Views/Controllers (dependência é unidirecional).

## Princípio de adaptação (projetos já parcialmente organizados)

Nem todo projeto-alvo é um monólito de 3-4 arquivos. Quando o projeto já possuir pastas como `models/`, `routes/`, `services/`, `utils/` (ver classificação da Fase 1 em `project-analysis.md`):

- **Não recrie a estrutura do zero.** Recriar pastas que já existem e já estão no lugar certo é retrabalho desnecessário e aumenta o risco de quebrar o que já funciona.
- **Corrija violações de responsabilidade dentro da estrutura existente.** Exemplos: se uma rota está fazendo `Model.query...` diretamente múltiplas vezes de forma repetitiva ao invés de usar um método do model/service, ou se um `service` faz SMTP com credenciais hardcoded em vez de usar o config central, corrija isso in-place.
- **Introduza apenas a(s) camada(s) que realmente faltam.** Ex: se não existe `config/` centralizado e os segredos estão espalhados em múltiplos arquivos, crie `config/` e migre os módulos para consumi-lo. Se não existe middleware de erro centralizado e cada rota repete o mesmo `try/except` genérico, extraia para `middlewares/error_handler.py` (ou equivalente) e registre-o no entry point.
- O critério de sucesso não é "a árvore de diretórios mudou", é "as violações de responsabilidade do relatório da Fase 2 foram eliminadas, preservando o que já estava correto".

## Compatibilidade com o comportamento existente

- Os endpoints (path, método HTTP, formato de request/response) devem continuar respondendo da mesma forma após a refatoração, **exceto** quando o próprio finding exigir mudança de comportamento por segurança (ex: remoção de um endpoint que executa SQL arbitrário, ou de um endpoint que vaza segredos na resposta). Nesses casos, a mudança deve ser explicitamente documentada no resumo final da Fase 3.
- Nunca "quebre" um endpoint só para deixar o código estruturalmente mais bonito — o objetivo é eliminar anti-patterns sem regressão funcional.
