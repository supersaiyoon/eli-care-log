from datetime import date, time

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func

from models import db, Feed


def init_feed_routes(app):
    # Show history of feeds
    @app.get("/feed")
    def feed_list():
        rows = Feed.query.order_by(Feed.date.desc(), Feed.feed_num.desc()).all()
        return render_template("feed_list.html", rows=rows)

    # New feed entry form
    @app.get("/feed/new")
    def feed_new():
        # Pre-fill date field with today's date
        today = date.today().isoformat()

        # Pre-fill feed number field with next feed number
        last_feed_num = (db.session.query(func.max(Feed.feed_num))
            .filter(Feed.date == today)
            .scalar()
        )
        next_feed_num = (last_feed_num or 0) + 1

        return render_template(
            "feed_new.html",
            today=today,
            next_feed_num=next_feed_num
        )

    # Create new feed entry
    @app.post("/feed/new")
    def feed_create():
        # Raw values from form
        feed_date_str = request.form["date"]
        feed_num_str = request.form["feed_num"].strip()
        start_time_str = request.form["start_time"]
        end_time_str = request.form["end_time"]
        feed_vol_ml_str = request.form["feed_vol_ml"].strip()
        feed_rate_str = request.form["feed_rate"].strip()
        notes = request.form.get("notes").strip() or None

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

    # Edit feed entry form
    @app.get("/feed/<int:feed_id>/edit")
    def feed_edit(feed_id):
        row = Feed.query.get_or_404(feed_id)
        return render_template("feed_edit.html", row=row)

    # Update from editing feed entry
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
        notes = request.form.get("notes").strip() or None

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

    # Delete feed entry
    @app.post("/feed/<int:feed_id>/delete")
    def feed_delete(feed_id):
        row = Feed.query.get_or_404(feed_id)     # Find entry
        db.session.delete(row)                   # Mark for delete
        db.session.commit()                      # Save change
        flash("Feed entry deleted.", "success")  # Notify user
        return redirect(url_for("feed_list"))    # Back to list