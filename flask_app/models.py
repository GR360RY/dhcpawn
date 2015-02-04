from .app import app, ldap_obj
from flask.ext.sqlalchemy import SQLAlchemy
import ldap

db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def dn(self):
        return 'cn=%s,%s' % (self.name, self.group.dn())

    def ldap_add(self):
        modlist = [('dhcpHWAddress','ethernet %s' % (self.mac))]
        ldap_obj.add(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete(self.dn())

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    hosts = db.relationship('Host', backref='group', lazy='dynamic')
    server_id = db.Column(db.Integer, db.ForeignKey('dhcpserver.id'))

    def dn(self):
        return 'cn=%s,%s' % (self.name, self.server.dn())

    def ldap_add(self):
        modlist = [('objectClass', ['organizationalUnit', 'top']),('ou',['Groups'])]
        ldap_obj.add(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete(self.dn())

class Subnet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    netmask = db.Column(db.String(255))
    broadcast_address = db.Column(db.String(255))
    routers = db.Column(db.String(255))
    ips = db.relationship('IP', backref='subnet', lazy='dynamic')
    server_id = db.Column(db.Integer, db.ForeignKey('dhcpserver.id'))

class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))

class DHCPServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255))
    groups = db.relationship('Group', backref='server', lazy='dynamic')
    subnets = db.relationship('Subnet', backref='server', lazy='dynamic')

    def dn(self):
        return 'dc=%s,dc=%s' % (self.hostname.split('.')[0], self.hostname.split('.')[1])
