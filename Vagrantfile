Vagrant.configure("2") do |config|
  # Use an Ubuntu base image
  config.vm.box = "bento/ubuntu-24.04"

  # Network configuration to expose port 80
  config.vm.network "forwarded_port", guest: 80, host: 8080

  # Sync current directory with VM
  config.vm.synced_folder ".", "/vagrant"

  # Provision with Ansible
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible-playbook.yml"
    ansible.become = true
    ansible.compatibility_mode = "2.0"
  end

  # Define VM resources
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
    vb.cpus = 1
  end
end