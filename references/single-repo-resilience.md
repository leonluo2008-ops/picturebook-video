---
name: single-repo-resilience
description: "单仓集成韧性模式（class-level · 跨 skill 适用）—— 用户原话触发'我担心那个仓崩了坏了，这边用不了了'（2026-06-16 picturebook-video v5.0 沉淀）。把关键外部依赖内联进主仓降低外部故障点。**5 步决策树**：① 依赖是否关键（业务链路必需）② 内联成本（< 1500 行 + 单真源 + 无 spike）③ 升级链路（独立 vs 同步）④ 决策树（满足 3+ 项必内联）⑤ 验收（7 步脚本）。**3 类反模式**：误把 spike 当核心 / 升级分裂 vs 同步 / 删干净外仓。**7 项评估标准**：依赖大小 / 状态 / 兼容 / 可维护 / 验收 / 测试 / 文档。**触发场景**：用户担心外部 repo 失败 / 仓库有 spike throwaway / MCP server 集成 / wrapper.sh + .env 模式。**适用范围**：picturebook-video v5.0 / 任何 skill 对外部 repo 的依赖决策。"
license: Apache-2-2
metadata:
  hermes:
    tags: [single-repo, integration, resilience, mcp-integration, dependency-management, picturebook-video-v5]
  related_skills: [picturebook-video, seedance2.0-tool, hermes-multi-agent, subagent-safety-defense, skill-organizer]
  toolkit_role: architecture-pattern
---

# 单仓集成韧性模式（single-repo resilience）

> **类级别架构模式**·2026-06-16 picturebook-video v5.0 实战沉淀

## 触发信号（何时考虑这个模式）

用户在以下情境表达过"担心外部依赖失效"：

- "**我担心那个仓崩了坏了，这边用不了了，那就麻烦了**"（picturebook-video v5.0 实战原话）
- "X 仓库挂了怎么办"
- "我能不能不依赖那个项目"
- 任何**外部 repo 是关键路径** + **用户对可用性敏感**的场景

## 核心命题

**关键外部依赖内联进主仓 = 把"故障点 × N"变成"故障点 × 1"**

```
多仓架构（高风险）：
  主仓 ──→ 外部仓 A（关键）
        ──→ 外部仓 B（关键）
        ──→ 外部仓 C（关键）
  故障点 = N 个仓任一挂了 = 主仓失效

单仓架构（低风险）：
  主仓（含 A+B+C 核心）
  故障点 = 1 个仓
```

## 5 步决策树（满足 3+ 项 → 必内联）

### Step 1 · 依赖是否关键？

| 关键度 | 判定 | 处理 |
|---|---|---|
| **关键** | 业务链路必需 + 缺失 = 主仓完全不可用 | **必内联** |
| 辅助 | 主仓可降级运行（fallback 路径）| 可选内联 |
| 装饰 | 不影响核心功能 | 不必内联 |

### Step 2 · 内联成本可承受？

| 项 | 可承受阈值 | 超阈值处理 |
|---|---|---|
| 代码量 | < 1500 行 | > 1500 行 = 部分内联（核心内联/spike 留外仓）|
| 单真源 | ✅ 1 个核心模块（不是 spike 多版本）| 多版本 = 抽 1 个内联 / 其他留外仓 |
| 无重依赖 | 不引入新的 pip/npm/cargo 依赖 | 重依赖 = 在 README 标"需先装 X" |

### Step 3 · 升级链路决策

| 场景 | 处理 |
|---|---|
| 外仓**继续独立迭代**（用户保留 spike 005/006 实验）| ✅ 内联核心 + 外仓保留 = **并存模式** |
| 外仓**已废弃 / 用户不再维护** | 内联 + 外仓归档（README 写 DEPRECATED）|
| 外仓**定期同步**（用户主动 cherry-pick 新能力）| 内联 = 单 git 仓库 = 同步成本 ↓ |

### Step 4 · 决策矩阵（满足 3+ 项 = 必内联）

| # | 条件 | 加分 |
|---|---|---|
| 1 | 关键度 = "关键" | ✅ |
| 2 | 代码量 < 1500 行 | ✅ |
| 3 | 单真源 = 1 个核心模块 | ✅ |
| 4 | 外仓继续独立维护（不冲突）| ✅ |
| 5 | 验收可写脚本（7 步一键）| ✅ |
| 6 | 文档可同步（不绑专名）| ✅ |
| 7 | 用户原话表达"担心" | ✅ |

**满足 3+ 项 = 内联。** 满足 7/7 = 强烈推荐。

### Step 5 · 内联后必写 7 步验收脚本

```bash
# INSTALL_TEST.sh 模板（v5.0 实战）
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/<主仓>
HERMES_ROOT=/home/luo/.hermes
PROFILE_BIN=$HERMES_ROOT/profiles/huiben/bin

# Step 1: skill 仓结构
test -d $SKILL_DIR/<集成模块>/ && echo "✅ step 1"

# Step 2: .env 配置（关键 API key 必填）
grep -q '^ARK_API_KEY=...' $SKILL_DIR/<集成模块>/.env && echo "✅ step 2"

# Step 3: wrapper 部署
test -f $PROFILE_BIN/<wrapper>.sh && echo "✅ step 3"

# Step 4: Python 依赖
$PY -c "import mcp, httpx, dotenv" && echo "✅ step 4"

# Step 5: API key 有效性（不扣费）
$PY smoke_test.py  # 内含 verify_api_key 调用

# Step 6: 外部图床 / API 可达
curl -sF "files[]=@/tmp/test.jpg" https://uguu.se/upload.php | grep -q '"success":true' && echo "✅ step 6"

# Step 7: 端到端 smoke test（5s 视频 succeeded）
$PY -c "import asyncio; ... wait_and_download ... succeeded"
```

**核心规则**：`$HOME` 在 hermes-agent 内会被重定向到 `~/.hermes/profiles/huiben/home`，**必用绝对路径** `$HERMES_ROOT=/home/luo/.hermes` · 不能用 `$HOME/...`。

## 3 类反模式（必避）

### ❌ 反模式 1 · 误把 spike 当核心

**症状**：把 spike 005/006（实验性代码）当核心内联 = 主仓膨胀到 5000+ 行 + spike 跟核心混淆 = 维护噩梦

**修复**：**只内联 1 个核心模块**（如 `seedance_uploads.py` 569 行）· spike 留在原仓 = 主仓保持精简（picturebook-video v5.0 实际集成 = 569 行 uploads + 290 行 mcp_server 协议壳 = 共 ~860 行）

### ❌ 反模式 2 · 升级分裂 vs 同步 二选一僵化

**症状**：内联 = 强行删除原仓 = 用户失去 spike 实验场 · **OR** 保留原仓 = 升级不同步 = 两仓冲突

**修复**：**并存模式**（picturebook-video v5.0 默认）：
- 内联仓 = 稳定版 + 单仓可用（生产）
- 外仓 = 实验场 + spike/CLI（用户继续优化）
- 新能力 = cherry-pick 从外仓到主仓 = 同步成本 = 单 commit

### ❌ 反模式 3 · 删干净外仓 = 失去历史

**症状**：内联后 = 删 seedance2.0-tool 仓 = 失去 spike 历史 + 用户早期 commit 不可见

**修复**：**保留外仓**（不删）· README 加 DEPRECATED 提示 = 历史可查 · 内联只取必要核心 · 详见 `references/skill-distillation-governance.md` 的 3-way 分类法

## 7 项评估标准（v5.0 自检表）

| # | 项 | 评估 | 期望 |
|---|---|---|---|
| 1 | 依赖大小 | 主仓代码 +集成 < 原总行数？| ✅ v5.0 = 909 行集成 vs 原 spike 1000+ 行 |
| 2 | 状态 | mcp_seedance_* 4 个工具自动注册？| ✅ verified |
| 3 | 兼容 | 老用户升级无破坏？| ✅ git checkout v5.0 = 替换种子仓 |
| 4 | 可维护 | 改动只 commit 到 1 仓？| ✅ |
| 5 | 验收 | 7 步脚本 5 分钟内跑通？| ✅ INSTALL_TEST.sh 实测 < 5min |
| 6 | 测试 | 端到端 video 生成 succeeded？| ✅ 5.04s 视频 md5 验证 |
| 7 | 文档 | README/INSTALL 同步更新？| ✅ v5.0 双文件重写 |

## 实战 case · picturebook-video v5.0

**触发**：用户原话"**我担心那个仓崩了坏了，这边用不了了**"

**决策矩阵满足**：
- ✅ 关键度 = 关键（seedance 仓提供 MCP 工具 = 主仓业务不可缺）
- ✅ 代码量 = 860 行 < 1500
- ✅ 单真源 = 1 个 uploads 模块 + 1 个 mcp_server 协议壳
- ✅ 外仓继续维护（用户继续优化 spike）
- ✅ 验收可写脚本（INSTALL_TEST.sh 7 步）
- ✅ 文档可同步（README/INSTALL 重写）
- ✅ 用户原话表达"担心"

7/7 = 强烈内联

**实施步骤**（30-60 分钟）：
1. `cp seedance_uploads.py seedance_mcp/` + `bin/seedance-mcp-wrapper.sh`
2. 写简化 `mcp_server.py`（200-300 行 · 协议壳 · 委托 uploads）
3. 写 `.env.example` + `INSTALL_TEST.sh` 7 步
4. 跑 `smoke_test.py` 验证 .env + 集成层
5. 改 README.md / INSTALL.md（去掉必装 seedance2.0-tool）
6. commit v5.0 + tag + push dev
7. **不**删 seedance2.0-tool 仓（保留）

**修复 1 个 bug**：原 spike 写错域名 `volcsandbox.com` → 实际是 `volces.com`（v5.0 mcp_server.py 修复）。**这种隐藏 bug 在内联前不会被发现**。

## 跨 skill 适用（class-level 模式）

| 场景 | 适用？ |
|---|---|
| picturebook-video v5.0 集成 seedance_mcp | ✅ 已实施 |
| 其他 skill 集成外部 MCP server | ✅ 同模式 |
| 集成外部 CLI 工具（避免依赖安装）| ✅ 同模式 |
| 集成外部 API 客户端 | ✅ 同模式 |
| 单纯外部脚本调用（如 shell script）| ⚠️ 看代码量（> 500 行 = 不必内联）|
| 复杂多仓系统（每个仓独立可运行）| ❌ 不要内联（破坏解耦）|

## 配套铁律（写入 picturebook-video SKILL.md Step 6 应变表）

| 异常 | 应变 |
|---|---|
| AI agent 调 mcp_seedance_* 工具不可见 | 检查 `bin/seedance-mcp-wrapper.sh` 是否已部署 + `seedance_mcp/.env` 是否有 ARK_API_KEY |
| mcp_server.py 报域名错误 | 检查 ARK_BASE_URL = `https://ark.cn-beijing.volces.com/...`（不是 volcsandbox.com）|
| AI agent 找不到 hermes-agent 仓内的 wrapper.sh | 必走 `cp bin/seedance-mcp-wrapper.sh ~/.hermes/profiles/huiben/bin/` 步骤 |

## 1 行口诀

> **关键依赖内联降故障点 · 860 行集成 + 7 步验收 + 域名修复（volces.com 不是 volcsandbox.com）= 单仓可用**