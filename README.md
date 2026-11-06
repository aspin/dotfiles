# dotfiles

Configuration details stored here.

**Getting Started:**

Generate SSH keys for Github: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Generate GPG keys: https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key

**Run setup:**
```
$ ./setup.zsh
```

Apps and CLI tools live in `Brewfile`. On a work machine, `WORK_MACHINE=1 ./setup.zsh`
skips the guarded apps.

**Git identity:**

`gitconfig` includes `~/.gitconfig.local` (machine default, created empty by setup) and
`~/.gitconfig.aspin` for repos under `~/workspace/github.com/aspin/`. Put the machine's
`[user]` email/signingkey and `core.sshCommand` in `~/.gitconfig.local`.

`gitconfig` rewrites `https://github.com` to SSH. If a network blocks port 22, GitHub also
serves SSH on `ssh.github.com:443`.

**iTerm2:**

setup.zsh points iTerm2 at `preferences/` for its settings. Shift+Return sends `0x0a`
(newline without submit, for Claude Code and other TUIs).

**Setup vim:**

```
$ vi ~/.vimrc

:PlugInstall
```

**Claude Code:** see `claude/README.md`.
