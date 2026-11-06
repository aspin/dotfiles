# Installed by setup.zsh. WORK_MACHINE=1 skips the work_machine-guarded apps.

work_machine = ENV["WORK_MACHINE"] == "1"

tap "agavra/tap"

# CLI
brew "git"
brew "wget"
brew "cmake"
brew "thefuck"
brew "the_silver_searcher"
brew "ripgrep"
brew "tmux"
brew "pyenv"
brew "pyenv-virtualenv"
brew "gh"
brew "jq"
brew "glow"
brew "hunk"
brew "herdr"
brew "agavra/tap/tuicr"
brew "pre-commit"
brew "rustup"
brew "git-filter-repo"
brew "watchman"
brew "ykman"
brew "pinentry-mac"

# Coding agents
cask "claude-code@latest"
cask "codex"

# Apps
cask "alfred"
cask "readdle-spark"
cask "iterm2"
cask "arc"
cask "google-chrome"
cask "rectangle"
cask "caffeine"
cask "flux-app"
cask "scroll-reverser"
cask "fantastical"
cask "spotify"
cask "jetbrains-toolbox"
cask "macvim-app"
cask "cursor"
cask "postman"
cask "cyberduck"
cask "docker-desktop"
cask "gpg-suite"
cask "yubico-authenticator"
cask "logi-options+"
cask "wispr-flow"
cask "ledger-live"
cask "chatgpt"

# Blocked on work machines, or installed and managed there by other means.
unless work_machine
  cask "1password"
  cask "claude"
  cask "slack"
  cask "zoom"
  cask "notion"
  cask "discord"
  cask "dropbox"
end
