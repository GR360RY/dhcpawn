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
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7','group':1})
    webapp.put('/api/hosts/1', data={'name':'test_host_01','group':'None'})
    host = webapp.get('/api/hosts/1')
    assert host['name'] == 'test_host_01'
    assert host['group'] == None

def test_delete_host(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.delete('/api/hosts/1')
    hosts = webapp.get('/api/hosts/')
    assert len(hosts['items']) == 0

# TODO: define required subnet fields
def test_create_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    subnets = webapp.get('/api/subnets/')
    assert len(subnets['items']) == 1
    subnet = webapp.get('/api/subnets/1')
    assert subnet['name'] == 'test_subnet_00'

def test_update_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.put('/api/subnets/1', data={'netmask':21})
    subnet = webapp.get('/api/subnets/1')
    assert subnet['name'] == 'test_subnet_00'
    assert subnet['netmask'] == 21

def test_delete_subnet(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':20})
    webapp.delete('/api/subnets/1')
    subnets = webapp.get('/api/subnets/')
    assert len(subnets['items']) == 0

def test_create_ip(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.post('/api/ips/', data={'address':'10.0.0.10','subnet':1})
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 1
    ip = webapp.get('/api/ips/1')
    assert ip['address'] ==  '10.0.0.10'
    assert ip['host'] == None

def test_update_ip(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10'})
    webapp.put('/api/ips/1', data={'host':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.0.0.10'
    assert ip['host'] == 1
    assert ip['subnet'] == None

def test_delete_ip(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10'})
    webapp.delete('/api/ips/1')
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 0
    webapp.post('/api/ips/', data={'address':'10.0.0.10', 'host':1})
    webapp.delete('/api/hosts/1')
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 1
    ip = webapp.get('/api/ips/2')
    assert ip['host'] == None

def test_create_range(webapp):
    webapp.post('/api/ranges/', data={'min':'10.0.0.200','max':'10.0.0.253','type':'static'})
    ip_ranges = webapp.get('/api/ranges/')
    assert len(ip_ranges['items']) == 1
    ip_range = webapp.get('/api/ranges/1')
    assert ip_range['max'] == '10.0.0.253'

def test_update_range(webapp):
    webapp.post('/api/ranges/', data={'min':'10.0.0.200','max':'10.0.0.253','type':'static'})
    ip_range = webapp.get('/api/ranges/1')
    assert ip_range['type'] == 'static'
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.put('/api/ranges/1', data={'type':'dynamic','subnet':1})
    ip_range = webapp.get('/api/ranges/1')
    assert ip_range['type'] == 'dynamic'
    assert ip_range['subnet'] == 1

def test_delete_range(webapp):
    webapp.post('/api/ranges/', data={'min':'10.0.0.200','max':'10.0.0.253','type':'static'})
    webapp.delete('/api/ranges/1')
    ip_ranges = webapp.get('/api/ranges/')
    assert len(ip_ranges['items']) == 0

def test_create_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.post('/api/ranges/', data={'type':'dynamic','min':'10.0.0.200','max':'10.0.0.253'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet':1,'range':1})
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 1
    pool = webapp.get('/api/pools/1')
    assert pool['name'] == 'test_pool_00'
    assert pool['range'] == 1

def test_update_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.post('/api/subnets/', data={'name':'test_subnet_01','netmask':23})
    webapp.post('/api/ranges/', data={'type':'dynamic','min':'10.0.0.200','max':'10.0.0.253'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet':1,'range':1})
    webapp.put('/api/pools/1', data={'name':'test_pool_01','subnet':2})
    pool = webapp.get('/api/pools/1')
    assert pool['name'] == 'test_pool_01'
    assert pool['subnet'] == 2

def test_delete_pool(webapp):
    webapp.post('/api/subnets/', data={'name':'test_subnet_00','netmask':22})
    webapp.post('/api/ranges/', data={'type':'dynamic','min':'10.0.0.200','max':'10.0.0.253'})
    webapp.post('/api/pools/', data={'name':'test_pool_00','subnet':1,'range':1})
    webapp.delete('/api/pools/1')
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 0
    webapp.post('/api/pools/', data={'name':'test_pool_01','subnet':1,'range':1})
    webapp.delete('/api/subnets/1')
    pools = webapp.get('/api/pools/')
    assert len(pools['items']) == 0
