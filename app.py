# stdlib
from datetime import datetime
import os

# Third-party
from flask import Flask, flash, redirect, render_template_string, request, url_for
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

TPL_BASE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>CareLog</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('list_diapers') }}">CareLog</a>
        <div>
          <a class="btn btn-outline-light btn-sm" href="{{ url_for('new_diaper_form') }}">+ Diaper</a>
        </div>
      </div>
    </nav>
    <main class="container">
      {% with messages = get_flashed_messages() %}
        {% if messages %}
          <div class="alert alert-info">{{ messages[0] }}</div>
        {% endif %}
      {% endwith %}
      {% block body %}{% endblock %}
    </main>
  </body>
</html>
"""

# Only the body chunks — no extends, no base here.
TPL_LIST_BODY = """
<h3 class="mb-3">Diaper entries</h3>
<div class="mb-3">
  <a class="btn btn-primary" href="{{ url_for('new_diaper_form') }}">New entry</a>
</div>
<table class="table table-striped align-middle">
  <thead>
    <tr>
      <th>Time</th><th>Type</th><th>Size</th><th>Initials</th><th>Notes</th>
    </tr>
  </thead>
  <tbody>
    {% for x in rows %}
    <tr>
      <td>{{ x.dt.strftime('%Y-%m-%d %H:%M') }}</td>
      <td>{{ x.type }}</td>
      <td>{{ x.size }}</td>
      <td>{{ x.initials }}</td>
      <td>{{ x.notes or '' }}</td>
    </tr>
    {% else %}
    <tr><td colspan="5" class="text-muted">No entries yet.</td></tr>
    {% endfor %}
  </tbody>
</table>
"""

TPL_NEW_BODY = """
<h3 class="mb-3">New diaper entry</h3>
<form method="post" class="vstack gap-3">
  <div>
    <label class="form-label">Time</label>
    <input class="form-control" type="datetime-local" name="dt" required>
  </div>

  <div>
    <label class="form-label">Type</label>
    <select class="form-select" name="type" required>
      <option value="wet">Wet</option>
      <option value="BM">BM</option>
    </select>
  </div>

  <div>
    <label class="form-label">Size</label>
    <select class="form-select" name="size" required>
      <option value="S">S</option>
      <option value="M">M</option>
      <option value="L">L</option>
    </select>
  </div>

  <div>
    <label class="form-label">Initials</label>
    <input class="form-control" name="initials" maxlength="8" placeholder="AB" required>
  </div>

  <div>
    <label class="form-label">Notes</label>
    <textarea class="form-control" name="notes" rows="2"></textarea>
  </div>

  <button class="btn btn-primary" type="submit">Save</button>
  <a class="btn btn-outline-secondary" href="{{ url_for('list_diapers') }}">Cancel</a>
</form>
"""

def render_view(body_html: str, **ctx):
    page = TPL_BASE.replace("{% block body %}{% endblock %}", body_html)
    return render_template_string(page, **ctx)

class Diaper(db.Model):
    __tablename__ = "diapers"
    
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime, nullable=False)
    type = db.Column(Enum("wet", "BM", name="diaper_type"), nullable=False)
    size = db.Column(Enum("S", "M", "L", name="diaper_size"), nullable=False)
    initials = db.Column(db.String(2), nullable=False)
    notes = db.Column(db.Text)    

# ---- Sanity route
@app.get("/")
def ping():
    return "OK"

@app.get("/diapers")
def list_diapers():
    rows = Diaper.query.order_by(Diaper.dt.desc()).all()
    return render_view(TPL_LIST_BODY, rows=rows)

@app.get("/diapers/new")
def new_diaper_form():
    return render_view(TPL_NEW_BODY)

@app.post("/diapers/new")
def create_diaper():
    # Parse datetime-local string: "YYYY-MM-DDTHH:MM" (seconds optional)
    raw_dt = request.form["dt"].strip()
    dt = datetime.fromisoformat(raw_dt)  # Parse datetime-local input

    type_ = request.form["type"]
    size = request.form["size"]
    initials = request.form["initials"].strip()
    notes = request.form.get("notes") or None

    row = Diaper(dt=dt, type=type_, size=size, initials=initials, notes=notes)
    db.session.add(row)
    db.session.commit()

    flash("Saved diaper entry.")
    return redirect(url_for("list_diapers"))

# Dev server entry point.
if __name__ == "__main__":
    # One-time table creation; only creates missing tables.
    with app.app_context():
        db.create_all()

    # debug=True auto reloads on code changes.
    app.run(host="127.0.0.1", port=5000, debug=True)