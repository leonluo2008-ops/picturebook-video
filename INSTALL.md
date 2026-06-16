# picturebook-video 安装说明

> **目标读者**：在新机器上安装 hermes-agent + picturebook-video skill 仓的 AI 助手 / 工程师
> **AI 可自动化程度**：100%（含验收测试 + 故障排查 + 子 skill 联动）
> **安装总耗时**：约 10-15 分钟（含视频生成验收测试）
> **当前稳定版本**：v5.0（v8 prompt 模板 + seedance_mcp 集成 · 2026-06-16）

---

## 🎯 v5.0 重大变更

**单仓可用** — v5.0 起 picturebook-video 自带 `seedance_mcp/` 集成（uguu 上传 + Ark API 调用 + MCP 协议壳），**不再依赖** `seedance2.0-tool` 仓。**克隆 1 个仓 = 完整可用**。

---

## 0. 概览

### 0.1 必装组件一览

| # | 组件 | 类型 | 必填 | 用途 |
|---|---|---|---|---|
| 1 | Python 3.11+ | 系统依赖 | ✅ | 运行 hermes-agent + seedance_mcp |
| 2 | ffmpeg / ffprobe | 系统依赖 | ✅ | 视频抽帧 + 时长验证 |
| 3 | git | 系统依赖 | ✅ | 拉取 skill 仓 |
| 4 | hermes-agent | 主框架 | ✅ | AI agent 运行环境 |
| 5 | picturebook-video | 本仓（自带 seedance_mcp 集成）| ✅ | 7 步调度 + 28 铁律 + MCP 工具 |
| 6 | lark-cli | 兄弟 skill（可选）| ⭕ | 飞书云盘/消息/文档 |
| 7 | douyin-ops | 兄弟 skill（可选）| ⭕ | 抖音数据调研 + 发布 |

> **v5.0 移除依赖**：`seedance2.0-tool` 不再需要装（功能已并入本仓 `seedance_mcp/`）。

### 0.2 必填环境变量

| 变量 | 必填 | 用途 | 获取地址 |
|---|---|---|---|
| `ARK_API_KEY` | ✅ | Volcengine Ark API（视频生成）| https://console.volcengine.com/ark |

> **配置位置**：`<skill_dir>/seedance_mcp/.env`（wrapper.sh 自动加载，无需手动 source）

### 0.3 已废弃 / 不再需要

| 变量 | 状态 | 替代方案 |
|---|---|---|
| `CHEVERETO_API_KEY` | ❌ 已废弃 | 本地图片上传改用 **uguu.se** 兜底路线，无需任何 env 变量。详见 `references/uguu-fallback-route.md` |

---

## 1. 系统依赖安装

### 1.1 检查现有依赖

```bash
# 必须项检查
which python3 git ffmpeg ffprobe

# 版本要求
python3 --version    # >= 3.11
ffmpeg -version      # >= 4.0（推荐 6.x）
git --version        # >= 2.20
```

### 1.2 安装缺失依赖

**Ubuntu / Debian**：
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git ffmpeg
```

**macOS**（homebrew）：
```bash
brew install python@3.11 git ffmpeg
```

**验证**：
```bash
python3 -c "import sys; assert sys.version_info >= (3, 11), 'need Python 3.11+'; print('✅ Python OK')"
ffmpeg -version 2>&1 | head -1
```

---

## 2. 安装 hermes-agent

如果新机器**没有 hermes-agent**，先安装主框架（参考官方文档）。

```bash
# 假设 hermes-agent 已装在 ~/.hermes/hermes-agent
# 检查
ls ~/.hermes/hermes-agent/
ls ~/.hermes/profiles/  # 应有 huiben profile 目录
```

如果 profile `huiben` 不存在：
```bash
mkdir -p ~/.hermes/profiles/huiben
# 复制或初始化 profile 配置（参考 hermes-agent 文档）
```

---

## 3. 安装 picturebook-video（v5.0 单仓 = 完整可用）

### 3.1 目录约定

所有 skill 仓统一放在 `~/.hermes/profiles/huiben/skills/` 下：
- `creative/`（创意类）
- `social-media/`（社媒类）

### 3.2 必装：本仓（v5.0 单仓含 seedance_mcp 集成）

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills

# 克隆 picturebook-video v5.0（自带 seedance_mcp/）
git clone -b v5.0 https://github.com/leonluo2008-ops/picturebook-video.git \
    $HUIBEN_SKILLS/creative/picturebook-video

# 验证目录结构（必含 seedance_mcp/）
ls $HUIBEN_SKILLS/creative/picturebook-video/
# 预期输出应包含：
#   SKILL.md  README.md  INSTALL.md  INSTALL_TEST.sh
#   references/  seedance_mcp/  bin/  assets/  scripts/
```

> ⚠️ **Git HTTPS TLS 间歇失败兜底**（v5.0 体检实测 · 部分网络环境 GnuTLS recv error）：
> 如果 `git clone https://...` 报 `GnuTLS recv error (-110)`，切 SSH：
> ```bash
> # 一次性：上传 SSH 公钥到 GitHub（https://github.com/settings/keys）
> cat ~/.ssh/id_rsa.pub   # 没的话先 ssh-keygen -t rsa -b 4096
>
> # 然后用 SSH URL：
> git clone -b v5.0 git@github.com:leonluo2008-ops/picturebook-video.git \
>     $HUIBEN_SKILLS/creative/picturebook-video
> ```

### 3.3 部署 MCP wrapper.sh（自动加载 .env）

```bash
# 复制 wrapper.sh 到 profile bin 目录
mkdir -p ~/.hermes/profiles/huiben/bin
cp ~/.hermes/profiles/huiben/skills/creative/picturebook-video/bin/seedance-mcp-wrapper.sh \
   ~/.hermes/profiles/huiben/bin/
chmod +x ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh

# 验证 wrapper.sh 自动指向本仓路径
head -25 ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh | grep SKILL_DIR
# 预期：SKILL_DIR="/home/.../.hermes/profiles/huiben/skills/creative/picturebook-video/seedance_mcp"
```

### 3.4 注册 MCP server 到 hermes-agent

编辑 `~/.hermes/profiles/huiben/config.yaml`，在 `mcp_servers:` 段下添加：

```yaml
mcp_servers:
  seedance:
    command: /home/YOUR_USER/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh
    args: []
    env: {}
```

> **注意**：把 `YOUR_USER` 替换为真实用户名（如 `luo`）。

### 3.5 可选：lark-cli + douyin-ops（按需）

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills

# lark-cli（飞书云盘/消息/文档 - 用到飞书时必装）
git clone https://github.com/leonluo2008-ops/lark-cli.git \
    $HUIBEN_SKILLS/lark-cli

# douyin-ops（抖音数据调研 + 内容发布）
git clone https://github.com/leonluo2008-ops/douyin-ops.git \
    $HUIBEN_SKILLS/social-media/douyin-ops
```

### 3.6 相关但非依赖

| 仓 | 用途 | 是否必装 |
|---|---|---|
| `picturebook-creator` | 绘本前期（从 0 创作角色 + 生图）| ❌ **非依赖**——本 skill 接收现成图片 + 旁白，不需要从 0 创作 |

### 3.7 验证 skill 仓

```bash
# 本仓应包含 seedance_mcp/ 集成
ls ~/.hermes/profiles/huiben/skills/creative/picturebook-video/seedance_mcp/
# 预期：mcp_server.py  seedance_uploads.py  .env.example  smoke_test.py

# 每个核心文件都应在
for f in SKILL.md INSTALL.md INSTALL_TEST.sh seedance_mcp/mcp_server.py seedance_mcp/seedance_uploads.py seedance_mcp/.env.example bin/seedance-mcp-wrapper.sh; do
  if [ -f ~/.hermes/profiles/huiben/skills/creative/picturebook-video/$f ]; then
    echo "✅ $f"
  else
    echo "❌ $f 缺失"
  fi
done
```

---

## 4. 配置 ARK_API_KEY

### 4.1 创建 `.env` 文件

```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video

# 复制模板
cp $SKILL_DIR/seedance_mcp/.env.example $SKILL_DIR/seedance_mcp/.env

# 编辑 .env 填入真实凭据
nano $SKILL_DIR/seedance_mcp/.env
```

### 4.2 必填环境变量

```bash
# === picturebook-video/seedance_mcp/.env ===
# Volcengine Ark API Key（视频生成）
ARK_API_KEY=<YOUR_ARK_API_KEY_HERE>
```

> **加载路径**（v5.0 体检实测）：
> - **MCP 路径**（AI agent 自动调 `mcp_seedance_*` 工具）：由 `bin/seedance-mcp-wrapper.sh` 自动从 `seedance_mcp/.env` 加载（**无需 source**）
> - **冒烟测试路径**（手动验证）：`smoke_test.py` 用 python-dotenv 自动读 `.env`
>
> **同一份 `.env` 服务 MCP + 冒烟测试**——只填一次 = 都通

> **不再需要** `CHEVERETO_API_KEY`。本地图片上传改用 uguu.se 兜底路线（无需任何 env 配置）。

### 4.3 可选环境变量

```bash
# === 抖音数据调研（如用 douyin-ops，按需）===
TIKHUB_TOKEN=<YOUR_TIKHUB_TOKEN_HERE>

# === 飞书消息/云盘（如用 lark-cli，按需）===
FEISHU_APP_ID=<YOUR_FEISHU_APP_ID_HERE>
FEISHU_APP_SECRET=<YOUR_FEISHU_APP_SECRET_HERE>
```

### 4.4 验证 env 加载

```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video

if [ -f "$SKILL_DIR/seedance_mcp/.env" ]; then
  KEY=$(grep '^ARK_API_KEY=*** "$SKILL_DIR/seedance_mcp/.env" | cut -d= -f2-)
  echo "✅ .env 已配置 (ARK_API_KEY 长度 ${#KEY})"
else
  echo "❌ .env 未创建"
fi
```

---

## 5. 依赖图与安装顺序（v5.0 单仓简化）

```
hermes-agent (主框架)
    └── picturebook-video v5.0（本仓 · 单仓含全部依赖）
        ├── SKILL.md + 28 铁律 + 7 步工作流
        ├── seedance_mcp/         # 集成
        │   ├── mcp_server.py        # MCP 协议壳（自动注册 mcp_seedance_*）
        │   ├── seedance_uploads.py  # uguu 上传 + Ark API 调用
        │   ├── .env.example
        │   └── smoke_test.py        # 冒烟测试脚本
        └── bin/seedance-mcp-wrapper.sh  # 加载 .env → 启动 mcp_server.py

可选扩展（按需）：
  ├── lark-cli（飞书云盘/消息）
  ├── douyin-ops（抖音数据）
  └── feishu-channel-quirks（飞书 quirks）

注意：picturebook-creator（绘本前期创作）非本 skill 依赖
```

**安装顺序原则**：

1. 系统依赖（Python / ffmpeg / git）
2. hermes-agent
3. picturebook-video v5.0 单仓（含 seedance_mcp 集成）
4. ARK_API_KEY（填 seedance_mcp/.env）
5. 注册 MCP server 到 hermes-agent
6. **跑 `INSTALL_TEST.sh` 验收**（必跑）
7. 可选 skill 仓（按需）

---

## 6. 验收测试（必跑 · 5 分钟内完成）

**v5.0 起单仓自带验收脚本**：

```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video

# 一键验收（7 步检查 + 端到端视频生成）
bash $SKILL_DIR/INSTALL_TEST.sh
```

**验收内容（7 步全跑）**：

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | skill 仓结构 | `seedance_mcp/` + `references/` + `SKILL.md` 都存在 |
| 2 | `.env` 配置 | `ARK_API_KEY` 已填（长度 > 30）|
| 3 | `wrapper.sh` 已部署 | `~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh` 存在 |
| 4 | Python 依赖 | `mcp` / `httpx` / `python-dotenv` 都可用 |
| 5 | API key 有效性 | 调 `verify_api_key` 返回 valid=true（不扣费）|
| 6 | uguu.se 图床 | 上传测试图返回公网直链 |
| 7 | 端到端视频 | 跑 1 个 5s 视频 · succeeded · 下载成功 |

**全部通过** → 安装完成。**任一失败** → 看具体 step 的报错 + 跳到第 7 节故障排查。

### 6.1 手动验收 MCP server 注册

```bash
# 启动 MCP server 一次，看 stdin/stdout 是否正常
~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh < /dev/null
# 预期：进程启动后等 stdin（mcp 协议），Ctrl+C 退出无报错
```

### 6.2 手动验证 hermes-agent 加载 skill

```bash
# 重启 hermes-agent 让 MCP server 重新加载
# 然后用 hermes CLI 看 picturebook-video + mcp_seedance_* 工具是否可见
hermes skills list --profile huiben | grep -E "picturebook|seedance"

# 预期：
#   │ picturebook-video       │ creative  │ local   │ enabled │
#   │ seedance2.0-tool        │ creative  │ local   │ enabled │（可选，老仓）
```

> **mcp_seedance_* 工具注册**：MCP server 启动后自动注册（无需额外配置）。AI agent 调用 `mcp_seedance_generate_video` 等 4 个工具即可。

---

## 7. 故障排查

### 7.1 `ARK_API_KEY not found` 或 wrapper 报 FATAL

**症状**：wrapper.sh 报 `[seedance-mcp-wrapper] FATAL: .env 里没有 ARK_API_KEY`

**修复**：
```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video

# 1. 检查 .env 文件存在
ls -la $SKILL_DIR/seedance_mcp/.env

# 2. 检查占位符已替换
grep "YOUR_ARK_API_KEY" $SKILL_DIR/seedance_mcp/.env
# 如有输出 = 占位符还没替换

# 3. 替换为真实 key（从 https://console.volcengine.com/ark 获取）
nano $SKILL_DIR/seedance_mcp/.env
```

### 7.2 MCP server 启动失败 / python 报错

**症状**：AI agent 说 `mcp_seedance_*` 工具不可用，或 wrapper.sh 报 ImportError

**修复**：
```bash
# 1. 检查 Python 版本 + 依赖
/home/luo/.hermes/hermes-agent/venv/bin/python3 -c "import mcp, httpx, dotenv; print('OK')"
# 如 ModuleNotFoundError：
/home/luo/.hermes/hermes-agent/venv/bin/pip install mcp httpx python-dotenv

# 2. 检查 seedance_uploads.py 能正常 import
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video/seedance_mcp
/home/luo/.hermes/hermes-agent/venv/bin/python3 -c "import seedance_uploads; print('OK')"

# 3. 跑冒烟测试看具体错
/home/luo/.hermes/hermes-agent/venv/bin/python3 smoke_test.py
```

### 7.3 uguu.se 上传失败

**症状**：冒烟测试 step 6 报 ❌

**修复**：
```bash
# 测试 uguu.se 可达性
curl -sF "files[]=@/etc/hostname" https://uguu.se/upload.php
# 预期返回 JSON: {"success":true,"files":[{"url":"https://h.uguu.se/xxxxx.jpg",...}]}
```

### 7.4 视频生成任务一直 running 不结束

**症状**：`wait_and_download` timeout 后 status 还是 running

**修复**：
```bash
# 1. 检查 seedance API 限额（console.volcengine.com）
# 2. 减小并发（≤2/批 + 主 agent 续跑）
# 3. 简化 prompt 长度（< 2000 字符）
# 4. 减少时长（4-7s 短档优先）
```

### 7.5 验收测试任务失败（status = failed）

**症状**：冒烟测试 step 7 报 failed

**修复**：
```bash
# 1. 看完整错误信息（task_id 在失败前已打印）
TASK_ID="cgt-XXXXXXXX-XXXX"

# 2. 查 task 状态（裸 curl 调 API）
curl -s -H "Authorization: Bearer $YOUR_KEY" \
    "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/$TASK_ID" \
    | python3 -m json.tool

# 3. 错误类型对照：
# - 401 Unauthorized = ARK_API_KEY 错或失效
# - 400 Bad Request = prompt 有敏感词 / 时长超 15s
# - 429 Too Many Requests = API 限流，稍后重试
# - 500 Server Error = Seedance 服务问题
```

### 7.6 ffmpeg 抽帧失败

**症状**：`ffmpeg: command not found` 或 `no such file`

**修复**：
```bash
# Ubuntu
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg
```

### 7.7 Git HTTPS TLS 间歇失败

**症状**：`git clone https://...` 报 `GnuTLS recv error (-110)`

**修复**：见 §3.2 末尾的 SSH 兜底步骤。

---

## 8. 升级与回滚

### 8.1 升级 picturebook-video

```bash
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git fetch origin
git checkout v5.0  # 或更新版本（查 https://github.com/leonluo2008-ops/picturebook-video/tags）

# 重启 hermes-agent 让 MCP server 重新加载
# 跑验收确认升级成功
bash INSTALL_TEST.sh
```

### 8.2 回滚到旧版本

```bash
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git checkout v4.0  # v4.0 仍可用（需另装 seedance2.0-tool 仓）
```

> **回滚 v4.0 提示**：v4.0 依赖 `seedance2.0-tool` 仓，回滚后需要重新安装那个仓 + 部署对应 wrapper.sh。

### 8.3 查看 tag 列表

```bash
git ls-remote --tags https://github.com/leonluo2008-ops/picturebook-video.git
```

当前稳定 tag：
- `v5.0`（**单仓含 seedance_mcp 集成 · 2026-06-16 · 推荐**）
- `v4.0.1`（v8 导演分镜 · 需另装 seedance2.0-tool 仓）
- `v4.0`（v8 导演分镜首版）
- `v3.0`（4 元方法论 + 20 铁律 · 2026-06-14）

---

## 9. 子 skill 联动验收

如果装了 lark-cli + douyin-ops，跑全链路测试：

```bash
# 测试 1：lark-cli 飞书消息
python3 ~/.hermes/profiles/huiben/skills/lark-cli/lark.py send \
    --target feishu \
    --message "✅ picturebook-video v5.0 安装完成"

# 测试 2：douyin-ops 抖音数据
python3 ~/.hermes/profiles/huiben/skills/social-media/douyin-ops/douyin.py search_user \
    --keyword "儿童绘本"
```

> **注**：picturebook-creator（绘本前期创作）与本 skill 无强业务联动，验收跳过。

---

## 10. 维护说明

- 本文档随 picturebook-video v5.0 同步发布
- **v5.0 单仓 = 完整可用**（不再依赖 seedance2.0-tool 仓）
- 验收测试必跑（`INSTALL_TEST.sh`）· 不通过 = 安装未完成
- 子 skill 联动验收 = 可选项 · 但建议跑通核心链路
- 故障排查覆盖 7 类常见问题 · 95% 失败可在此解决
