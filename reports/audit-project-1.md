I'll start Phase 1 of the architecture audit. Let me read the analysis guidelines and explore the project structure.

  Read 1 file, ran 1 shell command

The working tree currently has the monolithic pre-refactor files (app.py, controllers.py, database.py, models.py) — the previous MVC structure was deleted (uncommitted). I'll analyze this current monolithic state for Phase 1.

  Searched for 1 pattern, read 7 files

4 Python source files at the root, confirming the monolithic layout. Here's the Phase 1 summary:

================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors==5.0.1, sqlite3 (stdlib, no ORM)
Domain:        E-commerce API (produtos, usuários, pedidos/checkout)
Architecture:  Monolítico — 4 arquivos na raiz (app.py, controlly); app.py mistura definição de rotas com endpoints admin de alto risco (reset-db, execução de SQL arbitrário) e SECRET_KEY hardcoded; controllers.py mistura validação, orquestração e regra de negócio (envio de
"email/SMS/push" simulado); models.py concatena SQL cru via f-sttem camada de config nem middleware de erro/auth
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

Prosseguindo para a Fase 2 — Auditoria, lendo o catálogo de anti-patterns e o template de relatório.

  Searched for 2 patterns, read 2 files, ran 1 shell command

Now I have everything needed for the full audit report.

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] SQL Injection
File: models.py:28,48-50,58-60,68,92,110-111,126-129,140,148-151192,206,220,224,280,291-297
Description: Praticamente todas as queries de `models.py` são montadas por concatenação de string com valores vindos diretamente de parâmetros de rota/JSON do
request (id, nome, email, senha, termo de busca, status), sem plarâmetros do driver `sqlite3`. `buscar_produtos` (291-297) e`login_usuario` (109-111) são especialmente críticos por aceitarem texto livre do usuário.
Impact: Qualquer cliente pode ler, alterar ou apagar dados arbitbela de usuários/senhas) e potencialmente contornar o login viainjeção na query de autenticação.
Recommendation: Reescrever todas as queries usando parâmetros poor.execute("... WHERE id = ?", (id,))`) em vez deconcatenação/f-string.

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7, controllers.py:289
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` está hardcoded em `app.py:7` e o mesmo valor é reexposto publicamente na resposta JSON do endpoint
`/health` em `controllers.py:289`, junto com `debug: True`.
Impact: Qualquer pessoa com acesso ao repositório — ou simplesmente chamando `/health` — obtém a chave de assinatura de sessão da aplicação, permitindo forjar
sessões/tokens.
Recommendation: Ler `SECRET_KEY` de variável de ambiente via um módulo de config centralizado; nunca retornar segredos em respostas de API, inclusive
endpoints de diagnóstico.

### [CRITICAL] God Class / God Module
File: models.py:1-315
Description: Um único arquivo concentra acesso a dados e regras ão relacionados — produtos, usuários e pedidos/relatórios —incluindo cálculo de total de pedido, verificação de estoque e regras de desconto de faturamento.
Impact: Qualquer alteração em um domínio (ex: usuários) arrisca ex: pedidos); impossível testar cada domínio isoladamente.
Recommendation: Separar em módulos/models por domínio (`produto_model.py`, `usuario_model.py`, `pedido_model.py`).

### [CRITICAL] Endpoint de Execução Arbitrária (SQL)
File: app.py:59-78
Description: A rota `/admin/query` recebe uma string SQL bruta no corpo do request (`dados.get("sql", "")`) e a executa diretamente via
`cursor.execute(query)`, sem autenticação, allowlist ou validaçã
Impact: Qualquer cliente não autenticado pode executar SQL arbitrário — leitura, alteração ou destruição total do banco de dados (`DROP TABLE`, exfiltração de
senhas, etc.).
Recommendation: Remover o endpoint. Se houver necessidade legítima de administração, substituir por um conjunto fechado de ações pré-definidas, autenticadas e
auditadas.

### [HIGH] Lógica de Negócio Dentro de Controllers/Rotas
File: app.py:47-57,59-78; controllers.py:208-210,247-250
Description: `app.py` define as rotas `/admin/reset-db` e `/admidiretamente (`get_db()`, `cursor.execute`), pulando inteiramentea camada de controller/model. Em `controllers.py`, o disparo de notificações (e-mail/SMS/push simulados em `criar_pedido` e mensagens de notificação em
`atualizar_status_pedido`) é uma regra de negócio embutida direta um service.
Impact: Rotas administrativas ficam fora de qualquer padrão de validação/autorização usado pelo resto da app; regras de notificação não podem ser reutilizadas
nem testadas sem subir o servidor HTTP inteiro.
Recommendation: Mover toda query direta de `app.py` para models; extrair o disparo de notificações para um `notification_service` chamado pelo controller.

### [HIGH] Autenticação Quebrada / Fraca
File: models.py:105-120,72-87,122-131; database.py:75-84; controas `/admin/*` sem nenhum middleware de autenticação)
Description: Senhas são armazenadas e comparadas em **texto puro**, sem hash (`login_usuario` compara `senha` recebida diretamente contra a coluna `senha` do
banco; seed em `database.py:75-84` grava senhas como `"admin123" retornado pela API em `listar_usuarios`/`buscar_usuario`(`controllers.py:128-134`, via `models.get_todos_usuarios`/`get_usuario_por_id`). Nenhuma rota do projeto — nem as administrativas (`/admin/reset-db`,
`/admin/query`) — exige token/sessão.
Impact: Vazamento do banco expõe todas as senhas em claro; a API já vaza senhas de todos os usuários por padrão; qualquer cliente não autenticado pode resetar
o banco ou executar SQL arbitrário.
Recommendation: Fazer hash de senha com `werkzeug.security.generate_password_hash`/`check_password_hash` (ou bcrypt/argon2); nunca retornar o campo `senha`
nas respostas; implementar um middleware/decorator de autenticaçodas as rotas, especialmente `/admin/*`.

### [HIGH] Acoplamento Forte / Ausência de Injeção de Dependênci
File: database.py:4-11; models.py (todas as funções, via `from database import get_db`)
Description: `database.py` abre uma conexão SQLite concreta em urmazenada em variável de módulo; `models.py` importa e chama`get_db()` diretamente em cada função, sem nenhum ponto de injeção.
Impact: Impossível substituir a conexão por um mock/banco de tesase.py`; inviabiliza testes unitários isolados dos models.
Recommendation: Receber a conexão/sessão como parâmetro nas funções de model, ou usar um factory/contexto de aplicação (`app.config`/connection pool) injetado
na inicialização.

### [HIGH] Estado Global Mutável
File: database.py:4,9-10
Description: `db_connection = None` é uma variável de módulo mutrão singleton manual) e compartilhada por todas as requisiçõesconcorrentes.
Impact: Efeitos colaterais implícitos entre requisições, comportconcorrência e de isolar em testes.
Recommendation: Encapsular a conexão em uma classe/contexto de aplicação gerenciado pelo framework em vez de variável solta no módulo.

### [MEDIUM] Queries N+1
File: models.py:187-199,219-231
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem, para cada pedido, uma query para buscar seus itens e, para cada item, mais uma query para
buscar o nome do produto — um loop aninhado de queries em vez de
Impact: O número de queries cresce multiplicativamente com o volume de pedidos/itens, degradando performance rapidamente em produção.
Recommendation: Substituir por uma única query com `JOIN` entre produtos` (ou `IN (...)` em lote).

### [MEDIUM] Duplicação de Código
File: models.py:12-21,31-40,304-313 (construção do dict de produto); models.py:187-199 vs 219-231 (loop de itens de pedido); controllers.py:30-54 vs 74-90
(validação de produto)
Description: A montagem do dicionário de produto é repetida idêntica em três funções de `models.py`; o loop de montagem de itens de pedido é replicado entre
`get_pedidos_usuario` e `get_todos_pedidos`; e o bloco de validapiado entre `criar_produto` e `atualizar_produto` em`controllers.py`.
Impact: Qualquer mudança de regra (novo campo, nova validação) pnte em múltiplos lugares, com alto risco de divergência.
Recommendation: Extrair funções auxiliares compartilhadas (`_produto_to_dict`, `_montar_itens_pedido`, `_validar_dados_produto`).

### [MEDIUM] Tratamento de Erros Genérico
File: controllers.py:10-12,21-22,60-62,95-96,108-109,125-126,133218-220,226-227,234-235,254-255,261-262,291-292; app.py:77-78
Description: Toda função de controller (e o endpoint `/admin/query`) envolve sua lógica em `except Exception as e: return jsonify({"erro": str(e)}), 500`,
capturando qualquer exceção genericamente e retornando a mensagem log estruturado.
Impact: Mascara bugs reais (ex: erro de tipo vs erro de negócio ficam indistinguíveis), pode vazar detalhes internos de implementação/stack no corpo da
resposta, e dificulta debugging em produção.
Recommendation: Capturar exceções específicas por camada, usar um middleware central de tratamento de erros, e logar detalhes internos apenas no servidor
(nunca no corpo da resposta ao cliente).

### [LOW] Magic Numbers / Magic Strings
File: models.py:257-262; controllers.py:52
Description: Os limiares e percentuais de desconto de faturament.05`, `1000`, `0.02`) estão soltos no meio de `relatorio_vendas`; a lista de categorias válidas (`categorias_validas`) está hardcoded dentro da função `criar_produto`.
Impact: A regra de negócio de desconto e a lista de categorias vio do código, difíceis de localizar e alterar com segurança.
Recommendation: Extrair para constantes nomeadas (ex: `FAIXAS_DESCONTO`, `CATEGORIAS_VALIDAS`) em um módulo compartilhado.

### [LOW] Uso de `print` como Log de Produção
File: app.py:56,83-86; controllers.py:8,11,57,61,106,161,179,182
Description: Eventos de negócio e erros são registrados via `print(...)` espalhado por `app.py` e `controllers.py`, em vez de um logger configurável.
Impact: Sem níveis de severidade, timestamps estruturados nem dendo observabilidade em produção.
Recommendation: Adotar o módulo `logging` da stdlib (ou um logger central da aplicação) com níveis apropriados (`INFO`, `ERROR`).

### [LOW] Imports Não Utilizados
File: models.py:2
Description: `import sqlite3` em `models.py` nunca é referenciado — todo acesso ao banco passa por `database.get_db()`, que já encapsula o driver.
Impact: Ruído que sugere dependência direta do driver onde não e
Recommendation: Remover o import não utilizado.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
