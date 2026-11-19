const { get, all, run } = require("./db");

const PAID_STATUS = "PAID";

function findActiveCourse(db, courseId) {
    return get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
}

function findUserByEmail(db, email) {
    return get(db, "SELECT id FROM users WHERE email = ?", [email]);
}

function createUser(db, name, email, passwordHash) {
    return run(
        db,
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        [name, email, passwordHash]
    );
}

function createEnrollment(db, userId, courseId) {
    return run(
        db,
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId]
    );
}

function createPayment(db, enrollmentId, amount, status) {
    return run(
        db,
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollmentId, amount, status]
    );
}

function createAuditLog(db, action) {
    return run(
        db,
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
    );
}

function financialRows(db) {
    return all(
        db,
        `
        SELECT c.id AS course_id,
               c.title AS course,
               e.id AS enrollment_id,
               u.name AS student,
               p.amount AS amount,
               p.status AS status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id, e.id
        `
    );
}

async function deleteUserAggregate(db, userId) {
    await run(db, "BEGIN");
    try {
        await run(
            db,
            "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
            [userId]
        );
        await run(db, "DELETE FROM enrollments WHERE user_id = ?", [userId]);
        await run(db, "DELETE FROM users WHERE id = ?", [userId]);
        await run(db, "COMMIT");
    } catch (err) {
        await run(db, "ROLLBACK");
        throw err;
    }
}

module.exports = {
    PAID_STATUS,
    findActiveCourse,
    findUserByEmail,
    createUser,
    createEnrollment,
    createPayment,
    createAuditLog,
    financialRows,
    deleteUserAggregate,
};
