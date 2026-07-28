class PaymentModel {
    constructor(db) {
        this.db = db;
    }

    async create(enrollmentId, amount, status) {
        const { lastID } = await this.db.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );
        return lastID;
    }

    async deleteByEnrollmentIds(enrollmentIds) {
        if (enrollmentIds.length === 0) return;
        const placeholders = enrollmentIds.map(() => '?').join(',');
        await this.db.run(
            `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
            enrollmentIds
        );
    }
}

module.exports = PaymentModel;
