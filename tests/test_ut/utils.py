import ldap

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
