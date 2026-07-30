STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

# (limite de faturamento, percentual de desconto) — avaliado em ordem.
FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]


def _calcular_desconto(faturamento):
    for limite, percentual in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return 0


def _montar_pedidos_com_itens(conn, where_clause="", params=()):
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario,
               prod.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos prod ON prod.id = ip.produto_id
        {where_clause}
        ORDER BY p.id
        """,
        params,
    )
    rows = cursor.fetchall()

    pedidos_por_id = {}
    ordem = []
    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in pedidos_por_id:
            pedidos_por_id[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["produto_id"] is not None:
            pedidos_por_id[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })

    return [pedidos_por_id[pid] for pid in ordem]


def contar(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]


def get_todos(conn):
    return _montar_pedidos_com_itens(conn)


def get_por_usuario(conn, usuario_id):
    return _montar_pedidos_com_itens(conn, "WHERE p.usuario_id = ?", (usuario_id,))


def criar(conn, usuario_id, itens):
    cursor = conn.cursor()

    for item in itens:
        quantidade = item.get("quantidade")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            return {"erro": f"Quantidade inválida para o produto {item.get('produto_id')}"}

    produto_ids = list({item["produto_id"] for item in itens})
    placeholders = ",".join("?" for _ in produto_ids)
    cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", produto_ids)
    produtos_por_id = {row["id"]: row for row in cursor.fetchall()}

    # Soma por produto antes de validar estoque — evita overselling quando o
    # mesmo produto aparece em mais de um item do pedido.
    quantidade_total_por_produto = {}
    for item in itens:
        produto_id = item["produto_id"]
        quantidade_total_por_produto[produto_id] = (
            quantidade_total_por_produto.get(produto_id, 0) + item["quantidade"]
        )

    total = 0
    for produto_id, quantidade_total in quantidade_total_por_produto.items():
        produto = produtos_por_id.get(produto_id)
        if produto is None:
            return {"erro": f"Produto {produto_id} não encontrado"}
        if produto["estoque"] < quantidade_total:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}

    for item in itens:
        produto = produtos_por_id[item["produto_id"]]
        total += produto["preco"] * item["quantidade"]

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = produtos_por_id[item["produto_id"]]
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    conn.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(conn, pedido_id, novo_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conn.commit()


def relatorio_vendas(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",))
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",))
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",))
    cancelados = cursor.fetchone()[0]

    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
