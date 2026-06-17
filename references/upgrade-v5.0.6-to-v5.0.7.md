# picturebook-video 升级指令 · v5.0.6 → v5.0.7

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.6 的 picturebook-video。用户要求你升级到 **v5.0.7（多图蒙太奇 Clip 合并核心约束 + Step 4 重写）**。

**v5.0.7 的核心变化（修 3 类翻车问题）**：

### 问题 1 · @ImageN 与镜头段落脱节（严重）

- **多图蒙太奇 Clip = @ImageN 必跟随镜头段出现**（不堆在段 1 开头）
- 范式来源：Seedance 2.0 官方"分镜图参考"案例
- 自检命令加检查 6（@ImageN 跟随镜头段）

### 问题 2 · Clip 合并方案未考虑旁白时长（中等）

- **核心约束 = 拟时长 ∈ [4, 15]**（TTS 旁白能装下 + seedance 物理上限）
- 替代旧版"5 项视觉一致性 = 合并必要条件"思维
- 任何参考图都允许合并（按时序分镜切换 = seedance 模型能力覆盖）
- 自检命令加检查 8（拟时长计算）

### 问题 3 · Prompt 不符合 Seedance 官方分镜时序（低）

- 多图 Clip 必按分镜时序分段（2 种范本都接受）
  - **范本 A · 英文官方版**：`from 0.0s to 5.0s @Image1 is the first shot, ...; from 5.0s to 10.0s @Image2 is the second shot, ...;`
  - **范本 B · 中文镜头 N 版**：`镜头 1（0-5s）：参考 @Image1，...; 镜头 2（5-10s）：参考 @Image2，...;`
- 自检命令加检查 7（兼容 2 种范本）

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
# 期望看到 v5.0.7 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 v5.0.7 5 处必改

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 含铁律 #33（Clip 合并核心约束）==="
grep -nE "33.*Step 4.*Clip 合并|TTS 旁白时长 = Clip 合并" SKILL.md | head -3
# 期望看到：| **33** | **Step 4** Clip 合并 | **TTS 旁白时长 = Clip 合并/拆分唯一核心约束**

echo ""
echo "=== 2. v8-workflow-7steps.md Step 4 改写（核心约束 = 拟时长 ∈ [4, 15]）==="
grep "核心约束\|拟时长 ∈ \[4, 15\]" references/v8-workflow-7steps.md | head -3
# 期望看到：核心约束：seedance 物理上限 = 单 Clip ≤ 15s

echo ""
echo "=== 3. v8-workflow-7steps.md 含多图 Clip 分镜时序 2 种范本 ==="
grep "范本 A\|范本 B" references/v8-workflow-7steps.md | head -4
# 期望看到：范本 A · 英文官方基础版 + 范本 B · 中文镜头 N 分段版

echo ""
echo "=== 4. v8-prompt-template.md 自检命令含检查 6/7/8 ==="
grep -cE "^# 检查 [678]" references/v8-prompt-template.md
# 期望：3（检查 6 + 检查 7 + 检查 8）

echo ""
echo "=== 5. v8-prompt-template.md 多图蒙太奇 Clip 规则段已加 ==="
grep -A 1 "多图蒙太奇 Clip（v5.0.7 新增" references/v8-prompt-template.md | head -2
# 期望看到：多图蒙太奇 Clip（v5.0.7 新增 · 多图蒙太奇翻车沉淀）
```

**期望：5 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## v5.0.7 升级后主 agent 必走的新规则

### Clip 合并核心约束（**替代旧版"5 项视觉一致性"思维**）

| 项 | v5.0.7 新规 |
|---|---|
| **核心约束** | 拟时长 ∈ [4, 15]（TTS 旁白能装下 + seedance 物理上限）|
| **拟时长 ≤ 15s** | ✅ 允许合并任意参考图（seedance 可按时序切换）|
| **拟时长 > 15s** | ❌ 必拆 Clip（拆依据 = 旁白切分点）|
| **拟时长 < 4s** | ❌ 拆太碎 = 必合并 |
| **视觉一致性** | ❌ 不再是合并必要条件 |
| **任何参考图** | ✅ 都允许合并（不相关图也能按时序切换）|

### 多图 Clip 分镜时序写法（2 种范本都接受）

**范本 A · 英文官方版**：
```
from 0.0s to 5.0s @Image1 is the first shot, [运镜 + 动作 + 情绪 + 方向锚点];
from 5.0s to 10.0s @Image2 is the second shot, [运镜 + 动作 + 情绪 + 方向锚点];
```

**范本 B · 中文镜头 N 版**：
```
镜头 1（0-5s）：参考 @Image1，[运镜 + 动作 + 情绪 + 方向锚点];
镜头 2（5-10s）：参考 @Image2，[运镜 + 动作 + 情绪 + 方向锚点];
```

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.6 → v5.0.7 升级完成
- 修 3 类问题：
  1. @ImageN 与镜头段落脱节（多图蒙太奇 Clip 必跟随镜头段）
  2. Clip 合并方案未考虑旁白时长（核心约束 = 拟时长 ∈ [4, 15]）
  3. Prompt 不符合 Seedance 官方分镜时序（2 种范本都接受）
- 新增铁律：#33（Clip 合并核心约束）
- 自检命令加：检查 6（@ImageN 跟随镜头段）+ 检查 7（分镜时序分段）+ 检查 8（拟时长计算）
- 验证项：全部通过
- 下次跑绘本时，Step 4 合并决策 = 拟时长 ∈ [4, 15] 唯一核心约束
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
| v5.0.7 | (升级完成后查 git log) | 多图蒙太奇 Clip 合并核心约束 + 2 种范本 + 自检 6/7/8 |

---

**对应 commit**：v5.0.7 commit hash（升级完成后由 `git log --oneline -1` 输出确认）