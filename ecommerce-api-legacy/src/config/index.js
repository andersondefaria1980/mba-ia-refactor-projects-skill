require('dotenv').config();

module.exports = {
    port: Number(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    adminApiKey: process.env.ADMIN_API_KEY,
};
