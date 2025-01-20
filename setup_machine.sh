#!/bin/bash
# run setup_machine.sh
# FIX SUDOERS file first

echo "setting up bashrc"
cp bin/bashrc_to_copy_to_home_dir ~/.bashrc

echo "Installing a bunch of stuff"
sudo apt install -y sshpass
sudo apt install -y meld
sudo apt install -y fortune
sudo apt install -y ack-grep
sudo apt install -y tree
sudo apt install -y vim-gtk
# (sudo yum install vim-X11 vim-enhanced on centos7)
sudo apt install -y cloc
#sudo apt install -y cifs-utils
#sudo apt install -y ncdu
# for ansi2txt
sudo apt install -y colorized-logs

echo "Installing and configuring git"
sudo apt install -y git
cp gitconfig_to_copy_to_home_dir ~/.gitconfig
git maintainance start

# set up pip - ubuntu doesn't ship with it for some stupid reason
sudo apt install python3-pip

echo "Setting up ssh key"
ssh-keygen -t rsa -b 4096 -C "jima.coding@gmail.com"
cat .ssh/id_rsa.pub
echo " "
echo "Install that key on github

