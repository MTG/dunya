# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "dunya-server"

  config.vm.provider "virtualbox" do |v|
    # Need more memory to be able to compile Essentia with related libs
    v.memory = 1024
  end

  config.vm.provision :shell, path: "admin/install_server.sh"

  # Web server forwarding:
  config.vm.network "forwarded_port", guest: 8001, host: 8080

  # PostgreSQL forwarding:
  config.vm.network "forwarded_port", guest: 5432, host: 15432
end
