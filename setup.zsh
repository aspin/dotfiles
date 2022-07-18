#!/bin/zsh

rm -rf ~/.zprezto

# Download Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install packages
./packages.zsh
# ./packages-ubuntu.sh

# Prezto Setup
git clone --recursive https://github.com/aspin/prezto "${ZDOTDIR:-$HOME}/.zprezto"
setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  rm -f "${ZDOTDIR:-$HOME}/.${rcfile:t}"
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done

# symlink files
for file in $(ls ./)
do
  if ! ([[ "$file" =~ '.*zsh'$ ]] || [[ "$file" =~ '.*md' ]])
	then
		rm -f ~/.$file
		ln -s `pwd`/$file ~/.$file
	fi
done

# Install powerline fonts
git clone https://github.com/powerline/fonts ~/powerline-fonts
cd ~/powerline-fonts && ./install.sh
rm -rf ~/powerline-fonts
