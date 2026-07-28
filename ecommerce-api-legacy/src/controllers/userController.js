function createUserController({ userModel, enrollmentModel, paymentModel }) {
    return {
        deleteUser: async (req, res, next) => {
            try {
                const { id } = req.params;

                const enrollments = await enrollmentModel.getByUserId(id);
                const enrollmentIds = enrollments.map((e) => e.id);

                // Cascata explícita: remove pagamentos e matrículas antes do usuário,
                // corrigindo os registros órfãos deixados pela versão anterior.
                await paymentModel.deleteByEnrollmentIds(enrollmentIds);
                await enrollmentModel.deleteByUserId(id);
                await userModel.delete(id);

                res.json({ msg: 'Usuário e dados relacionados (matrículas, pagamentos) removidos com sucesso' });
            } catch (err) {
                next(err);
            }
        },
    };
}

module.exports = { createUserController };
