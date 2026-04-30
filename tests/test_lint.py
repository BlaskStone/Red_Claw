import sys
from pathlib import Path

# 让 tests/ 能 import tools/lint.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import lint  # noqa: E402


def test_parse_frontmatter_basic(tmp_path):
    f = tmp_path / "r.md"
    f.write_text("---\ncve: CVE-2022-0847\n---\n\nbody\n", encoding="utf-8")
    fm = lint.parse_frontmatter(f)
    assert fm == {"cve": "CVE-2022-0847"}


def test_parse_frontmatter_missing(tmp_path):
    f = tmp_path / "r.md"
    f.write_text("no frontmatter here\n", encoding="utf-8")
    assert lint.parse_frontmatter(f) is None
