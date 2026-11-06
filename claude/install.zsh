#!/bin/zsh
# Link skills and hooks into ~/.claude. Re-runnable.

cd "${0:A:h}"
mkdir -p ~/.claude/skills ~/.claude/hooks

for dir in skills/*(/); do
  ln -sfn "`pwd`/$dir" ~/.claude/skills/${dir:t}
done

for hook in hooks/*.py; do
  ln -sf "`pwd`/$hook" ~/.claude/hooks/${hook:t}
done

# Wire the hooks up only on a fresh machine; never overwrite existing settings
if [[ ! -e ~/.claude/settings.json ]]; then
  cp settings.json ~/.claude/settings.json
else
  echo "~/.claude/settings.json exists; merge the hooks from claude/settings.json by hand"
fi
