#!/bin/zsh

rm -rf ~/.zprezto

# Download Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install packages (WORK_MACHINE=1 skips IT-managed apps, see Brewfile)
brew tap agavra/tap
brew trust --formula agavra/tap/tuicr
brew bundle --file=./Brewfile
# ./packages-ubuntu.sh

# nvm: brew installation is not supported
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

# vim plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

pyenv install 3.11.15
pyenv global 3.11.15
pip install virtualenv
pip install virtualenvwrapper

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
  case "$file" in
    *zsh|*.sh|*.md|Brewfile|LICENSE|preferences|claude) ;;
    *)
      rm -f ~/.$file
      ln -s `pwd`/$file ~/.$file
      ;;
  esac
done

# `ls` above hides dot-prefixed files, so link .gitconfig.aspin by hand
ln -sf `pwd`/.gitconfig.aspin ~/.gitconfig.aspin

# Claude Code skills and hooks
./claude/install.zsh

# Machine-specific git identity; gitconfig includes it by default
touch ~/.gitconfig.local

# iTerm2 loads its settings from ./preferences
defaults write com.googlecode.iterm2 PrefsCustomFolder -string "`pwd`/preferences"
defaults write com.googlecode.iterm2 LoadPrefsFromCustomFolder -bool true

# Install powerline fonts
git clone https://github.com/powerline/fonts ~/powerline-fonts
cd ~/powerline-fonts && ./install.sh
rm -rf ~/powerline-fonts
