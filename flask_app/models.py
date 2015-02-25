from .app import app, ldap_obj
from flask.ext.sqlalchemy import SQLAlchemy
import ldap

db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def dn(self):
        if self.group_id:
            return 'cn=%s,%s' % (self.name, self.group.dn())
        return 'cn=%s,ou=Hosts,%s' % (self.name, self.server.dn())

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
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def dn(self):
        return 'cn=%s,ou=Groups,%s' % (self.name, self.server.dn())

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
                hosts = [host.id for host in self.hosts.all()],
                server = self.server_id)

class Subnet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    netmask = db.Column(db.String(255))
    broadcast_address = db.Column(db.String(255))
    routers = db.Column(db.String(255))
    ips = db.relationship('IP', backref='subnet', lazy='dynamic')
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255))
    groups = db.relationship('Group', backref='server', lazy='dynamic')
    subnets = db.relationship('Subnet', backref='server', lazy='dynamic')
    hosts = db.relationship('Host', backref='server', lazy='dynamic')

    def ldap_add(self):
        pass
        #TODO: set up ldap heirarchy:
#[('dc=dhcpawn,dc=net', {'dc': ['dhcpawn'], 'objectClass': ['domain']}),
# ('cn=dhcpsrv,dc=dhcpawn,dc=net',
#  {'cn': ['dhcpsrv'],
#   'dhcpServiceDN': ['cn=DHCP Config,cn=dhcpsrv,dc=dhcpawn,dc=net'],
#   'objectClass': ['dhcpServer', 'top']}),
# ('cn=DHCP Config,cn=dhcpsrv,dc=dhcpawn,dc=net',
#  {'cn': ['DHCP Config'],
#   'dhcpPrimaryDN': ['cn=dhcpsrv,dc=dhcpawn,dc=net'],
#   'objectClass': ['dhcpOptions', 'dhcpService', 'top']}),
# ('ou=Groups,cn=DHCP Config,cn=dhcpsrv,dc=dhcpawn,dc=net',
#  {'objectClass': ['organizationalUnit', 'top'], 'ou': ['Groups']}),
# ('ou=Subnets,cn=DHCP Config,cn=dhcpsrv,dc=dhcpawn,dc=net',
#  {'objectClass': ['organizationalUnit', 'top'], 'ou': ['Groups', 'Subnets']}),
# ('ou=Hosts,cn=DHCP Config,cn=dhcpsrv,dc=dhcpawn,dc=net',
#  {'objectClass': ['organizationalUnit', 'top'], 'ou': ['Groups', 'Hosts']})]

    def dn(self):
        return 'cn=DHCP Config,cn=dhcpsrv,dc=%s,dc=%s' % (self.hostname.split('.')[0], self.hostname.split('.')[1])

    def config(self):
        return dict(id = self.id,
                hostname = self.hostname,
                groups = [group.id for group in self.groups.all()],
                subnets = [subnet.id for subnet in self.subnets.all()])

