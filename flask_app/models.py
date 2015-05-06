from .app import app, ldap_obj
from .ldap_utils import server_dn
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy_utils import IPAddressType
import ldap
import ldap.modlist
import json
from ipaddr import IPAddress

db = SQLAlchemy(app)

def gen_modlist(obj_dict, options):
    if options:
        options = json.loads(options)
        for option in options:
            options[option] = [str(o) for o in options[option]]
        obj_dict.update(options)
    return obj_dict

class LDAPModel(db.Model):
    __abstract__ = True

    def dn(self):
        return ''

    def modlist(self):
        return dict()

    def ldap_add(self):
        if self.deployed:
            ldap_obj.add_s(self.dn(), ldap.modlist.addModlist(self.modlist()))

    def ldap_modify(self):
        if self.deployed:
            try:
                objs = ldap_obj.search_s(self.dn(), ldap.SCOPE_BASE)
                if objs[0][1] != dict(self.modlist()):
                    ldap_obj.modify_s(self.dn(), ldap.modlist.modifyModlist(objs[0][1], dict(self.modlist())))
            except ldap.NO_SUCH_OBJECT:
                self.ldap_add()

    def ldap_delete(self):
        if self.deployed:
            ldap_obj.delete_s(self.dn())

class Host(LDAPModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    ip = db.relationship('IP', backref='host', uselist=False)
    options = db.Column(db.Text)
    deployed = db.Column(db.Boolean, default=True)

    def dn(self):
        if self.group_id:
            return 'cn=%s,%s' % (self.name, self.group.dn())
        return 'cn=%s,ou=Hosts,%s' % (self.name, server_dn())

    def modlist(self):
        options = self.options
        if self.ip and self.ip.deployed:
            options = json.loads(self.options) if self.options else {}
            if not options.get('dhcpStatements'):
                options['dhcpStatements'] = []
            options['dhcpStatements'] += ['fixed-address %s' % (self.ip.address)]
            options = json.dumps(options)
        return gen_modlist(dict(objectClass=['dhcpHost','top'],
                dhcpHWAddress=['ethernet %s' % str(self.mac)],
                cn=str(self.name)), options)

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                mac = self.mac,
                group = self.group_id,
                options = json.loads(self.options) if self.options else None,
                deployed = self.deployed)

class Group(LDAPModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    hosts = db.relationship('Host', backref='group', lazy='dynamic')
    options = db.Column(db.Text)
    deployed = db.Column(db.Boolean, default=True)

    def dn(self):
        return 'cn=%s,ou=Groups,%s' % (self.name, server_dn())

    def modlist(self):
        return gen_modlist(dict(objectClass=['dhcpGroup', 'top'],
                cn=str(self.name)), self.options)

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                hosts = [host.id for host in self.hosts.all()],
                options = json.loads(self.options) if self.options else None,
                deployed = self.deployed)

class Subnet(LDAPModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    netmask = db.Column(db.Integer)
    options = db.Column(db.Text)
    ips = db.relationship('IP', backref='subnet', lazy='dynamic')
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    pools = db.relationship('Pool', backref='subnet', lazy='dynamic')
    deployed = db.Column(db.Boolean, default=True)

    def dn(self):
        return 'cn=%s,ou=Subnets,%s' % (self.name, server_dn())

    def modlist(self):
        mod_dict = dict(objectClass=['dhcpSubnet', 'top'],
                cn=str(self.name),
                dhcpNetMask=str(self.netmask))
        if self.range and self.range.deployed:
            mod_dict.update(dict(dhcpRange=[str('range %s %s' % (self.range.min, self.range.max))]))
        return gen_modlist(mod_dict, self.options)

    def config(self):
        return dict(id = self.id,
                dn = self.dn(),
                name = self.name,
                netmask = self.netmask,
                options = json.loads(self.options) if self.options else None,
                range = self.range_id,
                ips = [ip.id for ip in self.ips.all()],
                pools = [pool.id for pool in self.pools.all()],
                deployed = self.deployed)

class IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(IPAddressType)
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))
    deployed = db.Column(db.Boolean, default=True)

    def ldap_add(self):
        if self.host and self.deployed:
            self.host.ldap_modify()

    def ldap_delete(self):
        if self.host and self.deployed:
            host = self.host
            host.ip = None
            db.session.add(host)
            db.session.commit()
            host.ldap_modify()

    def config(self):
        return dict(id = self.id,
                address = self.address.compressed,
                subnet = self.subnet_id,
                range = self.range_id,
                host = self.host_id)

class Range(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255))
    min = db.Column(IPAddressType)
    max = db.Column(IPAddressType)
    subnet = db.relationship('Subnet', backref='range', uselist=False)
    pool = db.relationship('Pool', backref='range', uselist=False)
    ips = db.relationship('IP', backref='range')
    deployed = db.Column(db.Boolean, default=True)

    def ldap_add(self):
        if self.type == 'dynamic' and self.subnet and self.deployed:
            self.subnet.ldap_modify()

    def ldap_delete(self):
        if self.type == 'dynamic' and self.subnet and self.deployed:
            subnet = self.subnet
            subnet.ip = None
            db.session.add(subnet)
            db.session.commit()
            subnet.ldap_modify()

    def free_ips(self, num=1):
        # return the first IP address in the range, from the top, without conflict
        top = self.max+1
        addresses = []
        ips = [ip.address for ip in self.ips]
        ips.sort(reverse=True)
        ips = [self.max+1] + ips + [self.min-1]
        i = 0
        j = 0
        for ip in ips:
            while i < num:
                ip_j = top-j
                j+=1
                if ip_j < self.min:
                    return []
                if ip >= ip_j:
                    break
                addresses.append(ip_j)
                i+=1
            if i == num:
                break
        return addresses

    def contains(self, ip):
        return ip >= self.min and ip <= self.max

    def config(self):
        return dict(id = self.id,
                type = self.type,
                min = self.min.compressed,
                max = self.max.compressed,
                ips = [ip.id for ip in self.ips],
                subnet = self.subnet.id if self.subnet else None,
                pool = self.pool.id if self.pool else None,
                deployed = self.deployed)

class Pool(LDAPModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnet.id'))
    range_id = db.Column(db.Integer, db.ForeignKey('range.id'))
    options = db.Column(db.Text)
    deployed = db.Column(db.Boolean, default=True)

    def dn(self):
        return 'cn=%s,%s' % (self.name, self.subnet.dn())

    def modlist(self):
        # range is required
        mod_dict = dict(objectClass=['dhcpPool', 'top'],
                cn=str(self.name),
                dhcpRange=[str('range %s %s' % (self.range.min, self.range.max))])
        return gen_modlist(mod_dict, self.options)

    def config(self):
        return dict(id = self.id,
                name = self.name,
                subnet = self.subnet.id,
                range = self.range.id,
                options = self.options,
                deployed = self.deployed)
