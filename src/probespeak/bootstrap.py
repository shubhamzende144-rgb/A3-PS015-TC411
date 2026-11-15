"""Make the existing agent package importable without duplicating its rules."""
from __future__ import annotations

import sys
from pathlib import Path

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def install_agent() -> Path:
    agent = repo_root() / "agent"
    entry = str(agent)
    if entry not in sys.path:
        sys.path.insert(0, entry)
    return agent
