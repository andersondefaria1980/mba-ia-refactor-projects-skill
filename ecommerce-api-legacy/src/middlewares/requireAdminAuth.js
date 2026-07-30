function requireAdminAuth(config) {
    return function (req, res, next) {
        const apiKey = req.get('x-api-key');

        if (!apiKey || apiKey !== config.adminApiKey) {
            return res.status(401).json({ error: 'Não autorizado' });
        }

        next();
    };
}

module.exports = requireAdminAuth;
