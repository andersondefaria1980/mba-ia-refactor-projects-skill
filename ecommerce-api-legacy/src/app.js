const express = require('express');

const config = require('./config');
const Database = require('./models/database');
const userModel = require('./models/userModel');
const courseModel = require('./models/courseModel');
const enrollmentModel = require('./models/enrollmentModel');
const paymentModel = require('./models/paymentModel');
const auditLogModel = require('./models/auditLogModel');
const reportModel = require('./models/reportModel');
const seed = require('./models/seed');

const checkoutController = require('./controllers/checkoutController');
const reportController = require('./controllers/reportController');
const userController = require('./controllers/userController');

const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');

const requireAdminAuth = require('./middlewares/requireAdminAuth');
const errorHandler = require('./middlewares/errorHandler');

const Cache = require('./utils/cache');
const logger = require('./utils/logger');

async function createApp() {
    const db = new Database(config.dbPath);
    await db.init();

    const models = {
        userModel: userModel(db),
        courseModel: courseModel(db),
        enrollmentModel: enrollmentModel(db),
        paymentModel: paymentModel(db),
        auditLogModel: auditLogModel(db),
        reportModel: reportModel(db),
        cache: new Cache(),
    };

    await seed(models);

    const app = express();
    app.use(express.json());
    app.use('/api', requireAdminAuth(config));

    app.use(checkoutRoutes(checkoutController(models)));
    app.use(adminRoutes(reportController(models)));
    app.use(userRoutes(userController(models)));

    app.use(errorHandler);

    return app;
}

if (require.main === module) {
    createApp()
        .then((app) => {
            app.listen(config.port, () => {
                logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
            });
        })
        .catch((err) => {
            logger.error('Falha ao iniciar a aplicação', err);
            process.exit(1);
        });
}

module.exports = createApp;
