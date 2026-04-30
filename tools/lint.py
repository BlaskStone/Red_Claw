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


def parse_frontmatter(path: Path) -> dict | None:
    """从 markdown 文件头解析 YAML frontmatter；没有则返回 None。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    return yaml.safe_load(block) or {}
