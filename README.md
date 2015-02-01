DHCPawn
=========

ISC Bind DHCP Server with Ldap Backend.

Setting Up Development Environment
----------------------------------

### Install Prerequisites 

__Install Ansible:__

On Ubuntu:
    
    sudo apt-get install software-properties-common
    sudo apt-add-repository -y ppa:ansible/ansible
    sudo apt-get update
    sudo apt-get -y install ansible git

On Mac:

    brew install ansible git 

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

### Starting up the DHCP Server and Clients

Start the DHCP server:

    vagrant up

Starting up DHCP clients:

    vagrant up cl01
    vagrant up cl02

### Connecting to Backend Ldap

Install Apache Directory Studio ([Download Link](http://directory.apache.org/studio/downloads.html)). Configure Apache Directory Studio to connect to LDAP:

    Hostname: localhost
    Port: 10389
    Bind DN or User: cn=Manager,dc=dhcpawn,dc=net
    Bind password: dhcpawn
    Encryption Method: No encryption

### Development and deployment

DHCPawn uses ([weber-backend](https://github.com/vmalloc/weber-backend)). Further instructions can be read there, but DHCPawn is set up to allow deployment to the virtual DHCP server by running:

    python manage.py deploy --dest=vagrant
