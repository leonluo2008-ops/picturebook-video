# picturebook-video 升级指令 · v5.0.8 → v5.0.9

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.8 的 picturebook-video。用户要求你升级到 **v5.0.9（末尾约束 = seedance 官方约束词模板原话中文版）**。

**v5.0.9 的核心变化（修末尾约束误删参考图画面文字元素）**：

### 问题描述

v5.0.7 / v5.0.8 期间，prompt 末尾约束写的是 `No background music, no on-screen text.`。seedance 误读成"画面里不要任何文字"= **把参考图中属于画面元素的文字（如字母拼贴标题"peacock"+"孔雀"）也当字幕误删**。

### 修复（铁律 #36 新增）

1. **末尾约束改回官方 2-系列提示词指南 §5.3 原话中文版** = `无字幕、无 Logo、无水印、无背景音乐`
2. **seedance 支持中文**（官方教程示例本身就有中文）= 直接用中文版 = 不翻译不丢字
3. **修改末尾约束词 = 必先 grep 官方原话**（铁律 #36 强约束）

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

---

## Step 0 · 升级前快照

```bash
cp -r "$SKILL_DIR" "${SKILL_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
echo "✅ 已备份到 ${SKILL_DIR}.backup-<时间戳>"
```

---

## Step 1 · 拉 dev 分支最新代码

```bash
cd "$SKILL_DIR"
git pull origin dev
git log --oneline -1
# 期望看到 v5.0.9 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 v5.0.9 5 处必改

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 含铁律 #36（官方约束词对齐）==="
grep -nE "36.*官方约束词对齐" SKILL.md | head -2
# 期望看到：| **36** | **全流程** 官方约束词对齐 | **修改末尾约束词 = 必**逐字**复制 seedance 官方**

echo ""
echo "=== 2. v8-prompt-template.md v8 范例末尾约束 = 中文版 ==="
grep "无字幕.*无 Logo.*无水印.*无背景音乐" references/v8-prompt-template.md
# 期望看到：无字幕、无 Logo、无水印、无背景音乐。]

echo ""
echo "=== 3. SKILL.md v8 范例 line 1263 = 中文版 ==="
grep "无字幕.*无 Logo.*无水印.*无背景音乐" SKILL.md
# 期望看到至少 1 个命中

echo ""
echo "=== 4. v8-workflow-7steps.md 参数表 = 中文版引用 ==="
grep "无背景音乐" references/v8-workflow-7steps.md
# 期望看到：BGM 由 prompt 末尾约束\"无背景音乐\"排除

echo ""
echo "=== 5. mcp_server.py docstring = 中文版 ==="
python3 -c "import ast; ast.parse(open('seedance_mcp/mcp_server.py').read())"
grep "无背景音乐\|无字幕" seedance_mcp/mcp_server.py
# 期望看到：BGM 由 prompt 末尾约束 无背景音乐 排除
```

**期望：5 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本（确认末尾约束改后 = 不再误删参考图文字元素）

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## v5.0.9 升级后主 agent 必走的新规则

### 末尾约束（**铁律 #17 + #36**）

| 项 | v5.0.8 旧版（错）| v5.0.9 新版（对）|
|---|---|---|
| **末尾约束** | `No background music, no on-screen text.` | `无字幕、无 Logo、无水印、无背景音乐。` |
| **来源** | 我翻译时丢字 | seedance 官方 2-系列提示词指南 §5.3 原话中文版 |
| **行为** | seedance 误删参考图画面文字元素 | seedance 正确理解 = 只禁"新字幕"，不动参考图视觉元素 |

### 修改末尾约束词 = 必走规则（**铁律 #36**）

1. **必先 grep `references/seedance-official-docs/` 原话**（不凭印象/翻译/记忆）
2. **必逐字复制**（包括标点/顺序/空格）
3. **seedance 支持中文**（官方教程示例本身有中文）= **中文版优先**
4. 当前唯一允许的末尾约束 = `**无字幕、无 Logo、无水印、无背景音乐**`

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.8 → v5.0.9 升级完成
- 末尾约束改回官方 2-系列提示词指南 §5.3 原话中文版（无字幕、无 Logo、无水印、无背景音乐）
- 修复：v5.0.8 之前 seedance 误删参考图画面文字元素（如字母拼贴标题"peacock"）
- 新增铁律 #36：修改末尾约束词必 grep 官方原话 + 逐字 + 中文优先
- 自检命令加检查 10（末尾约束合规性）
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
| v5.0.9 | (升级完成后查 git log) | 末尾约束 = seedance 官方约束词模板原话中文版（铁律 #36）|

---

**对应 commit**：v5.0.9 commit hash（升级完成后由 `git log --oneline -1` 输出确认）