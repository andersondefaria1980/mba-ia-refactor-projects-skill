const express = require('express');

function createCheckoutRoutes(checkoutController) {
    const router = express.Router();
    router.post('/api/checkout', checkoutController);
    return router;
}

module.exports = { createCheckoutRoutes };
