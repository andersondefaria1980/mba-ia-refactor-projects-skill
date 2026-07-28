const { createApp } = require('./app');
const settings = require('./config/settings');

createApp()
    .then((app) => {
        app.listen(settings.port, () => {
            console.log(`Servidor rodando na porta ${settings.port}`);
        });
    })
    .catch((err) => {
        console.error('Falha ao iniciar aplicação', err);
        process.exit(1);
    });
