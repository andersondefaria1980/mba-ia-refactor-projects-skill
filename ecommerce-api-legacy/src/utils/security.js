const bcrypt = require('bcryptjs');

const SALT_ROUNDS = 10;

function hashPassword(plainPassword) {
    return bcrypt.hashSync(plainPassword, SALT_ROUNDS);
}

function verifyPassword(plainPassword, hash) {
    return bcrypt.compareSync(plainPassword, hash);
}

module.exports = { hashPassword, verifyPassword };
