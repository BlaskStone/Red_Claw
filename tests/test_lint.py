import sys
from pathlib import Path

# 让 tests/ 能 import tools/lint.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import lint  # noqa: E402
