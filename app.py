# stdlib
from datetime import datetime
import os

# Third-party
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

# App + config
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

# Sanity route
@app.get("/")
def index():
    return redirect(url_for("list_diapers"))

@app.get("/diapers")
def list_diapers():
    rows = Diaper.query.order_by(Diaper.dt.desc()).all()
    return render_template("diapers_list.html", rows=rows)

@app.get("/diapers/new")
def new_diaper_form():
    return render_template("diapers_new.html")

@app.post("/diapers/new")
def create_diaper():
    # Raw values from form
    raw_dt = request.form["dt"].strip()
    diaper_type = request.form["diaper_type"]
    diaper_size = request.form["diaper_size"]
    initials = request.form["initials"].strip()
    notes = request.form.get("notes") or None

    # validate datetime
    try:
        dt = datetime.fromisoformat(raw_dt)  # Parse datetime-local input
    except ValueError:
        flash("Invalid date/time. Please pick a valid time.")
        return redirect(url_for("new_diaper_form"))

    row = Diaper(dt=dt, diaper_type=diaper_type, diaper_size=diaper_size, initials=initials, notes=notes)
    db.session.add(row)
    db.session.commit()

    flash("Saved diaper entry.")
    return redirect(url_for("list_diapers"))

@app.post("/diapers/<int:diaper_id>/delete")
def delete_diaper(diaper_id):
    diaper = Diaper.query.get_or_404(diaper_id)  # Find entry
    db.session.delete(diaper)                    # Mark for delete
    db.session.commit()                          # Save change
    flash("Diaper entry deleted.", "success")    # Notify user
    return redirect(url_for("list_diapers"))     # Back to list

# Dev server entry point.
if __name__ == "__main__":
    # One-time table creation; only creates missing tables.
    with app.app_context():
        db.create_all()

    # debug=True auto reloads on code changes.
    app.run(host="127.0.0.1", port=5000, debug=True)