from .app import app, ldap_obj
from .ldap_utils import server_dn
from flask.ext.sqlalchemy import SQLAlchemy
import ldap

db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def dn(self):
        if self.group_id:
            return 'cn=%s,%s' % (self.name, self.group.dn())
        return 'cn=%s,ou=Hosts,%s' % (self.name, server_dn())

    def ldap_add(self):
        modlist = [('objectClass',['dhcpHost','top']),
                ('dhcpHWAddress','ethernet %s' % str(self.mac)),
                ('cn',str(self.name))]
        ldap_obj.add_s(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete_s(self.dn())

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                mac = self.mac,
                group = self.group_id)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    hosts = db.relationship('Host', backref='group', lazy='dynamic')

    def dn(self):
        return 'cn=%s,ou=Groups,%s' % (self.name, server_dn())

    def ldap_add(self):
        modlist = [('objectClass', ['dhcpGroup', 'top']),
                ('cn',str(self.name))]
        ldap_obj.add_s(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete_s(self.dn())

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                hosts = [host.id for host in self.hosts.all()])

class Subnet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    netmask = db.Column(db.String(255))
    broadcast_address = db.Column(db.String(255))
    routers = db.Column(db.String(255))
    ips = db.relationship('IP', backref='subnet', lazy='dynamic')

class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))
