# stdlib
from datetime import datetime
import os

# Third-party
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

# ---- App + config
app = Flask(__name__)

# Keep secrets out of code; falls back to "dev" if env var not set.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

# SQLite file lives next to app.py for now.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carelog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ORM handle; models will subclass db.Model later.
db = SQLAlchemy(app)

class Diaper(db.Model):
    __tablename__ = "diapers"
    
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    type = db.Column(Enum("wet", "BM", name="diaper_type"), nullable=False)
    size = db.Column(Enum("S", "M", "L", name="diaper_size"), nullable=False)
    initials = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text)    

# ---- Sanity route
@app.get("/")
def ping():
    return "OK"

# Dev server entry point.
if __name__ == "__main__":
    # One-time table creation; only creates missing tables.
    with app.app_context():
        db.create_all()

    # debug=True auto reloads on code changes.
    app.run(host="127.0.0.1", port=5000, debug=True)