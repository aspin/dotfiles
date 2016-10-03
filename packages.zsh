#!/bin/zsh

# homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew install wget nvm macvim cmake

# overriding vim with macvim
brew linkapps macvim
ln -s /usr/local/bin/mvim /usr/local/bin/vim
