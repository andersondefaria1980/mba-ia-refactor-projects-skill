function createAdminController({ reportModel }) {
    return {
        financialReport: async (req, res, next) => {
            try {
                const report = await reportModel.getFinancialReport();
                res.json(report);
            } catch (err) {
                next(err);
            }
        },
    };
}

module.exports = { createAdminController };
