function userController({ userModel }) {
    return {
        async deleteUser(req, res) {
            const id = Number(req.params.id);
            if (!Number.isInteger(id)) {
                return res.status(400).send('ID de usuário inválido');
            }

            await userModel.deleteById(id);
            res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        },
    };
}

module.exports = userController;
