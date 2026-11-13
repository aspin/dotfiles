#!/bin/zsh
# Link skills into ~/.claude and ~/.agents, and Claude hooks into ~/.claude. Re-runnable.
# Anything real in the way is moved to ~/.dotfiles-backup/<timestamp>/ first.

set -e
cd "${0:A:h:h}"
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

# ~/.agents/skills is the harness-neutral location Codex reads
for dir in agents/skills/*(/); do
  link $dir ~/.claude/skills/${dir:t}
  link $dir ~/.agents/skills/${dir:t}
done

# Merged rather than linked: Codex writes trust and other state into config.toml
python3 codex/merge-config.py codex/config.toml

for hook in claude/hooks/*.py; do
  link $hook ~/.claude/hooks/${hook:t}
done

# Wire the hooks up only on a fresh machine; never overwrite existing settings
if [[ ! -e ~/.claude/settings.json ]]; then
  cp claude/settings.json ~/.claude/settings.json
else
  echo "~/.claude/settings.json exists; merge the hooks from claude/settings.json by hand"
fi
