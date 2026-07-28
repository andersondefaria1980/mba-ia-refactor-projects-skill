function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    console.error(err);
    // Nunca vazar err.message cru ao cliente (pode conter detalhe de query/schema).
    res.status(err.status || 500).json({ erro: 'Erro interno do servidor' });
}

module.exports = { errorHandler };
