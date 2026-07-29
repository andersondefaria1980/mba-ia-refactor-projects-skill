================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Credenciais/Segredos Hardcoded
File: src/utils.js:2-6
Description: `dbUser`, `dbPass` ("senha_super_secreta_prod_123"), `paymentGatewayKey` (com prefixo `pk_live_...`, formato de chave de produção) e `smtpUser` hardcoded no objeto `config`, commitado no repositório.
Impact: Vazamento imediato de credenciais de produção e de uma chave de gateway de pagamento em caso de exposição do repositório.
Recommendation: Externalizar via variáveis de ambiente (playbook #1).

### [CRITICAL] Dado de Cartão de Crédito e Chave de Pagamento Logados em Texto Puro
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava o número completo do cartão e a chave do gateway em log.
Impact: Violação direta de práticas PCI-DSS; dado de cartão nunca deve chegar a um log.
Recommendation: Remover o log; se necessário auditar, logar apenas os últimos 4 dígitos do cartão, nunca a chave do gateway.

### [CRITICAL] "Hash" de Senha Falso/Reversível
File: src/utils.js:17-23 (`badCrypto`), usado em src/AppManager.js:68
Description: Senha é "hasheada" repetindo base64 truncado em loop — não é uma função de hash criptográfica, é reversível e sem salt.
Impact: Compromete todas as contas em caso de vazamento do banco; nenhuma proteção real.
Recommendation: Usar bcrypt (playbook #5).

### [CRITICAL] Aprovação de Pagamento Sem Validação Real
File: src/AppManager.js:46
Description: `let status = cc.startsWith("4") ? "PAID" : "DENIED"` — qualquer cartão com prefixo "4" é aprovado, sem checar formato, validade, CVV ou integração real com gateway.
Impact: Qualquer usuário "compra" qualquer curso de graça; nenhuma garantia financeira real.
Recommendation: Integrar com um gateway de pagamento real; nunca decidir aprovação por prefixo de string.

### [CRITICAL] God Class
File: src/AppManager.js (arquivo inteiro, 4-141)
Description: Uma única classe possui a conexão do banco (`initDb`, 10-23), todas as rotas HTTP (`setupRoutes`, 25-138) e toda a regra de negócio (decisão de pagamento, matrícula, auditoria) misturadas.
Impact: Impossível testar isoladamente; qualquer mudança tem alto risco de efeito colateral em partes não relacionadas.
Recommendation: Separar em models/controllers/routes por domínio (playbook #3).

### [HIGH] Endpoints Sensíveis Sem Autenticação/Autorização
File: src/AppManager.js:80, 131
Description: `GET /api/admin/financial-report` (dados financeiros e de alunos) e `DELETE /api/users/:id` não possuem nenhum middleware de autenticação/autorização.
Impact: Qualquer cliente lê dados financeiros completos ou apaga qualquer usuário.
Recommendation: Middleware de auth reutilizável antes desses handlers (playbook #9).

### [HIGH] Lógica de Negócio Embutida nas Rotas
File: src/AppManager.js:28-78, 80-129
Description: Criação de usuário, decisão de pagamento, matrícula e auditoria (checkout) e agregação financeira completa (relatório) vivem inteiramente dentro dos handlers Express, sem camada de serviço/controller.
Impact: Regra de negócio só é testável subindo um request HTTP completo.
Recommendation: Extrair para controllers/services nomeados e testáveis (playbook #4).

### [HIGH] Estado Global Mutável (Cache Sem Expiração)
File: src/utils.js:9-10, 12-15 — usado em src/AppManager.js:59
Description: `globalCache` é um objeto em escopo de módulo, mutado a cada checkout via `logAndCache`, sem TTL/limite de tamanho; `totalRevenue` é declarado e nunca atualizado (morto).
Impact: Cresce indefinidamente (memory leak), compartilhado entre requisições concorrentes sem isolamento.
Recommendation: Remover o cache ad-hoc ou substituir por um cache com TTL explícito gerenciado em `config/` (playbook #8).

### [HIGH] Acoplamento Forte / Ausência de Injeção de Dependência
File: src/AppManager.js:7
Description: `this.db = new sqlite3.Database(':memory:')` é instanciado diretamente no construtor da classe que também define as rotas.
Impact: Impossível substituir por um banco de teste/mock; qualquer mudança de infraestrutura de dados exige tocar na classe que também tem as rotas.
Recommendation: Injetar a conexão de fora, criada uma vez no composition root (playbook #7).

### [HIGH] Integridade de Dados — Registros Órfãos ao Deletar Usuário
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` apaga o usuário mas não remove/trata `enrollments`/`payments` relacionados — a própria mensagem de resposta admite isso ("ficaram sujos no banco").
Impact: Dados financeiros e de matrícula ficam inconsistentes (FKs órfãs) após toda exclusão de usuário.
Recommendation: Cascatear a exclusão (ou soft-delete) dentro de uma transação, tratado no model/service de usuário.

### [MEDIUM] N+1 Severo em Pirâmide de Callbacks
File: src/AppManager.js:83-127
Description: Para cada curso, uma query de matrículas; para cada matrícula, uma query de usuário e uma de pagamento — sequencial, sem JOIN, controlado por contadores manuais (`coursesPending`, `enrPending`) em vez de Promises.
Impact: Degrada performance com O(cursos × matrículas × 2) round-trips; contadores manuais são frágeis (erro em uma query pode travar a resposta).
Recommendation: Substituir por uma única query com JOIN (playbook #6).

### [MEDIUM] Validação de Entrada Fraca no Checkout
File: src/AppManager.js:35, 68
Description: Só verifica truthy de `u`/`e`/`cid`/`cc` (linha 35); `p` (senha) sequer é obrigatório — se ausente, cai silenciosamente em senha padrão `"123456"` (linha 68).
Impact: Permite registro de usuário com senha adivinhável por padrão; nenhuma validação de formato de email/cartão.
Recommendation: Validação explícita de todos os campos obrigatórios, sem fallback silencioso de senha.

### [MEDIUM] Erros Não Tratados em Callbacks Aninhados
File: src/AppManager.js:92, 104, 106
Description: O parâmetro `err` é capturado nos callbacks de `db.all`/`db.get` do relatório financeiro mas nunca checado — uma falha de banco ali produz dado incorreto silenciosamente em vez de erro reportado.
Impact: Relatório financeiro pode ficar incompleto/incorreto sem qualquer sinal de erro ao cliente.
Recommendation: Tratar `err` em todo callback ou migrar para Promises/async-await com try/catch central (playbook #12).

### [MEDIUM] Ausência de Middleware Básico
File: src/app.js:6
Description: Apenas `express.json()` é usado — sem helmet, rate limiting, logging de requisição ou handler de erro centralizado.
Impact: Superfície de segurança/observabilidade mínima para uma API que processa pagamento.
Recommendation: Adicionar handler de erro centralizado (playbook #7); demais middlewares como melhoria futura.

### [LOW] Nomenclatura Ruim (Variáveis de Uma Letra)
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, curso e cartão.
Impact: Dificulta entender o fluxo de checkout só de olhar o código.
Recommendation: Renomear para nomes descritivos (`nomeUsuario`, `email`, `senha`, `cursoId`, `numeroCartao`).

### [LOW] Magic Numbers/Strings
File: src/AppManager.js:46; src/utils.js:19
Description: `"4"` como prefixo mágico de bandeira de cartão, `10000` como número de iterações do hash falso, `"PAID"`/`"DENIED"` repetidos como literais soltos.
Impact: Qualquer alteração de regra exige caçar strings/números repetidos pelo código.
Recommendation: Extrair para constantes nomeadas.

### [LOW] `sqlite3.verbose()` Habilitado e Binding Inconsistente de `this`/`self`
File: src/AppManager.js:1, 26, 37, 40, 54, 57, 69
Description: Modo verbose (voltado para debug) fica ligado incondicionalmente; o código mistura arrow functions (que capturam `this` léxico) com `function(err)` nomeadas (necessárias para `this.lastID`), recorrendo à variável `self` só em parte dos callbacks.
Impact: Padrão frágil e confuso — fácil quebrar o binding de `this` em uma futura alteração.
Recommendation: Padronizar em uma única forma (ex: todas arrow functions com uma referência de conexão injetada, sem depender de `this`/`self`).

### [LOW] Log/Resposta Não Profissional
File: src/app.js:13; src/AppManager.js:135
Description: Log de boot ("Frankenstein LMS rodando...") e mensagem de erro ao cliente que admite corrupção interna de dados ("ficaram sujos no banco").
Impact: Não é um problema funcional, mas indica ausência de um contrato de resposta de erro padronizado.
Recommendation: Padronizar mensagens de log e de erro ao cliente.

================================
Total: 18 findings
================================
