function createUserModel(db) {
    return {
        findByEmail(email) {
            return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
        },

        findById(id) {
            return db.get('SELECT id, name, email FROM users WHERE id = ?', [id]);
        },

        async create({ name, email, passwordHash }) {
            const result = await db.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                [name, email, passwordHash]
            );
            return result.lastID;
        },

        async deleteById(id) {
            const result = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return result.changes > 0;
        },
    };
}

module.exports = createUserModel;
