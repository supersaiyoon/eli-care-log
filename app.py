# stdlib
import os

# Third-party
from flask import Flask, render_template

# Local
from models import db
from routes.diaper_routes import init_diaper_routes
from routes.feed_routes import init_feed_routes
from routes.medication_routes import init_medication_routes
from routes.sleep_routes import init_sleep_routes
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
init_sleep_routes(app)
init_vomit_routes(app)


def init_db():
    # Ensure we have app context when touching db
    with app.app_context():
        db.create_all()

# Run once at startup (both dev and container)
init_db()


# Helper functions
@app.template_filter("minutes_to_hhmm")
def minutes_to_hhmm(total_minutes):
    if total_minutes is None:
        return ""
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return f"{hours:02d}:{minutes:02d}"

@app.get("/")
def dashboard():
    return render_template("dashboard.html")


# Dev server entry point.
if __name__ == "__main__":
    # debug=True auto reloads on code changes.
    app.run(host="0.0.0.0", port=5000, debug=True)