const express = require("express");
const { config } = require("./config/settings");
const { openDatabase, initDatabase } = require("./models/db");
const { createRoutes } = require("./routes");
const { errorHandler } = require("./middlewares/errorHandler");

async function main() {
    const app = express();
    app.use(express.json());

    const db = openDatabase();
    await initDatabase(db);
    app.use(createRoutes(db));
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}...`);
    });
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
