const express = require('express');

function createCheckoutRoutes(checkoutController) {
    const router = express.Router();
    router.post('/checkout', checkoutController);
    return router;
}

module.exports = createCheckoutRoutes;
