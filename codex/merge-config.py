"""Merge TOML files into $CODEX_HOME/config.toml, keeping keys Codex wrote itself."""

import os
import sys
from collections.abc import Mapping
from pathlib import Path

import tomlkit


def plain(value):
    return value.unwrap() if hasattr(value, "unwrap") else value


def merge(dst, src):
    for key, value in src.items():
        if isinstance(value, Mapping) and isinstance(dst.get(key), Mapping):
            merge(dst[key], value)
        elif key not in dst or plain(dst[key]) != plain(value):
            dst[key] = value


target = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"
config = tomlkit.parse(target.read_text()) if target.exists() else tomlkit.document()
before = config.unwrap()
for path in sys.argv[1:]:
    merge(config, tomlkit.parse(Path(path).read_text()))
if config.unwrap() != before:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(tomlkit.dumps(config))
