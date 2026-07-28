from src.config.db import get_db
from src.models import produto_model


class PedidoError(Exception):
    """Erro de regra de negócio ao criar/atualizar um pedido (não é um erro de servidor)."""


def criar(usuario_id, itens):
    db = get_db()

    total = 0
    produtos_info = {}
    for item in itens:
        produto = produto_model.get_por_id(item["produto_id"])
        if produto is None:
            raise PedidoError(f"Produto {item['produto_id']} não encontrado")
        produtos_info[item["produto_id"]] = produto
        total += produto["preco"] * item["quantidade"]

    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos_info[item["produto_id"]]
            # Decremento atômico (UPDATE ... WHERE estoque >= ?) evita a race condition
            # de check-then-decrement em duas etapas separadas.
            if not produto_model.decrementar_estoque(item["produto_id"], item["quantidade"]):
                raise PedidoError(f"Estoque insuficiente para {produto['nome']}")
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
        db.commit()
        return {"pedido_id": pedido_id, "total": total}
    except PedidoError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def _montar_pedidos(where_clause, params):
    db = get_db()
    query = f"""
        SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
        WHERE {where_clause}
        ORDER BY p.id
    """
    rows = db.execute(query, params).fetchall()

    pedidos = {}
    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def get_por_usuario(usuario_id):
    return _montar_pedidos("p.usuario_id = ?", (usuario_id,))


def get_todos():
    return _montar_pedidos("1 = 1", ())


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def obter_agregados_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'"
    ).fetchone()[0]
    aprovados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'"
    ).fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'"
    ).fetchone()[0]
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": faturamento,
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
    }
