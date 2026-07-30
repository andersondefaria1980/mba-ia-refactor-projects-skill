const sqlite3 = require('sqlite3').verbose();

const SCHEMA_STATEMENTS = [
    'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
    'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
    'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
    'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
    'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

const SEED_STATEMENTS = [
    "INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')",
    "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)",
    'INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)',
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')",
];

class Database {
    constructor(path) {
        this.raw = new sqlite3.Database(path);
    }

    init() {
        return new Promise((resolve, reject) => {
            this.raw.serialize(() => {
                [...SCHEMA_STATEMENTS, ...SEED_STATEMENTS].forEach((sql) => this.raw.run(sql));
                this.raw.run('SELECT 1', (err) => (err ? reject(err) : resolve()));
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.raw.run(sql, params, function callback(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }
}

function createDatabase(path) {
    return new Database(path);
}

module.exports = { createDatabase, Database };
