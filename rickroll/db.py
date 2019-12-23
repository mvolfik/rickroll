from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Rickroll(db.Model):
    __tablename__ = "rickrolls"
    url = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    imgurl = db.Column(db.String(1024), nullable=False)
