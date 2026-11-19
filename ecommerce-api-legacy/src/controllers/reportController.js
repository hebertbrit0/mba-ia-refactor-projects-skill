const store = require("../models/courseModel");

function buildReport(rows) {
    const report = [];
    const byCourse = new Map();

    rows.forEach((row) => {
        if (!byCourse.has(row.course_id)) {
            const entry = { course: row.course, revenue: 0, students: [] };
            byCourse.set(row.course_id, entry);
            report.push(entry);
        }
        if (row.enrollment_id == null) {
            return;
        }
        const entry = byCourse.get(row.course_id);
        const paidAmount = row.amount || 0;
        if (row.status === store.PAID_STATUS) {
            entry.revenue += paidAmount;
        }
        entry.students.push({
            student: row.student || "Unknown",
            paid: paidAmount,
        });
    });

    return report;
}

async function financialReport(db, _req, res) {
    try {
        const rows = await store.financialRows(db);
        return res.json(buildReport(rows));
    } catch (_err) {
        return res.status(500).send("Erro DB");
    }
}

module.exports = { financialReport, buildReport };
