# Playbook de Refatoração (Fase 3)

Um padrão de transformação por anti-pattern do catálogo. Use o exemplo mais próximo da stack do projeto (Python/Flask ou Node/Express) como referência de estilo — o princípio da transformação é o mesmo em qualquer linguagem.

Regra geral para toda a Fase 3: **cada transformação deve preservar o contrato observável da API** (mesmo path, mesmo método HTTP, mesmo formato de resposta em caso de sucesso) — a não ser que o próprio anti-pattern seja sobre o contrato estar errado (ex: senha vazando na resposta, aí o campo deve ser removido).

---

## 1. Externalizar Credenciais/Config (corrige: Credenciais Hardcoded)

**Antes (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
DB_PATH = "loja.db"
```

**Depois:**
```python
# config/settings.py
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida — configure a variável de ambiente")
DB_PATH = os.environ.get("DB_PATH", "loja.db")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
```
```python
# app.py
from config import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
```
Crie também um `.env.example` com as chaves (sem valores reais) e adicione `.env` ao `.gitignore`.

**Antes (Node):**
```javascript
const config = {
  paymentGatewayKey: "pk_live_1234567890abcdef",
};
```

**Depois:**
```javascript
// config/index.js
require('dotenv').config();

const required = (name) => {
  const value = process.env[name];
  if (!value) throw new Error(`${name} não definida`);
  return value;
};

module.exports = {
  paymentGatewayKey: required('PAYMENT_GATEWAY_KEY'),
};
```

---

## 2. Parametrizar Queries SQL (corrige: SQL Injection)

**Antes:**
```python
query = f"SELECT * FROM usuarios WHERE email = '{email}' AND senha = '{senha}'"
cursor.execute(query)
```

**Depois:**
```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha_hash = ?",
    (email, senha_hash)
)
```

**Antes (Node):**
```javascript
db.get(`SELECT * FROM users WHERE email = '${email}'`, callback);
```

**Depois:**
```javascript
db.get("SELECT * FROM users WHERE email = ?", [email], callback);
```

Nunca use `.execute(query_string_do_usuario)` genérico (endpoint tipo `/admin/query`) — remova esse tipo de endpoint completamente; não há forma segura de expor execução de SQL arbitrário ao cliente.

---

## 3. Quebrar God Class/File em Models + Controllers + Views

**Antes:** `models.py` com 300+ linhas misturando SQL de produtos, usuários e pedidos.

**Depois:**
```
models/
├── produto_model.py   # get_produto_por_id, criar_produto, ...
├── usuario_model.py   # get_usuario_por_id, criar_usuario, ...
└── pedido_model.py    # criar_pedido, get_pedidos_usuario, ...
```
Cada arquivo só conhece a tabela/entidade correspondente. Uma função que hoje faz JOIN entre pedidos/itens/produtos continua podendo viver em `pedido_model.py`, mas não deve conter regra de checkout (isso é Controller).

**Antes (Node):** `AppManager.js` com conexão de banco + todas as rotas + toda a regra de negócio numa única classe.

**Depois:**
```
src/
├── config/db.js            # cria e exporta a conexão/pool
├── models/userModel.js     # queries de user
├── models/courseModel.js   # queries de curso/matrícula
├── controllers/checkoutController.js  # orquestra checkout (chama models, decide aprovação de pagamento)
├── routes/checkoutRoutes.js           # define POST /api/checkout → checkoutController.checkout
└── app.js                  # composition root
```

---

## 4. Extrair Lógica de Negócio do Controller/Rota para uma Função Nomeada

**Antes:**
```python
@app.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.json
    # 40 linhas verificando estoque, calculando total, "enviando" notificação...
```

**Depois:**
```python
# controllers/pedido_controller.py
def criar_pedido(dados):
    itens_validados = validar_itens_disponiveis(dados["itens"])
    pedido = pedido_model.criar_pedido(dados["usuario_id"], itens_validados)
    notification_service.notificar_novo_pedido(pedido)
    return pedido

# views/routes.py
@app.route("/pedidos", methods=["POST"])
def rota_criar_pedido():
    pedido = pedido_controller.criar_pedido(request.json)
    return jsonify(pedido), 201
```
A rota vira só "parse request → chama controller → formata resposta". Toda regra fica em uma função testável sem HTTP.

---

## 5. Hashing Seguro de Senha

**Antes:**
```python
# senha em texto puro, ou:
senha_hash = hashlib.md5(senha.encode()).hexdigest()
```

**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

senha_hash = generate_password_hash(senha)          # ao criar usuário
check_password_hash(usuario.senha_hash, senha_informada)  # ao autenticar
```
(Equivalente em Node: `bcrypt.hash(senha, 10)` / `bcrypt.compare(...)` em vez de qualquer "hash" caseiro.)

Garanta também que o campo de senha/hash nunca seja incluído em `to_dict()`/serializer de resposta.

---

## 6. Resolver N+1 Queries

**Antes:**
```python
for pedido in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
    for item in itens:
        produto = cursor.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**Depois (SQL cru, com JOIN):**
```python
cursor.execute("""
    SELECT p.id AS pedido_id, i.quantidade, pr.nome AS produto_nome, i.preco_unitario
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
```

**Depois (ORM, com eager loading):**
```python
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

---

## 7. Centralizar Error Handling

**Antes:** cada rota com seu próprio `try/except Exception as e: return jsonify({"erro": str(e)})`.

**Depois:**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception("Erro não tratado")
    if isinstance(e, HTTPException):
        return jsonify({"erro": e.description}), e.code
    return jsonify({"erro": "Erro interno"}), 500  # nunca vazar str(e) crua ao cliente
```
As rotas voltam a ser só o "caminho feliz" — deixam a exceção propagar para o handler central.

**Depois (Express):**
```javascript
// middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
  console.error(err);
  res.status(err.status || 500).json({ erro: 'Erro interno' });
};
// app.js
app.use(routes);
app.use(errorHandler); // registrado por último
```

---

## 8. Eliminar Estado Global Mutável

**Antes:**
```javascript
let globalCache = {};
function logAndCache(key, value) { globalCache[key] = value; }
```

**Depois:** mover o cache para dentro do escopo da requisição, ou usar um cache com TTL/tamanho máximo explícito (ex: `lru-cache`) instanciado uma vez em `config/` e injetado onde necessário — nunca uma variável solta em escopo de módulo mutada livremente.

Para conexão de banco única global (`db_connection` em módulo top-level sem pool): substituir por um pool de conexões gerenciado pelo driver/ORM (ex: `SQLAlchemy` engine com pool, ou `sqlite3` com uma conexão por request via `flask.g`), documentado em `config/`.

---

## 9. Adicionar Autenticação/Autorização

**Antes:** rota sem nenhuma checagem, ou token fake (`"fake-jwt-token-" + user.id`).

**Depois:**
```python
# middlewares/auth.py
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        usuario = verificar_token(token)  # valida assinatura/expiração de verdade
        if not usuario:
            return jsonify({"erro": "não autorizado"}), 401
        request.usuario = usuario
        return f(*args, **kwargs)
    return wrapper

@app.route("/admin/relatorio")
@login_required
def relatorio():
    ...
```
Emitir tokens com assinatura verificável (ex: JWT assinado com `SECRET_KEY` via `pyjwt`), nunca uma string concatenada previsível.

---

## 10. Conectar Camadas Mortas / Eliminar Duplicação

**Antes:** `Task.is_overdue()` existe no model mas cada rota reimplementa o mesmo `if` manualmente 6 vezes.

**Depois:** apagar as reimplementações e chamar o método existente:
```python
# routes/task_routes.py
overdue = task.is_overdue()   # em vez de reescrever a comparação de datas aqui
```
Se uma camada (`services/notification_service.py`) nunca é chamada por ninguém, decida explicitamente: (a) conectá-la de fato ao fluxo que deveria usá-la (ex: chamar `NotificationService` no controller de criação de tarefa), ou (b) removê-la caso não haja requisito de negócio que a justifique — nunca deixar código morto silenciosamente; documente a decisão tomada no relatório final.

---

## 11. Substituir print/console.log por Logging Estruturado

**Antes:**
```python
print("Pedido criado:", pedido_id)
```

**Depois:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Pedido criado", extra={"pedido_id": pedido_id})
```
(Node: `console.log` → `winston`/`pino` com níveis e formatação estruturada.)

---

## 12. Atualizar Uso de APIs Deprecadas

**Antes:**
```python
criado_em = datetime.utcnow()
usuario = Usuario.query.get(id)
```

**Depois:**
```python
from datetime import datetime, timezone
criado_em = datetime.now(timezone.utc)
usuario = db.session.get(Usuario, id)
```
Para cada API deprecada encontrada na Fase 2, aplique a troca pontual pelo substituto indicado em `reference/anti-pattern-catalog.md` — sem alterar comportamento observável.
