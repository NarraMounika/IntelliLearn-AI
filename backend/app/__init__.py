import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from .db import init_db
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")}})
    init_db()
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "IntelliLearn AI"}

    @app.errorhandler(413)
    def too_large(_):
        return {"error": "File is too large. Check MAX_UPLOAD_MB."}, 413

    return app
