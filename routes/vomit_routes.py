from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func

from models import db, Vomit


def init_vomit_routes(app):
    # Show history of vomits
    @app.get("/vomit")
    def vomit_list():
        PER_PAGE = 5
        page = request.args.get("page", default=0, type=int)
        offset = page * PER_PAGE

        q = Vomit.query.order_by(Vomit.dt.desc())
        rows = q.offset(offset).limit(PER_PAGE + 1).all()

        has_more = len(rows) > PER_PAGE
        rows = rows[:PER_PAGE]

        return render_template(
            "vomit_list.html",
            rows=rows,
            page=page,
            has_more=has_more,
        )

    # New vomit entry form
    @app.get("/vomit/new")
    def vomit_new():
        return render_template("vomit_new.html")

    # Create new vomit entry
    @app.post("/vomit/new")
    def vomit_create():
        # Raw values from form
        dt_str = request.form["dt"]
        vomit_size = request.form["vomit_size"]
        feed_rate = request.form["feed_rate"].strip()
        vomit_reason = request.form.get("vomit_reason").strip() or None
        
        # Convert date string to datetime
        dt = datetime.fromisoformat(dt_str)

        # Ensure inputs are stored as integers
        feed_rate = int(feed_rate)

        row = Vomit(
            dt=dt,
            vomit_size=vomit_size,
            feed_rate=feed_rate,
            vomit_reason=vomit_reason
        )
        
        db.session.add(row)
        db.session.commit()

        flash("Saved vomit entry.", "success")
        return redirect(url_for("vomit_list"))

    # Edit vomit entry form
    @app.get("/vomit/<int:vomit_id>/edit")
    def vomit_edit(vomit_id):
        row = Vomit.query.get_or_404(vomit_id)
        return render_template("vomit_edit.html", row=row)
    
    # Update from editing vomit entry
    @app.post("/vomit/<int:vomit_id>/edit")
    def vomit_update(vomit_id):
        row = Vomit.query.get_or_404(vomit_id)

        # Raw values from form
        dt_str = request.form["dt"]
        vomit_size = request.form["vomit_size"]
        feed_rate = request.form["feed_rate"].strip()
        vomit_reason = request.form.get("vomit_reason").strip() or None

        # SQLite Date type must be Python date object for table
        dt = datetime.fromisoformat(dt_str)

        # Ensure inputs are stored as integers
        feed_rate = int(feed_rate)

        # Apply updates
        row.dt = dt
        row.vomit_size = vomit_size
        row.feed_rate = feed_rate
        row.vomit_reason = vomit_reason

        db.session.commit()

        flash("Vomit entry updated.")
        return redirect(url_for("vomit_list"))

    # Delete vomit entry
    @app.post("/vomit/<int:vomit_id>/delete")
    def vomit_delete(vomit_id):
        row = Vomit.query.get_or_404(vomit_id)     # Find entry
        db.session.delete(row)                    # Mark for delete
        db.session.commit()                       # Save change
        flash("Vomit entry deleted.", "success")  # Notify user
        return redirect(url_for("vomit_list"))    # Back to list