from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',
                                              "FALLBACK USED IN DEV INSTANCES")
    app.config['RICKROLL_URLS'] = {
        'Rickroll':
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'Wreck-it-Ralph-roll':
        'https://www.youtube.com/watch?v=4JZSJ49gVJw',
        'Jebait':
        'https://www.youtube.com/watch?v=oGJr5N2lgsQ',
        'Duckroll':
        'https://i.kym-cdn.com/photos/images/original/000/002/941/Duckroll.jpg'
    }
    from .db import db
    db.init_app(app)

    from .core import bp
    app.register_blueprint(bp)

    return app
