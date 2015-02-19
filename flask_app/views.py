from flask import render_template, jsonify, request, abort
from flask.views import MethodView
import ldap
import json

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP, Server

def get_or_404(model, id):
    rv = model.query.get(id)
    if rv is None:
        abort(404, "{} {} does not exist" % (model.__name__, str(id)))
    return rv

class HostListAPI(MethodView):

    def get(self):
        hosts = Host.query.all()
        return jsonify(dict(items=[host.config() for host in hosts]))

    def post(self):
        if set(['name','mac','group_id']) != set(request.form.keys()):
            abort(400, "Host requires name, mac, and group_id")
        host = Host(name=request.form.get('name'),
                mac=request.form.get('mac'),
                group_id=request.form.get('group_id'))
        db.session.add(host)
        db.session.commit()
        host.ldap_add()
        return jsonify(host.config())

class HostAPI(MethodView):

    def get(self, host_id):
        host = get_or_404(Host, host_id)
        return jsonify(host.config())

    def put(self, host_id):
        host = get_or_404(Host, host_id)
        # TODO: ldap_update
        if 'name' in request.form:
            host.name = request.form.get('name')
        if 'mac' in request.form:
            host.mac = request.form.get('mac')
        if 'group_id' in request.form:
            host.group_id = request.form.get('group_id')
        db.session.add(host)
        db.session.commit()
        return jsonify(host.config())

    def delete(self, host_id):
        host = get_or_404(Host, host_id)
        host.ldap_delete()
        db.session.delete(host)
        db.session.commit()
        return jsonify(dict(items=[host.config() for host in Host.query.all()]))

class GroupListAPI(MethodView):

    def get(self):
        groups = Group.query.all()
        return jsonify(dict(items=[group.config() for group in groups]))

    def post(self):
        if set(['name','server_id']) != set(request.form.keys()):
            abort(400, "Group requires name and server_id")
        group = Group(name=request.form.get('name'),
                server_id=request.form.get('server_id'))
        db.session.add(group)
        db.session.commit()
        group.ldap_add()
        return jsonify(group.config())

class GroupAPI(MethodView):

    def get(self, group_id):
        group = get_or_404(Group, group_id)
        return jsonify(group.config())

    def put(self, group_id):
        group = get_or_404(Group, group_id)
        # TODO: ldap_update
        if 'name' in request.form:
            group.name = request.form.get('name')
        if 'server_id' in request.form:
            group.server_id = request.form.get('server_id')
        db.session.add(group)
        db.session.commit()
        return jsonify(group.config())

    def delete(self, group_id):
        group = get_or_404(Group, group_id)
        for host in group.hosts.all():
            host.ldap_delete()
            db.session.delete(host)
        db.session.delete(group)
        db.session.commit()
        return jsonify(dict(items=[group.config() for group in Group.query.all()]))

@app.route('/api/servers/', methods=['GET'])
def server_list_get():
    servers = Server.query.all()
    return jsonify(dict(items=[server.config() for server in servers]))

@app.route('/api/servers/', methods=['POST'])
def server_list_post():
    if set(['hostname']) != set(request.form.keys()):
        abort(400, "Server requires hostname")
    server = Server(hostname=request.form.get('hostname'))
    db.session.add(server)
    db.session.commit()
    return jsonify(server.config())

@app.route('/api/servers/<int:server_id>', methods=['GET'])
def server_get(server_id):
    server = get_or_404(Server, server_id)
    return jsonify(server.config())

@app.route('/api/servers/<int:server_id>', methods=['PUT'])
def server_put(server_id):
    server = get_or_404(Server, server_id)
    # TODO: ldap_update
    if hostname in request.form:
        server.hostname = request.form.get('hostname')
    db.session.add(server)
    db.session.commit()
    return jsonfiy(server.config())

@app.route('/api/servers/<int:server_id>', methods=['DELETE'])
def server_delete(server_id):
    server = get_or_404(Server, server_id)
    # TODO: delete all subobjects
    db.session.delete(server)
    db.session.commit()
    return jsonify(dict(items=[server.config() for server in Server.query.all()]))

host_list_view = HostListAPI.as_view('host_list_api')
host_view = HostAPI.as_view('host_api')
group_list_view = GroupListAPI.as_view('group_list_api')
group_view = GroupAPI.as_view('group_api')

app.add_url_rule('/api/hosts/', view_func=host_list_view, methods=['GET','POST'])
app.add_url_rule('/api/hosts/<int:host_id>', view_func=host_view, methods=['GET','PUT','DELETE'])
app.add_url_rule('/api/groups/', view_func=group_list_view, methods=['GET','POST'])
app.add_url_rule('/api/groups/<int:group_id>', view_func=group_view, methods=['GET','PUT','DELETE'])

@app.route("/")
def index():
    search = str(ldap_obj.search_st('dc=dhcpawn,dc=net', ldap.SCOPE_SUBTREE))
    return render_template("index.html", search=search)
