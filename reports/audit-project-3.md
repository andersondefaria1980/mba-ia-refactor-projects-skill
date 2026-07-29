================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 6 | HIGH: 5 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] Credenciais/Debug Hardcoded no Entry Point
File: app.py:13, 34
Description: `SECRET_KEY = 'super-secret-key-123'` hardcoded (apesar de `python-dotenv` estar nas dependências e nunca ser usado) e `app.run(debug=True, host='0.0.0.0', port=5000)` sem alternância por ambiente.
Impact: Segredo de sessão exposto no repositório; debugger interativo do Werkzeug acessível publicamente permite execução remota de código.
Recommendation: Externalizar via variável de ambiente e desabilitar debug por padrão (playbook #1).

### [CRITICAL] Senha com Hash MD5 Sem Salt
File: models/user.py:29, 32
Description: `set_password`/`check_password` usam `hashlib.md5(pwd.encode()).hexdigest()` — MD5 é criptograficamente quebrado para senhas, sem salt.
Impact: Trivial de reverter via rainbow tables em caso de vazamento do banco.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (playbook #5).

### [CRITICAL] Hash de Senha Vazado em Toda Resposta de Usuário
File: models/user.py:16-25; usado em routes/user_routes.py:25, 33, 85, 129, 209
Description: `User.to_dict()` inclui o campo `password` (hash MD5); esse método é chamado em `GET /users`, `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e no corpo de `POST /login`.
Impact: Qualquer cliente obtém o hash de senha de qualquer usuário só listando `/users`.
Recommendation: Remover `password`/hash da serialização de resposta (playbook #5).

### [CRITICAL] Credenciais SMTP Hardcoded
File: services/notification_service.py:9-10
Description: `self.email_user = 'taskmanager@gmail.com'`, `self.email_password = 'senha123'` hardcoded na classe (que, além disso, nunca é instanciada por nenhuma rota — ver finding HIGH abaixo).
Impact: Vazamento de credenciais de e-mail em caso de exposição do repositório.
Recommendation: Externalizar via variável de ambiente (playbook #1).

### [CRITICAL] Token de Autenticação Falso e Previsível
File: routes/user_routes.py:210
Description: `/login` emite `'fake-jwt-token-' + str(user.id)` como token — uma string previsível, sem assinatura verificável.
Impact: Qualquer cliente pode forjar um "token" válido para qualquer `user_id` só concatenando a string.
Recommendation: Emitir token assinado e verificável (playbook #9).

### [CRITICAL] Nenhuma Rota Exige Autenticação/Autorização
File: routes/user_routes.py:135 (DELETE /users/<id>); routes/task_routes.py:226 (DELETE /tasks/<id>); routes/report_routes.py:191, 211 (PUT/DELETE /categories/<id>)
Description: Confirmado por busca no projeto inteiro — não existe `before_request`/decorator/checagem de token em nenhuma rota, apesar de `User` ter um campo `role` (`admin`/`manager`/`user`) e `/login` emitir um token.
Impact: Qualquer cliente anônimo lê, altera ou apaga qualquer dado de qualquer usuário — o conceito de papel/permissão existe no modelo mas nunca é aplicado.
Recommendation: Middleware de auth reutilizável aplicado às rotas de escrita/exclusão (playbook #9).

### [HIGH] Lógica de Agregação Pesada na Rota Apesar de Existir `services/`
File: routes/report_routes.py:12-101 (`summary_report`)
Description: Toda a estatística (contagem por status/prioridade, overdue, produtividade por usuário) é calculada inline na rota, mesmo o projeto tendo uma pasta `services/` dedicada.
Impact: Regra de negócio de relatório só é testável subindo um request HTTP completo; a camada de serviço não é usada onde faria mais sentido.
Recommendation: Extrair para um `report_service` chamado pelo controller (playbook #4).

### [HIGH] Camadas Decorativas / Mortas — `services/` e `utils/` Nunca Usados
File: services/notification_service.py (arquivo inteiro); utils/helpers.py (arquivo inteiro, exceto `format_date`/`calculate_percentage` importados em report_routes.py:7 mas nunca chamados)
Description: `NotificationService` nunca é instanciado por nenhuma rota (confirmado via grep); `utils/helpers.py` define `process_task_data`, `validate_email`, `sanitize_string`, `log_action` e constantes (`VALID_STATUSES` etc.) que nenhuma rota chama — cada rota reimplementa a mesma lógica manualmente.
Impact: O projeto parece ter arquitetura em camadas pelas pastas, mas o fluxo real de execução ignora completamente `services/` e `utils/` — é o anti-pattern mais enganoso do projeto.
Recommendation: Conectar de fato as camadas ao fluxo que deveriam servir, ou removê-las se não fizerem sentido, documentando a decisão (playbook #10).

### [HIGH] Rotas Reimplementam Serialização/Validação Já Existente nos Models
File: routes/task_routes.py:17-59 (monta dict manualmente em vez de `task.to_dict()`); routes/user_routes.py:162-181 (idem)
Description: `get_tasks` e `get_user_tasks` constroem o dicionário de resposta campo a campo manualmente, duplicando exatamente o que `Task.to_dict()` já faz.
Impact: Qualquer mudança no formato de serialização precisa ser replicada em múltiplos lugares.
Recommendation: Reaproveitar `to_dict()` e apenas complementar com o campo calculado (`overdue`, `user_name`).

### [HIGH] `db.create_all()` Executado no Import do Módulo
File: app.py:30-31; efeito colateral disparado por seed.py:2 (`from app import app, db`)
Description: `db.create_all()` roda fora de `if __name__ == '__main__':`, então qualquer import de `app.py` (incluindo `seed.py`) já cria as tabelas e monta toda a aplicação como efeito colateral.
Impact: Ausência do padrão application factory — dificulta testes e reuso do módulo sem subir a aplicação inteira.
Recommendation: Encapsular criação de app/tabelas em uma função `create_app()` chamada explicitamente.

### [MEDIUM] Lógica de "Overdue" Duplicada em 6 Lugares
File: models/task.py:50-60 (`is_overdue`, nunca chamado); routes/task_routes.py:30-39, 71-80, 283-287; routes/user_routes.py:171-180; routes/report_routes.py:34-37, 132-135
Description: O mesmo bloco de comparação de data é copiado em 6 lugares em vez de chamar `Task.is_overdue()`, que já existe no model.
Impact: Qualquer correção da regra de "atraso" precisa ser replicada manualmente em 6 pontos.
Recommendation: Substituir todas as reimplementações por `task.is_overdue()` (playbook #10).

### [MEDIUM] Queries N+1
File: routes/task_routes.py:41-57 (`get_tasks`, uma query de `User`/`Category` por task); routes/report_routes.py:53-68 (`summary_report`, uma query de tasks por usuário)
Description: Loop que dispara uma query individual por item já carregado, em vez de `joinedload`/agregação em uma única query.
Impact: Degrada performance proporcional ao número de tasks/usuários.
Recommendation: Usar eager loading (`joinedload`) ou uma query agregada (playbook #6).

### [MEDIUM] Ausência de Paginação em Todas as Listagens
File: routes/task_routes.py:14; routes/user_routes.py:12; routes/report_routes.py:30, 53, 159
Description: `Task.query.all()`/`User.query.all()`/`Category.query.all()` sem `LIMIT`/`OFFSET` em nenhum endpoint de listagem — a própria seed (seed.py) já sinaliza isso como pendência conhecida.
Impact: Payload cresce sem limite conforme as tabelas crescem.
Recommendation: Adicionar paginação por query params (`page`, `per_page`).

### [MEDIUM] `except:` Genérico Sem Log
File: routes/task_routes.py:62; routes/report_routes.py:186, 207, 221; routes/user_routes.py:130, 149
Description: Vários blocos usam `except:` (sem classe de exceção, sem log) engolindo qualquer erro e retornando uma mensagem genérica.
Impact: Erros reais ficam invisíveis para debugging/observabilidade.
Recommendation: Capturar `Exception` explicitamente e logar antes de responder (playbook #7).

### [MEDIUM] Conversão de Query String Sem Tratamento
File: routes/task_routes.py:261, 264 (`search_tasks`)
Description: `int(priority)`/`int(user_id)` aplicados direto em parâmetro de query string sem validar formato antes — um valor não numérico gera `ValueError` não tratado (500).
Impact: Input malformado quebra o endpoint com erro não controlado.
Recommendation: Validar/capturar antes da conversão, retornando 400 em vez de deixar propagar.

### [MEDIUM] Validação Duplicada em Vez de Reaproveitar `utils/helpers.py`
File: routes/task_routes.py:96-114, 181-184; routes/user_routes.py:64-65
Description: Limite de caracteres do título, faixa de prioridade (1-5) e lista de status válidos são reescritos em cada rota como literais, em vez de usar as constantes já definidas (`VALID_STATUSES`, `MIN_TITLE_LENGTH` etc. em `utils/helpers.py:110-116`).
Impact: Qualquer mudança de regra (ex: faixa de prioridade) precisa ser replicada manualmente em cada rota.
Recommendation: Importar e usar as constantes centralizadas.

### [LOW] `datetime.utcnow()` Deprecado
File: models/task.py:15-16, 52; models/user.py:14; routes/task_routes.py, user_routes.py, report_routes.py (múltiplas ocorrências)
Description: `datetime.utcnow()` está deprecado desde Python 3.12 em favor de `datetime.now(timezone.utc)`.
Impact: Funciona hoje, mas gera warning e será removido em versão futura do Python.
Recommendation: Substituir por `datetime.now(timezone.utc)` (playbook #12).

### [LOW] `Model.query.get(id)` — Padrão Legado do SQLAlchemy
File: routes/task_routes.py:67, 158; routes/user_routes.py:29, 94, 136, 155; routes/report_routes.py:105, 192, 213
Description: `Model.query.get(id)` é o estilo legado (SQLAlchemy 1.x); a partir do SQLAlchemy 2.x/Flask-SQLAlchemy 3.x o padrão recomendado é `db.session.get(Model, id)`.
Impact: Ainda funciona, mas é a forma desencorajada — sinaliza código não atualizado para a API atual da própria dependência já instalada.
Recommendation: Substituir por `db.session.get(Model, id)` (playbook #12).

### [LOW] Imports Não Utilizados
File: app.py:7 (`os, sys, json` não usados, só `datetime`); routes/task_routes.py:7 (`json, os, sys, time` não usados)
Description: Módulos importados e nunca referenciados no corpo do arquivo.
Impact: Ruído no código, sinaliza ausência de lint configurado.
Recommendation: Remover os imports não usados.

================================
Total: 21 findings
================================
