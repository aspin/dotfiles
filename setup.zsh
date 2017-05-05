#!/bin/zsh

rm -f ~/.vimrc ~/.gitconfig ~/.npmrc ~/.tmux.conf ~/.tern-config
rm -rf ~/.zprezto

# Prezto Setup
git clone --recursive https://github.com/aspin/prezto "${ZDOTDIR:-$HOME}/.zprezto"
setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  rm -f "${ZDOTDIR:-$HOME}/.${rcfile:t}"
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done

# symlink files
ln -s `pwd`/.vimrc ~/.vimrc
ln -s `pwd`/.gitconfig ~/.gitconfig
ln -s `pwd`/.npmrc ~/.npmrc
ln -s `pwd`/.tmux.conf ~/.tmux.conf
ln -s `pwd`/.tern-config ~/.tern-config
