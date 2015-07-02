DHCPawn
=========

ISC Bind DHCP Server with Ldap Backend.

Setting Up Development Environment
----------------------------------

### Install Prerequisites

__Install virtualenv:__

    sudo apt-get install python-virtualenv

On Mac:

    sudo easy_install pip
    sudo pip install virtualenv

__Install VirtualBox:__

On Ubuntu:

    sudo echo "deb http://download.virtualbox.org/virtualbox/debian trusty contrib" >> /etc/apt/sources.list
    wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install virtualbox-4.3

On Mac:

Download [VirtualBox]( http://download.virtualbox.org/virtualbox/4.3.20/VirtualBox-4.3.20-96996-OSX.dmg ) and install from DMG file.

__Install Vagrant:__

On Ubuntu:

    sudo dpkg -i https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.1_x86_64.deb

On Mac:

Download [Vagrant]( https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.1.dmg ) and install from DMG file.

### Get the Source

    cd ~/
    git clone https://github.com/GR360RY/dhcpawn.git
    cd ~/dhcpawn

### Development and deployment

Deploy DHCPawn to the vagrant DHCP server:

    python manage.py deploy --dest=vagrant

DHCPawn is will run on port 80 of the virtual host, which is forwarded to port 10080. To see a list of registered hosts, use the DHCPawn API:

    curl http://localhost:10080/api/hosts/

DHCPawn can also be run locally for easier debugging. To use the vagrant host as a PostgreSQL and LDAP server, set the following:

    export SQLALCHEMY_DATABASE_URI=postgresql://dhcpawn:dhcpawn@localhost:15432/dhcpawn
    export LDAP_DATABASE_URI=ldap://localhost:10389

and run:

    python manage.py testserver

This starts a local Flask process on port 8000. Note that this, and the deployment, create a python virtualenv at .env/. To utilize this virtualenv outside of manage.py, run:

    source .env/bin/activate

### DHCPawn API

DHCPawn uses a REST API. More complete documentation will be added soon, but the following is an example of adding cl01 to a test group:

    curl http://localhost:10080/api/groups/ -d '{"name":"testgroup"}' -X POST
    curl http://localhost:10080/api/hosts/ -d '{"name":"cl01","mac":"08:00:27:26:7a:e7","group":"1"}' -X POST

### Connecting to Backend Ldap

Install Apache Directory Studio ([Download Link](http://directory.apache.org/studio/downloads.html)). Configure Apache Directory Studio to connect to LDAP:

    Hostname: localhost
    Port: 10389
    Bind DN or User: cn=Manager,dc=dhcpawn,dc=net
    Bind password: dhcpawn
    Encryption Method: No encryption

### Starting up the clients

Clients are provided to test address allocation. Their MAC addresses are predefined in the Vagrantfile. To start up DHCP clients:

    vagrant up cl01
    vagrant up cl02

### Database migrations

Migrations in DHCPawn use alembic. Running

    python manage.py deploy

will automatically migrate any database changes already in the migrations/ directory. To migrate new changes, run (with the environment variable SQLALCHEMY_DATABASE_URI properly set to your database):

    python manage.py db revision

Be sure to review the alembic migration file generated in migrations/ before deploying.
