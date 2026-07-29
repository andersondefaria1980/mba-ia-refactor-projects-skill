================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code

## Summary
CRITICAL: 6 | HIGH: 5 | MEDIUM: 5 | LOW: 4

## Findings

### [CRITICAL] Endpoint Destrutivo Sem Autenticação — Execução de SQL Arbitrário
File: app.py:59-78
Description: `POST /admin/query` executa `cursor.execute(query)` com SQL vindo direto do corpo da requisição (`dados.get("sql", "")`), sem qualquer autenticação.
Impact: Qualquer cliente na internet pode ler, alterar ou apagar qualquer dado do banco, ou executar DDL destrutivo — equivalente a um shell SQL exposto publicamente.
Recommendation: Remover esse endpoint por completo (playbook #2/#3). Não existe forma segura de expor execução de SQL arbitrário ao cliente.

### [CRITICAL] Endpoint Destrutivo Sem Autenticação — Reset de Banco
File: app.py:47-57
Description: `POST /admin/reset-db` apaga todas as linhas de `itens_pedido`, `pedidos`, `produtos` e `usuarios` sem nenhuma checagem de identidade/autorização.
Impact: Qualquer requisição não autenticada zera a base de dados de produção.
Recommendation: Proteger com middleware `login_required` + checagem de role admin (playbook #9), ou remover se não for uma operação necessária em produção.

### [CRITICAL] SQL Injection Pervasivo (inclui bypass de autenticação)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 158-161, 163-166, 174, 188, 192, 220, 224, 279-281, 291-297
Description: Todas as queries de `models.py` são montadas por concatenação de string com input do usuário, em vez de placeholders parametrizados. O caso mais grave é `login_usuario` (models.py:109-111), onde `email`/`senha` são concatenados diretamente na cláusula `WHERE` — um payload como `' OR '1'='1' --` autentica sem senha válida.
Impact: Leitura/alteração/exclusão arbitrária de dados; no caso do login, bypass completo de autenticação.
Recommendation: Parametrizar todas as queries com `?` (playbook #2).

### [CRITICAL] Credenciais/Segredo Hardcoded + Debug Habilitado
File: app.py:7-8, 88
Description: `SECRET_KEY` hardcoded (`"minha-chave-super-secreta-123"`) e `DEBUG=True`/`app.run(..., debug=True)` fixos no código, sem alternância por ambiente.
Impact: Segredo de sessão exposto no repositório; debugger interativo do Werkzeug acessível em produção permite execução remota de código.
Recommendation: Externalizar para variável de ambiente e desabilitar debug por padrão (playbook #1).

### [CRITICAL] Vazamento de Segredo e Debug Flag no /health
File: controllers.py:276-290
Description: O endpoint `/health` (não autenticado) devolve `"debug": True` e `"secret_key": "minha-chave-super-secreta-123"` em texto puro no JSON de resposta.
Impact: Qualquer cliente obtém o segredo da aplicação com um único `curl /health`.
Recommendation: Remover completamente segredo/flag de debug do payload de health check.

### [CRITICAL] Armazenamento de Senha em Texto Puro
File: database.py:75-83, models.py:82-83, 99, 122-131, 109-111
Description: Senhas são inseridas em texto puro na seed (`database.py:75-83`), armazenadas sem hash (`models.py:122-131`), comparadas em texto puro no login (`models.py:109-111`) e devolvidas cruas em `get_todos_usuarios`/`get_usuario_por_id` (`models.py:82-83,99`).
Impact: Vazamento do banco expõe a senha real de todos os usuários, sem nenhuma camada de proteção.
Recommendation: Hash com `werkzeug.security.generate_password_hash`/`check_password_hash`; nunca devolver o campo de senha nas respostas (playbook #5).

### [HIGH] Lógica de Negócio Embutida no Controller
File: controllers.py:188-220, 237-255
Description: `criar_pedido` e `atualizar_status_pedido` fazem orquestração completa (validação, chamada ao model, "envio" de notificação via `print`) direto no handler HTTP, sem camada de serviço.
Impact: Regra de negócio só é testável subindo um request HTTP completo; mistura transporte com domínio.
Recommendation: Extrair para uma função de controller/serviço nomeada e testável (playbook #4).

### [HIGH] Estado Global Mutável — Conexão de Banco Única
File: database.py:4, 8-11
Description: `db_connection` é uma variável de módulo global, reaproveitada por todas as requisições concorrentes (`check_same_thread=False` mascara o problema em vez de resolvê-lo).
Impact: Sem isolamento por requisição; risco de comportamento inconsistente sob concorrência real.
Recommendation: Usar conexão por requisição (ex: `flask.g`) ou um pool gerenciado (playbook #8).

### [HIGH] Ausência de Transação e Race Condition em Criação de Pedido
File: models.py:133-169
Description: `criar_pedido` faz `SELECT` de estoque, depois `INSERT`/`UPDATE` de decremento em passos separados sem transação nem lock — duas requisições concorrentes podem vender o mesmo estoque (TOCTOU).
Impact: Overselling de produtos sob carga concorrente; nenhum rollback se um item falhar no meio do loop.
Recommendation: Envolver em transação e usar `UPDATE ... WHERE estoque >= quantidade` verificando linhas afetadas.

### [HIGH] CORS Aberto Sem Restrição de Origem
File: app.py:9
Description: `CORS(app)` é chamado sem nenhuma configuração de origem permitida.
Impact: Qualquer domínio pode fazer requisições autenticadas/cross-origin contra a API.
Recommendation: Restringir `origins` às origens conhecidas do frontend.

### [HIGH] Exceções Cruas Vazadas ao Cliente
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Description: Todo handler tem seu próprio `except Exception as e: jsonify({"erro": str(e)})`, expondo mensagem de exceção interna (que pode incluir fragmento de SQL/schema) ao cliente.
Impact: Vazamento de detalhes internos, comportamento de erro inconsistente entre rotas.
Recommendation: Handler de erro centralizado (playbook #7).

### [MEDIUM] Queries N+1 em Listagem de Pedidos
File: models.py:171-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` disparam uma query de itens por pedido e, para cada item, uma query de produto — sem JOIN.
Impact: Degradação de performance proporcional ao volume de pedidos/itens.
Recommendation: Substituir por uma única query com JOIN (playbook #6).

### [MEDIUM] Duplicação Total Entre get_pedidos_usuario e get_todos_pedidos
File: models.py:171-233
Description: O laço de enriquecimento de itens/produto é copiado quase verbatim entre as duas funções.
Impact: Qualquer correção precisa ser replicada manualmente nos dois lugares.
Recommendation: Extrair a lógica compartilhada para uma função auxiliar única.

### [MEDIUM] Validação Duplicada Entre Criar/Atualizar Produto
File: controllers.py:24-62, 64-96
Description: O bloco de checagem de campos obrigatórios e valores negativos é copiado entre `criar_produto` e `atualizar_produto`.
Impact: Divergência de regra entre os dois endpoints ao longo do tempo (ex: `atualizar_produto` não valida `len(nome)` nem categoria válida, diferente de `criar_produto`).
Recommendation: Extrair um validador único reutilizado pelas duas rotas.

### [MEDIUM] Categorias Válidas Hardcoded Inline
File: controllers.py:52
Description: Lista de categorias válidas (`["informatica", "moveis", ...]`) hardcoded dentro do handler, e não reaproveitada em `atualizar_produto`.
Impact: Qualquer mudança de categoria exige lembrar de atualizar em múltiplos lugares; inconsistência já existe entre criar/atualizar.
Recommendation: Mover para `config/` ou tabela/enum central.

### [MEDIUM] Validação Inconsistente Entre Endpoints
File: controllers.py:146-165
Description: `criar_usuario` só checa presença de nome/email/senha, sem validar formato de email nem força de senha — bem menos rigoroso que a validação de `criar_produto`.
Impact: Dados inconsistentes/malformados entram no banco sem barreira.
Recommendation: Padronizar validação com um schema (ex: marshmallow/pydantic) usado por todas as rotas de escrita.

### [LOW] Logging via print() em Vez do Módulo logging
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: Toda a aplicação usa `print()` para registrar eventos, incluindo o próprio "!!! BANCO DE DADOS RESETADO !!!".
Impact: Sem nível de severidade, sem timestamp estruturado, impossível filtrar/desligar em produção.
Recommendation: Substituir por `logging` (playbook #11).

### [LOW] Imports Não Utilizados
File: database.py:2, models.py:2
Description: `import os` em `database.py` e `import sqlite3` em `models.py` nunca são referenciados.
Impact: Ruído no código, sinaliza ausência de lint configurado.
Recommendation: Remover os imports não usados.

### [LOW] Registro de Rotas Inconsistente
File: app.py:11-30 vs 32, 47, 59
Description: A maioria das rotas usa `app.add_url_rule(...)`, enquanto três rotas usam o decorator `@app.route`, sem critério aparente.
Impact: Reduz previsibilidade e legibilidade do roteamento.
Recommendation: Padronizar em um único estilo de registro de rota.

================================
Total: 20 findings
================================
