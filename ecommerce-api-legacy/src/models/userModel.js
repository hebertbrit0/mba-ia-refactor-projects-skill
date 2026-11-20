const crypto = require("crypto");

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString("hex");
    const hash = crypto.scryptSync(String(password), salt, 32).toString("hex");
    return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
    if (!stored || !stored.includes(":")) {
        return false;
    }
    const [salt, hash] = stored.split(":");
    const candidate = crypto.scryptSync(String(password), salt, 32).toString("hex");
    if (candidate.length !== hash.length) {
        return false;
    }
    return crypto.timingSafeEqual(Buffer.from(candidate), Buffer.from(hash));
}

module.exports = { hashPassword, verifyPassword };
