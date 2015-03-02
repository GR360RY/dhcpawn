import ldap
import requests
import pytest

def _server_dn(webapp):
    return 'cn=DHCP Config,cn=dhcpsrv,dc=%s,dc=%s' % (
            webapp.app.config['openldap_server_domain_name'].split('.')[0],
            webapp.app.config['openldap_server_domain_name'].split('.')[1])

def _ldap_init(webapp):
    ldap_obj = ldap.initialize(webapp.app.config['LDAP_DATABASE_URI'])
    ldap_obj.bind_s('cn=Manager,dc=%s,dc=%s' % (
        webapp.app.config['openldap_server_domain_name'].split('.')[0],
        webapp.app.config['openldap_server_domain_name'].split('.')[1]),
        webapp.app.config['openldap_server_rootpw'], ldap.AUTH_SIMPLE)
    return ldap_obj

def test_create_host(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert 'dhcpHost' in ldap_hosts[0][1]['objectClass']

def test_duplicate_mac(webapp):
    # check for error
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/hosts/', data={'name':'test_host_01','mac':'08:00:27:26:7a:e7'})

def test_create_group(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    ldap_obj = _ldap_init(webapp)
    ldap_groups = ldap_obj.search_s('cn=test_group_00,ou=Groups,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_groups) == 1
    assert ldap_groups[0][1]['cn'] == ['test_group_00']

def test_move_host(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.post('/api/groups/', data={'name':'test_group_01'})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7','group_id':1})
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/hosts/1', data={'group_id':2})
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_01,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']

def test_rename_group(webapp):
    # check that contained hosts are updated
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7','group_id':1})
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    webapp.put('/api/groups/1', data={'name':'test_group_01'})
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_01,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']

def test_delete_group(webapp):
    # check that contained hosts are moved to Host
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7','group_id':1})
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,cn=test_group_00,ou=Groups,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    webapp.delete('/api/groups/1')
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_hosts) == 1
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']

def test_create_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22,
        'broadcast_address':'10.100.100.255','routers':'10.0.0.254'})
    ldap_obj = _ldap_init(webapp)
    ldap_subnets = ldap_obj.search_s('cn=10.100.100.0,ou=Subnets,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_subnets) == 1
    assert ldap_subnets[0][1]['cn'] == ['10.100.100.0']
    assert 'dhcpOptions' in ldap_subnets[0][1]['objectClass']
    assert 'dhcpSubnet' in ldap_subnets[0][1]['objectClass']
    assert ldap_subnets[0][1]['netmask'] == 22
    assert ldap_subnets[0][1]['dhcpOption'] == ['broadcast-address 10.100.100.255']

def test_create_dynamic_pool(webapp):
    # ldap should be updated
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/pools/', data={'name':'test_pool_00','range_min':'10.100.100.200',
        'range_max':'10.100.100.253','type':'dynamic','subnet_id':1})
    ldap_obj = _ldap_init(webapp)
    ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
        (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert len(ldap_pools) == 1
    assert ldap_pools[0][1]['cn'] == ['test_pool_00']
    assert 'dhcpPool' in ldap_pools[0][1]['objectClass']
    assert ldap_pools[0][1]['dhcpRange'] == ['10.100.100.200 10.100.100.253']
    assert ldap_pools[0][1]['dhcpOption'] == ['broadcast-address 10.100.100.255']

def test_create_static_pool(webapp):
    # ldap should not contain pool record
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/pools/', data={'name':'test_pool_00','range_min':'10.100.100.200',
        'range_max':'10.100.100.253','type':'static','subnet_id':1})
    ldap_obj = _ldap_init(webapp)
    with pytest.raises(ldap.NO_SUCH_OBJECT):
        ldap_pools = ldap_obj.search_s('cn=test_pool_00,cn=10.100.100.0,ou=Subnets,%s' %
            (_server_dn(webapp)), ldap.SCOPE_BASE)

def test_allocate_pool_ip(webapp):
    # address should be top IP entry from pool
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/pools/', data={'name':'test_pool_00','range_min':'10.100.100.200',
        'range_max':'10.100.100.253','type':'static','subnet_id':1})
    webapp.post('/api/ips/', data={'pool_id':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.100.100.253'

def test_host_static_ip(webapp):
    # host record gets fixed-address dhcpStatement
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10'}, host_id=1)
    ldap_obj = _ldap_init(webapp)
    ldap_hosts = ldap_obj.search_s('cn=test_host_00,ou=Hosts,%s' % (_server_dn(webapp)), ldap.SCOPE_BASE)
    assert ldap_hosts[0][1]['cn'] == ['test_host_00']
    assert ldap_hosts[0][1]['dhcpHWAddress'] == ['ethernet 08:00:27:26:7a:e7']
    assert ldap_hosts[0][1]['dhcpStatement'] == ['fixed-address 10.0.0.10']

def test_allocate_static_ips(webapp):
    # mark 100 addresses in a static pool as in use, check that IP allocation comes after this pool
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/pools/', data={'name':'test_pool_00','range_min':'10.100.100.100',
        'range_max':'10.100.100.250','type':'static','subnet_id':1})
    webapp.put('/api/pools/1/allocate/', data={'number':100})
    webapp.post('/api/ips/', data={'pool_id':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.100.100.149'

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
