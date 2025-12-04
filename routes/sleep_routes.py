from datetime import date, datetime, time, timedelta

from flask import flash, redirect, render_template, request, url_for

from models import db, Sleep


def init_sleep_routes(app):
    # Show history of sleep
    @app.get("/sleep")
    def sleep_list():
        rows = Sleep.query.order_by(Sleep.date.desc()).all()
        return render_template("sleep_list.html", rows=rows)

    # New sleep entry form
    @app.get("/sleep/new")
    def sleep_new():
        # Pre-fill date field with today's date
        today = date.today().isoformat()

        return render_template(
            "sleep_new.html",
            today=today,
        )

    # Create new sleep entry
    @app.post("/sleep/new")
    def sleep_create():
        # Raw values from form
        sleep_date_str = request.form["date"]
        start_time_str = request.form["start_time"]
        end_time_str = request.form["end_time"]
        notes = request.form.get("notes").strip() or None

        # SQLite Date type must be Python date object for table
        sleep_date = date.fromisoformat(sleep_date_str)

        # SQLite Time type must be Python time object for table
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        # Compute sleep duration in minutes
        start_dt = datetime.combine(sleep_date, start_time)
        end_dt = datetime.combine(sleep_date, end_time)
        
        # Handle case where sleep goes past midnight
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        sleep_duration = end_dt - start_dt
        sleep_duration_min = sleep_duration.total_seconds() // 60

        row = Sleep(
            date=sleep_date,
            start_time=start_time,
            end_time=end_time,
            sleep_duration_min=sleep_duration_min,
            notes=notes
        )
        
        db.session.add(row)
        db.session.commit()

        flash("Saved sleep entry.", "success")
        return redirect(url_for("sleep_list"))

    # Edit sleep entry form
    @app.get("/sleep/<int:sleep_id>/edit")
    def sleep_edit(sleep_id):
        row = Sleep.query.get_or_404(sleep_id)
        return render_template("sleep_edit.html", row=row)

    # Update from editing sleep entry
    @app.post("/sleep/<int:sleep_id>/edit")
    def sleep_update(sleep_id):
        row = Sleep.query.get_or_404(sleep_id)

        # Raw values from form
        sleep_date_str = request.form["date"]
        start_time_str = request.form["start_time"]
        end_time_str = request.form["end_time"]
        notes = request.form.get("notes").strip() or None

        # SQLite Date type must be Python date object for table
        sleep_date = date.fromisoformat(sleep_date_str)

        # SQLite Time type must be Python time object for table
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        # Compute sleep duration in minutes
        start_dt = datetime.combine(sleep_date, start_time)
        end_dt = datetime.combine(sleep_date, end_time)
        
        # Handle case where sleep goes past midnight
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        
        sleep_duration = end_dt - start_dt
        sleep_duration_min = sleep_duration.total_seconds() // 60

        # Apply updates
        row.date = sleep_date
        row.start_time = start_time
        row.end_time = end_time
        row.sleep_duration_min = sleep_duration_min
        row.notes = notes

        db.session.commit()

        flash("Sleep entry updated.")
        return redirect(url_for("sleep_list"))

    # Delete sleep entry
    @app.post("/sleep/<int:sleep_id>/delete")
    def sleep_delete(sleep_id):
        row = Sleep.query.get_or_404(sleep_id)    # Find entry
        db.session.delete(row)                    # Mark for delete
        db.session.commit()                       # Save change
        flash("Sleep entry deleted.", "success")  # Notify user
        return redirect(url_for("sleep_list"))    # Back to list