def test_create_group(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    groups = webapp.get('/api/groups/')
    assert len(groups['items']) == 1
    group = webapp.get('/api/groups/1')
    assert group['name'] == 'test_group_00'

def test_update_group(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.put('/api/groups/1', data={'name':'test_group_01'})
    group = webapp.get('/api/groups/1')
    assert group['name'] == 'test_group_01'

def test_delete_group(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.delete('/api/groups/1')
    groups = webapp.get('/api/groups/')
    assert len(groups['items']) == 0

def test_create_host(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    hosts = webapp.get('/api/hosts/')
    assert len(hosts['items']) == 1
    host = webapp.get('/api/hosts/1')
    assert host['name']=='test_host_00'

def test_update_host(webapp):
    webapp.post('/api/groups/', data={'name':'test_group_00'})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7','group_id':1})
    webapp.put('/api/hosts/1', data={'name':'test_host_01','group_id':'None'})
    host = webapp.get('/api/hosts/1')
    assert host['name'] == 'test_host_01'
    assert host['group_id'] == 'null'

def test_delete_host(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.delete('/api/hosts/1')
    hosts = webapp.get('/api/hosts/')
    assert len(hosts['items']) == 0

# TODO: define required subnet fields
def test_create_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22,
        'broadcast_address':'10.0.0.0','routers':'10.0.0.254'})
    subnets = webapp.get('/api/subnets/')
    assert len(hosts['items']) == 1
    subnet = webapp.get('/api/subnets/1')
    assert subnet['name'] == 'test_subnet_00'
    assert len(subnet['pools']) == 0

def test_update_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.put('/api/subnets/1', data={'name':'test_subnet_01','netmask':22})
    subnet = webapp.get('/api/subnets/1')
    assert subnet['name'] == 'test_subnet_01'
    assert subnet['netmask'] == 22

def test_delete_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.delete('/api/subnets/1')
    subnets = webapp.get('/api/subnets/')
    assert len(hosts['items']) == 0

def test_create_iprange(webapp):
    webapp.post('/api/ipranges/', data={'name':'test_range_00','ip_min':'10.0.0.200','ip_max':'10.0.0.253',
        'type':'static'})
    ipranges = webapp.get('/api/ipranges')
    assert len(ranges['items']) == 1
    iprange = webapp.get('/api/iprange/1')
    assert iprange['name'] == 'test_range_00'

def test_update_iprange(webapp):
    webapp.post('/api/ipranges/', data={'name':'test_range_00','ip_min':'10.0.0.200','ip_max':'10.0.0.253',
        'type':'static'})
    iprange = webapp.get('/api/iprange/1')
    assert iprange['type'] == 'static'
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.put('/api/iprange/1', data={'type':'dynamic','subnet_id':1})
    iprange = webapp.get('/api/iprange/1')
    assert iprange['type'] == 'dynamic'
    assert iprange['subnet_id'] == 1

def test_delete_iprange(webapp):
    webapp.post('/api/ipranges/', data={'name':'test_range_00','ip_min':'10.0.0.200','ip_max':'10.0.0.253'})
    webapp.delete('/api/ipranges/1')
    ipranges = webapp.get('/api/ipranges/')
    assert len(ipranges['items']) == 1

# TODO: define required pool fields
def test_create_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.post('/api/ipranges/', data={'name':'test_range_00','ip_min':'10.0.0.200','ip_max':'10.0.0.253'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','dns':'ns.test.com',
        'max_lease_time':28800,'iprange_id':1,'allow': 'unknown-clients','deny':'','subnet_id':1})
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 1
    pool = webapp.get('/api/pools/1')
    assert pool['name'] == 'test_pool_00'
    assert len(pools['ips']) == 0

def test_update_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.post('/api/subnets/', data={'name':'test_subnet_01'})
    webapp.post('/api/ipranges/', data={'name':'test_range_00','ip_min':'10.0.0.200','ip_max':'10.0.0.253'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','dns':'ns.test.com',
        'max_lease_time':28800,'iprange_id':1,'allow': 'unknown-clients','deny':'','subnet_id':1})
    webapp.put('/api/pools/1', data={'name':'test_pool_01','subnet_id':2})
    pool = webapp.get('/api/pools/1')
    assert pool['name'] == 'test_pool_01'
    assert pool['max_lease_time'] == 28800
    subnet = webapp.get('/api/subnets/%s' % pool['subnet_id'])
    assert subnet['name'] == 'test_subnet_01'

def test_delete_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet_id':1})
    webapp.delete('/api/pools/1')
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 0
    webapp.post('/api/pools/', data={'name':'test_pool_01','subnet_id':1})
    webapp.delete('/api/subnets/1')
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 0

def test_create_ip(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet_id':1})
    webapp.post('/api/ips/', data={'address':'10.0.0.10','pool_id':1})
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 1
    ip = webapp.get('/api/ips/1')
    assert ip['address'] ==  '10.0.0.10'
    assert ip['host_id'] == 'null'

def test_update_ip(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10'})
    webapp.put('/api/ips/1', data={'host_id':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.0.0.10'
    assert ip['host_id'] == 1
    assert ip['pool_id'] == 'null'

def test_delete_ip(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet_id':1})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10'})
    webapp.delete('/api/ips/1')
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 0
    webapp.post('/api/ips/', data={'address':'10.0.0.10'}, pool_id=1)
    webapp.delete('/api/pools/1')
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 0
    webapp.post('/api/ips/', data={'address':'10.0.0.10'}, host_id=1)
    webapp.delete('/api/hosts/1')
    ip = webapp.get('/api/ips/1')
    assert ip['host_id'] == 'null'
