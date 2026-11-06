#!/bin/zsh
# Link skills and hooks into ~/.claude. Re-runnable.
# Anything real in the way is moved to ~/.dotfiles-backup/<timestamp>/ first.

set -e
cd "${0:A:h}"
repo=`pwd`
backup=~/.dotfiles-backup/`date +%Y%m%d-%H%M%S`

link() {  # link <path in repo> <target>
  local src="$repo/$1" dst="$2"
  if [[ -L $dst ]]; then
    rm "$dst"
  elif [[ -e $dst ]]; then
    local rel="${dst#$HOME}"
    mkdir -p "$backup${rel:h}"
    mv "$dst" "$backup$rel"
    echo "backed up $dst"
  fi
  mkdir -p "${dst:h}"
  ln -s "$src" "$dst"
}

for dir in skills/*(/); do
  link $dir ~/.claude/skills/${dir:t}
done

for hook in hooks/*.py; do
  link $hook ~/.claude/hooks/${hook:t}
done

# Wire the hooks up only on a fresh machine; never overwrite existing settings
if [[ ! -e ~/.claude/settings.json ]]; then
  cp settings.json ~/.claude/settings.json
else
  echo "~/.claude/settings.json exists; merge the hooks from claude/settings.json by hand"
fi
