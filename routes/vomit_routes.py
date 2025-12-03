from flask import render_template

def init_vomit_routes(app):
    @app.get("/vomit")
    def vomit_list():
        # Placeholder page
        return render_template("vomit_list.html")