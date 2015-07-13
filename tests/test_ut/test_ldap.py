import ldap
import requests
import pytest
import json
from .utils import _server_dn, _ldap_init

def test_create_host(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert 'dhcpHost' in ldap_hosts[0][1]['objectClass']

def test_delete_host(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.delete('/api/hosts/1')
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_duplicate_mac(webapp):
    # check for error
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_01','mac':'08:00:27:26:7a:e7'}))

def test_update_host(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/hosts/1', data=json.dumps({'mac':'08:00:27:26:7a:e8',
        'options':{'dhcpStatements': ['default-lease-time 120'], 'dhcpOption': ['routers 10.0.0.254']}}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e8']
    assert ldap_hosts[0][1]['dhcpStatements'] == ['default-lease-time 120']

def test_create_group(webapp):
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_00'}))
    ldap_obj = _ldap_init(webapp)
    ldap_groups = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_groups) == 1
    assert ldap_groups[0][1]['cn'] == ['test_group_00']

def test_move_host(webapp):
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_00'}))
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_01'}))
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/hosts/1', data=json.dumps({'group':2}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_01,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']

def test_rename_group(webapp):
    # check that contained hosts are updated
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_00'}))
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/groups/1', data=json.dumps({'name':'test_group_01'}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_01,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']

def test_delete_group(webapp):
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_00'}))
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    webapp.delete('/api/groups/1')
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_hosts = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_create_subnet(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22,
        'options':{'dhcpStatements': ['default-lease-time 240'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_subnets) == 1
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    assert 'dhcpSubnet' in ldap_subnets[0][1]['objectClass']
    assert ldap_subnets[0][1]['dhcpNetMask'] == ['22']
    assert 'routers 10.0.0.254' in ldap_subnets[0][1]['dhcpOption']
    assert ldap_subnets[0][1]['dhcpStatements'] == ['default-lease-time 240']

def test_update_subnet(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22,
        'options':{'dhcpStatements': ['default-lease-time 120'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_subnets) == 1
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    assert ldap_subnets[0][1]['dhcpStatements'] == ['default-lease-time 120']
    webapp.put('/api/subnets/1', data=json.dumps({'netmask':21,
        'options':{'dhcpStatements': ['default-lease-time 240'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_subnets) == 1
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    assert ldap_subnets[0][1]['dhcpNetMask'] == ['21']
    assert ldap_subnets[0][1]['dhcpStatements'] == ['default-lease-time 240']

def test_host_static_ip(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    webapp.post('/api/ips/', data=json.dumps({'address':'10.0.0.10','host':1}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert 'fixed-address 10.0.0.10' in ldap_hosts[0][1]['dhcpStatements']

def test_release_static_ip(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    webapp.post('/api/ips/', data=json.dumps({'address':'10.0.0.10','host':1}))
    webapp.put('/api/ips/1', data=json.dumps({'host':None}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert 'dhcpStatements' not in ldap_hosts[0][1]

def test_allocate_dynamic_range(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'min':'10.100.100.100','max':'10.100.100.253',
        'subnet':1,'type':'dynamic'}))
    subnet = webapp.get('/api/subnets/1')
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert '10.100.100.100 10.100.100.253' in ldap_subnets[0][1]['dhcpRange']

def test_create_dynamic_pool(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253'}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','subnet':1}))
    webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1,
        'options':{'dhcpStatements': ['default-lease-time 120'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_obj = _ldap_init(webapp)
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_pools) == 1
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    assert 'dhcpPool' in ldap_pools[0][1]['objectClass']
    assert ldap_pools[0][1]['dhcpRange'] == ['10.100.100.200 10.100.100.253']
    assert 'broadcast-address 10.100.100.255' in ldap_pools[0][1]['dhcpOption']

def test_move_dynamic_pool(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253'}))
    webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1}))
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.200','netmask':22}))
    webapp.put('/api/pools/1', data=json.dumps({'subnet':2}))
    ldap_obj = _ldap_init(webapp)
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.200,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_pools) == 1
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_delete_subnet(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253',
        'subnet':1}))
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_subnets[0][1]['cn'] == ['test_pool_00']
    webapp.delete('/api/subnets/1')
    with pytest.raises(requests.HTTPError):
        webapp.get('/api/ranges/1')
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253'}))
    webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1,
        'options':{'dhcpStatements': ['default-lease-time 120'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_obj = _ldap_init(webapp)
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    webapp.delete('/api/subnets/2')
    with pytest.raises(requests.HTTPError):
        webapp.get('/api/pools/1')
    with pytest.raises(requests.HTTPError):
        webapp.get('/api/ranges/2')
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' % 
                (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_delete_pool(webapp):
    # make sure range is deleted
    assert False
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253'}))
    webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1,
        'options':{'dhcpStatements': ['default-lease-time 120'], 'dhcpOption': ['routers 10.0.0.254', 'broadcast-address 10.100.100.255']}}))
    ldap_obj = _ldap_init(webapp)
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    webapp.delete('/api/pools/1')
    with pytest.raises(requests.HTTPError):
        webapp.get('/api/ranges/1')
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' % 
                (_server_dn(webapp)), ldap.SCOPE_BASE)
