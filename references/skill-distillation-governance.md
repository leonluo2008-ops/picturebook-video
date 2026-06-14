---
name: skill-distillation-governance
description: "skill 蒸馏治理（元方法论 #M4 · 跨 skill 仓通用 · 不限于绘本视频）= 业务层 / 方法论层 / 铁律层 三层架构 + 跨本验证升铁律 3 次原则 + sibling agent 防污染 + 3-way 分类法 + 自检清单。维护陷阱 #25-26 已整合进本文档作为实战案例。"
license: Apache-2-2
metadata:
  hermes:
    tags: [distillation, governance, sibling, validation, methodology, cross-skills]
  related_skills: [picturebook-video]
---

# skill 蒸馏治理（元方法论 #M4）

> **核心命题**：绘本 / 漫剧 / 任何 skill 沉淀过程 = **3 层架构（业务/work/通用方法论）+ 跨本验证 3 次升铁律原则**。维护陷阱 #25（skill 装绘本版本号）+ #26（sibling 断链污染）已整合到本文档作为实战案例。

---

## 1. 三层架构（业务 / 方法论 / 铁律）

| 层 | 位置 | 内容 | 命名 | 寿命 |
|---|---|---|---|---|
| **业务层** | `~/.hermes/profiles/huiben/work/<日期-绘本名>/` | 每本绘本的踩坑、prompt 迭代、vision 笔记 | 含日期+绘本名 | 永远在（**不入** skill 仓）|
| **方法论层** | `references/<通用名>.md` | 跨本验证 ≥ 1 次的通用方法论 | 通用名（**不含**绘本名/日期/vX.X+picN）| 永久 |
| **铁律层** | `SKILL.md` 顶部纠错表 | 跨本验证 ≥ 3 次的硬规律 | 通用名 | 永久 |

---

## 2. 跨本验证升铁律机制（3 次原则）

```
绘本 A 跑完 → work/A/notes.md 标 "X 规律第 1 次"（业务层）
绘本 B 跑完 → work/B/notes.md 标 "X 规律第 2 次"
绘本 C 跑完 → work/C/notes.md 标 "X 规律第 3 次"
        ↓
跨本验证 ≥ 3 次 = 升 SKILL.md 铁律（铁律名 = 通用名）
        ↓
升铁律时同步：
- 在 references/ 加 1 份 <通用名>.md（记录 A/B/C 实战证据）
- 删除 3 份 work 笔记里的踩坑细节（蒸馏到 references/）
- 0 绘本名 / 0 日期 / 0 vX.X+picN 标签
```

**判定口诀**：3 次原则 = 防止"凭印象升级" = 单次翻车不该升铁律（避免 skill 仓污染）。

---

## 3. 反模式（不蒸馏 = 污染）

- ❌ **绘本 A 踩坑 → 直接写 references/A-validation.md** = 业务数据进 skill
- ❌ **单本绘本规律没跨本验证 = 升 SKILL.md 铁律** = 凭印象升级
- ❌ **"v1.0.5+picN" / "2026-06-14-XX 绘本"** 命名 = 业务标签污染通用方法论
- ❌ **绘本做完不写 work 笔记** = 业务数据丢失（下次跑没参考）
- ❌ **references 过度分裂**（同一方法论拆 N 个文件）= 单文件信息量薄 = 用户要查"整本故事节奏"得翻 3 个文件 · **正确范式：1 个跨场景元方法论 = 1 个 holistic 文档** = 触达快、好维护

---

## 4. sibling agent 防污染（陷阱 #25-26 整合）

**触发条件**：跨 agent 并发改 SKILL.md 时，sibling agent 自动补全 maintenance 章节、写新 references 引用 = 容易出现两类污染：
1. **绑绘本名**（"duck clip2 v6 翻车沉淀" / "v6 错 → v7 对 · duck clip2 真实案例"）= 违反铁律 #116 绘本名不绑
2. **指向不存在的文件**（引用 `story-arc-rhythm-paradigm.md` 但实际只建了 `holistic-storyboard-thinking.md`）= grep 报 missing

**根因**：sibling 不读本 agent 刚建的文件，凭印象编新文件名 + 直接抄用户原话附绘本名当引用。

**修复**（sibling 写完 references 后必走 3 步）：

1. **0 绘本名污染**：`grep -nE "(duck clip|duck 绘本|clip2 v6|duck 4\.jpg|duck 后续)" references/*.md` = 0 处
2. **所有引用文件存在**：`grep -oE "references/[a-zA-Z0-9_-]+\.md" SKILL.md | sort -u | while read f; do test -f "$f" || echo "❌ $f"; done` = 0 missing
3. **统一指向已建文件**：优先指向 1 个 holistic 文档，不要分裂成 3-4 个 references（"整本故事节奏" = 1 个文档最易维护）

**判定口诀**：
- sibling 写完 = 必 grep 0 绘本名 + 0 missing
- 不依赖 sibling "应该写对了" = 必自检
- references 优先 1 个 holistic 文档 > N 个分裂文件

---

## 5. 3-way 分类法（commit 前必跑）

skill 仓 `git status` 出现 N 个 untracked 文件（references/scripts/templates/ 子目录 + `_inbox/` + `data/`）= 准备 commit 时**不知道该不该 add**。

**反模式**：直接 `git add -A` = 误把绘本名污染 + 业务数据一并 commit = 违反铁律 #116 / #117。

### 3 类判定 + 动作

| 类别 | 判定标准 | 动作 |
|---|---|---|
| ✅ **应 commit** | 在 `references/` / `scripts/` / `templates/` 下 + **0 绘本名** + 是**通用方法论** | `git add <file>` |
| ❌ **绘本名污染** | 文件名或内容含特定绘本名 = 违反铁律 #117 绘本名不绑 | `rm <file>` · 内容可重写到 `work/<日期-绘本名>/` 业务笔记 |
| ❌ **业务数据** | 在 `_inbox/` / `data/` / `work/` 目录下 = 业务产物 = 违反铁律 #116 不入 skill 仓 | `rm -rf <dir>` · 或保持 untracked（不入 commit） |

### 操作流程

```bash
# 1. 看未跟踪
git status

# 2. 对每个 untracked 文件做判定
for f in $(git status --porcelain | grep '^??' | awk '{print $2}'); do
  case "$f" in
    # 业务数据 → 删
    _inbox/*|data/*|work/*) echo "❌ 业务数据·删: $f" ;;
    # 绘本名污染 → 删
    *mango*|*kangaroo*|*horse*|*cherry*|*bird*|*cow*|*banana*)
      echo "❌ 绘本名污染·删: $f" ;;
    # references/scripts/templates 通用方法论 → 检查内容是否含绘本名
    references/*|scripts/*|templates/*)
      if grep -lE "Mango|Kangaroo|Horse|Cherry|Bird|Cow|No\.|Banana" "$f" >/dev/null 2>&1; then
        echo "❌ 内容含绘本名·删: $f"
      else
        echo "✅ 通用方法论·add: $f"
      fi ;;
    *) echo "⚠️ 未知类别·人工判断: $f" ;;
  esac
done

# 3. 执行 add / rm（按上面输出操作）
```

**判断口诀**：**"`git add -A` 永远错 · 3-way 分类必跑一遍"** · **"通用方法论 = commit · 绘本名 = 删 · 业务数据 = 删/不 commit"**

---

## 6. 自检清单（沉淀前必跑 · 不靠记忆）

**核心问题**：agent 写完 SKILL.md / references / prompt 后，**必跑自检**才认为"沉淀完成"。写完 ≠ 沉淀完。

### 5 项必跑自检（沉淀前不跑 = 翻车）

| # | 自检项 | 命令 / 判定 | 期望 |
|---|---|---|---|
| 1 | **0 绘本名污染** | `grep -nE "(duck clip\|duck 绘本\|duck v6\|clip2 v6\|绘本名+版本号)" SKILL.md references/*.md` | **0 处**（duck 泛指/TTS 旁白文本除外）|
| 2 | **0 vX.X+picN 标签** | `grep -nE "v[0-9]+\.[0-9]+\+pic[0-9]+" SKILL.md references/*.md` | **0 处**（反例占位符也用通用占位符）|
| 3 | **所有 references 引用 = 真实存在** | `grep -oE "references/[a-zA-Z0-9_-]+\.md" SKILL.md \| sort -u \| while read f; do test -f "$f" \|\| echo "❌ $f"; done` | **0 missing**（见下方 §3.1 断链判定 3 分类） |
| 4 | **元方法论命名 = 通用方法论名**（不绑具体绘本）| 反问自检："这个方法论是因为某本绘本踩坑，还是因为通用方法论？" | **通用方法论** → 写 skill 仓 |
| 5 | **patch 工具前 = 必先全量 read**（防 sibling 并发覆盖）| `read_file` 全文件**不用 offset/limit** → 再 `patch` | 避免"partial view"警告 + sibling 改动丢失 |

**判定口诀**：
- 5/5 全过 = 沉淀完成
- 任意 1 项失败 = **先修自检项** → 再交付
- 漏跑 = 翻车（绘本名污染 / 引用空文件 / 方法论绑专名 / 跨 agent 覆盖）= 下个 session 复用 skill 时必翻车

### §3.1 断链引用判定 3 分类 + 修复决策树

自检 §3 报 missing 时，先判定是真断链还是假断链，再选修复策略（**不**默认补空文件 = 治标）：

| 分类 | 触发 | 判定方法 | 修复策略 |
|---|---|---|---|
| **A · 假断链**（反例占位符）| 在"反模式"区 + 文件名是泛指占位符（如 `A-validation.md` / `XX-绘本.md`）| 看上下文 = 反例 / 教学 = 占位符 = 不是真引用 | **不改** = 保留作为反例教学 |
| **B · 真断链**（正文引用）| 在正文 / Step 章节 + 说"详细见 X" / "修复路径见 X"= 真指引用 | grep 该引用的内容是否在 SKILL.md 表格/章节内已含 | **删引用 + 改成内联指向上文**（信息 0 损失）|
| **C · 真断链**（目录索引）| 在 references 列表 = 目录索引 | 看文件名是否含具体绘本名（如 `mango-validation.md`）= 违反铁律 #116 业务数据不入 skill 仓 | **删索引条目** = 不建空文件 |

**修复优先级**：

```
报 missing
   ↓
1. 看上下文判定 A/B/C
   ↓
A → 保留（反例占位符）
B → 删引用 + 改成内联指向上文表格/章节
C → 删索引条目
   ↓
不补空文件（"该删就删"原则 · 违反 = skill 仓多个永远不补的废文件）
   ↓
重跑自检 §3 = 期望 0 missing
```

**根因**（为什么之前不区分）：
- 自检脚本 `test -f` 只判文件存在，不看上下文语义
- 人工判定 3 分类 = 看引用位置的"反模式区 / 正文 / 目录索引"3 个固定区域

### 反模式（必避）

- ❌ 报 missing → 立即建空文件标"待补"= 治标 = 违反"该删就删"
- ❌ 报 missing → 不看上下文直接删 = 误删反例占位符 = 教学价值丢失
- ❌ 报 missing → 在 references/ 加 `XX-validation.md` 通用占位文件 = 污染

---

## 7. 绘本做完 = 不动 skill（元教训 · 用户原话）

> 用户原话（2026-06-13）："**绘本做完不要在 skill 里加版本号**" + "**绘本做法规范到 skill 里作为标准的制作流程**" + "**不要有太多分支/版本**" + "**不要再开新分支**"

**绘本完成 = 全部产物在工作目录（`~/.hermes/profiles/huiben/work/<日期-绘本名>/`）· skill 不变**：

- ❌ **不**在 SKILL.md 加铁律"v1.0.5+picXX · XX 绘本踩坑"
- ❌ **不**在 references/ 加 `2026-06-XX-绘本名-validation.md`
- ❌ **不**修改 fill 脚本（除非发现通用 bug）
- ❌ **不**开新 git 分支
- ❌ **不**在 SKILL.md / fill 脚本注释 / 铁律名出现特定绘本名
- ✅ **可以**在 work/<日期-绘本名>/ 加本绘本专属笔记（业务文档·不入 skill）
- ✅ **可以**清理 work 旧绘本残留（每绘本完成一周后）

**反问自检**："这个铁律是因为某本绘本踩坑，还是因为通用方法论？"
- **通用方法论** → 加铁律（不绑绘本名）
- **某本绘本踩坑** → work/<日期-绘本名>/ 写笔记，不加 skill

---

## 8. 自检命令（绘本完成时必跑 0 残留验证）

```bash
# 1. SKILL.md 内 0 绘本名残留
grep -E "特定绘本名" SKILL.md scripts/*.py references/*.md templates/*.md assets/example-prompts/*.txt
# 期望：无任何输出

# 2. SKILL.md 内 0 v\d+\.\d+\+pic\d+ 标签
grep -E "v[0-9]+\.[0-9]+\+pic[0-9]+" SKILL.md scripts/*.py references/*.md templates/*.md
# 期望：无任何输出（反例占位也用 `v\d+\.\d+\+pic\d+` 通用占位符）
```

**反例教学的正确写法**（示范）：

```markdown
# ❌ 错：绑了具体绘本名和版本号
**#110**（v1.0.5+pic32 实战新增 · 某绘本踩坑 ...）
每本绘本 = 新分支（`某绘本-4clip-v1.0.5+pic37` 等）

# ✅ 对：用通用占位符
**#110**（绘本踩坑实战新增）
每本绘本 = 新分支（`{绘本名}-Nclip-{vX.X+picN}` 模式）
```

---

## 9. 跨 skill 适用（不限于绘本视频）

- ✅ **绘本视频**（picturebook-video）：方法论 #M1-#M4 全适用
- ✅ **漫剧分镜**（ai-drama）：方法论 #M1 / #M3 适用（节奏 + 镜头序列）
- ✅ **AI 短剧**：方法论 #M1 / #M2 适用（节奏 + 规则推导）
- ✅ **任何用 seedance / Midjourney / 即梦 创作工具的 skill**：方法论 #M4 全适用（蒸馏治理）
- ✅ **任何 huiben profile 下 skill 仓**：方法论 #M4 全适用（commit/sibling/3-way）

**根因同源**：所有 skill 沉淀过程 = 业务数据 → 通用方法论 → 铁律 = 3 层蒸馏。**不蒸馏 = 污染 = 半年后 token 爆炸**。
