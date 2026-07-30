const express = require('express');
const config = require('./config');
const logger = require('./utils/logger');
const MemoryCache = require('./utils/cache');
const { createDatabase } = require('./models/database');
const createUserModel = require('./models/userModel');
const createCourseModel = require('./models/courseModel');
const createEnrollmentModel = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const createAuditLogModel = require('./models/auditLogModel');
const createReportModel = require('./models/reportModel');
const createCheckoutController = require('./controllers/checkoutController');
const createAdminController = require('./controllers/adminController');
const createUserController = require('./controllers/userController');
const requireAdminAuth = require('./middlewares/requireAdminAuth');
const errorHandler = require('./middlewares/errorHandler');
const createCheckoutRoutes = require('./routes/checkoutRoutes');
const createAdminRoutes = require('./routes/adminRoutes');
const createUserRoutes = require('./routes/userRoutes');

async function bootstrap() {
    const db = createDatabase(config.dbPath);
    await db.init();

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const reportModel = createReportModel(db);
    const cache = new MemoryCache();

    const checkoutController = createCheckoutController({
        courseModel,
        userModel,
        enrollmentModel,
        paymentModel,
        auditLogModel,
        cache,
    });
    const adminController = createAdminController({ reportModel });
    const userController = createUserController({ userModel, enrollmentModel, paymentModel });

    const adminAuthMiddleware = requireAdminAuth(config);

    const app = express();
    app.use(express.json());

    app.use('/api', createCheckoutRoutes(checkoutController));
    app.use('/api', createAdminRoutes(adminController, adminAuthMiddleware));
    app.use('/api', createUserRoutes(userController, adminAuthMiddleware));

    app.use(errorHandler);

    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

bootstrap();
