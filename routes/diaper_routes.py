from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from models import db, Diaper

def init_diaper_routes(app):
    # Show history of diapers
    @app.get("/diaper")
    def diaper_list():
        rows = Diaper.query.order_by(Diaper.dt.desc()).all()
        return render_template("diaper_list.html", rows=rows)

    # New diaper entry form
    @app.get("/diaper/new")
    def diaper_new():
        return render_template("diaper_new.html")

    # Create new diaper entry
    @app.post("/diaper/new")
    def diaper_create():
        # Raw values from form
        dt_str = request.form["dt"]
        diaper_type = request.form["diaper_type"]
        diaper_size = request.form["diaper_size"]
        notes = request.form.get("notes").strip() or None

        # Convert date string to datetime
        dt = datetime.fromisoformat(dt_str)
        
        row = Diaper(
            dt=dt,
            diaper_type=diaper_type,
            diaper_size=diaper_size,
            notes=notes
        )

        db.session.add(row)
        db.session.commit()

        flash("Saved diaper entry.", "success")
        return redirect(url_for("diaper_list"))

    # Edit diaper entry form
    @app.get("/diaper/<int:diaper_id>/edit")
    def diaper_edit(diaper_id):
        row = Diaper.query.get_or_404(diaper_id)
        return render_template("diaper_edit.html", row=row)

    # Update from editing diaper entry
    @app.post("/diaper/<int:diaper_id>/edit")
    def diaper_update(diaper_id):
        row = Diaper.query.get_or_404(diaper_id)

        # Raw values from form
        raw_dt = request.form["dt"]
        diaper_type = request.form["diaper_type"]
        diaper_size = request.form["diaper_size"]
        notes = request.form.get("notes").strip() or None

        # Convert date string to datetime
        dt = datetime.fromisoformat(raw_dt)

        # Apply updates
        row.dt = dt
        row.diaper_type = diaper_type
        row.diaper_size = diaper_size
        row.notes = notes

        db.session.commit()

        flash("Diaper entry updated.", "success")
        return redirect(url_for("diaper_list"))

    # Delete diaper entry
    @app.post("/diaper/<int:diaper_id>/delete")
    def diaper_delete(diaper_id):
        diaper = Diaper.query.get_or_404(diaper_id)  # Find entry
        db.session.delete(diaper)                    # Mark for delete
        db.session.commit()                          # Save change
        flash("Diaper entry deleted.", "success")    # Notify user
        return redirect(url_for("diaper_list"))      # Back to list