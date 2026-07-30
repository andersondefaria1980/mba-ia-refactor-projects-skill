const logger = require('./logger');

class MemoryCache {
    constructor() {
        this.store = {};
    }

    set(key, value) {
        logger.info(`Salvando no cache: ${key}`);
        this.store[key] = value;
    }

    get(key) {
        return this.store[key];
    }
}

module.exports = MemoryCache;
