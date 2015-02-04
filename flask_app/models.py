from .app import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mac = db.Column(db.String(100), unique=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    hosts = db.relationship('Host', backref='group', lazy='dynamic')
    server_id = db.Column(db.Integer, db.ForeignKey('dhcpserver.id'))

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
