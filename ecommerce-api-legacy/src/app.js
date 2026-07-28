const express = require('express');

const settings = require('./config/settings');
const { createDb } = require('./config/db');
const { initSchema, seedInitialData } = require('./config/seed');
const { errorHandler } = require('./middlewares/errorHandler');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const { createCheckoutController } = require('./controllers/checkoutController');
const { createAdminController } = require('./controllers/adminController');
const { createUserController } = require('./controllers/userController');

const { createCheckoutRoutes } = require('./routes/checkoutRoutes');
const { createAdminRoutes } = require('./routes/adminRoutes');
const { createUserRoutes } = require('./routes/userRoutes');

async function createApp() {
    const db = createDb(settings.dbPath);
    await initSchema(db);
    await seedInitialData(db);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);
    const reportModel = new ReportModel(db);

    const checkoutController = createCheckoutController({
        userModel, courseModel, enrollmentModel, paymentModel, auditLogModel,
    });
    const adminController = createAdminController({ reportModel });
    const userController = createUserController({ userModel, enrollmentModel, paymentModel });

    const app = express();
    app.use(express.json());

    app.use(createCheckoutRoutes(checkoutController));
    app.use(createAdminRoutes(adminController));
    app.use(createUserRoutes(userController));

    app.use(errorHandler);

    return app;
}

module.exports = { createApp };
