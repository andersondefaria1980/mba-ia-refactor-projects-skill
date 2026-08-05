const express = require('express');
const asyncHandler = require('../utils/asyncHandler');

function adminRoutes(controller) {
    const router = express.Router();
    router.get('/api/admin/financial-report', asyncHandler(controller.financialReport));
    return router;
}

module.exports = adminRoutes;
