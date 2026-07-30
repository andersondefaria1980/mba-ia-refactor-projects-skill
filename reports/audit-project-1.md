  Searched for 1 pattern, read 7 files

================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1 (requirements.txt: flask==3.1.1)
Dependencies:  flask-cors==5.0.1, sqlite3 (stdlib driver, no ORM)
Domain:        E-commerce API (produtos, usuários, pedidos/checkout, relatório de vendas)
Architecture:  Parcialmente organizado — existem app.py/controllers.py/models.py/database.py separados por arquivo, mas com violações de responsabilidade: app.py contém rotas administrativas com lógica de negócio e SQL cru embutido (reset-db, execução de query arbitrária), controllers.py mistura validação de negócio com logging via print, models.py monta SQL por concatenação de string (sem parametrização), e não há camada de config (segredos e flags hardcoded em app.py).
Source files:  4 files analyzed (app.py, controllers.py, database.py, models.py)
DB tables:     produtos, usuarios, pedidos, itens_pedido

Prosseguindo para a Fase 2 (Auditoria).

  Read 2 files

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 4

## Findings

### [CRITICAL] SQL Injection
File: models.py:28,48-50,58-61,68,92,109-111,126-129,140,148-151,155,158-161,163-166,174,188,192,220,224,279-281,289-297
Description: Praticamente toda a camada de acesso a dados monta queries SQL por concatenação de string direta com valores vindos do request (id, nome, descricao, categoria, email, senha, termo de busca, status), sem placeholders (`?`) nem parametrização do driver `sqlite3`.
Impact: Qualquer cliente pode injetar SQL arbitrário via parâmetros de rota, query string ou corpo do request (ex: `/produtos/1; DROP TABLE produtos--`, ou usando `nome`/`categoria` no POST de produto, ou `email`/`senha` no login) para ler, alterar ou apagar dados de todo o banco, incluindo bypass de autenticação em `login_usuario`.
Recommendation: Reescrever todas as queries usando placeholders parametrizados do `sqlite3` (`cursor.execute("... WHERE id = ?", (id,))`), nunca concatenar valores de entrada na string SQL.

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7-8, controllers.py:285-289
Description: `SECRET_KEY` e a flag `DEBUG` são hardcoded em `app.py`; o mesmo `SECRET_KEY`, o `db_path` e o próprio valor de `debug` são reexpostos em texto plano na resposta pública do endpoint `/health` (`controllers.py:285-289`), sem nenhuma autenticação.
Impact: Qualquer pessoa que chame `GET /health` obtém a chave secreta da aplicação (usada por Flask para assinar sessões/cookies), permitindo forjar sessões; segredos versionados em código não podem ser rotacionados com segurança.
Recommendation: Mover `SECRET_KEY` e `DEBUG` para variáveis de ambiente lidas por um módulo de config central; remover completamente esses valores da resposta de `/health` (retornar no máximo `status`/`database`/`counts`).

### [CRITICAL] God Class / God Module
File: models.py:1-314
Description: Um único módulo concentra acesso a dados e regra de negócio para três domínios completamente distintos — produtos, usuários e pedidos (incluindo cálculo de total, baixa de estoque e relatório de vendas) — sem nenhuma separação por domínio.
Impact: Qualquer alteração em uma regra de um domínio (ex: pedidos) exige tocar no mesmo arquivo usado por outros domínios (produtos, usuários), aumentando o risco de efeito colateral; impossível testar um domínio isoladamente.
Recommendation: Dividir em módulos por domínio (`models/produto.py`, `models/usuario.py`, `models/pedido.py`), cada um responsável apenas pelo seu conjunto de tabelas/regras.

### [CRITICAL] Endpoint de Execução Arbitrária (SQL)
File: app.py:59-78
Description: A rota `POST /admin/query` recebe uma string SQL livre no corpo do request (`dados.get("sql")`) e a executa diretamente via `cursor.execute(query)`, sem allowlist, sem autenticação e sem qualquer restrição de comando.
Impact: Qualquer cliente não autenticado pode executar SQL arbitrário (incluindo `DROP TABLE`, `DELETE`, leitura de qualquer coluna de qualquer tabela) — comprometimento total do banco de dados.
Recommendation: Remover este endpoint (não há caso de uso legítimo de produção para execução livre de SQL via HTTP público). Se for necessário para debug, restringir a ambiente local, exigir autenticação forte e um allowlist fechado de operações.

### [HIGH] Lógica de Negócio Dentro de Controllers/Rotas
File: app.py:47-78
Description: As rotas `/admin/reset-db` e `/admin/query` estão definidas diretamente em `app.py`, obtendo a conexão de banco (`get_db()`) e executando comandos/queries diretamente na função de rota, sem passar por controller ou model.
Impact: Não há como testar essas operações sem subir o servidor HTTP; a camada de transporte (rota) fica acoplada diretamente à camada de dados, quebrando a separação de responsabilidades do restante do projeto.
Recommendation: Extrair essas ações para funções de controller/model dedicadas (ex: `admin_controller.reset_database()`), com a rota apenas delegando a chamada.

### [HIGH] Autenticação Quebrada / Fraca
File: models.py:105-120, database.py:75-79, app.py:47-78
Description: Senhas são armazenadas e comparadas em **texto plano** (`login_usuario`, `models.py:109-111`, comparando `senha` diretamente na cláusula `WHERE`), inclusive nos dados de seed (`database.py:75-79`). O login não gera nenhum token de sessão — apenas retorna os dados do usuário. Além disso, as rotas administrativas `/admin/reset-db` e `/admin/query` (`app.py:47-78`) não possuem nenhum middleware/decorator de autenticação ou verificação de papel (`tipo == 'admin'`).
Impact: Vazamento do banco expõe senhas de todos os usuários diretamente; não existe mecanismo real de sessão autenticada, então nenhuma rota pode de fato verificar "quem está logado"; qualquer cliente pode resetar ou ler todo o banco de produção sem se autenticar.
Recommendation: Fazer hash de senha com `werkzeug.security.generate_password_hash`/`check_password_hash` (ou bcrypt/argon2); gerar token de sessão real (JWT assinado ou sessão Flask) com expiração; proteger rotas administrativas com um decorator de autenticação + checagem de papel.

### [HIGH] Acoplamento Forte / Ausência de Injeção de Dependência
File: database.py:4-11, models.py (todas as funções, via `from database import get_db`)
Description: `database.py` mantém uma conexão global (`db_connection`) instanciada diretamente dentro de `get_db()`; todas as funções de `models.py` chamam `get_db()` diretamente em vez de receber a conexão/repositório por parâmetro.
Impact: Impossível substituir a conexão real por um mock/fake em teste unitário sem monkeypatch do módulo; qualquer teste de `models.py` exige um banco SQLite real.
Recommendation: Injetar a conexão (ou uma camada de repositório) como parâmetro/dependência nas funções de model, permitindo substituição em testes.

### [HIGH] Estado Global Mutável
File: database.py:4,9-10
Description: `db_connection` é uma variável de módulo (`global db_connection`) inicializada como `None` e mutada dentro de `get_db()` a cada chamada, sendo compartilhada por todas as requisições concorrentes.
Impact: Efeitos colaterais implícitos entre requisições concorrentes; comportamento pode variar conforme a ordem/momento de inicialização, dificultando testes e depuração.
Recommendation: Encapsular a conexão em um contexto de aplicação gerenciado (ex: `app.config`/extensão Flask com `teardown_appcontext`, ou um pool de conexões) em vez de uma variável solta no módulo.

### [MEDIUM] Queries N+1
File: models.py:139-146,154-166,187-199,219-231
Description: `criar_pedido` executa uma query de produto por item do pedido dentro de um loop (duas vezes: para validar estoque e novamente para pegar o preço). `get_pedidos_usuario` e `get_todos_pedidos` fazem, para cada pedido, uma query de itens e, para cada item, mais uma query do nome do produto (cursors aninhados `cursor2`/`cursor3`).
Impact: O número de queries cresce proporcionalmente ao número de itens/pedidos, degradando a performance rapidamente conforme o catálogo/histórico de pedidos cresce.
Recommendation: Substituir os loops por `JOIN` (ex: `pedidos JOIN itens_pedido JOIN produtos`) ou por uma query única com `WHERE produto_id IN (...)` para carregar tudo de uma vez.

### [MEDIUM] Duplicação de Código
File: controllers.py:24-62,64-96; models.py:9-21,171-201,203-233,302-314
Description: `criar_produto` e `atualizar_produto` (controllers.py) repetem o mesmo bloco de validação de `nome`/`preco`/`estoque`. `get_pedidos_usuario` e `get_todos_pedidos` (models.py) são quase idênticos exceto pelo filtro `WHERE`. A montagem do dicionário de produto se repete em `get_todos_produtos` e `buscar_produtos`.
Impact: Qualquer correção de regra de validação ou de formatação de resposta precisa ser replicada manualmente em todos os pontos, gerando risco de divergência (ex: `atualizar_produto` não valida `categoria`, diferente de `criar_produto`).
Recommendation: Extrair a validação de produto para uma função compartilhada e unificar a montagem de pedidos/produtos em um helper único parametrizado pelo filtro.

### [MEDIUM] Tratamento de Erros Genérico
File: controllers.py:10-12,21-22,60-62,95-96,108-109,125-126,133-134,143-144,164-165,185-186,218-220,226-227,234-235,254-255,261-262,291-292; app.py:77-78
Description: Toda função de controller (e o endpoint `/admin/query`) usa `except Exception as e: return jsonify({"erro": str(e)}), 500`, capturando qualquer exceção genericamente e devolvendo `str(e)` diretamente ao cliente.
Impact: Mascara a causa real de bugs (todo erro vira "500 genérico" sem contexto/log estruturado) e pode vazar detalhes internos de implementação (mensagens de exceção do driver de banco, stack) para o cliente.
Recommendation: Capturar exceções específicas, logar detalhes internamente com um logger estruturado, e retornar ao cliente apenas uma mensagem de erro genérica e segura.

### [LOW] Nomenclatura Ruim de Variáveis
File: models.py:187,191,219,223; controllers.py:56,160
Description: Cursors aninhados nomeados `cursor2`/`cursor3` em vez de nomes descritivos (`cursor_itens`, `cursor_produto`); variável `id` (controllers.py:56,160) sombreia o builtin `id` do Python.
Impact: Reduz legibilidade e aumenta o risco de erro ao dar manutenção nesses trechos.
Recommendation: Renomear cursors para nomes descritivos do que buscam; renomear `id` para `produto_id`/`usuario_id` (o valor retornado pelo insert).

### [LOW] Magic Numbers / Magic Strings
File: models.py:257-262; controllers.py:52,242
Description: Faixas de desconto do relatório de vendas (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`) e as listas de categorias/status válidos (`controllers.py:52,242`) estão soltas no meio da lógica, sem constante nomeada.
Impact: A regra de negócio (faixas de desconto, categorias/status permitidos) fica implícita no meio do código, difícil de localizar e alterar com segurança — e já causou inconsistência (categoria só é validada em `criar_produto`, não em `atualizar_produto`).
Recommendation: Extrair para constantes nomeadas (ex: `FAIXAS_DESCONTO`, `CATEGORIAS_VALIDAS`, `STATUS_VALIDOS`) compartilhadas entre as funções que precisam delas.

### [LOW] Uso de `print` como Log de Produção
File: controllers.py:8,11,57,61,106,161,179,182,208-210,248,250; app.py:56,83-86
Description: Eventos de negócio e erros são registrados via `print(...)` espalhados pelo código (incluindo simulação de envio de e-mail/SMS/push em `criar_pedido`), em vez de um logger configurável.
Impact: Sem níveis de severidade, timestamps estruturados ou destino configurável, dificultando observabilidade e troubleshooting em produção.
Recommendation: Substituir por um logger padrão (`logging` do Python), configurado com nível e formato apropriados.

### [LOW] Imports Não Utilizados
File: database.py:2; models.py:2
Description: `database.py` importa `os` mas nunca o referencia; `models.py` importa `sqlite3` mas nunca o referencia diretamente (usa apenas `get_db()`).
Impact: Ruído que dificulta leitura e pode indicar refatoração incompleta.
Recommendation: Remover os imports não utilizados.

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
