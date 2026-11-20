const store = require("../models/courseModel");
const { verifyPassword } = require("../models/userModel");
const { issueToken, userIdFromHeader } = require("../middlewares/auth");

async function login(db, req, res) {
    const body = req.body || {};
    const email = body.email || body.eml;
    const password = body.password || body.pwd;
    if (!email || !password) {
        return res.status(400).send("Bad Request");
    }

    const user = await store.findUserCredentials(db, email);
    if (!user || !verifyPassword(password, user.pass)) {
        return res.status(401).send("Credenciais inválidas");
    }

    return res.status(200).json({ token: issueToken(user.id) });
}

function requireUser(req, res) {
    const userId = userIdFromHeader(req.headers.authorization);
    if (userId == null) {
        res.status(401).send("Não autenticado");
        return null;
    }
    return userId;
}

async function deleteUser(db, req, res) {
    const actorId = requireUser(req, res);
    if (actorId == null) {
        return undefined;
    }
    if (Number(actorId) !== Number(req.params.id)) {
        return res.status(403).send("Acesso negado");
    }
    await store.deleteUserAggregate(db, req.params.id);
    return res.send("Usuário deletado.");
}

module.exports = { login, deleteUser, requireUser };
