from .app import app, ldap_obj
from .ldap_utils import server_dn
from flask.ext.sqlalchemy import SQLAlchemy
import ldap
from ipaddr import IPAddress

db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    ip = db.relationship('IP', backref='group', uselist=False)
    options = db.Column(db.Text)

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
    options = db.Column(db.Text)

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
    netmask = db.Column(db.Integer)
    deployed = db.Column(db.Boolean,default=False)
    options = db.Column(db.Text)
    ips = db.relationship('IP', backref='subnet', lazy='dynamic')
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    pools = db.relationship('Pool', backref='subnet', lazy='dynamic')

    def dn(self):
        return 'cn=%s,ou=Subnets,%s' % (self.name, server_dn())

    def ldap_add(self):
        modlist = [('objectClass', ['dhcpSubnet', 'top']),
                ('cn', str(self.name)),
                ('dhcpNetmask', str(self.netmask))]
        ldap_obj.add_s(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete_s(self.dn())

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                netmask = self.netmask,
                deployed = self.deployed,
                options = self.options,
                range = self.range_id,
                ips = [ip.id for ip in self.ips.all()],
                pools = [pool.id for pool in self.pools.all()])

class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))

    def ldap_add(self):
        # TODO
        pass

    def ldap_delete(self):
        # TODO
        pass

    def config(self):
        return dict(id = self.id,
                address = self.address,
                subnet = self.subnet_id,
                range = self.range_id,
                host = self.host_id)

    def as_ip(self):
        return IPAddress(self.address)

class Range(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    min = db.Column(db.String(255))
    max = db.Column(db.String(255))
    subnet = db.relationship('Subnet', backref='range', uselist=False)
    pool = db.relationship('Pool', backref='range', uselist=False)

    def ldap_add(self):
        if self.type == 'dynamic':
            # TODO
            pass

    def ldap_delete(self):
        if self.type == 'dynamic':
            # TODO
            pass

    def config(self):
        return dict(id = self.id,
                type = self.type,
                min = self.min,
                max = self.max,
                subnet = self.subnet.id if self.subnet else None,
                pool = self.pool.id if self.pool else None)

class Pool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    options = db.Column(db.Text)

    def dn(self):
        return 'cn=%s,%s' % (self.name, self.subnet.dn())

    def ldap_add(self):
        modlist = [('objectClass',['dhcpPool','top']),
                ('cn', str(self.name)),
                ('dhcpRange', str('%s %s' % (self.range.min, self.range.max)))]
        ldap_obj.add_s(self.dn(), modlist)

    def ldap_delete(self):
        ldap_obj.delete_s(self.dn())

    def config(self):
        return dict(id = self.id,
                name = self.name,
                subnet = self.subnet.id,
                range = self.range.id,
                options = self.options)


