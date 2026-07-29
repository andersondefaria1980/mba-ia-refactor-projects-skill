const passwordService = require('../services/passwordService');

async function initSchema(db) {
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
        CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
        CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
        CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
    `);
}

async function seedInitialData(db) {
    const existing = await db.get('SELECT COUNT(*) AS count FROM users', []);
    if (existing.count > 0) return;

    const passwordHash = await passwordService.hash('123');
    const { lastID: userId } = await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', passwordHash]
    );

    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
        ['Clean Architecture', 997.0, 'Docker', 497.0]
    );
    const course = await db.get('SELECT id FROM courses WHERE title = ?', ['Clean Architecture']);

    const { lastID: enrollmentId } = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, course.id]
    );
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, 997.0, 'PAID']
    );
}

module.exports = { initSchema, seedInitialData };
