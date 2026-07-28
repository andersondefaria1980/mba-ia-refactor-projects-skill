class UserModel {
    constructor(db) {
        this.db = db;
    }

    async getByEmail(email) {
        return this.db.get('SELECT * FROM users WHERE email = ?', [email]);
    }

    async getById(id) {
        return this.db.get('SELECT * FROM users WHERE id = ?', [id]);
    }

    async create(name, email, passwordHash) {
        const { lastID } = await this.db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash]
        );
        return lastID;
    }

    async delete(id) {
        await this.db.run('DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = UserModel;
