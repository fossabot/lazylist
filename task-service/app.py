import os
import time
from functools import wraps

import jwt
from flask import Flask, request, jsonify

from models import db, Task

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"


def build_db_uri():
    return (
        f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '3306')}"
        f"/{os.environ['DB_NAME']}"
    )


def init_db(app, retries=10, delay=3):
    with app.app_context():
        for attempt in range(retries):
            try:
                db.create_all()
                return
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(delay)


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "token ausente"}), 401
        try:
            payload = jwt.decode(header.split(" ", 1)[1], JWT_SECRET,
                                 algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "token invalido"}), 401
        request.user_id = int(payload["sub"])
        request.user_role = payload["role"]
        return f(*args, **kwargs)
    return wrapper


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    init_db(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
