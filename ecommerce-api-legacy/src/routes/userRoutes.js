const express = require('express');

function createUserRoutes(userController, requireAdminAuthMiddleware) {
    const router = express.Router();
    router.delete('/users/:id', requireAdminAuthMiddleware, userController);
    return router;
}

module.exports = createUserRoutes;
