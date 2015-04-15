import ldap
import requests
import pytest
from .utils import _server_dn, _ldap_init

def test_postgres_sync(webapp):
    # create LDAP group, host, and subnet entries manually and check for them in postgres
    ldap_obj = _ldap_init(webapp)
    modlist = [('objectClass',['dhcpHost','top']),('dhcpHWAddress','ethernet 08:00:27:26:7a:e7'),
            ('cn','test_host_00')]
    ldap_obj.add_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), modlist)
    modlist = [('objectClass',['dhcpGroup','top']),('cn','test_group_00')]
    ldap_obj.add_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), modlist)
    modlist = [('objectClass',['dhcpOptions','dhcpSubnet','top']),
            ('dhcpOption',['broadcast-address 10.100.100.255']),
            ('cn','10.100.100.0'),('dhcpNetMask',22)]
    ldap_obj.add_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), modlist)
    webapp.post('/api/sync/')
    host = webapp.get('/api/hosts/1')
    assert host['name'] == 'test_host_00'
    assert host['mac_address'] == '08:00:27:26:7a:e7'
    group = webapp.get('/api/groups/1')
    assert group['name'] == 'test_group_00'
    subnet = webapp.get('/api/subnets/1')
    assert subnet['name'] == '10.100.100.0'
    assert subnet['netmask'] == 22
    assert subnet['broadcast_address'] == '10.100.100.255'

def test_ldap_sync(webapp):
    # create postgres group, host, and subnet entries, delete their LDAP equivalents, and recheck for them in LDAP
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    ldap_obj = _ldap_init(webapp)
    ldap_obj.delete_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)))
    ldap_obj.delete_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)))
    ldap_obj.delete_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)))
    webapp.post('/api/sync/')
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    ldap_groups = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_groups[0][1]['cn'] == ['test_group_00']
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    assert ldap_subnets[0][1]['netmask'] == 22
