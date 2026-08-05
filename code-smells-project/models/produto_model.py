CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

MENSAGENS_CAMPO_OBRIGATORIO = {
    "nome": "Nome é obrigatório",
    "preco": "Preço é obrigatório",
    "estoque": "Estoque é obrigatório",
}


def _row_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def contar(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    return cursor.fetchone()[0]


def get_todos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_row_to_dict(row) for row in cursor.fetchall()]


def get_por_id(conn, produto_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def criar(conn, nome, descricao, preco, estoque, categoria):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conn.commit()
    return cursor.lastrowid


def atualizar(conn, produto_id, nome, descricao, preco, estoque, categoria):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conn.commit()


def deletar(conn, produto_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()


def buscar(conn, termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor = conn.cursor()
    cursor.execute(query, params)
    return [_row_to_dict(row) for row in cursor.fetchall()]


def validar_campos_basicos(dados):
    """Checagens compartilhadas por criação e atualização de produto."""
    for campo, mensagem in MENSAGENS_CAMPO_OBRIGATORIO.items():
        if campo not in dados:
            return mensagem
    preco, estoque = dados["preco"], dados["estoque"]
    if isinstance(preco, bool) or not isinstance(preco, (int, float)):
        return "Preço deve ser numérico"
    if isinstance(estoque, bool) or not isinstance(estoque, int):
        return "Estoque deve ser um número inteiro"
    if preco < 0:
        return "Preço não pode ser negativo"
    if estoque < 0:
        return "Estoque não pode ser negativo"
    return None
