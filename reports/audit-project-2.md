
Fase 1 concluída. Avançando para a Fase 2 — vou ler o catálogo de anti-patterns e o template de relatório para auditar o código.

  Read 2 files, ran 1 shell command

================================
ARCHITECTURE AUDIT REPORT

Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary

CRITICAL: 2 | HIGH: 4 | MEDIUM: 2 | LOW: 4

## Findings

[CRITICAL] Hardcoded Credentials / Secrets

File: src/utils.js:2-6
Description: O módulo de config define dbPass ("senha_super_secreta_prod_123"), paymentGatewayKey ("pk_live_1234567890abcdef") e outros valores diretamente no código-fonte, apesar de já existir um .env no projeto com PORT, DB_PATH, PAYMENT_GATEWAY_KEY e ADMIN_API_KEY — que são completamente ignorados. A chave de pagamento hardcoded ainda é logada em texto puro no console em src/AppManager.js:45.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais e uma chave de gateway de pagamento "live"; segredos versionados não podem ser rotacionados com segurança e ficam expostos também nos logs de aplicação.
Recommendation: Centralizar config em um módulo único que lê exclusivamente de process.env (usando o .env já existente via dotenv), removendo todo valor sensível hardcoded do código-fonte.

[CRITICAL] God Class / God Module

File: src/AppManager.js:1-141
Description: Uma única classe concentra conexão com banco, criação de schema, seeds, roteamento HTTP, validação de request, regras de negócio de pagamento/matrícula e queries SQL diretas para 5 entidades diferentes (users, courses, enrollments, payments, audit_logs).
Impact: Impossível testar qualquer regra de negócio isoladamente sem subir um banco e um servidor HTTP; qualquer alteração em uma rota arrisca efeitos colaterais em domínios não relacionados.
Recommendation: Separar em camadas por domínio: models (User, Course, Enrollment, Payment) para acesso a dados, controllers para orquestração, e rotas dedicadas apenas ao roteamento.

[HIGH] Lógica de Negócio Dentro de Controllers/Rotas

File: src/AppManager.js:28-78 (checkout), 80-129 (financial-report), 131-137 (delete user)
Description: As três rotas fazem validação de entrada, cálculo de regras de negócio (status de pagamento, agregação de receita) e execução direta de queries SQL dentro do mesmo callback de rota, sem nenhuma camada intermediária.
Impact: Regras de negócio (ex: critério de aprovação de pagamento) não podem ser testadas sem HTTP e banco reais; qualquer mudança de regra exige mexer na camada de transporte.
Recommendation: Extrair a lógica de checkout, geração de relatório financeiro e exclusão de usuário para métodos de model/service, deixando a rota apenas repassar request/response.

[HIGH] Autenticação Quebrada / Fraca

File: src/utils.js:17-23 (badCrypto), src/AppManager.js:68 (uso do hash), src/AppManager.js:80 e 131 (rotas sensíveis sem autenticação)
Description: Senhas são "hasheadas" com badCrypto, uma função caseira e reversível (repetição de base64 truncado), não um algoritmo criptográfico real. Além disso, o endpoint /api/admin/financial-report e o DELETE /api/users/:id não possuem nenhum middleware de autenticação/autorização.
Impact: Senhas de usuários podem ser recuperadas trivialmente a partir do "hash"; qualquer cliente não autenticado pode ler o relatório financeiro completo ou deletar qualquer usuário do sistema.
Recommendation: Substituir badCrypto por bcrypt/scrypt/argon2 com salt, e adicionar middleware de autenticação/autorização nas rotas administrativas e destrutivas.

[HIGH] Acoplamento Forte / Ausência de Injeção de Dependência

File: src/AppManager.js:4-8
Description: O construtor de AppManager instancia diretamente new sqlite3.Database(':memory:'), sem possibilidade de injetar uma conexão/mocks externamente.
Impact: Inviabiliza testes unitários reais das rotas sem subir um banco SQLite de verdade; amarra a classe a uma implementação concreta de banco.
Recommendation: Receber a conexão de banco (ou uma factory) via construtor/parâmetro, permitindo injeção de mocks em testes.

[HIGH] Estado Global Mutável

File: src/utils.js:9-10, 12-15
Description: globalCache e totalRevenue são variáveis mutáveis no nível do módulo, lidas/escritas por logAndCache e potencialmente por qualquer requisição concorrente, sem encapsulamento.
Impact: Efeitos colaterais implícitos entre requisições concorrentes, comportamento difícil de rastrear/testar e risco de vazamento de memória (cache nunca expira).
Recommendation: Encapsular esse estado em uma classe/contexto de aplicação gerenciado (ex: um cache com TTL ou serviço próprio), nunca em variável solta de módulo.

[MEDIUM] Queries N+1

File: src/AppManager.js:89-125
Description: O endpoint de relatório financeiro executa uma query de enrollments por curso, e dentro dela uma query de users e outra de payments por matrícula, tudo dentro de forEach aninhados.
Impact: O número de queries cresce proporcionalmente a cursos × matrículas, degradando performance rapidamente conforme o volume de dados cresce.
Recommendation: Substituir por um único JOIN entre courses, enrollments, users e payments (ou carregamento em lote com IN (...)).

[MEDIUM] Tratamento de Erros Genérico ou Ausente / Validação de Rota Ausente

File: src/AppManager.js:131-137, 38,41,48,51,55
Description: DELETE /api/users/:id ignora completamente o err do callback (linha 133) e sempre responde sucesso, mesmo que a query falhe ou id não seja válido; as demais rotas retornam apenas strings genéricas ("Erro DB", "Erro Matrícula", "Erro Pagamento") sem log estruturado nem diferenciação de causa.
Impact: Falhas reais de banco passam despercebidas para o cliente e para quem opera o sistema; a própria mensagem do endpoint de delete admite que matrículas e pagamentos ficam "sujos" no banco após a exclusão.
Recommendation: Checar err explicitamente em todo callback antes de responder sucesso, validar id/tipos de entrada, e tratar a exclusão em cascata (ou soft-delete) das entidades relacionadas.

[LOW] Nomenclatura Ruim de Variáveis

File: src/AppManager.js:29-33
Description: Variáveis do fluxo de checkout usam abreviações não óbvias: u, e, p, cid, cc em vez de nomes descritivos.
Impact: Reduz legibilidade e aumenta a chance de erro ao alterar a lógica de pagamento/matrícula.
Recommendation: Renomear para username, email, password, courseId, cardNumber.

[LOW] Magic Numbers / Magic Strings

File: src/AppManager.js:46; src/utils.js:19
Description: O critério de aprovação de pagamento usa a string mágica "4" (cc.startsWith("4")) e os status "PAID"/"DENIED" soltos no código; badCrypto usa o número mágico 10000 de iterações.
Impact: Regra de negócio de aprovação de pagamento fica implícita e difícil de localizar/alterar com segurança.
Recommendation: Extrair para constantes nomeadas (ex: PAYMENT_STATUS.PAID, VISA_CARD_PREFIX).

[LOW] Uso de console.log como Log de Produção

File: src/AppManager.js:45; src/utils.js:13
Description: Eventos de negócio (incluindo dados sensíveis: número de cartão e chave de gateway de pagamento) são registrados via console.log em vez de um logger configurável.
Impact: Sem níveis de severidade nem destino configurável, prejudicando observabilidade em produção; pior, dados sensíveis (cartão, chave de pagamento) ficam expostos em texto puro nos logs.
Recommendation: Adotar um logger padrão (ex: pino/winston) e nunca logar dados sensíveis brutos.

[LOW] Imports/Código Morto

File: src/utils.js:9-10, 25
Description: totalRevenue é declarado e exportado, mas nunca incrementado nem importado/usado em nenhum outro módulo; globalCache é exportado diretamente mas só é efetivamente usado através de logAndCache.
Impact: Ruído que dificulta a leitura e sinaliza uma refatoração incompleta.
Recommendation: Remover totalRevenue e a exportação direta de globalCache se não houver uso real planejado.

================================
Total: 12 findings

Observação: verifiquei explicitamente uso de APIs deprecated (Buffer legado, body-parser standalone, etc.) — não foram encontradas ocorrências; o projeto já usa Buffer.from e express.json() nativo. Também não foram encontradas queries SQL concatenadas (todas usam placeholders ?) nem endpoints de execução arbitrária de SQL/código.

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]