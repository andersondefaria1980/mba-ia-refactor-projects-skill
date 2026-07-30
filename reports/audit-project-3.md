 Ran 2 shell commands

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (flask-sqlalchemy)
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:11,13
Description: `SQLALCHEMY_DATABASE_URI` e `SECRET_KEY` estão hardcoded diretamente no código-fonte (`'sqlite:///tasks.db'`, `'super-secret-key-123'`), embora o projeto já tenha um `.env` com `DATABASE_URL` e `SECRET_KEY` reais e `python-dotenv` esteja instalado (`requirements.txt:6`) — `load_dotenv()` nunca é chamado.
Impact: A `SECRET_KEY` real (usada por Flask para assinar sessão/CSRF) fica versionada e idêntica em todos os ambientes; trocar de banco ou rotacionar o segredo exige editar e reimplantar código em vez de apenas mudar uma variável de ambiente.
Recommendation: Criar um módulo `config.py` que chama `load_dotenv()` e lê `SECRET_KEY`/`DATABASE_URL`/demais variáveis via `os.environ`, com falha explícita se obrigatórias estiverem ausentes; `app.py` deve apenas consumir esse config.

### [CRITICAL] Hardcoded Credentials / Secrets
File: services/notification_service.py:7-10
Description: Credenciais SMTP (`email_host`, `email_port`, `email_user`, `email_password = 'senha123'`) estão hardcoded na classe, apesar do `.env` já definir `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` e `NOTIFICATIONS_ENABLED`.
Impact: Credenciais de e-mail de produção ficam expostas a qualquer pessoa com acesso ao repositório; não há como desabilitar notificações ou trocar de provedor sem editar código.
Recommendation: Ler todas as credenciais SMTP e a flag `NOTIFICATIONS_ENABLED` do config centralizado (variáveis de ambiente), nunca hardcoded na classe.

### [HIGH] Lógica de Negócio Dentro de Controllers/Rotas
File: routes/task_routes.py:12-299, routes/user_routes.py:42-211, routes/report_routes.py:12-155
Description: As rotas fazem validação de entrada, cálculo de regras de negócio (status/prioridade válidos, cálculo de atraso, taxas de conclusão, agregações de relatório) e acesso a dados diretamente na função de rota, sem nenhuma camada de controller/service intermediária.
Impact: Impossível testar as regras de negócio (ex: "quando uma task está atrasada", "taxa de conclusão de um usuário") sem subir um servidor Flask completo; qualquer mudança de regra obriga mexer no código de transporte HTTP.
Recommendation: Extrair a lógica para controllers (orquestração) e métodos de model/service (regra de negócio pura), deixando a rota apenas: parsear request → chamar controller → devolver resposta.

### [HIGH] Autenticação Quebrada / Fraca
File: models/user.py:29,31-32; routes/user_routes.py:210; routes/task_routes.py, routes/user_routes.py, routes/report_routes.py (rotas de escrita, sem decorator/middleware de auth)
Description: Senhas são hasheadas com MD5 sem salt (`hashlib.md5(pwd.encode()).hexdigest()`); o login retorna um "token" previsível e não assinado (`'fake-jwt-token-' + str(user.id)`); nenhuma rota (incluindo criação de usuário `admin`, deleção de usuário/task, atualização de categoria) exige autenticação/autorização.
Impact: Um atacante pode forjar a identidade de qualquer usuário sabendo apenas seu `id` (o token não é verificado em lugar nenhum), quebrar senhas MD5 por rainbow table, e qualquer cliente não autenticado pode criar contas admin ou apagar dados de outros usuários.
Recommendation: Usar hashing com salt e custo adaptativo (`werkzeug.security.generate_password_hash`/`check_password_hash` ou bcrypt), emitir tokens assinados com expiração (JWT real) e adicionar um middleware/decorator de autenticação nas rotas sensíveis.

### [MEDIUM] Queries N+1
File: routes/task_routes.py:41-57; routes/report_routes.py:53-68,161-164
Description: `get_tasks` busca `User`/`Category` dentro de um loop por task; `summary_report` busca as tasks de cada usuário dentro de um loop por usuário; `get_categories` conta tasks de cada categoria dentro de um loop por categoria — todos gerando 1 query extra por iteração em vez de um único JOIN/agregação.
Impact: O número de queries cresce linearmente com o volume de tasks/usuários/categorias, degradando a performance rapidamente em produção.
Recommendation: Usar `joinedload`/`selectinload` do SQLAlchemy ou agregações (`GROUP BY`) para trazer os dados relacionados em uma única query.

### [MEDIUM] Duplicação de Código
File: models/task.py:38-60 (nunca chamado pelas rotas); routes/task_routes.py:17-39,71-80,283-287,296; routes/user_routes.py:61,106,171-180; routes/report_routes.py:34-37,67,132-135,151; utils/helpers.py:14-23,57-108 (equivalentes nunca usados)
Description: A lógica de "task atrasada" (`overdue`), o cálculo de `completion_rate` (`round((x/y)*100,2)`) e a validação de e-mail por regex estão reimplementados de forma quase idêntica em 4-6 lugares diferentes, enquanto `Task.is_overdue()`, `utils/helpers.calculate_percentage()` e `utils/helpers.validate_email()` já existem mas nunca são chamados.
Impact: Uma correção de regra (ex: mudar o critério de "atrasado") precisa ser replicada manualmente em todos os pontos, com alto risco de divergência/bugs de inconsistência.
Recommendation: Centralizar cada regra em um único método de model/service (ex: `Task.is_overdue`, `Task.completion_rate`) e fazer todas as rotas chamarem essa única implementação.

### [MEDIUM] Tratamento de Erros Genérico ou Ausente / Validação de Rota Ausente
File: routes/task_routes.py:62,236-238; routes/user_routes.py:130-132,149-151; routes/report_routes.py:186-188,196-202,207-209,221-223
Description: Vários blocos usam `except:`/`except Exception` genéricos sem log estruturado, mascarando a causa real do erro; `update_category` (report_routes.py:196) acessa `data['name']`/`data['description']`/`data['color']` sem checar antes se `data` é `None` (diferente das demais rotas, que validam), podendo lançar `TypeError` não tratado.
Impact: Erros reais (ex: constraint de banco, bug de lógica) ficam indistinguíveis de falhas esperadas, dificultando debugging em produção; `update_category` pode devolver um erro 500 não controlado em vez de 400 para payload ausente.
Recommendation: Capturar exceções específicas com log estruturado, e validar `data` no início de toda rota que o utiliza, de forma consistente com as demais.

### [MEDIUM] Uso de API Deprecated — `datetime.utcnow()`
File: models/task.py:15,16,52; models/user.py:14; routes/task_routes.py:31,72,215,285; routes/user_routes.py:172; routes/report_routes.py:35,42,45,71,133; utils/helpers.py:38; services/notification_service.py:35; seed.py:66,67,69,70,74
Description: `datetime.utcnow()`/`datetime.utcnow` é usado em todo o projeto para gerar timestamps; a API está deprecated desde Python 3.12 e retorna um `datetime` *naive* (sem timezone).
Impact: Comportamento sutilmente incorreto ao comparar/serializar datas entre fusos horários, e quebra futura quando a API for removida em versões mais novas do Python.
Recommendation: Substituir por `datetime.now(datetime.UTC)` (ou `datetime.now(timezone.utc)`), centralizando a criação de timestamps em uma única função utilitária.

### [LOW] Nomenclatura Ruim de Variáveis
File: routes/task_routes.py (`t` em vários loops); routes/user_routes.py (`u`, `t`); routes/report_routes.py:24-28 (`p1..p5`), 55-68 (`u`, `t`), 161-164 (`c`)
Description: Variáveis de uma letra são usadas para representar entidades de negócio (task, user, categoria, faixas de prioridade) em vários loops e agregações.
Impact: Reduz a legibilidade e aumenta a chance de erro ao alterar essas regras de negócio no futuro.
Recommendation: Renomear para nomes descritivos (`task`, `user`, `category`, `priority_1_count`, etc.).

### [LOW] Magic Numbers / Magic Strings
File: routes/task_routes.py:110,113,177,182; routes/user_routes.py:71,120; models/task.py:39,46
Description: Listas de status (`['pending', 'in_progress', 'done', 'cancelled']`), papéis (`['user', 'admin', 'manager']`) e limites de prioridade (`1`/`5`) aparecem como literais repetidos em várias rotas, apesar de já existirem constantes equivalentes não usadas em `utils/helpers.py` (`VALID_STATUSES`, `VALID_ROLES`, etc.).
Impact: A regra de negócio (quais status/papéis são válidos) fica implícita e espalhada, dificultando alteração seguraconsistente.
Recommendation: Extrair para constantes nomeadas centralizadas (reaproveitando as já existentes em `utils/helpers.py`) e importá-las onde necessário.

### [LOW] Uso de `print` como Log de Produção
File: routes/task_routes.py:149,153,219,234; routes/user_routes.py:83,89,147; seed.py:93-96
Description: Eventos de negócio e erros são registrados via `print(...)` em vez de um logger configurável.
Impact: Sem níveis de severidade, timestamps estruturados ou destino configurável, o que prejudica observabilidade em produção.
Recommendation: Usar o módulo `logging` do Python configurado no entry point, com níveis apropriados (`INFO`/`ERROR`).

### [LOW] Imports/Código Morto
File: app.py:7 (`os`, `sys`, `json` não usados); routes/task_routes.py:7 (`json`, `os`, `sys`, `time` não usados); routes/user_routes.py:6 (`hashlib`, `json` não usados); utils/helpers.py (arquivo inteiro — `format_date`, `calculate_percentage`, `validate_email`, `sanitize_string`, `generate_id`, `log_action`, `parse_date`, `is_valid_color`, `process_task_data` e as constantes `VALID_STATUSES`/`VALID_ROLES`/etc. nunca são chamadas em nenhum outro módulo); services/notification_service.py (arquivo inteiro — `NotificationService` nunca é instanciada em nenhuma rota)
Description: Imports não referenciados espalhados pelas rotas, e duas camadas inteiras (`utils/helpers.py`, `services/notification_service.py`) que existem mas nunca são conectadas ao restante da aplicação.
Impact: Ruído que dificulta a leitura e sinaliza refatoração incompleta; funcionalidades como notificação por e-mail parecem existir mas nunca disparam de fato.
Recommendation: Remover imports não usados; decidir se `helpers.py`/`notification_service.py` devem ser efetivamente conectados (ex: chamar `NotificationService` ao atribuir uma task) ou removidos.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]