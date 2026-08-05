function info(message) {
    console.log(`[INFO] ${message}`);
}

function error(message, err) {
    console.error(`[ERROR] ${message}`, err ? err.message : '');
}

module.exports = { info, error };
