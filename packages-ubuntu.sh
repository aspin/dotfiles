#!/bin/sh

# Tested for Ubuntu 12.04

sudo apt-get install curl wget zsh vim python-pip python-software-properties silversearcher-ag fzf -yqq
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.7

sudo pip install -i https://pypi.python.org/simple -U pip distribute

sudo pip install virtualenv virtualenvwrapper
