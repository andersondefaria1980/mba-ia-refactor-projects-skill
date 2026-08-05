================================
PHASE 1: PROJECT ANALYSIS

Language:      Python
Framework:      Flask 3.0.0 (flask-sqlalchemy 3.1.1, flask-cors 4.0.0)
Dependencies:  flask-sqlalchemy (ORM), flask-cors (CORS), marshmallow (não utilizado no código), python-dotenv, requests
Domain:        Task Manager API (tasks, usuários, categorias)
Architecture:  Parcialmente organizado — há separação em models/, routes/, services/, utils/, mas as rotas concentram validação, regras de negócio, montagem manual de resposta (duplicando to_dict()) e não há camada de config nem de controllers; segredos hardcoded apesar de existir .env com as variáveis corretas
Source files:  15 files analyzed
DB tables:     tasks, users, categories

Prosseguindo para a Fase 2 — Auditoria.

================================
ARCHITECTURE AUDIT REPORT

Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code

Summary

CRITICAL: 1 | HIGH: 3 | MEDIUM: 4 | LOW: 4

Findings

[CRITICAL] Hardcoded Credentials / Secrets

File: app.py:9,11; services/notification_service.py:7-10; models/user.py:16-25
Description: SECRET_KEY e a connection string do banco estão hardcoded em app.py, e as credenciais SMTP (incluindo senha em texto puro 'senha123') estão hardcoded em notification_service.py — apesar de existir um .env no projeto com SECRET_KEY, DATABASE_URL, SMTP_HOST/PORT/USER/PASSWORD corretamente definidos e nunca lidos pelo código. Além disso, User.to_dict() inclui o campo password (hash) em toda resposta de API (GET /users, GET /users/:id, POST /users, PUT /users/:id, POST /login).
Impact: Qualquer pessoa com acesso ao repositório obtém a chave de sessão e a senha do servidor de e-mail; qualquer cliente da API consegue capturar o hash de senha de qualquer usuário, viabilizando ataques offline de força bruta.
Recommendation: Centralizar toda configuração em um módulo lido de variáveis de ambiente (.env), remover literais hardcoded do código-fonte, e excluir o campo password da serialização pública do usuário.

[HIGH] Lógica de Negócio Dentro de Controllers/Rotas

File: routes/task_routes.py:11-299; routes/user_routes.py:10-211; routes/report_routes.py:12-223
Description: As funções de rota concentram validação de entrada, regras de negócio (cálculo de "overdue", regras de status/prioridade, agregações estatísticas) e acesso direto ao banco (db.session, Model.query) na mesma função, sem nenhuma camada intermediária (controller/service).
Impact: Impossível testar regras de negócio sem subir o servidor HTTP e o banco; qualquer alteração de regra exige mexer na camada de transporte HTTP.
Recommendation: Extrair validação e regras para models/controllers dedicados, deixando as rotas apenas orquestrar (receber request → chamar controller → devolver resposta).

[HIGH] Autenticação Quebrada / Fraca

File: models/user.py:27-32; routes/user_routes.py:210; routes/task_routes.py (todas as rotas); routes/user_routes.py (todas as rotas); routes/report_routes.py (todas as rotas)
Description: Senhas são hasheadas com MD5 sem salt (set_password/check_password); o "token" de login é apenas a string previsível 'fake-jwt-token-' + str(user.id), sem assinatura nem expiração; e nenhuma das 18 rotas do projeto (tasks, users, reports, categories) possui middleware/decorator de verificação de autenticação — todas são públicas.
Impact: Um atacante pode forjar a identidade de qualquer usuário (inclusive admin) apenas conhecendo o id, e qualquer cliente não autenticado pode ler/alterar/excluir dados de qualquer usuário ou task.
Recommendation: Usar hashing com salt e custo adaptativo (werkzeug.security.generate_password_hash), gerar tokens assinados com expiração real, e criar um middleware/decorator de autenticação aplicado a todas as rotas.

[HIGH] Acoplamento Forte / Ausência de Injeção de Dependência

File: services/notification_service.py:5-10
Description: NotificationService instancia a configuração SMTP diretamente no construtor (host/porta/usuário/senha fixos) e nunca recebe essas dependências por parâmetro; além disso, a classe nunca é importada/instanciada por nenhuma rota — é código órfão, então notificações de "task atribuída"/"task atrasada" nunca disparam de fato.
Impact: Impossível mockar o serviço de e-mail em testes; funcionalidade de notificação está desconectada do restante da aplicação sem que isso seja perceptível no comportamento da API.
Recommendation: Injetar a configuração SMTP via parâmetro/factory e conectar o service ao fluxo real de criação/atribuição de tasks, ou removê-lo se não for mais necessário.

[MEDIUM] Queries N+1

File: routes/task_routes.py:41-57; routes/report_routes.py:55-68,161-164
Description: Em get_tasks, para cada task é feito um User.query.get() e um Category.query.get() dentro do loop; em summary_report, para cada usuário é feito um Task.query.filter_by() dentro do loop; em get_categories, idem por categoria.
Impact: Número de queries cresce linearmente com o volume de dados, degradando performance rapidamente em produção.
Recommendation: Usar eager loading (joinedload) ou uma única query agregada (JOIN/GROUP BY) em vez de consultar o banco dentro do loop.

[MEDIUM] Duplicação de Código

File: models/task.py:50-60 (não usado); routes/task_routes.py:30-39,71-80,283-287; routes/user_routes.py:171-180; routes/report_routes.py:34-37,132-135; routes/task_routes.py:17-28; routes/user_routes.py:162-169; routes/user_routes.py:61,106; utils/helpers.py:19-23
Description: A lógica de "task atrasada" é reescrita inline em 6 lugares diferentes em vez de chamar Task.is_overdue() (que existe no model mas nunca é usado); a serialização manual de Task duplica Task.to_dict(); e o regex de validação de e-mail é duplicado em 2 rotas em vez de reusar utils.helpers.validate_email.
Impact: Qualquer correção na regra de "atrasado" (ou no formato de e-mail válido) precisa ser replicada manualmente em todos os pontos, gerando risco de divergência.
Recommendation: Consolidar cada regra em um único ponto (Task.is_overdue(), Task.to_dict(), validate_email()) e chamar esse ponto único a partir de todas as rotas.

[MEDIUM] Tratamento de Erros Genérico / Validação de Rota Ausente

File: routes/task_routes.py:62,137,204,236; routes/user_routes.py:130,149; routes/report_routes.py:186,207,221,196
Description: Múltiplos blocos except: genéricos engolem qualquer exceção sem log estruturado; update_category (report_routes.py:196) usa data['name'] sem antes checar se data é None, quebrando com erro não tratado se o corpo da requisição vier vazio.
Impact: Mascara bugs reais em produção e pode causar erro 500 não tratado (ou comportamento inconsistente) em requisições malformadas.
Recommendation: Capturar exceções específicas com log estruturado, e validar data antes de acessar suas chaves (seguindo o mesmo padrão já usado nas outras rotas de report_routes.py).

[MEDIUM] Uso de API Deprecated — datetime.utcnow()

File: models/task.py:15,16,52; models/user.py:14; models/category.py:11; routes/task_routes.py:31,72,215,285; routes/user_routes.py:172; routes/report_routes.py:35,42,45,71,133; services/notification_service.py:35; utils/helpers.py:38
Description: datetime.utcnow() é usado extensivamente para timestamps; a função é deprecated desde Python 3.12 e retorna um datetime naive (sem timezone), fonte comum de bugs de comparação.
Impact: Quebra em versões futuras do Python e comportamento sutilmente incorreto em comparações/serializações que assumem UTC.
Recommendation: Substituir por um equivalente não-deprecated que preserve o valor/formato naive-UTC já usado em todo o projeto.

[LOW] Nomenclatura Ruim de Variáveis

File: routes/task_routes.py (t para task); routes/user_routes.py (u para user); routes/report_routes.py (t, u, c)
Description: Uso extensivo de variáveis de uma letra para entidades de domínio importantes em loops de negócio.
Impact: Reduz legibilidade e aumenta risco de erro ao alterar o código.
Recommendation: Renomear para nomes descritivos (task, user, category).

[LOW] Magic Strings

File: routes/task_routes.py:110,177-178; routes/user_routes.py:71,120
Description: Listas de status (['pending','in_progress','done','cancelled']) e de roles (['user','admin','manager']) são reescritas como literais em várias rotas, apesar de já existirem as constantes VALID_STATUSES/VALID_ROLES em utils/helpers.py:110-111.
Impact: Regra de domínio implícita e espalhada; alterar os valores válidos exige encontrar e editar todas as ocorrências manualmente.
Recommendation: Importar e reutilizar VALID_STATUSES/VALID_ROLES de utils/helpers.py em vez de repetir os literais.

[LOW] Uso de print como Log de Produção

File: services/notification_service.py:21,24; routes/user_routes.py:83,89,147; routes/task_routes.py:149,153,219,234; utils/helpers.py:39,41; seed.py:93-96
Description: Eventos de negócio e erros são registrados via print() espalhado pelo código em vez de um logger configurável.
Impact: Sem níveis de severidade, timestamps estruturados nem destino configurável — prejudica observabilidade em produção.
Recommendation: Adotar o módulo logging padrão do Python com um logger único configurado centralmente.

[LOW] Código Morto

File: services/notification_service.py (classe inteira); models/task.py:38-48; requirements.txt:4
Description: NotificationService nunca é instanciada por nenhuma rota; Task.validate_status/Task.validate_priority nunca são chamados (a validação é reimplementada inline nas rotas); a dependência marshmallow está declarada no requirements.txt mas nunca é importada em nenhum arquivo .py.
Impact: Ruído que dificulta leitura, sinaliza refatoração incompleta, e infla dependências sem benefício real.
Recommendation: Remover o código/dependência não utilizados, ou conectá-los ao fluxo real se a funcionalidade for necessária (ex: notificações de task atribuída).

================================
Total: 12 findings

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
