const express = require('express');

const { adminRequired } = require('../middlewares/auth');

function createUserRoutes(userController) {
    const router = express.Router();
    router.delete('/api/users/:id', adminRequired, userController.deleteUser);
    return router;
}

module.exports = { createUserRoutes };
