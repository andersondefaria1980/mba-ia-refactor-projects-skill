function enrollmentModel(db) {
    return {
        async create({ userId, courseId }) {
            const result = await db.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, courseId]
            );
            return result.lastID;
        },

        findByCourseId(courseId) {
            return db.all('SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
        },
    };
}

module.exports = enrollmentModel;
