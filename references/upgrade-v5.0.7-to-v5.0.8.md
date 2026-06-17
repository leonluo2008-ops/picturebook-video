# picturebook-video 升级指令 · v5.0.7 → v5.0.8

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.7 的 picturebook-video。用户要求你升级到 **v5.0.8（领读型绘本 TTS 测算规则）**。

**v5.0.8 的核心变化（修领读型绘本 TTS 时长偏差）**：

### 问题描述

领读型绘本旁白格式 = "独立英文列 + 中文列含嵌入英文目标词"。**TTS 实测只读中文列**（独立英文列 = 展示用 = 不参与朗读）。

AI 计算 TTS 时长时，把独立英文列 + 中文列分别计算再相加，导致总时长**严重偏高 6-11s**（实测：8 段 = 正确算法 39.17s，错误算法约 45-50s）。

### 修复（铁律 #35）

1. **只算中文列**（独立英文列 = 展示用 = 不算时长）
2. 嵌入英文在中文列里**合并念一遍**（不重复算）
3. 嵌入英文按 **英文 1.4 词/秒**算（跟铁律 #25 速率档一致）
4. **实测匹配目标**：AI 算的总时长尽量跟用户给 TTS 数值匹配（**差 ≤ 5s**）

**判定口诀**："**领读型 = 双列 / 只算中文列 / 嵌入英文按 1.4 词/秒 / 实测匹配用户 TTS ≤ 5s**"

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
# 期望看到 v5.0.8 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 v5.0.8 4 处必改

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 含铁律 #35（领读型 TTS 测算）==="
grep -nE "35.*领读型|TTS 实测只读中文列" SKILL.md | head -3
# 期望看到：| **35** | **Step 3** TTS 测算 | **领读型绘本旁白 = 双列结构**

echo ""
echo "=== 2. v8-workflow-7steps.md Step 3 含领读型规则段 ==="
grep "领读型绘本专用规则" references/v8-workflow-7steps.md | head -2
# 期望看到：### 领读型绘本专用规则（**2026-06-17 ... · 铁律 #35**）

echo ""
echo "=== 3. v8-tts-rate.md 含领读型测算段 ==="
grep "领读型绘本专用测算" references/v8-tts-rate.md | head -2
# 期望看到：### 领读型绘本专用测算（**2026-06-17 ... · 铁律 #35**）

echo ""
echo "=== 4. v8-prompt-template.md 自检命令含检查 9（领读型识别）==="
grep -cE "^# 检查 9" references/v8-prompt-template.md
# 期望：1
```

**期望：4 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## v5.0.8 升级后主 agent 必走的新规则

### 领读型绘本 TTS 测算（**铁律 #35**）

| 项 | 规则 |
|---|---|
| **判定** | 旁白格式 = "独立英文列 + 中文列含嵌入英文" = 领读型 |
| **TTS 实测** | 只读中文列（独立英文列 = 展示用 = 不朗读）|
| **AI 测算** | **只算中文列** + 嵌入英文按 **英文 1.4 词/秒** |
| **实测匹配** | 算的总时长尽量跟用户给 TTS 匹配（**差 ≤ 5s**）|

### 自动识别（自检命令 9）

```
if grep -E "^\s*[0-9]+\s+[A-Z][a-z]+.*[.!?]\s+[^\x00-\x7f]" narration.txt
  → 检测到领读型旁白结构 → 启用铁律 #35
  → 独立英文列字数不计入 TTS 时长
```

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.7 → v5.0.8 升级完成
- 新增铁律 #35：领读型绘本 TTS 测算规则
- 修复：AI 误把独立英文列 + 中文列分别计算再相加（+6~11s 偏差）
- 自检命令加：检查 9（领读型识别）
- 验证项：全部通过
- 下次跑领读型绘本时，AI 只算中文列 + 嵌入英文按 1.4 词/秒 = 算的总时长尽量跟用户 TTS 匹配
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
| v5.0.8 | (升级完成后查 git log) | 领读型绘本 TTS 测算规则（铁律 #35）|

---

**对应 commit**：v5.0.8 commit hash（升级完成后由 `git log --oneline -1` 输出确认）