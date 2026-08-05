const express = require('express');
const asyncHandler = require('../utils/asyncHandler');

function userRoutes(controller) {
    const router = express.Router();
    router.delete('/api/users/:id', asyncHandler(controller.deleteUser));
    return router;
}

module.exports = userRoutes;
