function createAdminController({ reportModel }) {
    return async function getFinancialReport(req, res, next) {
        try {
            const report = await reportModel.getFinancialReport();
            res.json(report);
        } catch (err) {
            next(err);
        }
    };
}

module.exports = createAdminController;
