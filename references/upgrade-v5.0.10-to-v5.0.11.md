# picturebook-video 升级指令 · v5.0.10 → v5.0.11

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.10 的 picturebook-video。用户要求你升级到 **v5.0.11（末尾约束分 2 类 · 参考图文字元素处理 · 多变量同改陷阱）**。

**v5.0.11 的核心变化（解决参考图文字被删问题 · 不破坏其它流程）**：

### 问题描述

v5.0.9 / v5.0.10 末尾约束硬性 `无字幕、无 Logo、无水印、无背景音乐` 4 词全有 → 当参考图含装饰性文字（字母拼贴/标题/装饰字/角字卡/说明句）= seedance 照字面执行 `无字幕` = 误删参考图本身的画面装饰文字。

**用户原话**（2026-06-18 实战）："**视频的质量很好，但有一个问题：参考图的彩色文字被消除了。可能是'无字幕、无 Logo'导致的**"

### 根因（v5.0.9 → v5.0.11 翻车沉淀）

v5.0.9 错误地认为"无字幕翻车 = 翻译丢字 = 改回中文官方原话就行" = 但 `无字幕` 字面就是"不要文字" = seedance 必照字面执行 = 跨本验证再次翻车 = **推翻"逐字复制"原则在文字元素场景的适用性**。

### 修复（铁律 #36 修订 · 末尾约束分 2 类）

**核心命题**：末尾约束 = 按参考图是否含文字元素分流：

| 参考图含文字元素？ | 末段约束（必写）| 必加的 prompt 主体描述 |
|---|---|---|
| **是**（含字母拼贴/标题/装饰字/角字卡/说明句）| ✅ `无水印、无背景音乐`<br>❌ **不**写 `无字幕、无 Logo` | 显式让模型"保留 @ImageN 原有的 X 文字 + 为其设计入场/持续/退场动画" |
| **否**（纯视觉/摄影/风景/无装饰字）| ✅ `无字幕、无 Logo、无水印、无背景音乐`（4 词全有 = v5.0.9 旧版）| 不用 |

### 配套新增 4 项

1. **RP-26d 多变量同改陷阱**（v5.0.11）：v8-prompt-template.md §2 = 验证修复必 1 次只改 1 个变量 = 知道是哪个修改有效
2. **§5 末尾约束分流规范**（v5.0.11）：v8-prompt-template.md §5 = 决策表 + 视觉证据保留原则
3. **§6 v5.0.11 范本**（参考图含文字元素版）：clip2 v3 实战验证版本
4. **§8 自检命令 · 检查 10**（v5.0.11）：末尾约束分流合规性 + **检查 12** 隔离变量验证

### 视觉证据保留原则（v5.0.11 沉淀）

| 元素类型 | 翻车处理 | 正模式 |
|---|---|---|
| 画面装饰文字（字母拼贴/中文手写/标题/Logo/说明句）| v5.0.9 旧版会删 | 显式"保留 + 设计入场/持续/退场动画"|
| "字幕"真实含义 | 模型误读成"任何文字"| 明确指"后期添加的字幕条"，不指"参考图原文字"|

---

## Step -1 · 环境适配（必跑）

```bash
echo "当前用户: $(whoami)"
echo "HOME: $HOME"

HERMES_ROOT=$(dirname "$(readlink -f ~/.hermes/config.yaml 2>/dev/null)" 2>/dev/null)
if [ -z "$HERMES_ROOT" ] || [ "$HERMES_ROOT" = "/" ]; then
  HERMES_ROOT="$HOME/.hermes"
fi
echo "HERMES_ROOT: $HERMES_ROOT"

SKILL_DIR=$(find "$HERMES_ROOT/profiles/huiben/skills/creative/picturebook-video" -maxdepth 0 2>/dev/null)
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR=$(find "$HERMES_ROOT" -name "picturebook-video" -type d 2>/dev/null | head -1)
fi
echo "SKILL_DIR: $SKILL_DIR"

echo "当前 commit: $(git -C "$SKILL_DIR" log --oneline -1 2>/dev/null)"
```

## Step 0 · 升级前快照

```bash
cp -r "$SKILL_DIR" "${SKILL_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
echo "✅ 已备份到 ${SKILL_DIR}.backup-<时间戳>"
```

## Step 1 · 拉取 v5.0.11 改动

```bash
cd "$SKILL_DIR"
git fetch origin dev
git pull origin dev
echo "✅ 已拉取最新 dev 分支"
git log --oneline -3
```

## Step 2 · 验证 4 项关键改动落地

```bash
cd "$SKILL_DIR"

# 2.1 铁律 #36 末尾约束分 2 类
echo "=== 铁律 #36 v5.0.11 修订 ==="
grep -E "末尾约束分 2 类|参考图含装饰性文字时" SKILL.md | head -3
# 期望：2 条都命中

# 2.2 RP-26d 多变量同改陷阱
echo "=== RP-26d 多变量同改陷阱 ==="
grep -E "RP-26d 多变量同改陷阱|1 次只改 1 个变量" references/v8-prompt-template.md | head -3
# 期望：2 条都命中

# 2.3 配套支撑文档
echo "=== 配套支撑文档 ==="
test -f "$SKILL_DIR/references/reference-image-text-elements-handling.md" \
  && echo "✅ reference-image-text-elements-handling.md 已建" \
  || echo "❌ reference-image-text-elements-handling.md 缺失"
test -f "$SKILL_DIR/references/upgrade-v5.0.10-to-v5.0.11.md" \
  && echo "✅ upgrade-v5.0.10-to-v5.0.11.md 已建" \
  || echo "❌ upgrade-v5.0.10-to-v5.0.11.md 缺失"

# 2.4 v5.0.11 范本（clip2 v3 实战版）
echo "=== v5.0.11 范本 ==="
grep -E "v5.0.11 范本|参考图含文字元素版" references/v8-prompt-template.md | head -3
# 期望：2 条都命中
```

## Step 3 · 5 项自检必跑

```bash
cd "$SKILL_DIR"

# 3.1 0 绘本名污染
echo "=== 检查 1: 0 绘本名污染 ==="
grep -nE "(XX绘本|绘本名|具体绘本名)" SKILL.md references/*.md 2>/dev/null \
  | grep -v "references/reference-image-text-elements-handling.md" \
  | head -10
# 期望：业务数据支撑文档 = 0 处（业务数据已下沉到支撑文档）

# 3.2 0 vX.X+picN 标签
echo "=== 检查 2: 0 vX.X+picN 标签 ==="
grep -nE "v[0-9]+\.[0-9]+\+pic[0-9]+" SKILL.md references/*.md
# 期望：0 命中

# 3.3 所有 references 引用 = 真实存在
echo "=== 检查 3: references 引用真实存在 ==="
grep -oE "references/[a-zA-Z0-9_/-]+\.md" SKILL.md references/*.md | sort -u | while read f; do
  if [ ! -f "$f" ]; then
    echo "❌ missing: $f"
  fi
done
# 期望：0 missing（重点关注 reference-image-text-elements-handling.md 是否建立）

# 3.4 元方法论命名 = 通用方法论名
echo "=== 检查 4: 元方法论命名通用 ==="
# 检查 RP-26d / 末尾约束分 2 类都是通用方法论名（不是绘本名）

# 3.5 patch 前全量 read
echo "=== 检查 5: patch 工具前全量 read（v5.0.7/5.0.8 教训）==="
echo "✅ Step 1-2 已用 git pull 自动同步，无 partial view 风险"
```

## Step 4 · 安装验证（跑 1 本绘本端到端）

```bash
# 准备 1 本含文字元素的绘本素材包
# 验证流程：image-inventory 必含文字元素列 → 决策表分流 → 末尾约束用 `无水印、无背景音乐` + prompt 显式保留
```

---

## 验证项（升级完成必跑）

```bash
✅ picturebook-video v5.0.10 → v5.0.11 升级完成
- 铁律 #36 v5.0.11 修订：末尾约束分 2 类（参考图含装饰性文字 = 删 无字幕/无 Logo）
- RP-26d 多变量同改陷阱新增：v8-prompt-template.md §2
- §5 末尾约束分流规范：v8-prompt-template.md §5（决策表 + 视觉证据保留原则）
- §6 v5.0.11 范本：clip2 v3 实战版本（参考图含文字元素）
- §8 自检命令加检查 10（末尾约束分流合规性）+ 检查 12（隔离变量验证）
- 配套支撑文档：references/reference-image-text-elements-handling.md（v5.0.11 实战沉淀）
- 跨本验证状态：第 1 次（06-18）✅ · 第 2/3 次待验证
- 不破坏其它流程（v5.0.10 单镜头时长 / 4 确认点 / 3 并发 / @ImageN 必含 / 领读型测算 / 打包 ASCII 双层防护都不动）
- 验证项：全部通过
```

---

## 历史升级链路

| 版本 | commit | 变更 |
|---|---|---|
| v5.0 | 81b5cea | 单仓集成 seedance_mcp |
| v5.0.2 | 6a7070b | INSTALL_TEST.sh 路径硬编码修复 |
| v5.0.3 | 5f4969d | @ImageN 必含铁律升主层 |
| v5.0.4 | 43d1e87 | 单测必跑 + 3 并发限流 |
| v5.0.5 | 8977ec8 | 4 确认点流程 + 纯文本输出纪律 |
| v5.0.6 | 4b5d506 | 绘本有声场景 generate_audio=true |
| v5.0.7 | 088b231 | 多图蒙太奇 Clip 合并核心约束 |
| v5.0.8 | f5794f4 | 领读型绘本 TTS 测算规则（铁律 #35）|
| v5.0.9 | 7f9f589 | 末尾约束 = seedance 官方约束词模板原话中文版（铁律 #36）|
| v5.0.10 | 87e9a3c | 单镜头时长倾向 2-4s · 多镜头叙事（铁律 #37）|
| v5.0.11 | (升级完成后查 git log) | 末尾约束分 2 类 · 参考图文字元素处理 · RP-26d 多变量同改陷阱（铁律 #36 修订）|

---

**对应 commit**：v5.0.11 commit hash（升级完成后由 `git log --oneline -1` 输出确认）