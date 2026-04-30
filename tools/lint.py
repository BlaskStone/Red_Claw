"""RedClaw lint: frontmatter validation + index rebuild."""
from __future__ import annotations
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
POCS_DIR = REPO_ROOT / "pocs"

REQUIRED_FIELDS = ("cve", "target_os", "target_versions",
                   "vuln_type", "capability", "status", "references")
VALID_STATUS = {"verified", "partial", "theoretical", "archived"}


@dataclass
class Entry:
    path: Path
    frontmatter: dict
    errors: list[str] = field(default_factory=list)

    @property
    def cve(self) -> str:
        return self.frontmatter.get("cve", "")
