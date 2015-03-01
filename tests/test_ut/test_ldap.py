import ldap

def _ldap_init(webapp):
    ldap_obj = ldap.initialize(webapp.app.config['LDAP_DATABASE_URI'])
    ldap_obj.bind_s('cn=Manager,dc=%s,dc=%s' % (webapp.app.config['openldap_server_domain_name'].split('.')[0],
        webapp.app.config['openldap_server_domain_name'].split('.')[1]),
        webapp.app.config['openldap_server_rootpw'], ldap.AUTH_SIMPLE)
    return ldap_obj

def test_create_host(webapp):
    ldap_obj = _ldap_init(webapp)

def test_move_host(webapp):
    ldap_obj = _ldap_init(webapp)

def test_duplicate_mac(webapp):
    # check for error
    ldap_obj = _ldap_init(webapp)

def test_create_group(webapp):
    ldap_obj = _ldap_init(webapp)

def test_rename_group(webapp):
    # check that contained hosts are updated
    ldap_obj = _ldap_init(webapp)

def test_delete_group(webapp):
    # check that contained hosts are moved to Host
    ldap_obj = _ldap_init(webapp)

def test_create_subnet(webapp):
    ldap_obj = _ldap_init(webapp)

def test_create_dynamic_pool(webapp):
    # ldap should be updated
    ldap_obj = _ldap_init(webapp)

def test_create_static_pool(webapp):
    # ldap should not contain pool record
    ldap_obj = _ldap_init(webapp)

def test_allocate_pool_ip(webapp):
    # address should be top IP entry from pool
    ldap_obj = _ldap_init(webapp)

def test_host_static_ip(webapp):
    # host record gets fixed-address dhcpStatement
    ldap_obj = _ldap_init(webapp)

def test_allocate_static_ips(webapp):
    # mark 100 addresses in a static pool as in use, check that IP allocation comes after this pool
    ldap_obj = _ldap_init(webapp)

def test_postgres_sync(webapp):
    # create LDAP group, host, and subnet entries manually and check for them in postgres
    ldap_obj = _ldap_init(webapp)

def test_ldap_sync(webapp):
    # create postgres group, host, and subnet entries, delete their LDAP equivalents, and recheck for them in LDAP
    ldap_obj = _ldap_init(webapp)
