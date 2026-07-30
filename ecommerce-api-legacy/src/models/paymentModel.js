const PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };
const APPROVED_CARD_PREFIX = '4';

function simulateCharge(cardNumber) {
    return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
}

function createPaymentModel(db) {
    return {
        simulateCharge,

        create(enrollmentId, amount, status) {
            return db.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amount, status]
            );
        },

        deleteByEnrollmentIds(enrollmentIds) {
            if (enrollmentIds.length === 0) return Promise.resolve();

            const placeholders = enrollmentIds.map(() => '?').join(', ');
            return db.run(
                `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
                enrollmentIds
            );
        },
    };
}

module.exports = { createPaymentModel, PAYMENT_STATUS };
