#!/bin/zsh

# packages
brew install wget nvm macvim cmake thefuck hub the_silver_searcher z tmux pyenv

# overriding vim with macvim
brew install --cask macvim
ln -s /usr/local/bin/mvim /usr/local/bin/vim

# vim plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

pip install virtualenv
pip install virtualenvwrapper
