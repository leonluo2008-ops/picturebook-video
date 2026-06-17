# picturebook-video 升级指令 · v5.0.9 → v5.0.10

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.9 的 picturebook-video。用户要求你升级到 **v5.0.10（单镜头时长倾向 2-4s · 多镜头叙事优化）**。

**v5.0.10 的核心变化（优化单镜头设计 · 不破坏其它流程）**：

### 问题描述

单镜头时长 > 5s 时画面容易机械（循环/丢失运镜/动作卡顿），应优先多镜头叙事。

### 官方依据（seedance 2-系列提示词指南 §2）

- 官方 8s 总时长示例 = 平均 **2s/镜头**（4 镜头）
- 官方原话："**不强制限制每段时长**，优先让模型根据剧情自然生成节奏"
- 官方原话："模型对精确时间（如 0-3 秒）的支持不稳定，**强行限制时长可能导致生成结果异常**"

### 修复（铁律 #37 新增）

1. **单镜头时长倾向 2-4s**（参考官方 8s/4 镜头示例节奏）
2. **总时长 ≥ 4s 时 = 优先多镜头叙事**（拆 2-4 个镜头 = 每段独立运镜）
3. **总时长 ≤ 4s 时 = 单镜头**（seedance 物理下限）
4. **不硬卡秒数**（prompt 里**不**写"前 3 秒做 X / 4-6 秒做 Y"）= 违反官方"强行限制时长可能异常"警告
5. **靠镜头切换 = 模型自然分时序**

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
# 期望看到 v5.0.10 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 v5.0.10 3 处必改

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 含铁律 #37（单镜头时长）==="
grep -nE "37.*单镜头时长" SKILL.md | head -2
# 期望看到：| **37** | **Step 5** 单镜头时长 | **单镜头时长倾向 2-4s**

echo ""
echo "=== 2. v8-prompt-template.md 含"单镜头时长倾向"段 ==="
grep "### 单镜头时长倾向" references/v8-prompt-template.md | head -2
# 期望看到：### 单镜头时长倾向（v5.0.10 新增 · 官方教程示例 2-4s 节奏沉淀）

echo ""
echo "=== 3. v8-prompt-template.md 自检命令含检查 11 ==="
grep "检查 11: 单镜头时长倾向" references/v8-prompt-template.md
# 期望看到：# 检查 11: 单镜头时长倾向（v5.0.10 新增 ...）
```

**期望：3 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## v5.0.10 升级后主 agent 必走的新规则

### 单镜头时长倾向（**铁律 #37**）

| 项 | 规则 |
|---|---|
| **单镜头时长** | **倾向 2-4s**（参考官方 8s/4 镜头示例节奏）|
| **总时长 ≥ 4s** | **优先多镜头叙事**（拆 2-4 个镜头 = 每段独立运镜 = 比单镜头长运镜更稳）|
| **总时长 ≤ 4s** | 单镜头（seedance 物理下限）|
| **不硬卡秒数** | prompt 里**不**写"前 3 秒做 X / 4-6 秒做 Y"（违反官方"强行限制时长可能异常"警告）|
| **靠镜头切换** | 模型自然分时序（"镜头 1：..."/"镜头 2：..."标识 + 不写秒数）|

### 示例对比（绘本 8s 旁白）

- ❌ 单镜头 8s + 1 个运镜 = 机械/卡顿
- ✅ 4 镜头 × 2s = 镜头 1 出现 / 镜头 2 转折 / 镜头 3 高潮 / 镜头 4 收尾（**不卡秒数**）

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.9 → v5.0.10 升级完成
- 新增铁律 #37：单镜头时长倾向 2-4s · 多镜头叙事
- 官方依据：seedance 2-系列提示词指南 §2（官方 8s 总时长示例 = 平均 2s/镜头）
- 自检命令加检查 11（单镜头 > 5s + 0 个镜头标识 = 自动报错）
- 不破坏其它流程（v5.0.9 / 末尾约束 / 4 确认点 / 3 并发都不动）
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
| v5.0.10 | (升级完成后查 git log) | 单镜头时长倾向 2-4s · 多镜头叙事（铁律 #37）|

---

**对应 commit**：v5.0.10 commit hash（升级完成后由 `git log --oneline -1` 输出确认）