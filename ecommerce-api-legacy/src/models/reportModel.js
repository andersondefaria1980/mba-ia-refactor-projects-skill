function createReportModel(db) {
    return {
        async getFinancialReport() {
            const rows = await db.all(`
                SELECT c.id AS course_id, c.title AS course_title,
                       e.id AS enrollment_id,
                       u.name AS student_name,
                       p.amount AS paid_amount, p.status AS payment_status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                ORDER BY c.id, e.id
            `);

            const reportByCourseId = new Map();

            rows.forEach((row) => {
                if (!reportByCourseId.has(row.course_id)) {
                    reportByCourseId.set(row.course_id, {
                        course: row.course_title,
                        revenue: 0,
                        students: [],
                    });
                }

                if (row.enrollment_id === null) return;

                const courseReport = reportByCourseId.get(row.course_id);

                if (row.payment_status === 'PAID') {
                    courseReport.revenue += row.paid_amount;
                }

                courseReport.students.push({
                    student: row.student_name || 'Unknown',
                    paid: row.paid_amount || 0,
                });
            });

            return Array.from(reportByCourseId.values());
        },
    };
}

module.exports = createReportModel;
