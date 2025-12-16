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
from ui_themes import PAGE_THEMES


def build_db_path():
    # Dev default (local folder)
    default_db_dir = "db"
    database_dir = os.environ.get("ELI_DB_DIR", default_db_dir)

    # If running in Docker, use container path unless overridden
    if os.path.exists("/.dockerenv") and "ELI_DB_DIR" not in os.environ:
        database_dir = "/app/db"
    
    # Ensure db dir exists
    os.makedirs(database_dir, exist_ok=True)

    db_file = "eli_care_log.db"
    db_path = os.path.abspath(os.path.join(database_dir, db_file))

    # SQLAlchemy wants forward slashes even on Windows
    db_uri_path = db_path.replace("\\", "/")

    return db_uri_path

def create_app():
    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{build_db_path()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensions
    db.init_app(app)

    # Template helpers
    register_template_helpers(app)

    # Routes
    register_routes(app)

    # Startup tasks
    init_db(app)

    return app

def register_template_helpers(app):
    @app.context_processor
    def inject_page_theme():
        def get_theme(page_key):
            return PAGE_THEMES.get(page_key)
        return {"get_theme": get_theme}

    @app.template_filter("minutes_to_hhmm")
    def minutes_to_hhmm(total_minutes):
        if total_minutes is None:
            return ""
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        return f"{hours:02d}:{minutes:02d}"

def register_routes(app):
    init_diaper_routes(app)
    init_feed_routes(app)
    init_medication_routes(app)
    init_sleep_routes(app)
    init_vomit_routes(app)

    # Homepage
    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

def init_db(app):
    with app.app_context():
        db.create_all()


app = create_app()


# Dev server entry point.
if __name__ == "__main__":
    # debug=True auto reloads on code changes.
    app.run(host="0.0.0.0", port=5000, debug=True)