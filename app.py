# stdlib
from datetime import datetime, time, timedelta
import os

# Third-party
from flask import Flask, render_template

# Local
from models import db, Diaper, Feed
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
        def minutes_ago(dt):
            delta = datetime.now() - dt
            minutes = int(delta.total_seconds() // 60)

            if minutes < 1:
                return "just now"
            if minutes < 60:
                return f"{minutes} min ago"

            hours = minutes // 60
            if hours == 1:
                return "1 hr ago"
            return f"{hours} hrs ago"

        def diaper_type_label(d):
            wet = d.wet_diaper_size is not None
            bm = d.bm_diaper_size is not None

            if wet and bm:
                return "Wet + BM"
            if wet:
                return "Wet"
            if bm:
                return "BM"
            return "Unknown"

        # Diaper stats for dashboard
        last_diaper = (
            Diaper.query
            .order_by(Diaper.dt.desc())
            .first()
        )

        last_diaper_ago = minutes_ago(last_diaper.dt) if last_diaper else None
        last_diaper_type = diaper_type_label(last_diaper) if last_diaper else None

        # Today's counts (resets at local midnight)
        today_start = datetime.combine(datetime.today().date(), time.min)

        wet_count = (
            Diaper.query
            .filter(
                Diaper.dt >= today_start,
                Diaper.wet_diaper_size.isnot(None),
            )
            .count()
        )

        bm_count = (
            Diaper.query
            .filter(
                Diaper.dt >= today_start,
                Diaper.bm_diaper_size.isnot(None),
            )
            .count()
        )

        # Avg feed duration (last 10 completed feeds) for dashboard
        recent_feeds = (
            Feed.query
            .filter(Feed.end_time.isnot(None))
            .order_by(Feed.date.desc(), Feed.feed_num.desc())
            .limit(10)
            .all()
        )

        durations_min = []
        for f in recent_feeds:
            start_dt = datetime.combine(f.date, f.start_time)
            end_dt = datetime.combine(f.date, f.end_time)

            # Handle feed crossing midnight
            if end_dt <= start_dt:
                end_dt += timedelta(days=1)

            minutes = int((end_dt - start_dt).total_seconds() // 60)
            durations_min.append(minutes)

        avg_feed_duration_min = None

        if durations_min:
            avg_feed_duration_min = sum(durations_min) // len(durations_min)


        return render_template(
            "dashboard.html",
            last_diaper=last_diaper,
            last_diaper_ago=last_diaper_ago,
            last_diaper_type=last_diaper_type,
            wet_count=wet_count,
            bm_count=bm_count,
            avg_feed_duration_min=avg_feed_duration_min,
        )


def init_db(app):
    with app.app_context():
        db.create_all()


app = create_app()


# Dev server entry point.
if __name__ == "__main__":
    # debug=True auto reloads on code changes.
    app.run(host="0.0.0.0", port=5000, debug=True)