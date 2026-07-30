const logger = {
    info(message) {
        console.log(`[INFO] ${message}`);
    },
    error(message, err) {
        console.error(`[ERROR] ${message}`, err || '');
    },
};

module.exports = logger;
