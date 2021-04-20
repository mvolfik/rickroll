from flask import Flask
import os
from datetime import timedelta


def create_app():
    app = Flask(__name__)

    db_uri = os.environ["DATABASE_URL"]
    if db_uri.startswith("postgres://"):
        db_uri = "postgresql+psycopg2" + db_uri[8:]
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "FALLBACK USED IN DEV INSTANCES"
    )
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
    app.config["RICKROLL_URLS"] = {
        "Rickroll": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "Wreck-it-Ralph-roll": "https://www.youtube.com/watch?v=ptw2FLKXDQE",
        "Jebait": "https://www.youtube.com/watch?v=oGJr5N2lgsQ",
        "Duckroll": "https://i.kym-cdn.com/photos/images/original/000/002/941/Duckroll.jpg",
        "Gamecube distraction": "https://www.youtube.com/watch?v=T3qrj4B08sc",
    }
    from .db import db

    db.init_app(app)

    from .core import bp

    app.register_blueprint(bp)

    return app
