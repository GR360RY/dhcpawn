from flask import jsonify, request, abort
from flask.views import MethodView

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP, Server

def get_or_404(model, id):
    rv = model.query.get(id)
    if rv is None:
        abort(404, "%s %s does not exist" % (model.__name__, str(id)))
    return rv

class HostListAPI(MethodView):

    def get(self):
        hosts = Host.query.all()
        return jsonify(dict(items=[host.config() for host in hosts]))

    def post(self):
        if set(['name','mac','server_id']) > set(request.form.keys()):
            abort(400, "Host requires name, mac, and server_id")
        host = Host(name=request.form.get('name'),
                mac=request.form.get('mac'),
                group_id=request.form.get('group_id'),
                server_id=request.form.get('server_id'))
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
        host.ldap_delete()
        if 'name' in request.form:
            host.name = request.form.get('name')
        if 'mac' in request.form:
            host.mac = request.form.get('mac')
        if 'group_id' in request.form:
            host.group_id = request.form.get('group_id')
        if 'server_id' in request.form:
            host.server_id = request.form.get('server_id')
        db.session.add(host)
        db.session.commit()
        host.ldap_add()
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
        if 'name' in request.form:
            group.name = request.form.get('name')
        if 'server_id' in request.form:
            # update all hosts in group
            group.server_id = request.form.get('server_id')
        db.session.add(group)
        db.session.commit()
        return jsonify(group.config())

    def delete(self, group_id):
        group = get_or_404(Group, group_id)
        for host in group.hosts.all():
            host.ldap_delete()
            host.group_id = None
            db.session.add(host)
        db.session.delete(group)
        db.session.commit()
        return jsonify(dict(items=[group.config() for group in Group.query.all()]))

class ServerListAPI(MethodView):
    def get(self):
        servers = Server.query.all()
        return jsonify(dict(items=[server.config() for server in servers]))

    def post(self):
        if set(['hostname']) != set(request.form.keys()):
            abort(400, "Server requires hostname")
        server = Server(hostname=request.form.get('hostname'))
        db.session.add(server)
        db.session.commit()
        return jsonify(server.config())

class ServerAPI(MethodView):

    def get(self, server_id):
        server = get_or_404(Server, server_id)
        return jsonify(server.config())

    def put(self, server_id):
        server = get_or_404(Server, server_id)
        # TODO: ldap_update
        if hostname in request.form:
            server.hostname = request.form.get('hostname')
        db.session.add(server)
        db.session.commit()
        return jsonfiy(server.config())
