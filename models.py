from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class Diaper(db.Model):
    __tablename__ = "diapers"
    
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False)
    diaper_type = db.Column(
        Enum("Wet", "BM", name="diaper_type"),
        nullable=False
    )
    diaper_size = db.Column(
        Enum("S", "M", "L", name="diaper_size"),
        nullable=False
    )
    initials = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text)