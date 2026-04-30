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
