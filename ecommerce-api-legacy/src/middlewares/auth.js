const crypto = require('crypto');

const settings = require('../config/settings');

function timingSafeEqual(a, b) {
    const bufA = Buffer.from(String(a));
    const bufB = Buffer.from(String(b));
    if (bufA.length !== bufB.length) return false;
    return crypto.timingSafeEqual(bufA, bufB);
}

function adminRequired(req, res, next) {
    const key = req.headers['x-admin-key'];
    if (!key || !timingSafeEqual(key, settings.adminApiKey)) {
        return res.status(401).json({ erro: 'Acesso restrito a administradores' });
    }
    next();
}

module.exports = { adminRequired };
