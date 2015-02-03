from flask import render_template
import sys
import ldap

from .app import app, ldap_obj

@app.route("/")
def index():
    whoami = ldap_obj.whoami_s()
    return render_template("index.html", version=sys.version)
