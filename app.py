# stdlib
from datetime import datetime, date, time
import os

# Third-party
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import func

# Local
from models import db, Diaper, Feed

# App + config
app = Flask(__name__)

# Keep secrets out of code; falls back to "dev" if env var not set.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

# SQLite file lives next to app.py for now.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carelog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind db to app
db.init_app(app)

@app.get("/")
def dashboard():
    return render_template("dashboard.html")

# Diaper log GET/POST routes
@app.get("/diaper")
def diaper_list():
    rows = Diaper.query.order_by(Diaper.dt.desc()).all()
    return render_template("diaper_list.html", rows=rows)

@app.get("/diaper/new")
def diaper_new():
    return render_template("diaper_new.html")

@app.post("/diaper/new")
def diaper_create():
    # Raw values from form
    raw_dt = request.form["dt"].strip()
    diaper_type = request.form["diaper_type"]
    diaper_size = request.form["diaper_size"]
    initials = request.form["initials"].strip().upper()
    notes = request.form.get("notes") or None

    # Validate datetime
    try:
        dt = datetime.fromisoformat(raw_dt)
    except ValueError:
        flash("Invalid date/time. Please pick a valid time.")
        return redirect(url_for("diaper_new"))

    row = Diaper(dt=dt, diaper_type=diaper_type, diaper_size=diaper_size, initials=initials, notes=notes)
    db.session.add(row)
    db.session.commit()

    flash("Saved diaper entry.", "success")
    return redirect(url_for("diaper_list"))

@app.get("/diaper/<int:diaper_id>/edit")
def diaper_edit(diaper_id):
    row = Diaper.query.get_or_404(diaper_id)
    return render_template("diaper_edit.html", row=row)

@app.post("/diaper/<int:diaper_id>/edit")
def diaper_update(diaper_id):
    row = Diaper.query.get_or_404(diaper_id)

    # Raw values from form
    raw_dt = request.form["dt"].strip()
    diaper_type = request.form["diaper_type"]
    diaper_size = request.form["diaper_size"]
    initials = request.form["initials"].strip().upper()
    notes = request.form.get("notes") or None

    # Apply updates
    row.dt = raw_dt
    row.diaper_type = diaper_type
    row.diaper_size = diaper_size
    row.initials = initials
    row.notes = notes

    db.session.commit()

    flash("Diaper entry updated.")
    return redirect(url_for("diaper_list"))

@app.post("/diaper/<int:diaper_id>/delete")
def diaper_delete(diaper_id):
    diaper = Diaper.query.get_or_404(diaper_id)  # Find entry
    db.session.delete(diaper)                    # Mark for delete
    db.session.commit()                          # Save change
    flash("Diaper entry deleted.", "success")    # Notify user
    return redirect(url_for("diaper_list"))      # Back to list


# Feed log GET/POST routes
@app.get("/feed")
def feed_list():
    rows = Feed.query.order_by(Feed.date.desc(), Feed.feed_num.desc()).all()
    return render_template("feed_list.html", rows=rows)

@app.get("/feed/new")
def feed_new():
    # Pre-fill date field with today's date
    today = date.today().isoformat()

    # Pre-fill feed number field with next feed number
    last_feed_num = db.session.query(func.max(Feed.feed_num)).scalar()
    next_feed_num = (last_feed_num or 0) + 1

    return render_template(
        "feed_new.html",
        today=today,
        next_feed_num=next_feed_num
    )

@app.post("/feed/new")
def feed_create():
    # Raw values from form
    feed_date_str = request.form["date"]
    feed_num_str = request.form["feed_num"].strip()
    start_time_str = request.form["start_time"]
    end_time_str = request.form["end_time"]
    feed_vol_ml_str = request.form["feed_vol_ml"].strip()
    feed_rate_str = request.form["feed_rate"].strip()
    notes = request.form.get("notes") or None

    # SQLite Date type must be Python date object for table
    feed_date = date.fromisoformat(feed_date_str)

    # Ensure inputs are stored as integers
    feed_num = int(feed_num_str)
    feed_vol_ml = int(feed_vol_ml_str)
    feed_rate = int(feed_rate_str)

    # SQLite Time type must be Python time object for table
    start_time = time.fromisoformat(start_time_str)
    end_time = time.fromisoformat(end_time_str)

    row = Feed(
        date=feed_date,
        feed_num=feed_num,
        start_time=start_time,
        end_time=end_time,
        feed_vol_ml=feed_vol_ml,
        feed_rate=feed_rate,
        notes=notes
    )
    
    db.session.add(row)
    db.session.commit()

    flash("Saved feed entry.", "success")
    return redirect(url_for("feed_list"))

@app.get("/feed/<int:feed_id>/edit")
def feed_edit(feed_id):
    row = Feed.query.get_or_404(feed_id)
    return render_template("feed_edit.html", row=row)

@app.post("/feed/<int:feed_id>/edit")
def feed_update(feed_id):
    row = Feed.query.get_or_404(feed_id)

    # Raw values from form
    feed_date_str = request.form["date"]
    feed_num_str = request.form["feed_num"].strip()
    start_time_str = request.form["start_time"]
    end_time_str = request.form["end_time"]
    feed_vol_ml_str = request.form["feed_vol_ml"].strip()
    feed_rate_str = request.form["feed_rate"].strip()
    notes = request.form.get("notes") or None

    # SQLite Date type must be Python date object for table
    feed_date = date.fromisoformat(feed_date_str)

    # Ensure inputs are stored as integers
    feed_num = int(feed_num_str)
    feed_vol_ml = int(feed_vol_ml_str)
    feed_rate = int(feed_rate_str)

    # SQLite Time type must be Python time object for table
    start_time = time.fromisoformat(start_time_str)
    end_time = time.fromisoformat(end_time_str)

    # Apply updates
    row.date = feed_date
    row.feed_num = feed_num
    row.start_time = start_time
    row.end_time = end_time    
    row.feed_vol_ml = feed_vol_ml
    row.feed_rate = feed_rate
    row.notes = notes

    db.session.commit()

    flash("Feed entry updated.")
    return redirect(url_for("feed_list"))

@app.post("/feed/<int:feed_id>/delete")
def feed_delete(feed_id):
    row = Feed.query.get_or_404(feed_id)     # Find entry
    db.session.delete(row)                   # Mark for delete
    db.session.commit()                      # Save change
    flash("Feed entry deleted.", "success")  # Notify user
    return redirect(url_for("feed_list"))    # Back to list


# Vomit log GET/POST routes
@app.get("/vomit")
def vomit_list():
    # Placeholder page
    return render_template("vomit_list.html")


# Dev server entry point.
if __name__ == "__main__":
    # One-time table creation; only creates missing tables.
    with app.app_context():
        db.create_all()

    # debug=True auto reloads on code changes.
    app.run(host="0.0.0.0", port=5000, debug=True)