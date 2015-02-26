import flask
import logging
import os
import sys
import yaml
from flask.ext.mail import Mail
import ldap

import logbook

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

app = flask.Flask(__name__, static_folder=os.path.join(ROOT_DIR, "..", "static"))

# Defaults
app.config["SECRET_KEY"] = ""

app.config['SQLALCHEMY_DATABASE_URI'] = os.path.expandvars(
    os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/__demo_db.sqlite'))

app.config['LDAP_DATABASE_URI'] = os.path.expandvars(os.environ.get('LDAP_DATABASE_URI','ldap://localhost:389'))

_CONF_D_PATH = os.environ.get('CONFIG_DIRECTORY', os.path.join(ROOT_DIR, "..", "conf.d"))

configs = [os.path.join(ROOT_DIR, "app.yml")]

if os.path.isdir(_CONF_D_PATH):
    configs.extend(sorted(os.path.join(_CONF_D_PATH, x) for x in os.listdir(_CONF_D_PATH) if x.endswith(".yml")))

for yaml_path in configs:
    if os.path.isfile(yaml_path):
        with open(yaml_path) as yaml_file:
            app.config.update(yaml.load(yaml_file))

ldap_obj = ldap.initialize(app.config['LDAP_DATABASE_URI'])
ldap_obj.bind_s('cn=Manager,dc=%s,dc=%s' % (app.config['openldap_server_domain_name'].split('.')[0],
    app.config['openldap_server_domain_name'].split('.')[1]),
    app.config['openldap_server_rootpw'], ldap.AUTH_SIMPLE)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
app.logger.addHandler(console_handler)

logbook.info("Started")

Mail(app)

from . import models
from . import errors
from . import views
