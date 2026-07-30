function createEnrollmentModel(db) {
    return {
        async create(userId, courseId) {
            const result = await db.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, courseId]
            );
            return result.lastID;
        },

        findIdsByUserId(userId) {
            return db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
        },

        deleteByUserId(userId) {
            return db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
        },
    };
}

module.exports = createEnrollmentModel;
