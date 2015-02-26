from flask import render_template, jsonify, request, abort
from flask.views import MethodView
import ldap

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP
from .methodviews import HostListAPI, HostAPI, GroupListAPI, GroupAPI

app.add_url_rule('/api/hosts/', view_func=HostListAPI.as_view('host_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/hosts/<int:host_id>', view_func=HostAPI.as_view('host_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/groups/', view_func=GroupListAPI.as_view('group_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/groups/<int:group_id>', view_func=GroupAPI.as_view('group_api'),
        methods=['GET','PUT','DELETE'])

@app.route("/")
def index():
    search = str(ldap_obj.search_st('dc=dhcpawn,dc=net', ldap.SCOPE_SUBTREE))
    return render_template("index.html", search=search)
