# Catálogo de Anti-Patterns (Fase 2)

Cada entrada tem: severidade, sinais de detecção (o que procurar no código, de forma agnóstica de linguagem, com exemplos por stack), por que é um problema, e o que reportar no finding. Use os **Sinais de detecção** como regex/heurística mental ao ler o código — não é preciso rodar uma ferramenta externa, apenas ler os arquivos e casar os padrões.

Escala de severidade (referência):

- **CRITICAL**: falhas graves de arquitetura/segurança que impedem funcionamento correto, expõem dados sensíveis, ou violam completamente a separação de responsabilidades.
- **HIGH**: fortes violações de MVC/SOLID que dificultam muito manutenção e testes.
- **MEDIUM**: problemas de padronização, duplicação, ou gargalos de performance moderada.
- **LOW**: legibilidade, nomenclatura, magic numbers.

---

### 1. [CRITICAL] SQL Injection

**Sinais de detecção:**
- Strings de query montadas por concatenação (`+`), f-string ou template literal contendo variáveis vindas de request/params: `"SELECT * FROM x WHERE id = " + str(id)`, `` `SELECT * FROM x WHERE id = ${id}` ``.
- Ausência de placeholders (`?`, `%s`, `$1`) ou de métodos de ORM (`.filter_by(...)`, `.where(...)`) na montagem de queries.

**Por que é um problema:** permite a qualquer cliente ler, alterar ou apagar dados arbitrários no banco, e frequentemente escalar para comprometimento total do servidor.

**O que reportar:** arquivo:linha de cada query concatenada; recomendar prepared statements / parâmetros do driver ou uso do ORM.

---

### 2. [CRITICAL] Hardcoded Credentials / Secrets

**Sinais de detecção:**
- Literais de string atribuídos diretamente a `SECRET_KEY`, `password`, `senha`, `api_key`, `token`, `dbPass`, chave de gateway de pagamento, etc., em vez de lidos de variável de ambiente/config.
- Segredo repetido/vazado em múltiplos lugares (ex: exposto também em uma resposta de endpoint de health-check).

**Por que é um problema:** qualquer pessoa com acesso ao repositório (ou a um endpoint que os vaze) obtém credenciais de produção; segredos versionados não podem ser rotacionados com segurança.

**O que reportar:** arquivo:linha de cada valor hardcoded; recomendar módulo de config centralizado lendo de `.env`/variáveis de ambiente, com o segredo removido do controle de versão.

---

### 3. [CRITICAL] God Class / God Module

**Sinais de detecção:**
- Um único arquivo (ou classe) concentrando: conexão/queries de banco + regras de negócio + roteamento/validação HTTP, para **múltiplos domínios diferentes** (ex: produtos, usuários e pedidos no mesmo `models.py`).
- Tamanho e responsabilidades desproporcionais (dezenas a centenas de linhas misturando camadas que deveriam ser independentes).

**Por que é um problema:** impossível testar em isolamento, qualquer mudança pequena arrisca efeitos colaterais em domínios não relacionados; viola Single Responsibility.

**O que reportar:** arquivo e faixa de linhas; recomendar separação em um arquivo de model/controller por domínio.

---

### 4. [CRITICAL] Endpoint de Execução Arbitrária (SQL/código)

**Sinais de detecção:**
- Rota que recebe SQL bruto, comando de shell, ou código serializado no corpo da requisição e o executa diretamente (`cursor.execute(request_body)`, `eval(...)`, `exec(...)`, `child_process.exec(userInput)`), sem allowlist nem autenticação.

**Por que é um problema:** é uma porta aberta para execução remota de comandos/queries arbitrárias — comprometimento total do banco/servidor por qualquer cliente não autenticado.

**O que reportar:** arquivo:linha do endpoint; recomendar remoção do endpoint (se não houver caso de uso legítimo) ou substituição por um conjunto fechado de ações pré-definidas e autenticadas.

---

### 5. [HIGH] Lógica de Negócio Dentro de Controllers/Rotas

**Sinais de detecção:**
- Função de rota/controller que, na mesma função, valida entrada, calcula regras de negócio (descontos, totais, permissões) **e** executa a query no banco — sem delegar a um model/service.
- Nenhuma camada intermediária entre "recebeu o request" e "tocou o banco".

**Por que é um problema:** impede testar a regra de negócio sem subir um servidor HTTP e um banco real; qualquer mudança de regra obriga mexer na camada de transporte.

**O que reportar:** arquivo:linha da função; recomendar extrair a regra para um model/service, deixando o controller apenas orquestrar.

---

### 6. [HIGH] Autenticação Quebrada / Fraca

**Sinais de detecção:**
- Hashing de senha com algoritmo criptograficamente quebrado e sem salt (`md5`, `sha1`) ou uma função de "hash" caseira e reversível.
- Token de sessão/autenticação que é apenas uma string previsível (`'fake-token-' + user.id`, concatenação simples), sem assinatura (JWT real) nem expiração.
- Rotas sensíveis sem nenhum middleware/decorator de verificação de autenticação.

**Por que é um problema:** compromete a identidade de qualquer usuário do sistema; um atacante pode forjar sessão de qualquer conta (inclusive admin) sem nunca autenticar de verdade.

**O que reportar:** arquivo:linha do hashing/geração de token; recomendar hashing com salt e custo adaptativo (bcrypt/scrypt/argon2 ou `werkzeug.security` no ecossistema Flask) e tokens assinados (JWT/session real) com expiração.

---

### 7. [HIGH] Acoplamento Forte / Ausência de Injeção de Dependência

**Sinais de detecção:**
- Módulos que instanciam diretamente uma dependência concreta (`new Database()`, conexão global aberta no import) em vez de recebê-la como parâmetro/injeção.
- Impossível trocar a implementação (ex: por um mock em teste) sem editar o módulo.

**Por que é um problema:** inviabiliza testes unitários reais (sempre precisa de infraestrutura real) e amarra o código a uma implementação específica.

**O que reportar:** arquivo:linha da instanciação direta; recomendar receber a dependência via parâmetro/construtor/factory.

---

### 8. [HIGH] Estado Global Mutável

**Sinais de detecção:**
- Variável no nível do módulo (`db_connection = None`, `globalCache = {}`) que é lida e escrita por múltiplas funções/requisições, sem encapsulamento.

**Por que é um problema:** efeitos colaterais implícitos entre requisições concorrentes, difícil de rastrear e testar; comportamento pode variar conforme ordem de chamadas.

**O que reportar:** arquivo:linha da declaração e dos pontos de mutação; recomendar encapsular em uma classe/contexto de aplicação (ex: `app.config`, connection pool gerenciado) em vez de variável solta no módulo.

---

### 9. [MEDIUM] Queries N+1

**Sinais de detecção:**
- Loop (`for`/`forEach`) que executa uma query de banco a cada iteração para buscar dados relacionados, em vez de um único `JOIN` ou carregamento em lote (`IN (...)`, eager loading do ORM).

**Por que é um problema:** número de queries cresce proporcionalmente ao volume de dados, degradando performance rapidamente em produção.

**O que reportar:** arquivo:linha do loop; recomendar `JOIN`/`IN`/eager loading (`joinedload`, `include`, `populate`, conforme o ORM).

---

### 10. [MEDIUM] Duplicação de Código

**Sinais de detecção:**
- Blocos de código quase idênticos (validação, formatação, cálculo de "atrasado", etc.) repetidos em 2+ funções/arquivos em vez de extraídos para uma função/módulo compartilhado.

**Por que é um problema:** qualquer correção/regra nova precisa ser replicada manualmente em todos os lugares, gerando divergência e bugs de inconsistência.

**O que reportar:** todos os arquivos:linhas onde o bloco se repete; recomendar extrair para uma função/util compartilhado.

---

### 11. [MEDIUM] Tratamento de Erros Genérico ou Ausente / Validação de Rota Ausente

**Sinais de detecção:**
- `except Exception`/`except:`/`catch (e)` genéricos que engolem qualquer erro e retornam mensagem não específica, sem log estruturado.
- Rota que usa dados do request (`request.get_json()`, `req.body`) sem checar tipo/presença antes de usar.

**Por que é um problema:** mascara bugs reais, dificulta debugging em produção, e pode deixar a aplicação processar dados inválidos silenciosamente.

**O que reportar:** arquivo:linha do bloco; recomendar capturar exceções específicas e validar entrada explicitamente (ou usar uma lib de schema validation).

---

### 12. [MEDIUM] Uso de APIs Deprecated / Obsoletas

**Sinais de detecção (procurar ativamente por estes padrões, e outros equivalentes da mesma família ao identificar a stack):**

| Stack | API deprecated | Equivalente moderno |
|---|---|---|
| Python | `datetime.datetime.utcnow()` / `utcfromtimestamp()` (deprecated desde 3.12) | `datetime.now(datetime.UTC)` |
| Python/Flask | `@app.before_first_request` (removido no Flask 2.3+) | inicialização no momento da criação do app / `with app.app_context()` |
| Python | `imp` module | `importlib` |
| Node.js | `new Buffer(...)` (deprecated/inseguro) | `Buffer.from(...)` / `Buffer.alloc(...)` |
| Node/Express | pacote `body-parser` standalone quando a versão do Express já inclui `express.json()`/`express.urlencoded()` nativamente (Express >= 4.16) | `express.json()` |
| Node.js | callbacks de `fs`/drivers de banco quando existe API baseada em Promise disponível na mesma lib | `fs.promises`, cliente async/await do driver |
| Geral | Biblioteca/driver com major version desatualizada listada no manifest com aviso de deprecation conhecido | versão suportada mais recente |

**Por que é um problema:** APIs deprecated podem ser removidas em versões futuras (quebra futura), frequentemente têm comportamento sutilmente diferente do equivalente moderno (ex: `utcnow()` retorna datetime *naive*, sem timezone, fonte de bugs), e sinalizam manutenção desatualizada.

**O que reportar:** arquivo:linha de cada uso; recomendar o equivalente moderno da tabela acima (ou o equivalente correto identificado para a stack, se não estiver na tabela).

---

### 13. [LOW] Nomenclatura Ruim de Variáveis

**Sinais de detecção:** variáveis de uma letra ou abreviações não óbvias (`u`, `e`, `p`, `cc`, `cid`) em fluxos de negócio importantes, em vez de nomes descritivos.

**Por que é um problema:** reduz legibilidade e aumenta a chance de erro ao ler/alterar o código.

**O que reportar:** arquivo:linha; recomendar renomear para nomes descritivos do domínio.

---

### 14. [LOW] Magic Numbers / Magic Strings

**Sinais de detecção:** valores numéricos ou strings literais soltos no meio da lógica de negócio (percentuais, limiares, status codes de domínio) sem constante nomeada.

**Por que é um problema:** a regra de negócio fica implícita e difícil de localizar/alterar com segurança.

**O que reportar:** arquivo:linha; recomendar extrair para constantes nomeadas.

---

### 15. [LOW] Uso de `print`/`console.log` como Log de Produção

**Sinais de detecção:** chamadas de `print(...)`/`console.log(...)` espalhadas pelo código para registrar eventos de negócio ou erros, em vez de um logger configurável.

**Por que é um problema:** sem níveis de severidade, timestamps, nem destino configurável — prejudica observabilidade em produção.

**O que reportar:** arquivo:linhas; recomendar um módulo/logger padrão da linguagem (`logging` em Python, `winston`/`pino` em Node, ou ao menos um wrapper único).

---

### 16. [LOW] Imports/Código Morto

**Sinais de detecção:** imports nunca referenciados no arquivo; variáveis/funções exportadas e nunca usadas em nenhum outro módulo.

**Por que é um problema:** ruído que dificulta leitura e pode indicar refatorações incompletas.

**O que reportar:** arquivo:linha do import/código não utilizado; recomendar remoção.

---

## Notas de uso do catálogo

- Este catálogo tem 16 anti-patterns (mínimo exigido: 8), cobrindo as 4 severidades e incluindo detecção de APIs deprecated (item 12).
- Nem todo projeto terá ocorrências de todos os itens — reporte apenas o que for efetivamente encontrado no código, com evidência (arquivo:linha).
- Um mesmo trecho de código pode disparar mais de um anti-pattern (ex: uma query concatenada que também está dentro de um God Module) — reporte cada um separadamente, pois cada um tem uma recomendação de correção distinta.
