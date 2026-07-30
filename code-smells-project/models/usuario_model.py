def _row_to_dict(row):
    """Representação interna, inclui o hash de senha (uso restrito a
    autenticação — nunca deve ser serializada diretamente numa resposta)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "senha": row["senha"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _to_public_dict(row):
    dados = _row_to_dict(row)
    dados.pop("senha")
    return dados


def contar(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    return cursor.fetchone()[0]


def get_todos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_to_public_dict(row) for row in cursor.fetchall()]


def get_por_id(conn, usuario_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _to_public_dict(row) if row else None


def get_por_email(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def criar(conn, nome, email, senha_hash, tipo="cliente"):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    conn.commit()
    return cursor.lastrowid
