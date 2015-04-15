import ldap
import requests
import pytest
import random
from ipaddr import IPv4Address
from .utils import _server_dn, _ldap_init

def test_ip_address_conflict(webapp):
    webapp.post('/api/hosts/', data={'name':'test_host_00','mac':'08:00:27:26:7a:e7'})
    webapp.post('/api/hosts/', data={'name':'test_host_01','mac':'08:00:27:26:7a:e8'})
    webapp.post('/api/ips/', data={'address':'10.0.0.10','host':1})
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ips/', data={'address':'10.0.0.10','host':2})

def test_ip_conflict_with_dynamic_range(webapp):
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','min':'10.100.100.100',
        'max':'10.100.100.253','subnet':1,'type':'dynamic'})
    with pytest.raises(requests.HTTPError):
        webapp.post('/api/ips/', data={'address': '10.100.100.101'})

def test_range_conflict(webapp):
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','min':'10.100.100.80',
        'max':'10.100.100.150','subnet':1,'type':'static'})
    with pytest.raises(request.HTTPError):
        webapp.post('/api/ranges/', data={'name':'test_range_01','min':'10.100.100.0',
            'max':'10.100.100.100','subnet':1,'type':'static'})
    with pytest.raises(request.HTTPError):
        webapp.post('/api/ranges/', data={'name':'test_range_02','min':'10.100.100.100',
            'max':'10.100.100.253','subnet':1,'type':'static'})

def test_ip_range_allocation(webapp):
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','ip_min':'10.100.100.100',
        'ip_max':'10.100.100.253','subnet':1,'type':'static'})
    webapp.post('/api/ips/', data={'range':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.100.100.253'

def test_mass_ip_allocation(webapp):
    # mark 100 addresses in a static range, check that IP allocation comes after this pool
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','ip_min':'10.100.100.100',
        'ip_max':'10.100.100.253','subnet':1,'type':'static'})
    webapp.put('/api/ranges/1/allocate/', data={'number':100})
    ips = webapp.get('/api/ips/')
    assert len(ips['items']) == 100
    assert ips['items'][0]['range'] == 1
    ip = IPv4Address(ips['items'][0]['address'])
    ip = webapp.get('/api/ips/2')
    assert ip['address'] == '10.100.100.252'
    ip = webapp.post('/api/ips/', data={'range':1})
    assert ip['address'] == '10.100.100.152'

def test_holey_ip_allocation(webapp):
    # make a random gap in a range, make sure allocation fills it
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','ip_min':'10.100.100.100',
        'ip_max':'10.100.100.253','subnet':1,'type':'static'})
    webapp.put('/api/ranges/1/allocate/', data={'number':100})
    rand_id = random.randint(0, 100)
    ip = webapp.get('/api/ips/%s' % (rand_id))
    webapp.delete('/api/ips/%s' % (rand_id))
    new_ip = webapp.post('/api/ips/', data={'range':1})
    assert new_ip['address'] == ip['address']

def test_too_large_allocation(webapp):
    # mark 100 addresses in a static range, check that IP allocation comes after this pool
    webapp.post('/api/subnets/', data={'name':'10.100.100.0','netmask':22})
    webapp.post('/api/ranges/', data={'name':'test_range_00','ip_min':'10.100.100.100',
        'ip_max':'10.100.100.253','subnet':1,'type':'static'})
    webapp.put('/api/ranges/1/allocate/', data={'number':100})
    webapp.post('/api/ips/', data={'range':1})
    ip = webapp.get('/api/ips/1')
    assert ip['address'] == '10.100.100.149'
