# stdlib
import os

# Third-party
from flask import Flask, render_template

# Local
from models import db
from routes.diaper_routes import init_diaper_routes
from routes.feed_routes import init_feed_routes
from routes.medication_routes import init_medication_routes
from routes.vomit_routes import init_vomit_routes


# App + config
app = Flask(__name__)

# Keep secrets out of code; falls back to "dev" if env var not set.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

# SQLite file lives next to app.py for now.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carelog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Bind db to app
db.init_app(app)

# Register routes
init_diaper_routes(app)
init_feed_routes(app)
init_medication_routes(app)
init_vomit_routes(app)

@app.get("/")
def dashboard():
    return render_template("dashboard.html")


# Dev server entry point.
if __name__ == "__main__":
    # One-time table creation; only creates missing tables.
    with app.app_context():
        db.create_all()

    # debug=True auto reloads on code changes.
    app.run(host="0.0.0.0", port=5000, debug=True)