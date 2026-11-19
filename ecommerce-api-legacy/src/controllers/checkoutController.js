const { hashPassword } = require("../models/userModel");
const store = require("../models/courseModel");

const PAID_CARD_PREFIX = "4";

function parseCheckout(body) {
    const userName = body.usr;
    const email = body.eml;
    const password = body.pwd;
    const courseId = body.c_id;
    const cardNumber = body.card;
    if (!userName || !email || !courseId || !cardNumber) {
        return { error: "Bad Request" };
    }
    return { userName, email, password, courseId, cardNumber };
}

function paymentStatus(cardNumber) {
    return String(cardNumber).startsWith(PAID_CARD_PREFIX) ? "PAID" : "DENIED";
}

async function checkout(db, req, res) {
    const parsed = parseCheckout(req.body || {});
    if (parsed.error) {
        return res.status(400).send(parsed.error);
    }

    let course;
    try {
        course = await store.findActiveCourse(db, parsed.courseId);
    } catch (_err) {
        return res.status(404).send("Curso não encontrado");
    }
    if (!course) {
        return res.status(404).send("Curso não encontrado");
    }

    let existingUser;
    try {
        existingUser = await store.findUserByEmail(db, parsed.email);
    } catch (_err) {
        return res.status(500).send("Erro DB");
    }

    let userId;
    if (!existingUser) {
        try {
            const created = await store.createUser(
                db,
                parsed.userName,
                parsed.email,
                hashPassword(parsed.password || "123456")
            );
            userId = created.lastID;
        } catch (_err) {
            return res.status(500).send("Erro ao criar usuário");
        }
    } else {
        userId = existingUser.id;
    }

    const status = paymentStatus(parsed.cardNumber);
    if (status === "DENIED") {
        return res.status(400).send("Pagamento recusado");
    }

    let enrollmentId;
    try {
        const enrollment = await store.createEnrollment(db, userId, parsed.courseId);
        enrollmentId = enrollment.lastID;
    } catch (_err) {
        return res.status(500).send("Erro Matrícula");
    }

    try {
        await store.createPayment(db, enrollmentId, course.price, status);
    } catch (_err) {
        return res.status(500).send("Erro Pagamento");
    }

    try {
        await store.createAuditLog(db, `Checkout curso ${parsed.courseId} por ${userId}`);
    } catch (_err) {
        // The legacy flow still returned success when the audit insert failed.
    }

    return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
}

module.exports = { checkout, parseCheckout, paymentStatus };
