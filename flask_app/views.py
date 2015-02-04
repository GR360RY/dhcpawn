from flask import render_template
import ldap

from .app import app, ldap_obj

@app.route("/")
def index():
    search = str(ldap_obj.search_st('dc=dhcpawn,dc=net', ldap.SCOPE_SUBTREE))
    return render_template("index.html", search=search)
