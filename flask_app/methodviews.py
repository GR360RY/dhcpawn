from flask import jsonify, request, abort
from flask.views import MethodView
from ipaddr import IPv4Address, IPv4Network
import json

from .app import app, ldap_obj
from .models import db, Host, Group, Subnet, IP, Range, Pool

def get_or_404(model, id):
    rv = model.query.get(id)
    if rv is None:
        abort(404, "%s %s does not exist" % (model.__name__, str(id)))
    return rv

def _get_or_none(model, id):
    if id:
        return model.query.get(id)
    return None

class HostListAPI(MethodView):

    def get(self):
        hosts = Host.query.all()
        return jsonify(dict(items=[host.config() for host in hosts]))

    def post(self):
        data = request.get_json(force=True)
        if any(key not in data for key in ['name','mac']):
            abort(400, "Host requires name and mac")
        if Host.query.filter(Host.mac==data.get('mac')).all():
            abort(400, "A host with this MAC already exists")
        host = Host(name=data.get('name'),
                mac=data.get('mac'),
                group_id=data.get('group'),
                options=json.dumps(data.get('options',{})))
        deployable = True
        if host.group_id:
            group = get_or_404(Group, host.group_id)
            deployable = group.deployed
        host.deployed = data.get('deployed',True)
        if 'deployed' in data:
            if data.get('deployed') and not deployable:
                abort(400, "Cannot deploy host as subobject of non-deployed group")
        else:
            if not deployable:
                host.deployed = False
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
        data = request.get_json(force=True)
        if 'deployed' in data:
            deployed = data.get('deployed',True)
            if deployed and host.group_id:
                group = get_or_404(Group, host.group_id)
                if not group.deployed:
                    abort(400, "Cannot deploy host as subobject of non-deployed group")
        host.ldap_delete()
        if 'name' in data:
            host.name = data.get('name')
        if 'mac' in data:
            host.mac = data.get('mac')
        if 'group' in data:
            host.group_id = data.get('group')
        if 'options' in data:
            host.options = json.dumps(data.get('options'))
        if 'deployed' in data:
            host.deployed = data.get('deployed',True)
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
        data = request.get_json(force=True)
        if any(key not in data for key in ['name']):
            abort(400, "Group requires name")
        group = Group(name=data.get('name'),
                options=json.dumps(data.get('options',{})),
                deployed=data.get('deployed'))
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
        data = request.get_json(force=True)
        for host in group.hosts.all():
            host.ldap_delete()
        group.ldap_delete()
        if 'name' in data:
            group.name = data.get('name')
        if 'options' in data:
            group.options = json.dumps(data.get('options'))
        if 'deployed' in data:
            group.deployed = data.get('deployed')
            if not group.deployed:
                for host in group.hosts.all():
                    host.deployed = False
                    db.session.add(host)
        db.session.add(group)
        db.session.commit()
        group.ldap_add()
        if group.deployed:
            for host in group.hosts.all():
                host.ldap_add()
        return jsonify(group.config())

    def delete(self, group_id):
        group = get_or_404(Group, group_id)
        hosts = []
        for host in group.hosts.all():
            host.ldap_delete()
            host.group_id = None
            hosts.append(host)
            db.session.add(host)
        group.ldap_delete()
        db.session.delete(group)
        db.session.commit()
        for host in hosts:
            host.ldap_add()
        return jsonify(dict(items=[group.config() for group in Group.query.all()]))

class SubnetListAPI(MethodView):

    def get(self):
        subnets = Subnet.query.all()
        return jsonify(dict(items=[subnet.config() for subnet in subnets]))

    def post(self):
        data = request.get_json(force=True)
        if any(key not in data for key in ['name','netmask']):
            abort(400, "Subnet requires name and netmask")
        subnet = Subnet(name=data.get('name'),
                netmask=data.get('netmask'),
                options=json.dumps(data.get('options',{})),
                deployed=data.get('deployed'))
        db.session.add(subnet)
        db.session.commit()
        subnet.ldap_add()
        return jsonify(subnet.config())

class SubnetAPI(MethodView):

    def get(self, subnet_id):
        subnet = get_or_404(Subnet, subnet_id)
        return jsonify(subnet.config())

    def put(self, subnet_id):
        subnet = get_or_404(Subnet, subnet_id)
        data = request.get_json(force=True)
        if 'netmask' in data:
            subnet.netmask = data.get('netmask')
        if 'options' in data:
            subnet.options = json.dumps(data.get('options'))
        if 'deployed' in data:
            subnet.deployed = data.get('deployed')
        db.session.add(subnet)
        db.session.commit()
        if subnet.deployed:
            subnet.ldap_modify()
        else:
            subnet.deployed = True
            for pool in subnet.pools.all():
                pool.ldap_delete()
                pool.deployed = False
                db.session.add(pool)
            for ip in subnet.ips.all():
                ip.ldap_delete()
                ip.deployed = False
                db.session.add(ip)
            if subnet.range:
                subnet.range.deployed = False
                db.session.add(subnet)
            # manually delete, as deployed is False
            ldap_obj.delete_s(subnet.dn())
            db.session.commit()
        return jsonify(subnet.config())

    def delete(self, subnet_id):
        subnet = get_or_404(Subnet, subnet_id)
        for pool in subnet.pools.all():
            pool.ldap_delete()
            if pool.range:
                db.session.delete(pool.range)
            db.session.delete(pool)
        for ip in subnet.ips.all():
            db.session.delete(ip)
        if subnet.range:
            db.session.delete(subnet.range)
        db.session.commit()
        subnet.ldap_delete()
        db.session.delete(subnet)
        db.session.commit()
        return jsonify(dict(items=[subnet.config() for subnet in Subnet.query.all()]))

class IPListAPI(MethodView):

    def get(self):
        ips = IP.query.all()
        return jsonify(dict(items=[ip.config() for ip in ips]))

    def post(self):
        data = request.get_json(force=True)
        if all(key not in data for key in ['address','range']):
            abort(400, "IP requires address or range")
        address = data.get('address')
        existing_ips = IP.query.filter(IP.address==address).all()
        if existing_ips:
            abort(400, "This IP address is already allocated")
        range_id = data.get('range')
        if range_id:
            iprange = get_or_404(Range, range_id)
            if iprange.type == 'dynamic':
                abort(400, "Provided dynamic range, and IPs cannot be allocated in a dynamic range")
            if address:
                if not iprange.contains(IPv4Address(data.get('address'))):
                    abort(400, "IP address not in provided range")
            else:
                address = iprange.free_ips(1)[0].compressed
        else:
            ip = IPv4Address(address)
            for iprange in Range.query.all():
                if iprange.contains(ip):
                    if iprange.type == 'dynamic':
                        abort(400, "IP address conflicts with dynamic range %s" % (iprange.id))
                    if iprange.type == 'static':
                        if range_id:
                            abort(400, "Both ranges %s and %s contain IP" % (range_id, iprange.id))
                        range_id = iprange.id
        ip = IP(address=address,
                subnet_id=data.get('subnet'),
                range_id=range_id,
                host_id=data.get('host'))
        deployable = True
        if ip.subnet_id:
            subnet = get_or_404(Subnet, ip.subnet_id)
            if not subnet.deployed:
                deployable = False
        if ip.range_id:
            range = get_or_404(Range, ip.range_id)
            if not range.deployed:
                deployable = False
        if ip.host_id:
            host = get_or_404(Host, ip.host_id)
            if not host.deployed:
                deployable = False
        ip.deployed = data.get('deployed', True)
        if 'deployed' in data:
            if ip.deployed and not deployable:
                abort(400, "Cannot deploy IP in non-deployed host, subnet, or range")
        else:
            if not deployable:
                ip.deployed = False
        db.session.add(ip)
        db.session.commit()
        ip.ldap_add()
        return jsonify(ip.config())

class IPAPI(MethodView):

    def get(self, ip_id):
        ip = get_or_404(IP, ip_id)
        return jsonify(ip.config())

    def put(self, ip_id):
        ip = get_or_404(IP, ip_id)
        data = request.get_json(force=True)
        if data.get('address') or data.get('range'):
            abort(400, "IP POST requests only accept host and subnet IDs")
        if 'deployed' in data:
            deployed = data.get('deployed')
            if deployed:
                if ip.host_id:
                    host = get_or_404(Host, ip.host_id)
                    if not host.deployed:
                        abort(400, "Cannot deploy IP as parameter of non-deployed host")
                if ip.subnet_id:
                    subnet = get_or_404(Subnet, ip.subnet_id)
                    if not subnet.deployed:
                        abort(400, "Cannot deploy IP as part of non-deployed subnet")
                if ip.range_id:
                    ip_range = get_or_404(Range, ip.range_id)
                    if not ip_range.deployed:
                        abort(400, "Cannot deploy IP as part of non-deployed IP range")
        ip.ldap_delete()
        if 'host' in data:
            ip.host_id = data.get('host')
        if 'subnet' in data:
            ip.subnet_id = data.get('subnet')
        if 'deployed' in data:
            ip.deployed = data.get('deployed')
        db.session.add(ip)
        db.session.commit()
        ip.ldap_add()
        return jsonify(ip.config())

    def delete(self, ip_id):
        ip = get_or_404(IP, ip_id)
        db.session.delete(ip)
        db.session.commit()
        return jsonify(dict(items=[ip.config() for ip in IP.query.all()]))

class RangeListAPI(MethodView):

    def get(self):
        ranges = Range.query.all()
        return jsonify(dict(items=[range.config() for range in ranges]))

    def post(self):
        data = request.get_json(force=True)
        if any(key not in data for key in ['type','min','max']):
            abort(400, "Range requires a type, min, and max")
        ipmin = IPv4Address(data.get('min'))
        ipmax = IPv4Address(data.get('max'))
        rangetype = data.get('type')
        for iprange in Range.query.all():
            if iprange.contains(ipmin) or iprange.contains(ipmax):
                abort(400, "Range overlaps with existing ranges %s" % (iprange.id))
        range_ips = []
        for ip in IP.query.all():
            if ip.address >= ipmin and ip.address <= ipmax:
                if rangetype == 'dynamic':
                    abort(400, "Allocated IP %s within this dynamic range" % (ip.address.compressed))
                if rangetype == 'static':
                    if ip.range_id:
                        abort(400, "Allocated IP %s within this range, but is in range %s" % (
                            ip.address.compressed, ip.range_id))
                    range_ips.append(ip)
        ip_range = Range(type=rangetype,
                min=data.get('min'),
                max=data.get('max'),
                subnet=_get_or_none(Subnet,data.get('subnet')),
                pool=_get_or_none(Pool,data.get('pool')))
        deployable = True
        if ip_range.subnet:
            if not (ip_range.subnet.contains(ipmin) and ip_range.subnet.contains(ipmax)):
                abort(400, "This range %s - %s is not contained in the subnet %s/%d" %
                        (ip_range.min, ip_range.max, ip_range.subnet.name, ip_range.subnet.netmask))
            if not ip_range.subnet.deployed:
                deployable = False
        if ip_range.pool:
            if ip_range.pool.subnet_id:
                subnet = get_or_404(Subnet, ip_range.pool.subnet_id)
                if not (ip_range.subnet.contains(ipmin) and ip_range.subnet.contains(ipmax)):
                    abort(400, "This range %s - %s is not contained in the subnet %s/%d" %
                            (ip_range.min, ip_range.max, ip_range.subnet.name, ip_range.subnet.netmask))
            if not ip_range.pool.deployed:
                deployable = False
        ip_range.deployed = data.get('deployed',True)
        if 'deployed' in data:
            if ip_range.deployed and not deployable:
                abort(400, "Cannot deploy IP range as part of non-deployed subnet or pool")
        else:
            if not deployable:
                ip_range.deployed = False
        db.session.add(ip_range)
        db.session.commit()
        for ip in range_ips:
            ip.range = ip_range
            db.session.add(ip)
        db.session.commit()
        ip_range.ldap_add()
        return jsonify(ip_range.config())

class RangeAPI(MethodView):

    def get(self, range_id):
        ip_range = get_or_404(Range, range_id)
        return jsonify(ip_range.config())

    def put(self, range_id):
        ip_range = get_or_404(Range, range_id)
        data = request.get_json(force=True)
        if 'deployed' in data:
            deployed = data.get('deployed')
            if deployed:
                if ip_range.pool:
                    if not ip_range.pool.deployed:
                        abort(400, "Cannot deploy IP range as parameter of non-deployed pool")
                if ip_range.subnet:
                    if not ip_range.subnet.deployed:
                        abort(400, "Cannot deploy IP range as part of non-deployed subnet")
            if not deployed:
                if ip_range.pool:
                    if ip_range.pool.deployed:
                        abort(400, "Cannot revoke IP range as parameter of deployed pool")
        ip_range.ldap_delete()
        if 'type' in data:
            ip_range.type = data.get('type')
        if 'subnet' in data:
            ip_range.subnet = _get_or_none(Subnet,data.get('subnet'))
        if 'pool' in data:
            ip_range.pool = _get_or_none(Pool,data.get('pool'))
        if 'deployed' in data:
            ip_range.deployed = data.get('deployed')
        db.session.add(ip_range)
        db.session.commit()
        ip_range.ldap_add()
        return jsonify(ip_range.config())

    def delete(self, range_id):
        ip_range = get_or_404(Range, range_id)
        if ip_range.pool and ip_range.pool.deployed:
            abort(400, "Cannot delete range of deployed pool")
        ip_range.ldap_delete()
        db.session.delete(ip_range)
        db.session.commit()
        return jsonify(dict(items=[ip_range.config() for ip_range in Range.query.all()]))

class PoolListAPI(MethodView):

    def get(self):
        pools = Pool.query.all()
        return jsonify(dict(items=[pool.config() for pool in pools]))

    def post(self):
        data = request.get_json(force=True)
        if any(key not in data for key in ['name','subnet','range']):
            abort(400, "Pool requires name, subnet, and range")
        pool = Pool(name=data.get('name'),
                subnet_id=data.get('subnet'),
                range_id=data.get('range'),
                options=json.dumps(data.get('options', {})))
        deployable = True
        subnet = get_or_404(Subnet, pool.subnet_id)
        if not subnet.deployed:
            deployable = False
        ip_range = get_or_404(Range, pool.range_id)
        if not ip_range.deployed:
            deployable = False
        if not (subnet.contains(ip_range.min) and subnet.contains(ip_range.max)):
            abort(400, "This pool range %s - %s is not contained in the subnet %s/%d" %
                            (ip_range.min, ip_range.max, subnet.name, subnet.netmask))
        pool.deployed = data.get('deployed', True)
        if 'deployed' in data:
            if pool.deployed and not deployable:
                abort(400, "Cannot deploy pool with non-deployed IP range or subnet")
        else:
            if not deployable:
                pool.deployed = False
        db.session.add(pool)
        db.session.commit()
        pool.ldap_add()
        return jsonify(pool.config())

class PoolAPI(MethodView):

    def get(self, pool_id):
        pool = get_or_404(Pool, pool_id)
        return jsonify(pool.config())

    def put(self, pool_id):
        pool = get_or_404(Pool, pool_id)
        data = request.get_json(force=True)
        if 'deployed' in data:
            deployed = data.get('deployed')
            if deployed:
                if pool.subnet_id:
                    subnet = get_or_404(Subnet, pool.subnet_id)
                    if not subnet.deployed:
                        abort(400, "Cannot deploy pool with non-deployed subnet")
        pool.ldap_delete()
        if 'name' in data:
            pool.name = data.get('name')
        if 'subnet' in data:
            pool.subnet_id = data.get('subnet')
        if 'range' in data:
            pool.range_id = data.get('range')
        if 'options' in data:
            pool.options = json.dumps(data.get('options'))
        if 'deployed' in data:
            pool.deployed = data.get('deployed')
            if pool.range_id:
                ip_range = get_or_404(Range, pool.range_id)
                ip_range.deployed = pool.deployed
                db.session.add(ip_range)
        db.session.add(pool)
        db.session.commit()
        pool.ldap_add()
        return jsonify(pool.config())

    def delete(self, pool_id):
        pool = get_or_404(Pool, pool_id)
        pool.ldap_delete()
        if pool.range:
            db.session.delete(pool.range)
        db.session.delete(pool)
        db.session.commit()
        return jsonify([pool.config() for pool in Pool.query.all()])
