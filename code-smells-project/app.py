from flask import Flask
from flask_cors import CORS

from config.settings import settings
from middlewares.error_handler import register_error_handlers
from models.db import close_db, init_db
from views.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["DEBUG"] = settings.debug
    app.config["DB_PATH"] = settings.db_path
    CORS(app)
    register_error_handlers(app)
    register_routes(app)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://{settings.host}:{settings.port}")
    print("=" * 50)
    app.run(host=settings.host, port=settings.port, debug=settings.debug)
