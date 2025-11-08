# stdlib
import os

# Third-party
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ---- App + config
app = Flask(__name__)

# Keep secrets out of code; falls back to "dev" if env var not set.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

# SQLite file lives next to app.py for now.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carelog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ORM handle; models will subclass db.Model later.
db = SQLAlchemy(app)

# ---- Sanity route
@app.get("/")
def ping():
    return "OK"

# Dev server entry point.
if __name__ == "__main__":
    # debug=True auto reloads on code changes.
    app.run(host="127.0.0.1", port=5000, debug=True)