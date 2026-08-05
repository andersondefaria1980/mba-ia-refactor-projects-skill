const PAYMENT_STATUS = {
    PAID: 'PAID',
    DENIED: 'DENIED',
};

function paymentModel(db) {
    return {
        create({ enrollmentId, amount, status }) {
            return db.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amount, status]
            );
        },

        findByEnrollmentId(enrollmentId) {
            return db.get(
                'SELECT amount, status FROM payments WHERE enrollment_id = ?',
                [enrollmentId]
            );
        },
    };
}

module.exports = paymentModel;
module.exports.PAYMENT_STATUS = PAYMENT_STATUS;
