# RedClaw Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 RedClaw 从空目录引导成一个可用的 CVE/POC 武器库骨架：schema 文档、索引骨架、示例 CVE 条目、带索引重建能力的 lint 工具，全部按 spec 跑通。

**Architecture:** 静态 markdown 内容（README/SCHEMA/索引骨架/示例 CVE）一次性写入；`tools/lint.py` 是单文件 Python 脚本，负责 frontmatter 校验 + 从所有 CVE 条目聚合重建索引。采用 TDD 开发 lint.py，用 pytest + tmp_path fixture。

**Tech Stack:** Python 3.10+（dataclass、pathlib）、PyYAML、pytest

---

## File Structure

| Path | 职责 |
|---|---|
| `SCHEMA.md` | CVE 条目/topics/writeups 的 frontmatter + 正文写法约束（对照 spec 第 4 节） |
| `README.md` | 项目介绍 + 目录导航 + 五个 operation 速查 |
| `index.md` | 主索引骨架（首次 lint 后会被重建） |
| `log.md` | 时间线日志骨架 |
| `indices/by-capability.md` | 按攻击能力交叉索引（骨架） |
| `indices/by-vuln-type.md` | 按漏洞类型交叉索引（骨架） |
| `indices/by-year.md` | 按 CVE 年份交叉索引（骨架） |
| `pocs/linux/CVE-2022-0847/` | 示例 CVE 条目（DirtyPipe），验证 SCHEMA 落地 |
| `tools/lint.py` | 单文件：frontmatter 校验 + 索引重建 + CLI |
| `tools/requirements.txt` | `PyYAML`, `pytest` |
| `tests/test_lint.py` | lint.py 的单元测试，用 fixture pocs 目录 |
| `.gitkeep` | 空目录占位（topics/ writeups/ patches/） |

`tools/ingest.py` 延后（spec 第 8 节明示可暂缓）—— 不在本计划范围。

---

## Task 1: 顶层 README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: 写 README.md**

```markdown
# RedClaw

Linux / macOS CVE + POC 攻防实战武器库。按 [Karpathy LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式组织。

## 怎么用

四条检索入口：

- **按目标系统/版本** → [`index.md`](index.md)
- **按攻击能力** → [`indices/by-capability.md`](indices/by-capability.md)（LPE / sandbox-escape / kernel-RCE / …）
- **按漏洞类型** → [`indices/by-vuln-type.md`](indices/by-vuln-type.md)（UAF / OOB / race / …）
- **按 CVE 年份** → [`indices/by-year.md`](indices/by-year.md)

每个 CVE 自包含在 `pocs/<os>/CVE-YYYY-NNNN/` 里，拷走就能用。

## 怎么写

所有 CVE 条目必须遵守 [`SCHEMA.md`](SCHEMA.md)。

## 维护动作

| 动作 | 触发 | 脚本 |
|---|---|---|
| `ingest` | 新增 CVE | 建目录 → 写 `README.md` → 放 exploit → `tools/lint.py --rebuild-indices` → 追加 `log.md` |
| `query` | 检索 | 从 `index.md` 或 `indices/*` 入口 |
| `lint` | 体检 | `python tools/lint.py` |
| `promote` | 抽经验到 `topics/` 或 `writeups/` | 新建文档 → 源 CVE README 里加 `See also` → 追加 `log.md` |
| `archive` | 归档失效条目 | 改 frontmatter `status: archived` + `archived_reason` + `archived_date` → 重建索引 |

详见 [`docs/superpowers/specs/2026-04-30-redclaw-design.md`](docs/superpowers/specs/2026-04-30-redclaw-design.md)。

## 目录

```
pocs/        每个 CVE 一个自包含目录
topics/      横向技法文章
writeups/    实战利用链复盘
patches/     官方补丁归档（raw source）
indices/     交叉索引（自动生成，人不手改）
tools/       lint / ingest 辅助脚本
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add project README with usage and operations"
```

---

## Task 2: SCHEMA.md

**Files:**
- Create: `SCHEMA.md`

- [ ] **Step 1: 写 SCHEMA.md**

```markdown
# RedClaw Schema

本文档是强制约束：所有 `pocs/<os>/CVE-YYYY-NNNN/README.md` 必须符合。`tools/lint.py` 会校验每一项。

## 1. Frontmatter

每个条目 README 开头必须是一段 YAML frontmatter。

### 1.1 必填字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `cve` | string | `CVE-YYYY-NNNN` 格式，与目录名一致 |
| `target_os` | enum | `linux` / `macos` / `ios` / `ipados` |
| `target_versions` | string | 受影响版本表达式（人类可读，如 `">=5.8, <5.16.11"`） |
| `vuln_type` | list[string] | 漏洞类型标签，如 `[UAF, race]` |
| `capability` | list[string] | 攻击能力标签，如 `[LPE, arbitrary-file-write]` |
| `status` | enum | `verified` / `partial` / `theoretical` / `archived` |
| `references` | list[url] | 至少 1 条外部参考（paper / blog / commit） |

### 1.2 可选字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `aliases` | list[string] | 俗名，如 `[DirtyPipe]` |
| `cvss` | number | 官方 CVSS 分数 |
| `disclosed` | date | 公开披露日期 `YYYY-MM-DD` |
| `patched` | date | 官方补丁日期 `YYYY-MM-DD` |

### 1.3 条件必填

- `status: verified` → 必须有 `tested_on`（list of `{os, kernel, result}`，至少 1 条）
- `status: archived` → 必须有 `archived_reason`（string）和 `archived_date`（`YYYY-MM-DD`）

### 1.4 完整示例

```yaml
---
cve: CVE-2022-0847
aliases: [DirtyPipe]
cvss: 7.8
disclosed: 2022-03-07
patched: 2022-02-23
target_os: linux
target_versions: ">=5.8, <5.16.11 | <5.15.25 | <5.10.102"
vuln_type: [uninitialized-memory, pipe-buffer]
capability: [LPE, arbitrary-file-write]
status: verified
tested_on:
  - { os: "Ubuntu 20.04", kernel: "5.13.0-30", result: "root shell" }
references:
  - https://dirtypipe.cm4all.com/
---
```

## 2. 正文七段

Frontmatter 之后，条目 README 按下列顺序包含七个二级标题。允许留空但不能缺。

```markdown
## TL;DR           一句话：是什么 + 能干什么
## 影响范围         具体版本/架构/配置前提、不可达的前置条件
## 根因             漏洞机理，patch 前代码片段 + 为什么错
## 利用思路         primitive → 能力提升 → 最终落点（列主要步骤）
## 复现步骤         环境搭建、编译、运行、预期输出
## 检测与修复       patch diff 要点、绕过可能性、监测信号
## 参考             paper / blog / commit / 其他 POC 仓库
```

可选追加 `## See also` 用于 `promote` 后的反向引用。

## 3. `topics/` 和 `writeups/`

```yaml
---
kind: topic              # 或 writeup
title: "Linux 内核堆喷方法论"
covers_cves: [CVE-2022-0847, CVE-2023-XXXXX]
tags: [heap-spray, linux-kernel, primitive]
---
```

## 4. 受控词表

为了索引稳定，下列标签使用受控词表（首次引入新值时请更新本节）：

**capability**：`LPE`, `RCE`, `sandbox-escape`, `container-escape`, `kernel-RCE`, `arbitrary-file-write`, `arbitrary-read`, `info-leak`, `DoS`

**vuln_type**：`UAF`, `OOB-read`, `OOB-write`, `race`, `type-confusion`, `uninitialized-memory`, `double-free`, `integer-overflow`, `logic`, `pipe-buffer`

**target_os**：`linux`, `macos`, `ios`, `ipados`

不在词表里的值允许但 lint 会告警。
```

- [ ] **Step 2: Commit**

```bash
git add SCHEMA.md
git commit -m "docs: add SCHEMA.md defining frontmatter and body structure"
```

---

## Task 3: 索引和日志骨架

**Files:**
- Create: `index.md`, `log.md`
- Create: `indices/by-capability.md`, `indices/by-vuln-type.md`, `indices/by-year.md`
- Create: `topics/.gitkeep`, `writeups/.gitkeep`, `patches/.gitkeep`, `tools/.gitkeep`
- Create: `pocs/linux/.gitkeep`, `pocs/macos/.gitkeep`

- [ ] **Step 1: 写 index.md 骨架**

```markdown
# Master Index

> 自动生成，不要手改。运行 `python tools/lint.py --rebuild-indices` 重建。

## Linux

_(empty)_

## macOS

_(empty)_
```

- [ ] **Step 2: 写 log.md 骨架**

```markdown
# Change Log

时间线：ingest / update / promote / archive 的全部动作。

格式：`## [YYYY-MM-DD] <action> | <detail>`

---

## [2026-04-30] init | RedClaw bootstrap
```

- [ ] **Step 3: 写 indices/ 三个骨架**

`indices/by-capability.md`:
```markdown
# By Capability

> 自动生成。

_(empty)_
```

`indices/by-vuln-type.md`:
```markdown
# By Vulnerability Type

> 自动生成。

_(empty)_
```

`indices/by-year.md`:
```markdown
# By Year

> 自动生成。

_(empty)_
```

- [ ] **Step 4: 创建空目录占位**

Run:
```bash
mkdir -p topics writeups patches tools pocs/linux pocs/macos
touch topics/.gitkeep writeups/.gitkeep patches/.gitkeep tools/.gitkeep pocs/linux/.gitkeep pocs/macos/.gitkeep
```

- [ ] **Step 5: Commit**

```bash
git add index.md log.md indices/ topics/.gitkeep writeups/.gitkeep patches/.gitkeep tools/.gitkeep pocs/linux/.gitkeep pocs/macos/.gitkeep
git commit -m "chore: scaffold index/log/indices and empty top-level dirs"
```

---

## Task 4: 示例 CVE 条目 —— DirtyPipe

验证 SCHEMA 写得通；lint 测试也会拿它做基准。

**Files:**
- Create: `pocs/linux/CVE-2022-0847/README.md`
- Create: `pocs/linux/CVE-2022-0847/exploit.c` (占位源码，标注非真实 exploit)
- Create: `pocs/linux/CVE-2022-0847/build.sh`

- [ ] **Step 1: 写 pocs/linux/CVE-2022-0847/README.md**

```markdown
---
cve: CVE-2022-0847
aliases: [DirtyPipe]
cvss: 7.8
disclosed: 2022-03-07
patched: 2022-02-23
target_os: linux
target_versions: ">=5.8, <5.16.11 | <5.15.25 | <5.10.102"
vuln_type: [uninitialized-memory, pipe-buffer]
capability: [LPE, arbitrary-file-write]
status: partial
references:
  - https://dirtypipe.cm4all.com/
  - https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9d2231c5d74e13b2a0546fee6737ee4446017903
---

## TL;DR

Linux 内核 5.8+ 管道缓冲区未清理 `PIPE_BUF_FLAG_CAN_MERGE` 标志，导致只读文件的 page cache 可被非特权用户改写，实现任意只读文件覆写 → LPE。

## 影响范围

- Linux kernel `>= 5.8`
- 修复版本：`5.16.11`, `5.15.25`, `5.10.102`
- 架构无关；不依赖特殊 capability

## 根因

`copy_page_to_iter_pipe()` 和 `push_pipe()` 在申请新 pipe_buffer 时复用了上次的 flags 字段，未清零 `PIPE_BUF_FLAG_CAN_MERGE`。攻击者通过预先污染 flags，再 splice 只读文件到 pipe，后续写操作会直接写入 page cache。

## 利用思路

1. 创建 pipe 并写满以"污染" `flags`
2. 清空 pipe（保留 flags）
3. `splice(ro_fd, pipe, 1, 0)` 把目标文件 page 绑到 pipe_buffer
4. 向 pipe 写入：绕过 write 路径，直接改 page cache
5. 落地：改写 `/etc/passwd` / suid binary → root shell

## 复现步骤

```bash
bash build.sh
./dirtypipe /etc/passwd
```

预期输出：任意 root 密码被改写，`su` 成功。（本仓库中 `exploit.c` 是占位，需替换为正式 exploit 源码再使用）

## 检测与修复

Patch（commit `9d2231c5d74e`）在 `copy_page_to_iter_pipe` 和 `push_pipe` 里初始化 `buf->flags = 0`。检测：内核版本比较即可；运行时信号需看 splice/write 异常组合。

## 参考

- https://dirtypipe.cm4all.com/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9d2231c5d74e13b2a0546fee6737ee4446017903
```

- [ ] **Step 2: 写 exploit.c 占位**

```c
/*
 * DirtyPipe (CVE-2022-0847) — PLACEHOLDER
 *
 * 这是一个占位文件，用于验证仓库 SCHEMA 落地。
 * 正式 exploit 请从 https://dirtypipe.cm4all.com/ 获取 Max Kellermann 的原版 PoC。
 */
#include <stdio.h>
int main(void) {
    fprintf(stderr, "placeholder — replace with real exploit\n");
    return 1;
}
```

- [ ] **Step 3: 写 build.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
cc -O2 -o dirtypipe exploit.c
```

然后运行 `chmod +x pocs/linux/CVE-2022-0847/build.sh`。

- [ ] **Step 4: Commit**

```bash
git add pocs/linux/CVE-2022-0847/
git commit -m "feat(pocs): add DirtyPipe CVE-2022-0847 as schema exemplar"
```

---

## Task 5: lint.py —— 依赖与骨架

**Files:**
- Create: `tools/requirements.txt`
- Create: `tools/lint.py`
- Create: `tests/__init__.py`, `tests/test_lint.py`

- [ ] **Step 1: 写 tools/requirements.txt**

```
PyYAML>=6.0
pytest>=7.0
```

- [ ] **Step 2: 创建虚拟环境并安装**

Run:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r tools/requirements.txt
```

- [ ] **Step 3: 写 tools/lint.py 骨架**

```python
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
```

- [ ] **Step 4: 写 tests/__init__.py（空文件）+ tests/test_lint.py 基础 import**

`tests/__init__.py`: 空文件。

`tests/test_lint.py`:
```python
import sys
from pathlib import Path

# 让 tests/ 能 import tools/lint.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import lint  # noqa: E402
```

- [ ] **Step 5: 验证骨架 import 不报错**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: `collected 0 items` (无 test，但无 import 错)

- [ ] **Step 6: Commit**

```bash
git add tools/requirements.txt tools/lint.py tests/__init__.py tests/test_lint.py
git commit -m "feat(tools): scaffold lint.py with Entry dataclass"
```

---

## Task 6: parse_frontmatter —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
def test_parse_frontmatter_basic(tmp_path):
    f = tmp_path / "r.md"
    f.write_text("---\ncve: CVE-2022-0847\n---\n\nbody\n", encoding="utf-8")
    fm = lint.parse_frontmatter(f)
    assert fm == {"cve": "CVE-2022-0847"}


def test_parse_frontmatter_missing(tmp_path):
    f = tmp_path / "r.md"
    f.write_text("no frontmatter here\n", encoding="utf-8")
    assert lint.parse_frontmatter(f) is None
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: FAIL `AttributeError: module 'lint' has no attribute 'parse_frontmatter'`

- [ ] **Step 3: 实现 parse_frontmatter**

追加到 `tools/lint.py`:
```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): parse_frontmatter with tests"
```

---

## Task 7: validate_entry —— 必填字段 —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
def test_validate_entry_complete_ok():
    fm = {
        "cve": "CVE-2022-0847",
        "target_os": "linux",
        "target_versions": ">=5.8",
        "vuln_type": ["uninitialized-memory"],
        "capability": ["LPE"],
        "status": "partial",
        "references": ["https://example.com"],
    }
    assert lint.validate_entry(fm) == []


def test_validate_entry_missing_field():
    fm = {
        "cve": "CVE-2022-0847",
        "target_os": "linux",
        "target_versions": ">=5.8",
        "vuln_type": ["x"],
        "capability": ["LPE"],
        "status": "partial",
        # references missing
    }
    errors = lint.validate_entry(fm)
    assert any("references" in e for e in errors)


def test_validate_entry_invalid_status():
    fm = {
        "cve": "CVE-2022-0847",
        "target_os": "linux",
        "target_versions": ">=5.8",
        "vuln_type": ["x"],
        "capability": ["LPE"],
        "status": "bogus",
        "references": ["https://x"],
    }
    errors = lint.validate_entry(fm)
    assert any("status" in e for e in errors)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 3 new tests FAIL

- [ ] **Step 3: 实现 validate_entry**

追加到 `tools/lint.py`:
```python
def validate_entry(fm: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, "", []):
            errors.append(f"missing required field: {key}")
    status = fm.get("status")
    if status is not None and status not in VALID_STATUS:
        errors.append(f"invalid status: {status!r} (must be one of {sorted(VALID_STATUS)})")
    return errors
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): validate_entry checks required fields and status enum"
```

---

## Task 8: validate_entry —— 条件必填 —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
BASE_FM = {
    "cve": "CVE-2022-0847",
    "target_os": "linux",
    "target_versions": ">=5.8",
    "vuln_type": ["x"],
    "capability": ["LPE"],
    "references": ["https://x"],
}


def test_verified_requires_tested_on():
    fm = {**BASE_FM, "status": "verified"}
    errors = lint.validate_entry(fm)
    assert any("tested_on" in e for e in errors)


def test_verified_with_tested_on_ok():
    fm = {**BASE_FM, "status": "verified",
          "tested_on": [{"os": "Ubuntu 20.04", "kernel": "5.13", "result": "root"}]}
    assert lint.validate_entry(fm) == []


def test_archived_requires_reason_and_date():
    fm = {**BASE_FM, "status": "archived"}
    errors = lint.validate_entry(fm)
    assert any("archived_reason" in e for e in errors)
    assert any("archived_date" in e for e in errors)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 3 new tests FAIL

- [ ] **Step 3: 扩展 validate_entry**

替换 `tools/lint.py` 里的 `validate_entry`：
```python
def validate_entry(fm: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_FIELDS:
        if key not in fm or fm[key] in (None, "", []):
            errors.append(f"missing required field: {key}")
    status = fm.get("status")
    if status is not None and status not in VALID_STATUS:
        errors.append(f"invalid status: {status!r} (must be one of {sorted(VALID_STATUS)})")
    if status == "verified":
        if not fm.get("tested_on"):
            errors.append("status=verified requires non-empty tested_on")
    if status == "archived":
        if not fm.get("archived_reason"):
            errors.append("status=archived requires archived_reason")
        if not fm.get("archived_date"):
            errors.append("status=archived requires archived_date")
    return errors
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): conditional requirements for verified/archived status"
```

---

## Task 9: collect_entries —— 扫描 pocs/ —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
def _mk_entry(base: Path, cve: str, os_name: str, extra_fm: dict | None = None):
    d = base / "pocs" / os_name / cve
    d.mkdir(parents=True)
    fm = {
        "cve": cve,
        "target_os": os_name,
        "target_versions": ">=1.0",
        "vuln_type": ["UAF"],
        "capability": ["LPE"],
        "status": "partial",
        "references": ["https://x"],
    }
    if extra_fm:
        fm.update(extra_fm)
    body = "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n\n## TL;DR\n\nstub\n"
    (d / "README.md").write_text(body, encoding="utf-8")
    return d


def test_collect_entries(tmp_path):
    import yaml  # noqa: F401  (imported above in lint, but local scope)
    _mk_entry(tmp_path, "CVE-2022-0847", "linux")
    _mk_entry(tmp_path, "CVE-2023-0001", "macos")
    entries = lint.collect_entries(tmp_path / "pocs")
    cves = sorted(e.cve for e in entries)
    assert cves == ["CVE-2022-0847", "CVE-2023-0001"]
    for e in entries:
        assert e.errors == []


def test_collect_entries_reports_errors(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux",
              extra_fm={"status": "verified"})  # missing tested_on
    entries = lint.collect_entries(tmp_path / "pocs")
    assert len(entries) == 1
    assert any("tested_on" in e for e in entries[0].errors)
```

注意：测试文件顶部需要 `import yaml`，在 tests/test_lint.py 第一次 import 时追加：
```python
import yaml
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 2 new tests FAIL

- [ ] **Step 3: 实现 collect_entries**

追加到 `tools/lint.py`:
```python
def collect_entries(pocs_dir: Path) -> list[Entry]:
    entries: list[Entry] = []
    if not pocs_dir.exists():
        return entries
    for readme in sorted(pocs_dir.glob("*/*/README.md")):
        fm = parse_frontmatter(readme)
        if fm is None:
            entries.append(Entry(path=readme, frontmatter={},
                                 errors=["no frontmatter"]))
            continue
        errors = validate_entry(fm)
        # cve 字段和目录名一致性检查
        dir_cve = readme.parent.name
        if fm.get("cve") != dir_cve:
            errors.append(f"cve field {fm.get('cve')!r} != dir name {dir_cve!r}")
        entries.append(Entry(path=readme, frontmatter=fm, errors=errors))
    return entries
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): collect_entries walks pocs/ and validates frontmatter"
```

---

## Task 10: 索引重建 —— 主索引 —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
def test_build_main_index_groups_by_os(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux")
    _mk_entry(tmp_path, "CVE-2023-0001", "macos")
    entries = lint.collect_entries(tmp_path / "pocs")
    md = lint.build_main_index(entries)
    assert "# Master Index" in md
    assert "## linux" in md
    assert "## macos" in md
    assert "CVE-2022-0847" in md
    assert "CVE-2023-0001" in md


def test_build_main_index_excludes_archived(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux")
    _mk_entry(tmp_path, "CVE-2020-0001", "linux",
              extra_fm={"status": "archived",
                        "archived_reason": "obsolete",
                        "archived_date": "2026-01-01"})
    entries = lint.collect_entries(tmp_path / "pocs")
    md = lint.build_main_index(entries)
    assert "CVE-2022-0847" in md
    assert "CVE-2020-0001" not in md
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 2 new tests FAIL

- [ ] **Step 3: 实现 build_main_index**

追加到 `tools/lint.py`:
```python
def _entry_line(e: Entry) -> str:
    fm = e.frontmatter
    cve = fm.get("cve", "?")
    aliases = fm.get("aliases") or []
    alias_str = f" ({', '.join(aliases)})" if aliases else ""
    caps = ", ".join(fm.get("capability", []))
    vtypes = ", ".join(fm.get("vuln_type", []))
    status = fm.get("status", "?")
    versions = fm.get("target_versions", "?")
    rel = e.path.relative_to(REPO_ROOT) if e.path.is_absolute() and REPO_ROOT in e.path.parents else e.path
    return f"- [{cve}]({rel.parent}/README.md){alias_str} — `{versions}` — {caps} — *{vtypes}* — **{status}**"


def build_main_index(entries: list[Entry]) -> str:
    lines = ["# Master Index",
             "",
             "> 自动生成，不要手改。`python tools/lint.py --rebuild-indices` 重建。",
             ""]
    buckets: dict[str, list[Entry]] = {}
    for e in entries:
        if e.frontmatter.get("status") == "archived":
            continue
        os_name = e.frontmatter.get("target_os", "unknown")
        buckets.setdefault(os_name, []).append(e)
    for os_name in sorted(buckets):
        lines.append(f"## {os_name}")
        lines.append("")
        for e in sorted(buckets[os_name], key=lambda x: x.frontmatter.get("cve", "")):
            lines.append(_entry_line(e))
        lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): build_main_index grouped by target_os, skips archived"
```

---

## Task 11: 交叉索引 —— capability / vuln_type / year —— TDD

**Files:**
- Modify: `tools/lint.py`
- Modify: `tests/test_lint.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_lint.py`:
```python
def test_build_capability_index(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux",
              extra_fm={"capability": ["LPE", "arbitrary-file-write"]})
    _mk_entry(tmp_path, "CVE-2023-0001", "macos",
              extra_fm={"capability": ["sandbox-escape"]})
    entries = lint.collect_entries(tmp_path / "pocs")
    md = lint.build_capability_index(entries)
    assert "## LPE" in md
    assert "## arbitrary-file-write" in md
    assert "## sandbox-escape" in md
    # cross-listing: same CVE appears under both tags
    assert md.count("CVE-2022-0847") == 2


def test_build_vuln_type_index(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux",
              extra_fm={"vuln_type": ["UAF", "race"]})
    entries = lint.collect_entries(tmp_path / "pocs")
    md = lint.build_vuln_type_index(entries)
    assert "## UAF" in md
    assert "## race" in md


def test_build_year_index_keeps_archived(tmp_path):
    _mk_entry(tmp_path, "CVE-2022-0847", "linux")
    _mk_entry(tmp_path, "CVE-2020-0001", "linux",
              extra_fm={"status": "archived",
                        "archived_reason": "x", "archived_date": "2026-01-01"})
    entries = lint.collect_entries(tmp_path / "pocs")
    md = lint.build_year_index(entries)
    assert "## 2022" in md
    assert "## 2020" in md
    assert "CVE-2020-0001" in md   # archived 仍出现在年份索引
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 3 new tests FAIL

- [ ] **Step 3: 实现三个索引**

追加到 `tools/lint.py`:
```python
def _build_tag_index(entries: list[Entry], tag_field: str, title: str,
                    include_archived: bool = False) -> str:
    lines = [f"# {title}", "", "> 自动生成。", ""]
    buckets: dict[str, list[Entry]] = {}
    for e in entries:
        if not include_archived and e.frontmatter.get("status") == "archived":
            continue
        for tag in e.frontmatter.get(tag_field, []) or []:
            buckets.setdefault(tag, []).append(e)
    for tag in sorted(buckets):
        lines.append(f"## {tag}")
        lines.append("")
        for e in sorted(buckets[tag], key=lambda x: x.frontmatter.get("cve", "")):
            lines.append(_entry_line(e))
        lines.append("")
    return "\n".join(lines)


def build_capability_index(entries: list[Entry]) -> str:
    return _build_tag_index(entries, "capability", "By Capability")


def build_vuln_type_index(entries: list[Entry]) -> str:
    return _build_tag_index(entries, "vuln_type", "By Vulnerability Type")


def build_year_index(entries: list[Entry]) -> str:
    lines = ["# By Year", "", "> 自动生成。归档条目仍列出。", ""]
    buckets: dict[str, list[Entry]] = {}
    for e in entries:
        cve = e.frontmatter.get("cve", "")
        # CVE-YYYY-NNNN → YYYY
        parts = cve.split("-")
        year = parts[1] if len(parts) >= 3 and parts[0] == "CVE" else "unknown"
        buckets.setdefault(year, []).append(e)
    for year in sorted(buckets, reverse=True):
        lines.append(f"## {year}")
        lines.append("")
        for e in sorted(buckets[year], key=lambda x: x.frontmatter.get("cve", "")):
            lines.append(_entry_line(e))
        lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 15 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): build cross-cutting indices (capability/vuln-type/year)"
```

---

## Task 12: CLI 入口

**Files:**
- Modify: `tools/lint.py`

- [ ] **Step 1: 写失败测试（CLI 单元测试可选，但 smoke test 一下 main）**

追加到 `tests/test_lint.py`:
```python
def test_main_exit_zero_on_empty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(lint, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint, "POCS_DIR", tmp_path / "pocs")
    (tmp_path / "pocs").mkdir()
    rc = lint.main([])
    assert rc == 0
```

- [ ] **Step 2: 跑测试确认失败**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: FAIL `AttributeError: ... no attribute 'main'`

- [ ] **Step 3: 实现 main**

追加到 `tools/lint.py`:
```python
import argparse

INDEX_TARGETS = {
    "index.md": build_main_index,
    "indices/by-capability.md": build_capability_index,
    "indices/by-vuln-type.md": build_vuln_type_index,
    "indices/by-year.md": build_year_index,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lint.py",
                                 description="RedClaw frontmatter + index tool")
    ap.add_argument("--rebuild-indices", action="store_true",
                    help="regenerate index.md and indices/*.md")
    args = ap.parse_args(argv)

    entries = collect_entries(POCS_DIR)

    total_errors = 0
    for e in entries:
        if e.errors:
            print(f"[FAIL] {e.path.relative_to(REPO_ROOT)}")
            for err in e.errors:
                print(f"   - {err}")
            total_errors += len(e.errors)
        else:
            print(f"[ OK ] {e.path.relative_to(REPO_ROOT)}")

    if args.rebuild_indices:
        for rel, builder in INDEX_TARGETS.items():
            out = REPO_ROOT / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(builder(entries) + "\n", encoding="utf-8")
            print(f"[gen ] {rel}")

    if total_errors:
        print(f"\n{total_errors} error(s)")
        return 1
    print("\nall good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 跑测试确认通过**

Run: `.venv/bin/pytest tests/test_lint.py -v`
Expected: 16 passed

- [ ] **Step 5: Commit**

```bash
git add tools/lint.py tests/test_lint.py
git commit -m "feat(lint): CLI entrypoint with --rebuild-indices flag"
```

---

## Task 13: 端到端跑通 —— 用真实仓库生成索引

**Files:**
- Modify: `index.md`, `indices/by-capability.md`, `indices/by-vuln-type.md`, `indices/by-year.md`

- [ ] **Step 1: 跑 lint 校验示例 CVE**

Run: `.venv/bin/python tools/lint.py`
Expected: `[ OK ] pocs/linux/CVE-2022-0847/README.md` 且 `all good`（exit 0）

如果失败：按错误信息修 `pocs/linux/CVE-2022-0847/README.md` frontmatter，回到这一步。

- [ ] **Step 2: 重建所有索引**

Run: `.venv/bin/python tools/lint.py --rebuild-indices`
Expected: 四个索引文件被写入，`all good`。

- [ ] **Step 3: 人工检查生成的索引**

Run:
```bash
cat index.md
cat indices/by-capability.md
cat indices/by-vuln-type.md
cat indices/by-year.md
```
Expected：DirtyPipe 条目出现在 `## linux` 下，出现在 `## LPE` / `## arbitrary-file-write` 下，出现在 `## uninitialized-memory` / `## pipe-buffer` 下，出现在 `## 2022` 下。

- [ ] **Step 4: 更新 log.md**

在 `log.md` 末尾追加：
```markdown
## [2026-04-30] ingest | CVE-2022-0847 DirtyPipe (linux, LPE) — schema exemplar
```

- [ ] **Step 5: Commit 生成的索引和 log**

```bash
git add index.md indices/ log.md
git commit -m "chore: first index rebuild with DirtyPipe entry"
```

---

## Task 14: 更新 .gitignore 和文档收尾

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 确认 .gitignore 覆盖 tests 产物和 venv**

Run: `cat .gitignore`
预期应包含 `.venv/`、`__pycache__/`、`._*`、`.DS_Store`、`*.pyc`（Task 0 已创建；若 `.pytest_cache/` 也需要忽略则追加）。

如需追加：
```
.pytest_cache/
```

- [ ] **Step 2: 验证 git 工作目录干净**

Run: `git status`
Expected: `nothing to commit, working tree clean`（若 .pytest_cache 被追踪则先 `git rm --cached -r .pytest_cache` 再 commit）。

- [ ] **Step 3: 跑一遍全量测试**

Run: `.venv/bin/pytest tests/ -v`
Expected: 16 passed。

- [ ] **Step 4: 最后一次 commit（如有 .gitignore 变动）**

```bash
git add .gitignore
git commit -m "chore: ignore pytest cache"
```
若无改动，跳过。

---

## Done Criteria

- [ ] 目录结构与 spec 第 3 节一致
- [ ] `SCHEMA.md` 完整，含必填/条件必填/受控词表
- [ ] `README.md` 含四条检索入口和五个 operation 速查
- [ ] 示例 CVE `pocs/linux/CVE-2022-0847/` 通过 lint
- [ ] `tools/lint.py` 16 个测试全 pass
- [ ] `.venv/bin/python tools/lint.py --rebuild-indices` 能在新条目加入后一键同步所有索引
- [ ] git log 干净，每个任务一次 commit
