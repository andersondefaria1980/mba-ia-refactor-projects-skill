const express = require('express');

function createAdminRoutes(adminController, requireAdminAuthMiddleware) {
    const router = express.Router();
    router.get('/admin/financial-report', requireAdminAuthMiddleware, adminController);
    return router;
}

module.exports = createAdminRoutes;
