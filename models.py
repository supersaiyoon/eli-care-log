from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()


class Diaper(db.Model):
    __tablename__ = "diapers"
    
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True)
    wet_diaper_size = db.Column(
        Enum("S", "M", "L", name="wet_diaper_size"),
        nullable=True
    )
    bm_diaper_size = db.Column(
        Enum("S", "M", "L", name="bm_diaper_size"),
        nullable=True
    )
    notes = db.Column(db.Text)

class Feed(db.Model):
    __tablename__ = "feed"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    feed_num = db.Column(db.Integer, autoincrement=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    feed_vol_ml = db.Column(db.Integer, nullable=True)
    feed_rate = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)

class Medication(db.Model):
    __tablename__ = "medication"

    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False, index=True)
    med_name = db.Column(db.String(50), nullable=False)
    dosage_ml = db.Column(db.Float, nullable=False)
    initials = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text)

class Sleep(db.Model):
    __tablename__ = "sleep"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    sleep_duration_min = db.Column(db.Integer, nullable=False)
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

# TODO: Implement weekly tasks tracker model (trach change, G-tube balloon check, etc.)