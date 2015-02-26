from .app import app, ldap_obj
import ldap

def server_dn():
    return 'cn=DHCP Config,cn=dhcpsrv,dc=%s,dc=%s' % (
            app.config['openldap_server_domain_name'].split('.')[0],
            app.config['openldap_server_domain_name'].split('.')[1])

def _deep_delete(dn):
    try:
        objects = ldap_obj.search_s(dn, ldap.SCOPE_SUBTREE)
    except ldap.NO_SUCH_OBJECT:
        return
    for obj in objects:
        if obj[0] != dn:
            _deep_delete(obj[0])
    ldap_obj.delete_s(dn)

def drop_all():
    for ou in ['Hosts','Groups','Subnets']:
        objects = ldap_obj.search_s('ou=%s,%s' % (ou, server_dn()), ldap.SCOPE_SUBTREE)
        for obj in objects:
            if not obj[0].startswith('ou=%s' % ou):
                _deep_delete(obj[0])
