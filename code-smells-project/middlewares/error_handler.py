from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):
            return err
        app.logger.exception(err)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
