from flask import render_template

def init_medication_routes(app):
    @app.get("/medication")
    def medication_list():
        # Placeholder page
        return render_template("medication_list.html")