# Playbook de Refatoração (Fase 3)

Cada padrão de transformação corresponde a um anti-pattern do `antipattern-catalog.md`. Os exemplos usam Python/Flask e Node/Express (as stacks dos 3 projetos-alvo), mas o princípio de transformação é o mesmo em qualquer linguagem — adapte a sintaxe, preserve a ideia.

---

## 1. SQL Injection → Prepared Statements / ORM

**Antes (Python/sqlite3):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

**Depois (Python/sqlite3):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

**Antes (Node/sqlite3, quando a query é montada por concatenação):**
```javascript
db.all(`SELECT * FROM courses WHERE id = ${req.query.id}`);
```

**Depois (Node/sqlite3):**
```javascript
db.all("SELECT * FROM courses WHERE id = ?", [req.query.id]);
```

Se o projeto já usa um ORM (SQLAlchemy, Sequelize), prefira os métodos do ORM (`Model.query.filter_by(id=id)`) em vez de SQL cru, mesmo parametrizado.

---

## 2. Credenciais Hardcoded → Config Centralizado por Variável de Ambiente

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```javascript
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_1234567890abcdef" };
```

**Depois (Python):**
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

# app.py
from config.settings import Settings
app.config["SECRET_KEY"] = Settings.SECRET_KEY
```

**Depois (Node):**
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
    dbPass: process.env.DB_PASS,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
};
```

O valor real do segredo passa a existir apenas em `.env` (fora do controle de versão), nunca no código-fonte.

---

## 3. God Class / God Module → Separação por Domínio

**Antes:**
```python
# models.py (315 linhas: produtos, usuarios, pedidos, relatórios, tudo junto)
def get_todos_produtos(): ...
def criar_usuario(): ...
def criar_pedido(): ...
def relatorio_vendas(): ...
```

**Depois:**
```python
# models/produto_model.py
def get_todos_produtos(): ...
def criar_produto(...): ...

# models/usuario_model.py
def criar_usuario(...): ...
def login_usuario(...): ...

# models/pedido_model.py
def criar_pedido(...): ...
def relatorio_vendas(): ...
```

Cada arquivo passa a ter uma única razão para mudar (regra de negócio de um único domínio).

---

## 4. Endpoint de Execução Arbitrária → Remoção ou Allowlist

**Antes:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query)   # executa qualquer SQL enviado pelo cliente
```

**Depois:**
```python
# Endpoint removido. Operações administrativas passam a ser
# ações específicas e auditáveis, nunca SQL livre vindo do cliente:
@admin_bp.route("/admin/produtos/<int:id>/desativar", methods=["POST"])
@require_admin_auth
def desativar_produto(id):
    produto_model.desativar(id)
    return jsonify({"sucesso": True})
```

Se não houver requisito de negócio para a ação livre, ela deve ser eliminada — não "protegida", eliminada.

---

## 5. Lógica de Negócio em Controllers → Extração para Model/Service

**Antes:**
```python
def relatorio_vendas():
    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0
    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    # ... regra de negócio inteira dentro do controller/rota
```

**Depois:**
```python
# controllers/pedido_controller.py
def relatorio_vendas():
    relatorio = pedido_model.montar_relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200

# models/pedido_model.py
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]

def calcular_desconto(faturamento):
    for limite, percentual in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return 0

def montar_relatorio_vendas():
    faturamento = obter_faturamento_total()
    desconto = calcular_desconto(faturamento)
    return {"faturamento_bruto": faturamento, "desconto_aplicavel": desconto}
```

O controller apenas chama o model e formata a resposta HTTP; a regra de negócio (inclusive as faixas, agora nomeadas) mora no model.

---

## 6. Autenticação Quebrada → Hash Seguro + Token Real

**Antes:**
```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()
```
```python
token = 'fake-jwt-token-' + str(user.id)
```

**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```
```python
import jwt
from datetime import datetime, timedelta, timezone

token = jwt.encode(
    {"user_id": user.id, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
    Settings.SECRET_KEY,
    algorithm="HS256",
)
```

**Emitir o token não fecha este finding sozinho.** Toda rota (GET/POST/PUT/PATCH/DELETE) citada no finding precisa passar a validar esse token via um middleware/decorator — nunca confiar cegamente em um `user_id`/`role` enviado pelo cliente. Construa e aplique o middleware de verificação, com o mesmo nível de detalhe do exemplo de emissão acima:

**Depois (Python/Flask — middleware de verificação):**
```python
# middlewares/auth.py
from functools import wraps

import jwt
from flask import jsonify, request

from config.settings import Settings
from models.user import User


def token_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Autenticação necessária"}), 401

        token = auth_header[len("Bearer "):]
        try:
            payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        user = User.query.get(payload.get("user_id"))
        if not user or not user.active:
            return jsonify({"error": "Token inválido"}), 401

        request.current_user = user
        return view(*args, **kwargs)

    return wrapper

# routes/task_routes.py
from middlewares.auth import token_required

@task_bp.route("/tasks", methods=["POST"])
@token_required
def create_task():
    ...
```

**Depois (Node/Express — middleware de verificação):**
```javascript
// middlewares/authenticateToken.js
const jwt = require('jsonwebtoken');

function authenticateToken(config) {
    return function (req, res, next) {
        const authHeader = req.get('Authorization') || '';
        if (!authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ error: 'Autenticação necessária' });
        }

        const token = authHeader.slice('Bearer '.length);
        jwt.verify(token, config.secretKey, (err, payload) => {
            if (err) {
                return res.status(401).json({ error: 'Token inválido ou expirado' });
            }
            req.userId = payload.userId;
            next();
        });
    };
}

module.exports = authenticateToken;

// routes/taskRoutes.js
router.post('/tasks', authenticateTokenMiddleware, taskController.createTask);
```

Aplique o decorator/middleware em **cada** rota listada no finding (não só em uma como exemplo) — o Passo 5 da Fase 3 (`SKILL.md`) exige validar isso com `curl` antes de reportar a fase como concluída.

---

## 7. Acoplamento Forte → Injeção de Dependência

**Antes (Node):**
```javascript
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:'); // dependência concreta, criada internamente
    }
}
```

**Depois:**
```javascript
class AppManager {
    constructor(db) {
        this.db = db; // recebida de fora — pode ser um mock em teste
    }
}

// composition root (app.js)
const db = new sqlite3.Database(process.env.DB_PATH || ':memory:');
const manager = new AppManager(db);
```

---

## 8. Estado Global Mutável → Encapsulamento em Contexto/Classe

**Antes:**
```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path)
    return db_connection
```

**Depois:**
```python
class Database:
    def __init__(self, path):
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row

    def get_connection(self):
        return self._connection

# config/settings.py monta uma única instância e a injeta onde for preciso,
# em vez de uma variável global mutada por qualquer módulo.
```

---

## 9. Queries N+1 → JOIN / Carregamento em Lote

**Antes:**
```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Depois:**
```python
cursor.execute("""
    SELECT p.id AS pedido_id, p.status, p.total,
           ip.produto_id, ip.quantidade, ip.preco_unitario,
           prod.nome AS produto_nome
    FROM pedidos p
    JOIN itens_pedido ip ON ip.pedido_id = p.id
    JOIN produtos prod ON prod.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
# uma única query monta todos os pedidos com seus itens
```

Em ORMs, o equivalente é usar eager loading (`joinedload`, `.include`, `populate`) em vez de acessar a relação dentro de um loop.

---

## 10. Duplicação de Código → Extração de Função Compartilhada

**Antes:**
```python
if not dados.get("nome"): return jsonify({"erro": "Nome é obrigatório"}), 400
if not dados.get("preco"): return jsonify({"erro": "Preço é obrigatório"}), 400
# ... repetido em criar_produto E atualizar_produto
```

**Depois:**
```python
def validar_produto(dados):
    campos_obrigatorios = ["nome", "preco", "estoque"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return f"{campo.capitalize()} é obrigatório"
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    return None

# usado tanto em criar_produto quanto em atualizar_produto
erro = validar_produto(dados)
if erro:
    return jsonify({"erro": erro}), 400
```

---

## 11. APIs Deprecated → Equivalente Moderno

**Antes:**
```python
created_at = datetime.utcnow()
```

**Depois:**
```python
from datetime import datetime, UTC
created_at = datetime.now(UTC)
```

**Antes (Node):**
```javascript
const buf = new Buffer(data);
```

**Depois:**
```javascript
const buf = Buffer.from(data);
```

---

## 12. Tratamento de Erro Duplicado → Middleware Centralizado

**Antes:**
```python
def listar_produtos():
    try:
        ...
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def criar_pedido():
    try:
        ...
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
# o mesmo try/except genérico repetido em toda função de controller
```

**Depois:**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    app.logger.exception("Erro não tratado")
    return jsonify({"erro": "Erro interno do servidor"}), 500

# controllers só tratam erros de negócio esperados (404, 400),
# exceções inesperadas sobem naturalmente até o middleware.
def listar_produtos():
    produtos = produto_model.get_todos()
    return jsonify({"dados": produtos, "sucesso": True}), 200
```

---

## Como aplicar o playbook

1. Para cada finding do relatório da Fase 2, localize o padrão correspondente acima pelo nome do anti-pattern.
2. Aplique a transformação preservando o comportamento observável do endpoint (mesmo path, método, formato de resposta), salvo quando o próprio finding exigir mudança de comportamento por segurança (ex: padrão 4).
3. Depois de aplicar todas as transformações, siga para a validação descrita no `SKILL.md` (subir a aplicação e testar os endpoints) antes de reportar a Fase 3 como concluída.
