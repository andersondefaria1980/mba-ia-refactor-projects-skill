# Catálogo de Anti-Patterns (Fase 2)

Cada entrada tem: nome, severidade padrão, **sinais de detecção concretos** (o que procurar, não "código ruim"), por que importa, e como aparece tipicamente em Python/Flask vs Node.js/Express — mas os sinais valem para qualquer stack de backend web. Ajuste a severidade caso a caso conforme o impacto real (ex: um God Class que também contém SQL Injection continua CRITICAL; um God Class puramente organizacional sem falha de segurança pode ficar HIGH se o impacto for menor).

Ao rodar a Fase 2, percorra este catálogo item por item contra o código do projeto. Não pule itens só porque "parece que não se aplica" — confirme com uma busca (grep/leitura) antes de descartar.

---

## CRITICAL

### 1. Credenciais/Segredos Hardcoded
**Sinais:** literais de string atribuídos a variáveis/chaves como `SECRET_KEY`, `password`, `senha`, `api_key`, `token`, `db_pass`, especialmente valores realistas (não `"changeme"`) ou com prefixos reconhecíveis (`pk_live_`, `sk_`, `AKIA`). Também vale para credenciais em arquivos de seed/fixture usados em runtime.
**Por quê:** qualquer pessoa com acesso ao repositório (ou a um vazamento dele) tem acesso total ao segredo; segredos em produção nunca devem estar versionados.
**Exemplo real:** `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`; `const paymentGatewayKey = "pk_live_..."`.

### 2. SQL Injection
**Sinais:** montagem de query por f-string, `.format()`, concatenação (`+`) ou template literal (`` `...${var}...` ``) interpolando input do usuário diretamente no SQL, em vez de placeholders parametrizados (`?`, `%s`, `$1`, bind params do ORM). Preste atenção especial em queries de login/autenticação — SQLi ali é bypass de auth, não "apenas" vazamento de dados.
**Por quê:** permite ao atacante ler, alterar ou apagar qualquer dado, e em casos de auth, logar como qualquer usuário sem saber a senha.

### 3. God Class / God File
**Sinais:** um único arquivo/classe/módulo concentra 2 ou mais das responsabilidades: definição de rotas HTTP, acesso direto ao banco (SQL cru ou ORM), regra de negócio, e configuração/bootstrap da aplicação. Tamanho grande (200+ linhas) combinado com múltiplas responsabilidades é forte indício.
**Por quê:** impossível testar em isolamento, qualquer mudança tem alto risco de efeito colateral em partes não relacionadas.

### 4. Endpoint Destrutivo/Admin Sem Autenticação
**Sinais:** rotas que executam SQL arbitrário vindo do corpo da requisição, apagam/truncam dados em massa, ou expõem operações administrativas (`/admin/*`, `DELETE` em lote, reset de banco) sem nenhum middleware de auth/autorização antes do handler.
**Por quê:** é a versão mais severa de "sem auth" — não vaza um recurso, compromete a aplicação inteira.

### 5. Armazenamento Inseguro de Senha
**Sinais:** senha salva/comparada em texto puro; hash com algoritmo quebrado para senhas (MD5, SHA1 sem salt); "hash" caseiro (base64, XOR, truncamento) em vez de bcrypt/scrypt/argon2/PBKDF2; senha devolvida em respostas de API (`to_dict()`/serializer que inclui o campo de senha/hash).
**Por quê:** compromete todas as contas em caso de vazamento do banco, e reuso de senha entre serviços amplia o dano para fora da aplicação.

---

## HIGH

### 6. Lógica de Negócio em Controllers/Rotas (Fat Controller)
**Sinais:** handler de rota com múltiplos passos de regra de negócio (cálculos, validações complexas, orquestração de múltiplas entidades, "envio" de notificação) em vez de delegar a uma função/serviço nomeado e testável.
**Por quê:** mistura a camada de transporte HTTP com a regra de domínio; a regra só pode ser testada subindo um request HTTP completo.

### 7. Acoplamento Forte / Ausência de Injeção de Dependência
**Sinais:** classes/handlers que instanciam diretamente suas dependências pesadas (conexão de banco, cliente HTTP externo) dentro do próprio construtor/corpo, em vez de recebê-las de fora (parâmetro, factory, container).
**Por quê:** impossível substituir a dependência por um mock/fake em teste; qualquer mudança de infraestrutura exige tocar em código de negócio.

### 8. Estado Global Mutável
**Sinais:** variáveis em escopo de módulo que são reatribuídas/mutadas em tempo de execução e compartilhadas entre requisições (cache manual sem TTL, contador, conexão única sem pool), sem sincronização.
**Por quê:** race conditions sob concorrência, comportamento não determinístico entre requisições, memory leak (cache que só cresce).

### 9. Camadas Decorativas / Mortas
**Sinais:** pastas/arquivos como `services/`, `utils/`, `helpers.py` existem, mas ao buscar por importações (`grep -r "import nome_do_modulo"` / `grep -r "require.*nome"`) você não encontra nenhum uso real fora do próprio arquivo. Frequentemente acompanhado de rotas que reimplementam manualmente a mesma lógica que a camada "morta" já oferece.
**Por quê:** é o anti-pattern mais enganoso — o projeto *parece* ter arquitetura em camadas, mas o fluxo de execução real é idêntico a um God File. Detectar isso é essencial para não aprovar uma estrutura de pastas correta com comportamento incorreto.

### 10. Autenticação/Autorização Ausente ou Falsa
**Sinais:** rotas que deveriam exigir identidade (alterar/apagar dados de outro usuário, ver dados administrativos) sem nenhum middleware/decorator de auth; tokens "falsos" (string previsível como `"fake-token-" + id`, sem assinatura verificável) emitidos no login.
**Por quê:** qualquer cliente pode agir como qualquer usuário ou como admin.

---

## MEDIUM

### 11. Queries N+1
**Sinais:** loop que, para cada item de uma lista já carregada, dispara uma nova query individual para buscar dados relacionados, em vez de usar JOIN/eager loading/query única em lote.
**Por quê:** degrada performance linearmente com o volume de dados; em produção vira gargalo severo.

### 12. Duplicação de Código/Regra
**Sinais:** o mesmo bloco de validação, cálculo ou serialização aparece copiado (com pequenas variações) em 2+ lugares, especialmente quando já existe uma função/método que faz a mesma coisa e não é reaproveitado.
**Por quê:** qualquer correção de bug/regra precisa ser replicada manualmente em todos os pontos — alto risco de divergência.

### 13. Validação de Entrada Ausente ou Inconsistente
**Sinais:** rota que usa `int(request.args.get(...))` ou equivalente sem checar formato antes, campos opcionais tratados como obrigatórios em uma rota e não em outra, ausência de schema de validação (marshmallow/pydantic/zod/joi) num projeto que já tem a lib instalada mas não usa.
**Por quê:** input malformado vira exceção não tratada (500) ou, pior, é aceito silenciosamente e corrompe dado.

### 14. Uso Inadequado de Middleware
**Sinais:** CORS habilitado sem restringir origem (`CORS(app)` / `app.use(cors())` sem config), ausência de handler de erro centralizado (cada rota faz seu próprio try/except genérico que vaza mensagem de exceção crua ao cliente).
**Por quê:** CORS aberto amplia superfície de ataque para CSRF/XSS de outros domínios; erro não tratado de forma central vaza detalhes internos (stack trace, schema de banco) e é inconsistente entre rotas.

### 15. Ausência de Paginação
**Sinais:** endpoints de listagem que retornam `SELECT *` / `Model.query.all()` / `Model.find()` sem `LIMIT`/`OFFSET`/cursor.
**Por quê:** payload cresce sem limite conforme a tabela cresce, derruba performance de rede e memória.

---

## LOW

### 16. Nomenclatura Ruim / Magic Numbers
**Sinais:** variáveis de uma letra sem significado óbvio pelo contexto imediato, números/strings literais repetidos pelo código em vez de constantes nomeadas (limites, status, prefixos).
**Por quê:** aumenta o custo cognitivo de leitura e o risco de erro ao alterar um valor em um lugar e esquecer os outros.

### 17. Logging via print/console.log
**Sinais:** `print(...)` (Python) ou `console.log(...)` (Node) usados para registrar eventos de aplicação em vez do módulo de logging padrão (`logging`, `winston`, `pino`).
**Por quê:** sem nível de severidade, sem timestamp estruturado, impossível filtrar ou desligar em produção; risco extra de vazar dado sensível em log (ver item CRITICAL #2 relacionado).

### 18. Imports/Código Morto
**Sinais:** imports no topo do arquivo nunca referenciados no corpo; funções/métodos definidos e nunca chamados em lugar nenhum (confirmar com grep antes de reportar).
**Por quê:** ruído que dificulta entender o que o módulo realmente usa; geralmente sinaliza ausência de lint/CI.

---

## Detecção de APIs Deprecadas

Sempre verifique, além dos itens acima, o uso de APIs obsoletas da linguagem/framework/biblioteca em uso. Classifique como **LOW** se a API ainda funciona mas está marcada como deprecated (só precisa de warning + recomendação), ou **MEDIUM** se a API já foi removida na versão em uso (quebra em runtime) ou tem implicação de segurança.

**Referência rápida (expanda a busca para a versão exata detectada na Fase 1 — este é um ponto de partida, não uma lista fechada):**

| Linguagem/Stack | API Deprecada | Substituto Moderno |
|---|---|---|
| Python | `datetime.utcnow()` / `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)` |
| Python | `distutils` (removido no 3.12) | `setuptools` / `packaging` |
| SQLAlchemy / Flask-SQLAlchemy | `Model.query.get(id)` (estilo legado 1.x) | `db.session.get(Model, id)` |
| Flask | `@app.before_first_request` (removido no Flask 2.3+) | inicialização explícita antes do `app.run()` / factory pattern |
| Node.js | `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
| Node.js crypto | `crypto.createCipher` / `createDecipher` | `crypto.createCipheriv` / `createDecipheriv` |
| Node.js | `util._extend` | `Object.assign` / spread `{...obj}` |
| Express | callbacks aninhados manuais para operações assíncronas de biblioteca (ex: `sqlite3` callback-style) sem tratamento de erro consistente | Promises/`async-await` (ex: wrapper `sqlite`/`better-sqlite3`, ou `util.promisify`) |
| Qualquer stack | driver de banco síncrono/bloqueante rodando dentro de request handler sem pool de conexões | cliente com connection pool apropriado à stack |

Ao encontrar uma API deprecada, registre no relatório da Fase 2 com a mesma estrutura dos demais findings (arquivo:linha, descrição, recomendação do substituto moderno).
