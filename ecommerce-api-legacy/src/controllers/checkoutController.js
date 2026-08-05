const { PAYMENT_STATUS } = require('../models/paymentModel');
const { hashPassword } = require('../utils/security');
const logger = require('../utils/logger');

function checkoutController({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, cache }) {
    return {
        async checkout(req, res) {
            const { usr, eml, pwd, c_id: courseId, card } = req.body;

            if (!usr || !eml || !courseId || !card) {
                return res.status(400).send('Bad Request');
            }

            const course = await courseModel.findActiveById(courseId);
            if (!course) {
                return res.status(404).send('Curso não encontrado');
            }

            let user = await userModel.findByEmail(eml);
            let userId;

            if (!user) {
                if (!pwd) {
                    return res.status(400).send('Bad Request');
                }
                userId = await userModel.create({
                    name: usr,
                    email: eml,
                    passwordHash: hashPassword(pwd),
                });
            } else {
                userId = user.id;
            }

            logger.info(`Processando checkout do curso ${courseId} para o usuário ${userId}`);
            const status = card.startsWith('4') ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;

            if (status === PAYMENT_STATUS.DENIED) {
                return res.status(400).send('Pagamento recusado');
            }

            const enrollmentId = await enrollmentModel.create({ userId, courseId });
            await paymentModel.create({ enrollmentId, amount: course.price, status });
            await auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);
            cache.set(`last_checkout_${userId}`, course.title);

            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = checkoutController;
