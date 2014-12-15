# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.define "dhcpsrv", primary: true do |dhcpsrv|
    dhcpsrv.vm.box = "ubuntu/trusty64"
    dhcpsrv.vm.hostname = "dhcpsrv"
    dhcpsrv.vm.network "forwarded_port", guest: 389, host: 10389
    dhcpsrv.vm.network "private_network", ip: "10.100.100.254"
    dhcpsrv.vm.provision "ansible" do |ansible|
      ansible.playbook = "dhcpawn.yml"
      ansible.extra_vars = {
        dhcp_interfaces: 'eth1'
      }
      ansible.sudo = true
    end
    dhcpsrv.vm.provider :virtualbox do |box|
      box.customize ["modifyvm", :id, "--name", "dhcpsrv" ]
      box.customize ["modifyvm", :id, "--nic2", "intnet" ]
    end
  end

  config.vm.define "cl01", autostart: false do |cl01|
    cl01.vm.box = "ubuntu/trusty64"
    cl01.vm.hostname = "cl01"
    cl01.vm.network "private_network", type: "dhcp"
    cl01.vm.provider :virtualbox do |box|
      box.customize ["modifyvm", :id, "--name", "cl01" ]
      box.customize ["modifyvm", :id, "--nic2", "intnet" ]
    end
  end

  config.vm.define "cl02", autostart: false do |cl02|
    cl02.vm.box = "ubuntu/trusty64"
    cl02.vm.hostname = "cl02"
    cl02.vm.network "private_network", type: "dhcp"
    cl02.vm.provider :virtualbox do |box|
      box.customize ["modifyvm", :id, "--name", "cl02" ]
      box.customize ["modifyvm", :id, "--nic2", "intnet" ]
    end
  end

end
