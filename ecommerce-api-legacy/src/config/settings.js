require('dotenv').config();

function required(name) {
    const value = process.env[name];
    if (!value) {
        throw new Error(`${name} não definida — configure a variável de ambiente (veja .env.example)`);
    }
    return value;
}

module.exports = {
    port: parseInt(process.env.PORT || '3000', 10),
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: required('PAYMENT_GATEWAY_KEY'),
    adminApiKey: required('ADMIN_API_KEY'),
};
