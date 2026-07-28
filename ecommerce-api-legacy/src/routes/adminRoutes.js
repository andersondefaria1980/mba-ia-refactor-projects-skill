const express = require('express');

const { adminRequired } = require('../middlewares/auth');

function createAdminRoutes(adminController) {
    const router = express.Router();
    router.get('/api/admin/financial-report', adminRequired, adminController.financialReport);
    return router;
}

module.exports = { createAdminRoutes };
