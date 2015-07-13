import ldap
import requests
import pytest
import random
import json
from ipaddr import IPv4Address
from .utils import _server_dn, _ldap_init

def test_ip_address_conflict(webapp):
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_00','mac':'08:00:27:26:7a:e7'}))
    webapp.post('/api/hosts/', data=json.dumps({'name':'test_host_01','mac':'08:00:27:26:7a:e8'}))
    webapp.post('/api/ips/', data=json.dumps({'address':'10.0.0.10','host':1}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ips/', data=json.dumps({'address':'10.0.0.10','host':2}))

def test_ip_conflict_with_dynamic_range(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    iprange = webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.80',
        'max':'10.100.100.253','subnet':1,'type':'dynamic'}))
    assert iprange['min'] == '10.100.100.80'
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ips/', data=json.dumps({'address': '10.100.100.101'}))

def test_range_conflict(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    iprange = webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.80',
        'max':'10.100.100.150','subnet':1,'type':'static'}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_01','min':'10.100.100.0',
            'max':'10.100.100.90','subnet':1,'type':'dynamic'}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_02','min':'10.100.100.100',
            'max':'10.100.100.253','subnet':1,'type':'static'}))

def test_auto_static_ip_ranging(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    iprange = webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'static'}))
    ip = webapp.post('/api/ips/', data=json.dumps({'address':'10.100.100.253'}))
    assert ip['range'] == 1

def test_auto_static_range_ip_collection(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    ip = webapp.post('/api/ips/', data=json.dumps({'address':'10.100.100.253'}))
    iprange = webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'static'}))
    ip = webapp.get('/api/ips/1')
    assert ip['range'] == 1

def test_ip_range_allocation(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'static'}))
    webapp.post('/api/ips/', data=json.dumps({'range':1}))
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.100.100.253'

def test_mass_ip_allocation(webapp):
    # mark 100 addresses in a static range, check that IP allocation comes after this pool
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'static'}))
    iprange = webapp.put('/api/ranges/1/allocate/', data=json.dumps({'number':100}))
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 100
    assert ips['items'][0]['range'] == 1
    ip = IPv4Address(ips['items'][0]['address'])
    ip = webapp.get('/api/ips/2')
    assert ip['address'] == '10.100.100.252'
    ip = webapp.post('/api/ips/', data=json.dumps({'range':1}))
    assert ip['address'] == '10.100.100.153'

def test_holey_ip_allocation(webapp):
    # make a random gap in a range, make sure allocation fills it
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'static'}))
    iprange = webapp.put('/api/ranges/1/allocate/', data=json.dumps({'number':100}))
    addresses = []
    for rand_id in random.sample(xrange(99),10):
        rand_id += 1
        ip = webapp.get('/api/ips/%s' % (rand_id))
        addresses.append(IPv4Address(ip['address']))
        webapp.delete('/api/ips/%s' % (rand_id))
    new_addresses = []
    new_ip = IPv4Address(webapp.post('/api/ips/', data=json.dumps({'range':1}))['address'])
    assert new_ip == max(addresses)
    new_addresses.append(new_ip)
    for i in xrange(9):
        new_ip = webapp.post('/api/ips/', data=json.dumps({'range':1}))
        new_addresses.append(IPv4Address(new_ip['address']))
    assert set(new_addresses) == set(addresses)

def test_too_large_allocation(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.150','subnet':1,'type':'static'}))
    with pytest.raises(requests.HTTPError):
        iprange = webapp.put('/api/ranges/1/allocate/', data=json.dumps({'number':100}))

def test_incorrect_range_in_subnet(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ranges/', data=json.dumps({'name':'test_range_00','min':'172.100.100.100',
            'max':'172.100.100.150','subnet':1,'type':'static'}))

def test_incorrect_range_in_pool(webapp):
    webapp.post('/api/subnets/', data=json.dumps({'name':'10.100.100.0','netmask':22}))
    webapp.post('/api/ranges/', data=json.dumps({'type':'dynamic','min':'172.100.100.200','max':'172.100.100.253'}))
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/pools/', data=json.dumps({'name':'test_pool_00','range':1,'subnet':1}))
