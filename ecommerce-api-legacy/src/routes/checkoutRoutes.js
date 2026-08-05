const express = require('express');
const asyncHandler = require('../utils/asyncHandler');

function checkoutRoutes(controller) {
    const router = express.Router();
    router.post('/api/checkout', asyncHandler(controller.checkout));
    return router;
}

module.exports = checkoutRoutes;
