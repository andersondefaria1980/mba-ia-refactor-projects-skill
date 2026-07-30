const logger = require('../utils/logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    logger.error('Erro não tratado', err);
    res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = errorHandler;
