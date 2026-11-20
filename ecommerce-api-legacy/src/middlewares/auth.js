const crypto = require("crypto");

const tokens = new Map();

function issueToken(userId) {
    const token = crypto.randomBytes(24).toString("hex");
    tokens.set(token, userId);
    return token;
}

function userIdFromHeader(header) {
    if (!header || !header.startsWith("Bearer ")) {
        return null;
    }
    const token = header.slice("Bearer ".length).trim();
    if (!tokens.has(token)) {
        return null;
    }
    return tokens.get(token);
}

module.exports = { issueToken, userIdFromHeader };
