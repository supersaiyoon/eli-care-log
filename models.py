from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class Diaper(db.Model):
    __tablename__ = "diapers"
    
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True)
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

class Feed(db.Model):
    __tablename__ = "feed"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    feed_num = db.Column(db.Integer, autoincrement=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    feed_vol_ml = db.Column(db.Integer, nullable=False)
    feed_rate = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

class Medication(db.Model):
    __tablename__ = "medication"

    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True)
    med_name = db.Column(db.String(50), nullable=False)
    dosage_ml = db.Column(db.Float, nullable=False)
    initials = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text)

class Vomit(db.Model):
    __tablename__ = "vomit"

    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True)
    vomit_size = db.Column(
        Enum("S", "M", "L", name="vomit_size"),
        nullable=False
    )
    feed_rate = db.Column(db.Integer, nullable=False)
    vomit_reason = db.Column(db.Text)