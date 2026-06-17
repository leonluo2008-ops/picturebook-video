# picturebook-video 升级指令 · v5.0.4 → v5.0.5

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.4 的 picturebook-video。用户要求你升级到 **v5.0.5（4 确认点流程修订 + 纯文本输出纪律）**。

**v5.0.5 的核心变化（铁律 #30 重写 + 新增铁律 #32）**：

1. **铁律 #30 重写** = 从"单测必跑"修订为"**4 确认点流程**"
   - **确认点 1**（Step 3 后）= Clip 时长划分 / 合并策略确认
   - **确认点 2**（Step 5 后）= 每个 Clip 中文 prompt 确认
   - **确认点 3**（Step 6.0 spike 提交前）= 单测参数确认
   - **确认点 4**（spike 跑完后）= 视觉质量 + 批量 1 次确认（1 次回复 = 2 件事）
   - **模式开关** = 默认 4 确认点 / 用户明确说"全自动 / 静默跑 / 不用确认" = 切静默
2. **铁律 #32 新增** = 跟用户确认的输出方式 = **必用纯文本 + 标题 + 列表 · 严禁 GFM 表格**
   - 飞书渲染问题：GFM 表格显示成代码块 = 用户看原始代码 = 没法读

**升级意义**：修 v5.0.4 之后又出现的"云服跳 4 确认点直接进单测"翻车 + 飞书表格渲染问题。

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

## Step 0 · 升级前快照（出问题可回滚）

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
# 期望看到 v5.0.5 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 4 确认点流程 + 纯文本输出纪律升主层

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 铁律 #30 重写为"4 确认点流程" ==="
grep "30.*流程确认" SKILL.md
# 期望看到：| **30** | **Step 3-6** 流程确认 | **4 确认点流程 · 默认开启 · 用户说"全自动"才静默**

echo ""
echo "=== 2. SKILL.md 铁律 #32 新增（纯文本输出纪律）==="
grep "32.*输出纪律" SKILL.md
# 期望看到：| **32** | **全流程** 输出纪律 | **跟用户确认 = 必用纯文本 + 标题 + 列表 · 严禁 GFM 表格**

echo ""
echo "=== 3. v8-workflow-7steps.md Step 3.5（确认点 1）==="
grep "Step 3.5 · 必走 · 确认点 1" references/v8-workflow-7steps.md
# 期望看到：Step 3.5 · 必走 · 确认点 1 · Clip 时长划分/合并策略确认

echo ""
echo "=== 4. v8-workflow-7steps.md Step 5.5（确认点 2）==="
grep "Step 5.5 · 必走 · 确认点 2" references/v8-workflow-7steps.md
# 期望看到：Step 5.5 · 必走 · 确认点 2 · 每个 Clip 中文 prompt 确认

echo ""
echo "=== 5. v8-workflow-7steps.md Step 6.0 含确认点 3 + 4 ==="
grep -E "确认点 [34]" references/v8-workflow-7steps.md | head -4
# 期望看到：确认点 3 · spike 提交前参数确认 + 确认点 4 · spike 跑完后视觉质量 + 批量 1 次确认

echo ""
echo "=== 6. 铁律口诀含"4 确认点流程 + 用户说全自动才静默"和"跟用户确认必纯文本不用表格" ==="
grep "4 确认点流程 + 用户说全自动才静默" SKILL.md && echo "✅ 命中" || echo "❌ 0 命中"
grep "跟用户确认必纯文本不用表格" SKILL.md && echo "✅ 命中" || echo "❌ 0 命中"
```

**期望：6 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## 升级完成后主 agent 必走的新规则

**v5.0.5 起 4 条主 agent 路径强约束**：

| 编号 | 铁律 | 关键约束 |
|---|---|---|
| #29 | `@ImageN` 必含 | 每段 prompt 开头必含 + 多图覆盖 + ref_images 长度匹配 |
| **#30** | **4 确认点流程** | Step 3.5 / 5.5 / 6.0 前 / 6.0 后 · 默认开启 · 用户说全自动才静默 |
| #31 | 3 并发 | 每轮 ≤ 3 + 多轮分批 + 严禁超官方限流 |
| **#32** | **纯文本输出纪律** | 跟用户确认必用纯文本 + 标题 + 列表 · 严禁 GFM 表格 |

**违反任一 = 红线违规 = 不提交**。

---

## 4 确认点必走 · 输出范式（纯文本 · 不用表格）

### 确认点 1 · Step 3 后 · Clip 时长划分方案

```
## 确认点 1 · Clip 时长划分方案

绘本：[绘本名] · [N] 页 · TTS [Xs]

时长划分：
- Clip 1：[Xs] · 单图 · [主体]
- Clip 2：[Xs] · 单图 · [主体]
- ...（共 N 个）

合并策略：
- 单镜单图 [N] 个

总时长：[Xs] · [N] Clip

回复 OK / 修改意见。
```

### 确认点 2 · Step 5 后 · 中文 prompt 方案

```
## 确认点 2 · 每个 Clip 中文 prompt 方案

绘本：[绘本名] · [N] Clip

Clip 1 · [Xs] · @Image1（[主体]）：
中文描述：[主体外观 + 核心动作 + 1 组情绪外化 + 1 运镜 + 方向锚点]

（共 N 段）

回复 OK / 修改意见。
```

### 确认点 3 · Step 6.0 spike 提交前

```
## 确认点 3 · 准备跑 spike 单测

绘本：[绘本名] · Clip 1

参数：
- model: doubao-seedance-2-0-fast-260128
- duration: 4 秒
- resolution: 480p
- generate_audio: false
- watermark: none

回复 OK / 修改意见。
```

### 确认点 4 · spike 跑完后

```
## 确认点 4 · Spike 跑完，请目检

绘本：[绘本名] · Clip 1

时长：Xs
md5：xxx
文件：MEDIA:/path/clip1-spike.mp4

回复 OK = 视觉 OK + 可以批量。
回复 修改意见 = 重提新任务。
```

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.4 → v5.0.5 升级完成
- 铁律 #30 重写：4 确认点流程（Step 3.5 / 5.5 / 6.0 前 / 6.0 后）
- 铁律 #32 新增：纯文本输出纪律（飞书渲染问题）
- 模式开关：默认 4 确认点 / 用户说"全自动" = 切静默
- 验证项：全部通过
```

---

## 历史升级链路

| 版本 | commit | 变更 |
|---|---|---|
| v5.0 | 81b5cea | 单仓集成 seedance_mcp |
| v5.0.2 | 6a7070b | INSTALL_TEST.sh 路径硬编码修复 + wrapper 路径多候选适配 |
| v5.0.3 | 5f4969d | @ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线 |
| v5.0.4 | 43d1e87 | 单测必跑 + 用户确认 + 3 并发限流 |
| v5.0.5 | (升级完成后查 git log) | 4 确认点流程修订 + 纯文本输出纪律 |

---

**对应 commit**：v5.0.5 commit hash（升级完成后由 `git log --oneline -1` 输出确认）