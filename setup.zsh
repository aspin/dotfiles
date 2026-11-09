#!/bin/zsh

rm -rf ~/.zprezto

# Download Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install packages (WORK_MACHINE=1 skips IT-managed apps, see Brewfile)
brew tap agavra/tap
brew trust --formula agavra/tap/tuicr
HOMEBREW_WORK_MACHINE="${WORK_MACHINE:-}" brew bundle --file=./Brewfile
# ./packages-ubuntu.sh

# nvm: brew installation is not supported
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

PATH="/usr/bin:$PATH" PYTHON_BUILD_HOMEBREW_OPENSSL_FORMULA=openssl@3 pyenv install 3.11.15
pyenv global 3.11.15
pyenv exec pip install virtualenv
pyenv exec pip install virtualenvwrapper

# Prezto Setup
git clone --recursive https://github.com/aspin/prezto "${ZDOTDIR:-$HOME}/.zprezto"
setopt EXTENDED_GLOB
for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
  rm -f "${ZDOTDIR:-$HOME}/.${rcfile:t}"
  ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
done

# Install powerline fonts
git clone https://github.com/powerline/fonts ~/powerline-fonts
(cd ~/powerline-fonts && ./install.sh)
rm -rf ~/powerline-fonts

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

# Rectangle shortcuts; re-export after changing them with
#   defaults export com.knollsoft.Rectangle preferences/com.knollsoft.Rectangle.plist
defaults import com.knollsoft.Rectangle preferences/com.knollsoft.Rectangle.plist
