from flask import render_template, jsonify, request, abort
from flask.views import MethodView
import ldap
import subprocess

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP, Range, Pool
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

@app.route("/api/ranges/<int:range_id>/allocate/", methods=['PUT'])
def allocate(range_id):
    iprange = mv.get_or_404(Range, range_id)
    data = request.get_json(force=True)
    if not data.get('number'):
        abort(400, "Allocation requires number of IPs")
    ips = iprange.free_ips(int(data.get('number')))
    if not ips:
        abort(400, "Too many addresses requested")
    for ip in ips:
        ip_obj = IP(address = ip.compressed,
                range_id = iprange.id)
        db.session.add(ip_obj)
    db.session.commit()
    return jsonify(iprange.config())

@app.route("/api/status/", methods=['GET'])
def status():
    # return information about the server status
    # service slapd status
    services = {'isc-dhcp-server':'', 'slapd':''}
    for service in services:
        try:
            output = subprocess.check_output(['service',service,'status'])
            if 'running' in output:
                services[service] = dict(state='R', output='')
            else:
                # TODO: find more details in /var/log/syslog
                services[service] = dict(state='E', output=output)
        except (subprocess.CalledProcessError, OSError) as e:
            services[service] = dict(state='E', output=str(e))
    return jsonify(services)
