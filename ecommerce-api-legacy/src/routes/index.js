const express = require("express");
const { checkout } = require("../controllers/checkoutController");
const { financialReport } = require("../controllers/reportController");
const { deleteUser, login } = require("../controllers/userController");

function createRoutes(db) {
    const router = express.Router();

    router.post("/api/login", (req, res, next) => {
        login(db, req, res).catch(next);
    });

    router.post("/api/checkout", (req, res, next) => {
        checkout(db, req, res).catch(next);
    });

    router.get("/api/admin/financial-report", (req, res, next) => {
        financialReport(db, req, res).catch(next);
    });

    router.delete("/api/users/:id", (req, res, next) => {
        deleteUser(db, req, res).catch(next);
    });

    return router;
}

module.exports = { createRoutes };
