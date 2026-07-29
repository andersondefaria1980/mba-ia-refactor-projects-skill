const passwordService = require('../services/passwordService');
const paymentService = require('../services/paymentService');

function createCheckoutController({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
    return async function checkout(req, res, next) {
        try {
            // Mantém os nomes de campo originais do payload (usr/eml/pwd/c_id/card)
            // para preservar o contrato de API já usado pelo api.http.
            const { usr: nome, eml: email, pwd: senha, c_id: cursoId, card: numeroCartao } = req.body;

            if (!nome || !email || !cursoId || !numeroCartao) {
                return res.status(400).json({ erro: 'Dados obrigatórios ausentes' });
            }

            const curso = await courseModel.getActiveById(cursoId);
            if (!curso) {
                return res.status(404).json({ erro: 'Curso não encontrado' });
            }

            let usuario = await userModel.getByEmail(email);
            let usuarioId;
            if (!usuario) {
                const senhaHash = await passwordService.hash(senha || Math.random().toString(36).slice(2));
                usuarioId = await userModel.create(nome, email, senhaHash);
            } else {
                usuarioId = usuario.id;
            }

            const status = paymentService.processarPagamento(numeroCartao);
            if (status === 'DENIED') {
                return res.status(400).json({ erro: 'Pagamento recusado' });
            }

            const enrollmentId = await enrollmentModel.create(usuarioId, cursoId);
            await paymentModel.create(enrollmentId, curso.price, status);
            await auditLogModel.record(`Checkout curso ${cursoId} por ${usuarioId}`);

            return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        } catch (err) {
            next(err);
        }
    };
}

module.exports = { createCheckoutController };
