class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    async create(userId, courseId) {
        const { lastID } = await this.db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
        return lastID;
    }

    async getByUserId(userId) {
        return this.db.all('SELECT * FROM enrollments WHERE user_id = ?', [userId]);
    }

    async deleteByUserId(userId) {
        await this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    }
}

module.exports = EnrollmentModel;
