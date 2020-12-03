from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rickroll(db.Model):
    __tablename__ = "rickrolls"
    url = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    imgurl = db.Column(db.String, nullable=False)
    redirecturl = db.Column(db.String, nullable=False)
    rollcount = db.Column(db.Integer, nullable=False, default=0)
