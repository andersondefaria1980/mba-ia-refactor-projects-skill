function requireAdminAuth(config) {
    return function authenticateToken(req, res, next) {
        const authHeader = req.get('Authorization') || '';
        if (!authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ error: 'Autenticação necessária' });
        }

        const token = authHeader.slice('Bearer '.length);
        if (token !== config.apiKey) {
            return res.status(401).json({ error: 'Token inválido' });
        }

        next();
    };
}

module.exports = requireAdminAuth;
