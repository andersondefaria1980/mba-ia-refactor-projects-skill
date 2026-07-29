class CourseModel {
    constructor(db) {
        this.db = db;
    }

    async getActiveById(id) {
        return this.db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    }

    async getAll() {
        return this.db.all('SELECT * FROM courses', []);
    }
}

module.exports = CourseModel;
