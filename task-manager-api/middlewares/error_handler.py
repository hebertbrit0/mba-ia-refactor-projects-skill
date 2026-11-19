from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        db.session.rollback()
        app.logger.exception(err)
        return jsonify({"error": "Erro interno"}), 500
