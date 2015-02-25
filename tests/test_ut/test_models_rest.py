import requests
import json

def _setup(webapp):
    webapp.post('/api/servers/', data={'hostname':'dhcpawn.net'})
    webapp.post('/api/groups/', data={'name':'testgroup','server_id':1})
    webapp.post('/api/hosts/', data={'name':'cl01','mac':'08:00:27:26:7a:e7', 'group_id':1,'server_id':1})

def test_create_objects(webapp):
    _setup(webapp)
    host = webapp.get('/api/hosts/1')
    assert host['name']=='cl01'
    assert 'dhcpawn' in host['dn']
    assert 'testgroup' in host['dn']

def test_edit_objects(webapp):
    _setup(webapp)
    webapp.put('/api/hosts/1', data={'group_id':None})
    host = webapp.get('/api/hosts/1')
    assert 'Hosts' in host['dn']

def test_delete(webapp):
    _setup(webapp)
    webapp.delete('/api/groups/1')
    groups = webapp.get('/api/groups/')
    assert 'testgroup' not in groups['items']
    host = webapp.get('/api/hosts/1')
    assert 'Hosts' in host['dn']
