const { hashPassword } = require('../utils/security');
const { PAYMENT_STATUS } = require('../models/paymentModel');

const DEFAULT_PASSWORD = '123456';

function createCheckoutController({ courseModel, userModel, enrollmentModel, paymentModel, auditLogModel, cache }) {
    return async function checkout(req, res, next) {
        try {
            const { usr: username, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

            if (!username || !email || !courseId || !cardNumber) {
                return res.status(400).send('Bad Request');
            }

            const course = await courseModel.findActiveById(courseId);
            if (!course) {
                return res.status(404).send('Curso não encontrado');
            }

            const existingUser = await userModel.findByEmail(email);
            let userId = existingUser ? existingUser.id : null;

            if (!userId) {
                const passwordHash = hashPassword(password || DEFAULT_PASSWORD);
                userId = await userModel.create({ name: username, email, passwordHash });
            }

            const status = paymentModel.simulateCharge(cardNumber);
            if (status === PAYMENT_STATUS.DENIED) {
                return res.status(400).send('Pagamento recusado');
            }

            const enrollmentId = await enrollmentModel.create(userId, courseId);
            await paymentModel.create(enrollmentId, course.price, status);
            await auditLogModel.log(`Checkout curso ${courseId} por ${userId}`);

            cache.set(`last_checkout_${userId}`, course.title);

            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        } catch (err) {
            next(err);
        }
    };
}

module.exports = createCheckoutController;
