const { PAYMENT_STATUS } = require('./paymentModel');

function reportModel(db) {
    return {
        async buildFinancialReport() {
            const rows = await db.all(`
                SELECT c.id AS course_id, c.title AS course_title,
                       u.name AS student_name,
                       p.amount AS paid_amount, p.status AS payment_status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                ORDER BY c.id
            `);

            const coursesById = new Map();

            for (const row of rows) {
                if (!coursesById.has(row.course_id)) {
                    coursesById.set(row.course_id, {
                        course: row.course_title,
                        revenue: 0,
                        students: [],
                    });
                }

                const courseData = coursesById.get(row.course_id);

                if (row.student_name) {
                    if (row.payment_status === PAYMENT_STATUS.PAID) {
                        courseData.revenue += row.paid_amount;
                    }
                    courseData.students.push({
                        student: row.student_name,
                        paid: row.paid_amount || 0,
                    });
                }
            }

            return Array.from(coursesById.values());
        },
    };
}

module.exports = reportModel;
