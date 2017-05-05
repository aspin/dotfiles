#!/bin/zsh

rm -rf ~/.zprezto

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
	if ! [[ "$file" =~ '.*zsh'$ ]]
	then
		rm ~/.$file
		ln -s `pwd`/$file ~/.$file
	fi
done
