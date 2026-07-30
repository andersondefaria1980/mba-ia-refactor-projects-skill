function createUserController({ userModel, enrollmentModel, paymentModel }) {
    return async function deleteUser(req, res, next) {
        try {
            const userId = Number(req.params.id);

            if (!Number.isInteger(userId)) {
                return res.status(400).send('Bad Request');
            }

            const enrollments = await enrollmentModel.findIdsByUserId(userId);
            const enrollmentIds = enrollments.map((enrollment) => enrollment.id);

            await paymentModel.deleteByEnrollmentIds(enrollmentIds);
            await enrollmentModel.deleteByUserId(userId);
            const deleted = await userModel.deleteById(userId);

            if (!deleted) {
                return res.status(404).send('Usuário não encontrado');
            }

            res.send('Usuário deletado com sucesso, incluindo matrículas e pagamentos associados.');
        } catch (err) {
            next(err);
        }
    };
}

module.exports = createUserController;
