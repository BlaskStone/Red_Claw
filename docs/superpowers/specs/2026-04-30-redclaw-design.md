# RedClaw —— 攻防实战武器库设计

**日期**：2026-04-30
**定位**：Linux / macOS CVE + POC 武器库（Red Team 取向），按 Karpathy LLM-Wiki 模式组织

---

## 1. 目标与非目标

### 目标
- 拿到一个目标（OS + 内核/应用版本）后，能在 1 分钟内定位到可用的 POC
- 每个 CVE 条目自包含：一个文件夹里既有原理说明又有可运行代码，单独拷走就能用
- 四维可检索：目标系统/版本、攻击能力、漏洞类型/子系统、CVE 年份
- 索引随 ingest 自动同步，人工只维护条目正文，不维护索引
- 支持经验沉淀：单 CVE 里的技法能提炼到横向 `topics/` 或实战复盘 `writeups/`

### 非目标（YAGNI）
- 不做 CVE 数据库全量镜像，只收录自己用过/研究过的
- 不做在线 Web 界面，纯 markdown + 本地工具
- 不做自动化漏洞扫描/批量打点能力

---

## 2. 分层模型（对应 Karpathy 三层）

| 层 | 内容 | 目录 |
|---|---|---|
| **Schema** | 写法约束、字段定义 | `SCHEMA.md` |
| **Wiki** | 人工维护的条目与分析 | `pocs/*/README.md`、`topics/`、`writeups/` |
| **Raw sources** | 原始资料 | `patches/`、外部链接（存于 frontmatter `references`） |
| **派生产物** | 自动生成，人不手改 | `index.md`、`indices/*`、`log.md` 的索引摘要部分 |
| **工具链** | 辅助执行与维护 | `tools/` |

---

## 3. 目录结构

```
RedClaw/
├── README.md                    项目入口：用法 + 主索引链接
├── SCHEMA.md                    CVE 条目/topics/writeups 的写法约束
├── index.md                     主索引 —— 按 OS + 内核/应用版本（自动生成）
├── log.md                       时间线：ingest / update / promote / archive 记录
│
├── indices/                     交叉索引（自动生成）
│   ├── by-capability.md         LPE / sandbox-escape / kernel-RCE / container-escape / ...
│   ├── by-vuln-type.md          UAF / OOB / race / type-confusion / uninitialized-mem / ...
│   └── by-year.md               CVE 年份
│
├── pocs/
│   ├── linux/
│   │   └── CVE-YYYY-NNNN/
│   │       ├── README.md        条目正文（wiki 页）
│   │       ├── exploit.c        源码 / 脚本
│   │       ├── build.sh         编译/打包
│   │       └── notes/           调试笔记、patch 片段、参考截图
│   └── macos/
│       └── CVE-YYYY-NNNN/
│
├── topics/                      横向技法（不绑定某个 CVE）
│   └── linux-kernel-heap-spray.md
│
├── writeups/                    实战复盘（某次完整利用链的故事）
│   └── 2026-04-ios-jailbreak-chain.md
│
├── patches/                     官方补丁归档（raw source）
│   └── CVE-YYYY-NNNN/
│       └── <fix-commit>.diff
│
├── tools/                       辅助工具
│   ├── lint.py                  校验 + 重建索引
│   ├── ingest.py                交互式新增 CVE 脚手架
│   └── ...
│
└── docs/
    └── superpowers/specs/       设计文档
```

---

## 4. SCHEMA —— CVE 条目写法

每个 `pocs/<os>/CVE-YYYY-NNNN/README.md` 必须遵守：

### 4.1 Frontmatter（YAML，可检索字段）

```yaml
---
cve: CVE-2022-0847
aliases: [DirtyPipe]
cvss: 7.8
disclosed: 2022-03-07
patched: 2022-02-23
target_os: linux                 # linux | macos | ios | ipados
target_versions: ">=5.8, <5.16.11 | <5.15.25 | <5.10.102"
vuln_type: [uninitialized-memory, pipe-buffer]
capability: [LPE, arbitrary-file-write]
status: verified                 # verified | partial | theoretical | archived
archived_reason: ""              # 仅 archived 时填
archived_date: ""                # 仅 archived 时填
tested_on:
  - { os: "Ubuntu 20.04", kernel: "5.13.0-30", result: "root shell" }
references:
  - https://dirtypipe.cm4all.com/
---
```

**必填**：`cve`, `target_os`, `target_versions`, `vuln_type`, `capability`, `status`, `references`
**条件必填**：`status: verified` 必须有 `tested_on` 至少一条；`status: archived` 必须有 `archived_reason` + `archived_date`

### 4.2 标准章节（七段）

```markdown
## TL;DR           一句话：是什么 + 能干什么
## 影响范围         具体版本/架构/配置前提、不可达的前置条件
## 根因             漏洞机理，patch 前代码片段 + 为什么错
## 利用思路         primitive → 能力提升 → 最终落点（列主要步骤）
## 复现步骤         环境搭建、编译、运行、预期输出
## 检测与修复       patch diff 要点、绕过可能性、监测信号
## 参考             paper / blog / commit / 其他 POC 仓库

## See also        （可选）promote 后的反向引用到 topics/writeups
```

### 4.3 `topics/` 和 `writeups/` 的 frontmatter

```yaml
---
kind: topic                      # topic | writeup
title: "Linux 内核堆喷方法论"
covers_cves: [CVE-2022-0847, CVE-2023-XXXXX]
tags: [heap-spray, linux-kernel, primitive]
---
```

---

## 5. Operations

五类维护动作。除了 ingest 和 promote 需要人写正文，其余由 `tools/` 自动完成。

### 5.1 `ingest` —— 新增 CVE
1. `tools/ingest.py CVE-YYYY-NNNN --os linux` 创建目录骨架和 frontmatter 模板
2. 人填写 `README.md` 正文 + 放 exploit 源码
3. `patches/CVE-YYYY-NNNN/` 放官方补丁（可选）
4. `tools/lint.py --rebuild-indices` 重建 `index.md` 和 `indices/*`
5. log.md 追加：`## [2026-04-30] ingest | CVE-2022-0847 DirtyPipe (linux, LPE)`

### 5.2 `query` —— 检索
- 按 target：`index.md` → OS → 版本段
- 按需求：`indices/by-capability.md`
- 按研究：`indices/by-vuln-type.md`
- 按时间：`indices/by-year.md`

### 5.3 `lint` —— 体检
`tools/lint.py` 执行：
- frontmatter 字段完整性（必填/条件必填）
- `status: verified` 必须有 `tested_on`
- `status: archived` 必须有 `archived_reason` / `archived_date`
- 索引与实际目录一致性（孤儿条目、死链）
- 参考链接连通性（`--check-links` 可选，慢）
- `log.md` 时间线与实际文件 mtime 的一致性（软告警）

### 5.4 `promote` —— 抽经验
触发：两个以上 CVE 用同类技法，或单条利用链值得独立成文。
1. 新建 `topics/<slug>.md` 或 `writeups/<slug>.md`
2. 在相关 CVE 的 `README.md` 追加 `## See also` 反向链接
3. log.md 追加：`## [2026-04-30] promote | pipe-primitive → topics/linux-pipe-primitives.md`

### 5.5 `archive` —— 归档
触发：目标版本过时、POC 永久失效、被其他条目合并。
**不删不移**，只改 frontmatter：`status: archived` + `archived_reason` + `archived_date`。
`lint` 重建索引时：
- 从 `index.md` 主索引剔除
- 在 `indices/by-year.md` 保留（历史可查）
- 在 `indices/by-capability.md` / `by-vuln-type.md` 降到折叠区末尾
log.md 追加：`## [2026-04-30] archive | CVE-20xx-xxxx — <reason>`

---

## 6. 索引生成规则

`tools/lint.py --rebuild-indices` 从所有 `pocs/*/*/README.md` 的 frontmatter 聚合：

### 6.1 `index.md`（主索引）
按 `target_os` 分章，每章内按 `target_versions` 的最高版本降序：

```markdown
## Linux
### Kernel 6.x
- [CVE-20xx-xxxx] 一句话标题 — LPE, UAF @ io_uring — verified
### Kernel 5.15.x
- ...

## macOS
### macOS 14.x
- ...
```

### 6.2 `indices/by-capability.md`
按 `capability` 数组的每个值分章（CVE 会出现在多个章节）：

```markdown
## LPE
- [CVE-2022-0847] DirtyPipe — linux kernel uninitialized mem — verified

## sandbox-escape
- ...
```

`by-vuln-type.md` 和 `by-year.md` 同理。

---

## 7. 落地步骤（实现层面）

Spec 批准后的落地顺序：

1. 创建顶层 `README.md` / `SCHEMA.md` / 空 `index.md` / 空 `log.md`
2. 创建 `indices/` 三个文件骨架
3. 创建 `pocs/linux/` `pocs/macos/` 空目录（`.gitkeep`）
4. 创建 `topics/` `writeups/` `patches/` `tools/` 空目录（`.gitkeep`）
5. 写一个示例 CVE 条目（如 `pocs/linux/CVE-2022-0847/`）验证 SCHEMA 跑得通
6. 写 `tools/lint.py` 基础版（frontmatter 校验 + 重建索引）
7. 写 `tools/ingest.py` 交互式脚手架（可延后）
8. 初始化 git、首次 commit

**工具语言**：Python 3（依赖 PyYAML）。不引入框架，单文件脚本。

---

## 8. 非目标 / 暂不做

- 不集成 CVE 扫描器 / Nuclei / Metasploit
- 不做在线预览（纯本地 markdown）
- 不做多人协作的 review 流程
- `tools/ingest.py` 可暂缓到首个 CVE 落地后再写（手动建目录也不麻烦）
- 参考链接连通性检查（`lint --check-links`）初版不做

---

## 9. 开放决策点（实现期再定）

- `tools/lint.py` 是否生成 `indices/by-capability.md` 时合并 alias（如 `LPE` 与 `privilege-escalation`）—— 建议建一个受控词表
- `target_versions` 字段格式是否严格化成半结构化 DSL，还是先留字符串靠人肉解析 —— 初版先字符串
- `writeups/` 是否独立版本号（如 `v1`, `v2`），还是直接覆写 —— 建议 git history 即版本
