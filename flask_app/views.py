from flask import render_template
import ldap

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP, Server
from flask.ext.restless import APIManager

api_manager = APIManager(app, flask_sqlalchemy_db=db)

api_manager.create_api(Host, methods=['GET','POST','DELETE'])
api_manager.create_api(Group, methods=['GET','POST','DELETE'])
api_manager.create_api(Subnet, methods=['GET','POST','DELETE'])
api_manager.create_api(IP, methods=['GET','POST','DELETE'])
api_manager.create_api(Server, methods=['GET','POST','DELETE'])

@app.route("/")
def index():
    search = str(ldap_obj.search_st('dc=dhcpawn,dc=net', ldap.SCOPE_SUBTREE))
    return render_template("index.html", search=search)
