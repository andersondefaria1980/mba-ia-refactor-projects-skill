function userModel(db) {
    return {
        findByEmail(email) {
            return db.get('SELECT * FROM users WHERE email = ?', [email]);
        },

        findById(id) {
            return db.get('SELECT * FROM users WHERE id = ?', [id]);
        },

        async create({ name, email, passwordHash }) {
            const result = await db.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                [name, email, passwordHash]
            );
            return result.lastID;
        },

        deleteById(id) {
            return db.run('DELETE FROM users WHERE id = ?', [id]);
        },
    };
}

module.exports = userModel;
