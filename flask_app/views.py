from flask import render_template, jsonify, request, abort
from flask.views import MethodView
import ldap

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP
from . import methodviews as mv

app.add_url_rule('/api/hosts/', view_func=mv.HostListAPI.as_view('host_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/hosts/<int:host_id>', view_func=mv.HostAPI.as_view('host_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/groups/', view_func=mv.GroupListAPI.as_view('group_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/groups/<int:group_id>', view_func=mv.GroupAPI.as_view('group_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/subnets/', view_func=mv.SubnetListAPI.as_view('subnet_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/subnets/<int:subnet_id>', view_func=mv.SubnetAPI.as_view('subnet_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/ips/', view_func=mv.IPListAPI.as_view('ip_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/ips/<int:ip_id>', view_func=mv.IPAPI.as_view('ip_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/ranges/', view_func=mv.RangeListAPI.as_view('range_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/ranges/<int:range_id>', view_func=mv.RangeAPI.as_view('range_api'),
        methods=['GET','PUT','DELETE'])

app.add_url_rule('/api/pools/', view_func=mv.PoolListAPI.as_view('pool_list_api'),
        methods=['GET','POST'])

app.add_url_rule('/api/pools/<int:pool_id>', view_func=mv.PoolAPI.as_view('pool_api'),
        methods=['GET','PUT','DELETE'])


@app.route("/")
def index():
    search = str(ldap_obj.search_st('dc=dhcpawn,dc=net', ldap.SCOPE_SUBTREE))
    return render_template("index.html", search=search)
