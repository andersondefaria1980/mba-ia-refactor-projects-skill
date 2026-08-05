function reportController({ reportModel }) {
    return {
        async financialReport(req, res) {
            const report = await reportModel.buildFinancialReport();
            res.json(report);
        },
    };
}

module.exports = reportController;
