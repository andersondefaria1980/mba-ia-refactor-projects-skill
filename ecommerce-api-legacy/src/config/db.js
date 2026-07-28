const sqlite3 = require('sqlite3');

/**
 * Wrapper com Promises sobre o driver sqlite3 (callback-based) — elimina a
 * pirâmide de callbacks aninhados e o binding manual de this/self do código legado.
 */
function createDb(filename) {
    const raw = new sqlite3.Database(filename);

    return {
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.run(sql, params, function onRun(err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },
        exec(sql) {
            return new Promise((resolve, reject) => {
                raw.exec(sql, (err) => (err ? reject(err) : resolve()));
            });
        },
    };
}

module.exports = { createDb };
