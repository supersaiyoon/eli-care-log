from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from models import db, Medication

def init_medication_routes(app):
    # Show history of medications
    @app.get("/medication")
    def medication_list():
        PER_PAGE = 5
        page = request.args.get("page", default=0, type=int)
        offset = page * PER_PAGE

        q = Medication.query.order_by(Medication.dt.desc())
        rows = q.offset(offset).limit(PER_PAGE + 1).all()

        has_more = len(rows) > PER_PAGE
        rows = rows[:PER_PAGE]

        return render_template(
            "medication_list.html",
            rows=rows,
            page=page,
            has_more=has_more,
            page_key="medication",
        )
    
    # New medication entry form
    @app.get("/medication/new")
    def medication_new():
        return render_template(
            "medication_new.html",
            page_key="medication",
            )

    # Create new medication entry
    @app.post("/medication/new")
    def medication_create():
        # Raw values from form
        dt_str = request.form["dt"]
        med_name = request.form["med_name"]
        dosage_ml = request.form["dosage_ml"]
        initials = request.form["initials"].strip().upper()
        notes = request.form.get("notes").strip() or None

        # Convert date string to datetime
        dt = datetime.fromisoformat(dt_str)
        
        row = Medication(
            dt=dt,
            med_name=med_name,
            dosage_ml=dosage_ml,
            initials=initials,
            notes=notes
        )

        db.session.add(row)
        db.session.commit()

        flash("Saved medication entry.", "success")
        return redirect(url_for("medication_list"))

    # Edit medication entry form
    @app.get("/medication/<int:medication_id>/edit")
    def medication_edit(medication_id):
        row = Medication.query.get_or_404(medication_id)
        return render_template(
            "medication_edit.html",
            row=row,
            page_key="medication",
            )
    
    # Update from editing medication entry
    @app.post("/medication/<int:medication_id>/edit")
    def medication_update(medication_id):
        row = Medication.query.get_or_404(medication_id)
        
        # Raw values from form
        dt_str = request.form["dt"]
        med_name = request.form["med_name"]
        dosage_ml = request.form["dosage_ml"]
        initials = request.form["initials"].strip().upper()
        notes = request.form.get("notes").strip() or None

        # Convert date string to datetime
        dt = datetime.fromisoformat(dt_str)

        # Apply updates
        row.dt = dt
        row.med_name = med_name
        row.dosage_ml = dosage_ml
        row.initials = initials
        row.notes = notes

        db.session.commit()

        flash("Medication entry updated.", "success")
        return redirect(url_for("medication_list"))

    # Delete medication entry
    @app.post("/medication/<int:medication_id>/delete")
    def medication_delete(medication_id):
        medication = Medication.query.get_or_404(medication_id)  # Find entry
        db.session.delete(medication)                            # Mark for delete
        db.session.commit()                                      # Save change
        flash("Medication entry deleted.", "success")            # Notify user
        return redirect(url_for("medication_list"))              # Back to list