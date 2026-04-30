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
