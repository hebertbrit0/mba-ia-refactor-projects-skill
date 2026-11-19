const store = require("../models/courseModel");

async function deleteUser(db, req, res) {
    await store.deleteUserAggregate(db, req.params.id);
    return res.send("Usuário deletado.");
}

module.exports = { deleteUser };
