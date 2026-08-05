require('dotenv').config();

const config = {
    port: process.env.PORT || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    apiKey: process.env.ADMIN_API_KEY,
};

const requiredVars = ['paymentGatewayKey', 'apiKey'];
const missing = requiredVars.filter((key) => !config[key]);
if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
}

module.exports = config;
