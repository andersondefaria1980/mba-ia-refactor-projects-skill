class ReportModel {
    constructor(db) {
        this.db = db;
    }

    /** Uma única query com JOIN, em vez da pirâmide de callbacks N+1 original. */
    async getFinancialReport() {
        const rows = await this.db.all(`
            SELECT c.id AS course_id, c.title AS course_title,
                   u.name AS student_name,
                   p.amount AS paid_amount, p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id
        `);

        const byCourse = new Map();
        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            const courseData = byCourse.get(row.course_id);
            if (row.student_name) {
                if (row.payment_status === 'PAID') {
                    courseData.revenue += row.paid_amount;
                }
                courseData.students.push({
                    student: row.student_name,
                    paid: row.paid_amount || 0,
                });
            }
        }
        return Array.from(byCourse.values());
    }
}

module.exports = ReportModel;
