import ldap
import requests
import pytest
import json
from .utils import _server_dn, _ldap_init

def test_deploy_host_to_ldap(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','deployed':False}))
    ldap_obj = _ldap_init(webapp)
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    webapp.put('/api/hosts/1', data=json.dumps({'deployed':True}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/hosts/1', data=json.dumps({'deployed':False}))
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_deploy_group_to_ldap(webapp):
    webapp.post('/api/groups/', data=json.dumps({'name':'test_group_00','deployed':False}))
    ldap_obj = _ldap_init(webapp)
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_groups = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1}))
    webapp.put('/api/groups/1', data=json.dumps({'deployed':True}))
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1}))
    ldap_groups = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_groups) == 1
    assert ldap_groups[0][1]['cn'] == ['test_group_00']
    webapp.put('/api/groups/1', data=json.dumps({'deployed':False}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']

def test_deploy_subnet_to_ldap(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22,'deployed':False}))
    ldap_obj = _ldap_init(webapp)
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    webapp.put('/api/subnets/1', data=json.dumps({'deployed':True}))
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_subnets) == 1
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    webapp.put('/api/subnets/1', data=json.dumps({'deployed':False}))
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_deploy_ip_to_ldap(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7','deployed':False}))
    webapp.post('/api/ips/', data=json.dumps({'address':'10.0.0.10','host':1,'deployed':False}))
    with pytest.raises(requests.HTTPError):
        webapp.put('/api/ips/1', data=json.dumps({'deployed':True}))
    webapp.put('/api/hosts/1', data=json.dumps({'deployed':True}))
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert 'dhcpStatements' not in ldap_hosts[0][1]
    assert 'fixed-address 10.0.0.10' not in ldap_hosts[0][1].values()
    webapp.put('/api/ips/1', data=json.dumps({'deployed':True}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert 'fixed-address 10.0.0.10' in ldap_hosts[0][1]['dhcpStatements']
    webapp.put('/api/ips/1', data=json.dumps({'deployed':False}))
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert 'dhcpStatements' not in ldap_hosts[0][1]
    assert 'fixed-address 10.0.0.10' not in ldap_hosts[0][1].values()

def test_deploy_range_to_ldap(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22,'deployed':False}))
    webapp.post('/api/ranges/', data=json.dumps({'min':'10.100.100.100','max':'10.100.100.253',
        'subnet':1,'type':'dynamic','deployed':False}))
    with pytest.raises(requests.HTTPError):
        webapp.put('/api/ranges/1', data=json.dumps({'deployed':True}))
    webapp.put('/api/subnets/1', data=json.dumps({'deployed':True}))
    subnet = webapp.get('/api/subnets/1')
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert 'dhcpRange' not in ldap_subnets[0][1]
    assert '10.100.100.100 10.100.100.253' not in ldap_subnets[0][1].values()
    webapp.put('/api/ranges/1', data=json.dumps({'deployed':True}))
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert '10.100.100.100 10.100.100.253' in ldap_subnets[0][1]['dhcpRange']
    webapp.put('/api/ranges/1', data=json.dumps({'deployed':False}))
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert 'dhcpRange' not in ldap_subnets[0][1]
    assert '10.100.100.100 10.100.100.253' not in ldap_subnets[0][1].values()

def test_deploy_pool_to_ldap(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22,'deployed':False}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'10.100.100.200','max':'10.100.100.253',
        'deployed':False}))
    webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1,'deployed':False}))
    with pytest.raises(requests.HTTPError):
        webapp.put('/api/pools/1', data=json.dumps({'deployed':True}))
    with pytest.raises(requests.HTTPError):
        webapp.put('/api/ranges/1', data=json.dumps({'deployed':True}))
    webapp.put('/api/subnets/1', data=json.dumps({'deployed':True}))
    ldap_obj = _ldap_init(webapp)
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' % 
                (_server_dn(webapp)), ldap.SCOPE_BASE)
    webapp.put('/api/pools/1', data=json.dumps({'deployed':True}))
    # due to the requirement that pools have ranges, if a pool has a non-deployed range, it will override that upon creation/deployment
    iprange = json.loads(webapp.get('/api/ranges/1'))
    assert iprange['deployed']
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_pools) == 1
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    assert ldap_pools[0][1]['dhcpRange'] == ['10.100.100.200 10.100.100.253']
    with pytest.raises(requests.HTTPError):
        webapp.put('/api/ranges/1', data=json.dumps({'deployed':False}))
    webapp.put('/api/pools/1', data=json.dumps({'deployed':False}))
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' % 
                (_server_dn(webapp)), ldap.SCOPE_BASE)
    # due to the requirement that pools have ranges, if a pool has a non-deployed range, it will override that upon creation/deployment
    iprange = json.loads(webapp.get('/api/ranges/1'))
    assert not iprange['deployed']
