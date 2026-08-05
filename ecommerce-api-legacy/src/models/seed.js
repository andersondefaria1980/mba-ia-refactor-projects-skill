const { hashPassword } = require('../utils/security');

async function seed({ userModel, courseModel, enrollmentModel, paymentModel }) {
    const userId = await userModel.create({
        name: 'Leonan',
        email: 'leonan@fullcycle.com.br',
        passwordHash: hashPassword('123'),
    });

    const clean = await courseModel.create({ title: 'Clean Architecture', price: 997.0, active: 1 });
    await courseModel.create({ title: 'Docker', price: 497.0, active: 1 });

    const enrollmentId = await enrollmentModel.create({ userId, courseId: clean.lastID });
    await paymentModel.create({ enrollmentId, amount: 997.0, status: 'PAID' });
}

module.exports = seed;
