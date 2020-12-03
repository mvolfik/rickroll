from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rickroll(db.Model):
    __tablename__ = "rickrolls"
    url = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    imgurl = db.Column(db.String(1024), nullable=False)
    redirecturl = db.Column(db.String(1024), nullable=False)
    rollcount = db.Column(db.Integer, nullable=False, default=0)
