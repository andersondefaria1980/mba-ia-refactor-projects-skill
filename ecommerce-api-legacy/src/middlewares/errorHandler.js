const logger = require('../utils/logger');

function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    logger.error(`Erro não tratado em ${req.method} ${req.originalUrl}`, err);
    res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
