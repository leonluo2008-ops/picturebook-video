# 测试数据清理记录（2026-06-07）

> **v1.0.3+pic12 闭环清理**（用户拍板）
> 触发：v1.0.3+pic12 上线 + pic4 v6 实战沉淀完毕 + 21 新铁律落地 + 铁律 #80 情绪基调 AI 判定标准建立
> 原则：保留 skill 仓（生产代码），清理测试产物（pic1-4 + 临时文件）

---

## 1. 清理范围（不可逆 · 已完成）

### A. 9 个 pic 测试项目目录（共释放 ~352M）
| 目录 | 大小 | 清理原因 |
|---|---|---|
| `/home/luo/huiben-projects/20260603-eat-picbook/` | 52M | 早期 eat 绘本测试，已无关 |
| `/home/luo/huiben-projects/20260603-feishu-new/` | 17M | 早期飞书功能测试，已无关 |
| `/home/luo/huiben-projects/20260604-feishu-绘本/` | 88M | 早期飞书绘本测试，已无关 |
| `/home/luo/huiben-projects/20260605-folder-test/` | 25M | 早期 folder 调试 |
| `/home/luo/huiben-projects/20260605-folder2-test/` | 41M | 早期 folder 调试 |
| `/home/luo/huiben-projects/20260606-pic1/` | 19M | pic1 早期实战（v0.7.x），结论已沉淀 |
| `/home/luo/huiben-projects/20260606-pic2/` | 37M | pic2 8 clip v15 翻车教训已写进 SKILL.md |
| `/home/luo/huiben-projects/20260607-pic3/` | 19M | pic3 9 clip 实战已写进 references/2026-06-07-pic3-welcome-validation.md |
| `/home/luo/huiben-projects/20260607-pic4-compress/` | 54M | pic4 9 clip v6 实战已写进 references/2026-06-07-pic4-no-validation.md |

**总释放**：~352M

### B. /tmp 测试文件（共释放 ~58M）
| 路径 | 大小 | 清理原因 |
|---|---|---|
| `/tmp/pic2-clip1-frames/` | 8.6M | vision_analyze 抽帧，结论已沉淀 |
| `/tmp/pic2-v1-clip1-frames/` | 4.9M | vision_analyze 抽帧，结论已沉淀 |
| `/tmp/pic2-v1-clip1~7-fixed-frames/` × 7 | ~43M | vision_analyze 抽帧，结论已沉淀 |
| `/tmp/pic2-v1-logs/` | 40K | pic2 v1 submit 日志 |
| `/tmp/pic2-v1-clip{1-8}-prompt.txt` × 8 | 32K | pic2 v1 prompt 文件（已写进 SKILL.md）|
| `/tmp/pic2-v1-driver.sh` + `pic2-v1-submit-all.sh` | 12K | pic2 v1 提交脚本（已被 skill 仓 fill_v15_template.py 取代）|
| `/tmp/chevereto_1.jpg` | 100K | chevereto 图床测试图 |
| `/tmp/uguu_test.mp3` | 164K | uguu 图床早期测试 |
| `/tmp/seedance_*.log` × 5 | 20K | seedance 历史日志 |
| `/tmp/seedance_result.json` + `seedance-env.sh` | 2K | 单次结果，已无关 |
| `/tmp/seedance_backup.py` | 17K | seedance 旧脚本备份（正式版在 skill 仓）|

**总释放**：~58M

---

## 2. 保留资产（生产代码 · 长期资产）

| 路径 | 状态 | 备注 |
|---|---|---|
| `/home/luo/.hermes/profiles/huiben/skills/creative/picturebook-video/` | ✅ v1.0.3+pic12 | 主体 skill 仓 |
| `/home/luo/.hermes/profiles/huiben/skills/.hub/` + `.curator_backups/` | ✅ 保留 | skill hub 索引和备份 |
| `/home/luo/huiben-projects/` | ✅ 空目录保留 | 给新项目用 |
| `/home/luo/.lark-cli/` | ✅ 保留 | 飞书 CLI 工具 |
| `~/.config/gh/` | ✅ 保留 | GitHub CLI 配置 + token |
| `/home/luo/.hermes/memory/MEMORY.md` | ✅ 保留 | 跨会话记忆 |

---

## 3. 关键搬迁（持久化 · 不可丢）

### `/tmp/seedance_docs/` → `references/seedance-official-docs/`

**原因**：`/tmp` 重启会丢，但官方教程是**兜底文档**（遇到 skill 解决不了的问题必查），必须持久化。

**搬迁清单**：
- `1-Doubao_Seedance_2.0_系列教程.docx` (103K)
- `1-Doubao_Seedance_2.0_系列教程.md` (77K)
- `2-Doubao_Seedance_2.0_系列提示词指南.docx` (54K)
- `2-Doubao_Seedance_2.0_系列提示词指南.md` (36K)
- `3-视频生成教程.docx` (130K)
- `3-视频生成教程.md` (100K)

**总大小**：508K

**新增索引**：`references/seedance-official-docs/README.md`（4.3K · 4.2K 内容 + 检索词）

**SKILL.md 引用**：失败模式决策树新增一行"遇到 skill 兜不住的问题 → 先查官方 docs 索引"

---

## 4. 总计

| 项 | 数量 |
|---|---|
| 释放磁盘空间 | **~410M** |
| 删除文件/目录 | 9 个项目目录 + 22 个 /tmp 文件/目录 |
| 保留+搬迁文件 | 6 个官方教程 + 1 个 README 索引 |
| 新增 references 文档 | 2 个（seedance-official-docs/README.md + 本文件）|
| git commit | 1 个（v1.0.3+pic12 cleanup）|

---

## 5. 复现保证

**任何 pic1-4 实战数据**都可以从 skill 仓 references 复现：
- pic2 翻车 → `SKILL.md` § v1.0.0 实战翻车决策树 + § v0.7.1+pic7
- pic3 实战 → `references/2026-06-07-pic3-welcome-validation.md`
- pic4 v6 实战 → `references/2026-06-07-pic4-no-validation.md`
- pic4 v5 节奏公式 → `references/2026-06-07-pic4-no-v5-rhythm-formula.md`
- pic4 v6 最终版 → `references/2026-06-07-pic4-no-v6-final.md`

**任何 seedance 官方知识**都可以从 `references/seedance-official-docs/` 查：
- 写 prompt 问题 → `2-系列提示词指南.md`
- 功能/参数问题 → `1-系列教程.md` + `3-视频生成教程.md`

---

## 6. 检索词

`测试数据清理` / `2026-06-07 cleanup` / `v1.0.3+pic12 闭环` / `seedance 官方教程持久化` / `pic1-4 实战复现` / `410M 释放`
