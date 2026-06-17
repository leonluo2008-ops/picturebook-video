# 安装验收脚本路径自动检测范式（**v5.0.2 沉淀 · 跨 skill 通用**）

> **核心问题**：任何 hermes skill 自带验收脚本（如 `INSTALL_TEST.sh` / `smoke.sh` / `validate.sh`），如果硬编码 `/home/luo/.hermes/...` 或假设 `profiles/huiben` 这个 profile 名 = **跨用户/跨主机必失败**。

---

## 真实事故（2026-06-16 picturebook-video 升级）

云服按本 skill v5.0 升级手册执行升级，升级报告反馈：

```
P1（🔴 严重）INSTALL_TEST.sh 路径硬编码 /home/luo/.hermes/... 不匹配实际环境 /home/ubuntu/.hermes/
P2（🔴 严重）INSTALL_TEST.sh 未被执行 → 端到端能力未验证
P3（🟡 中等）wrapper.sh 部署路径（/home/ubuntu/.hermes/bin/）与 INSTALL_TEST.sh 期望路径（profiles/huiben/bin/）不一致
P4（🟡 中等）升级文档路径假设（/home/luo）需要环境适配说明
P5（🟢 低）hermes-agent restart 超时 → 新 MCP 可能未生效
```

**根因 = 同一个**：硬编码用户名 `luo` = 本地（`/home/luo`）能跑，云服（`/home/ubuntu`）必挂。

---

## 修复范式（5 步走 · 适用于任何 hermes skill）

### Step 1 · 不硬编码任何路径

```bash
# ❌ 反模式（v5.0.1 翻车）
HERMES_ROOT="/home/luo/.hermes"
SKILL_DIR="$HERMES_ROOT/profiles/huiben/skills/creative/picturebook-video"
PY="/home/luo/.hermes/hermes-agent/venv/bin/python3"

# ✅ 正模式（v5.0.2 起 · 从 $0 反推）
SCRIPT_PATH="$(readlink -f "$0")"
SKILL_DIR="$(dirname "$SCRIPT_PATH")"
```

### Step 2 · 用 `dirname` 反推 HERMES_ROOT（**必数对次数**）

```bash
# 标准 picturebook-video 路径 = 6 段
# /home/<user>/.hermes/profiles/huiben/skills/creative/picturebook-video/INSTALL_TEST.sh
#           ^1       ^2        ^3       ^4       ^5         ^6

# 从 SKILL_DIR（去掉末段 picturebook-video）反推到 HERMES_ROOT
# = 5 次 dirname
HERMES_ROOT="$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SKILL_DIR")")")")")"
```

**dirname 次数速算表**：

| 路径形态 | 段数 | 必 dirname 次数 |
|---|---|---|
| `<ROOT>/profiles/<profile>/skills/creative/<skill>/script.sh` | 5 + .hermes = 6 段 | **5 次**（从 SKILL_DIR 起） |
| `<ROOT>/skills/<skill>/script.sh` | 2 + .hermes = 3 段 | **2 次** |
| `<ROOT>/bin/<tool>.sh` | 1 + .hermes = 2 段 | **1 次** |

**反模式**：dirname 次数凭印象写（少 1 = 多一层 `profiles/`，多 1 = 削到 `profiles/` 没了 `.hermes`）→ **必实测**：`echo "$HERMES_ROOT"` 后用 `ls -ld $HERMES_ROOT` 验证路径真实存在。

### Step 3 · wrapper 部署位置兼容多候选

```bash
# v5.0 升级文档推荐 ~/.hermes/bin/，INSTALL_TEST.sh 之前期望 profiles/huiben/bin/
# v5.0.2 = 两个都接受，找到哪个用哪个
PROFILE_BIN="$HERMES_ROOT/profiles/huiben/bin"

WRAPPER=""
for CAND in "$PROFILE_BIN/seedance-mcp-wrapper.sh" "$HERMES_ROOT/bin/seedance-mcp-wrapper.sh"; do
  if [ -f "$CAND" ]; then
    WRAPPER="$CAND"
    break
  fi
done
```

**交叉验证**：找到 wrapper 后 grep `~/.hermes/config.yaml` 的 `seedance.command` 字段，对比实际路径，不一致时 warn（可能 hermes-agent 加载了错的 wrapper）。

### Step 4 · Python 解释器兜底

```bash
if [ -x "$HERMES_ROOT/hermes-agent/venv/bin/python3" ]; then
  PY="$HERMES_ROOT/hermes-agent/venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "❌ 找不到 python3"
  exit 1
fi
```

**根因**：hermes-agent venv 是 hermes 自带 · 系统 python3 兜底 · 直接 `python3` 可能调错。

### Step 5 · 头部 echo 检测结果（让用户立刻看到）

```bash
# 跑任何验收前 4 行
echo "  SCRIPT_PATH=$SCRIPT_PATH"
echo "  SKILL_DIR=$SKILL_DIR"
echo "  HERMES_ROOT=$HERMES_ROOT"
echo "  PY=$PY"
```

**作用**：用户眼睛一扫就知道检测到啥，路径不对立刻报错（比跑完 7 步才报"找不到 X"友好）。

---

## 升级手册必含 Step -1 环境适配

云服执行任何升级指令前，必先跑这段（写到 references/upgrade-*.md 开头）：

```bash
# Step -1: 环境适配（必跑 · 任何升级指令都先跑这个）
echo "当前用户: $(whoami)"
echo "HOME: $HOME"

# 从 config.yaml 反推 HERMES_ROOT（最可靠 · 不假设路径）
HERMES_ROOT=$(dirname "$(readlink -f ~/.hermes/config.yaml 2>/dev/null)" 2>/dev/null)
if [ -z "$HERMES_ROOT" ] || [ "$HERMES_ROOT" = "/" ]; then
  HERMES_ROOT="$HOME/.hermes"
fi

# profile 目录名探测（不假设是 huiben）
PROFILE_DIR="$HERMES_ROOT/profiles/huiben"
[ ! -d "$PROFILE_DIR" ] && PROFILE_DIR=$(ls -d $HERMES_ROOT/profiles/*/ 2>/dev/null | head -1)

# 告诉用户检测到的路径
echo "检测到 HERMES_ROOT=$HERMES_ROOT"
echo "检测到 PROFILE_DIR=$PROFILE_DIR"
```

**关键**：升级文档不直接调这些变量往下走，**而是先 echo 让用户确认**——用户拍板后再继续。避免"agent 猜路径 → 跑 9 步升级 → 才发现路径错 = 全推倒重来"。

---

## 完整模板（直接 copy · 适用于任何 hermes skill）

```bash
#!/usr/bin/env bash
set -e

# ===== 配置（必走 5 步 · 跨 skill 通用）=====
# Step 1: 反推 SCRIPT_PATH
SCRIPT_PATH="$(readlink -f "$0")"

# Step 2: 反推 HERMES_ROOT（按实际路径段数 dirname）
SKILL_DIR="$(dirname "$SCRIPT_PATH")"
#   ⚠️ 必改这里的 dirname 次数 = 你的 skill 路径段数 - 1
#   picturebook-video = 6 段 → 5 次
#   其他 skill = 自己数
HERMES_ROOT="$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SKILL_DIR")")")")")"

# Step 3: 多候选 wrapper 位置
PROFILE_BIN="$HERMES_ROOT/profiles/huiben/bin"

# Step 4: PY 兜底
if [ -x "$HERMES_ROOT/hermes-agent/venv/bin/python3" ]; then
  PY="$HERMES_ROOT/hermes-agent/venv/bin/python3"
else
  PY="$(command -v python3)"
fi

# Step 5: 头部 echo
echo "  SCRIPT_PATH=$SCRIPT_PATH"
echo "  SKILL_DIR=$SKILL_DIR"
echo "  HERMES_ROOT=$HERMES_ROOT"
echo "  PY=$PY"

# ===== 验收逻辑（你的 skill 特有）=====
# ... 你的 7 步验收 / smoke test / validation
```

---

## 跨 skill 适用清单

✅ 任何 hermes skill 自带 `.sh` 验收脚本都应该走这 5 步：

- `picturebook-video/INSTALL_TEST.sh`（v5.0.2 已用）
- `seedance2.0-tool/spikes/001-mcp-uguu-server/INSTALL.sh`（如存在 = 待修）
- 任何第三方 skill 自带的 INSTALL.sh / smoke.sh / validate.sh
- 任何 hermes cron 任务里的 shell script 引用 hermes 路径

**触发场景**：

- 写新 skill 自带验收脚本
- 升级现有 skill 验收脚本
- 给云服 / 其他用户发升级指令
- 跨用户 / 跨主机部署 skill

---

## 实战 case 库

### Case 1 · v5.0.1 → v5.0.2（2026-06-16）

- 错误：`HERMES_ROOT="/home/luo/.hermes"`（硬编码 luo）
- 正确：`HERMES_ROOT="$(dirname ... 5 次 ...)"` + 头部 echo 检测结果
- 验证：本地 `/home/luo` 跑 → ✅ 路径 `/home/luo/.hermes` · 云服 `/home/ubuntu` 跑 → ✅ 路径 `/home/ubuntu/.hermes`
- 关键修复点：dirname 次数从 4 改 5（首次算错路径变 `~/.hermes/profiles` = 多了一层）

### Case 2 · 待补充

（如未来出现同类翻车 = 加到这）

---

## 自检命令（写完验收脚本必跑）

```bash
# 1. 验证 HERMES_ROOT 反推正确
bash your_script.sh 2>&1 | head -6
# 期望：第 1-4 行 echo 出 SCRIPT_PATH / SKILL_DIR / HERMES_ROOT / PY
# 期望：HERMES_ROOT = 你当前的 .hermes 绝对路径

# 2. 验证没有硬编码用户名
grep -nE "home/(luo|ubuntu|user)" your_script.sh
# 期望：0 命中（除了头部 echo 调试信息里的 SCRIPT_PATH 实际值）

# 3. 验证 dirname 次数正确（手算一次）
# 例：路径 = /home/luo/.hermes/profiles/huiben/skills/creative/picturebook-video/INSTALL_TEST.sh
# 段数 = 6 · 从 SKILL_DIR 起 dirname 5 次 = 削 5 段 = 剩 .hermes
echo "/home/luo/.hermes/profiles/huiben/skills/creative/picturebook-video" | \
  xargs dirname | xargs dirname | xargs dirname | xargs dirname | xargs dirname
# 期望输出：/home/luo/.hermes
```

---

## 参考引用

- 实战事故：`references/upgrade-v4-to-v5.md`（云服升级报告 + Step -1 环境适配段）
- SKILL.md 安装段：「安装与验收（v5.0.2 · 路径自动检测 · 跨 skill 通用）」
- 父元方法论：skill 蒸馏治理（元方法论 #M4 · 5 项自检清单）