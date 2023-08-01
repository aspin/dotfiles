#!/bin/zsh

# nvm: brew installation is not supported
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

# packages
brew install git wget cmake thefuck the_silver_searcher tmux pyenv gh jq

# overriding vim with macvim
brew install --cask macvim
ln -s /usr/local/bin/mvim /usr/local/bin/vim

# vim plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

pyenv install 3.11.4
pyenv global 3.11.4
pip install virtualenv
pip install virtualenvwrapper
