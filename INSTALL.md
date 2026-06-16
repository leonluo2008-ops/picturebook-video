# picturebook-video 安装说明

> **目标读者**：在新机器上安装 hermes-agent + picturebook-video skill 仓的 AI 助手 / 工程师
> **AI 可自动化程度**：100%（含验收测试 + 故障排查 + 子 skill 联动）
> **安装总耗时**：约 10-15 分钟（含视频生成验收测试）
> **当前稳定版本**：v4.0（v8 prompt 模板 · 2026-06-16）

---

## 0. 概览

### 0.1 必装组件一览

| # | 组件 | 类型 | 必填 | 用途 |
|---|---|---|---|---|
| 1 | Python 3.11+ | 系统依赖 | ✅ | 运行 hermes-agent + seedance.py |
| 2 | ffmpeg / ffprobe | 系统依赖 | ✅ | 视频抽帧 + 时长验证 |
| 3 | git | 系统依赖 | ✅ | 拉取 skill 仓 |
| 4 | hermes-agent | 主框架 | ✅ | AI agent 运行环境 |
| 5 | seedance2.0-tool | 视频底层工具 | ✅ | 调用 Volcengine Seedance API |
| 6 | picturebook-video | 本仓（绘本视频工作流）| ✅ | 7 步调度 + 4 子 agent + 28 铁律 |
| 7 | lark-cli | 兄弟 skill（可选）| ⭕ | 飞书云盘/消息/文档 |
| 8 | douyin-ops | 兄弟 skill（可选）| ⭕ | 抖音数据调研 + 发布 |

### 0.2 必填环境变量

| 变量 | 必填 | 用途 | 获取地址 |
|---|---|---|---|
| `ARK_API_KEY` | ✅ | Volcengine Ark API（视频生成）| https://console.volcengine.com/ark |

### 0.3 已废弃 / 不再需要

| 变量 | 状态 | 替代方案 |
|---|---|---|
| `CHEVERETO_API_KEY` | ❌ 已废弃 | 本地图片上传改用 **uguu.se** 兜底路线（multipart field `files[]` 上传 + 直接 curl 调 ark API），无需任何 env 变量。详见 `picturebook-video/references/uguu-fallback-route.md` |

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

## 3. 安装 skill 仓（2 必装 + 2 可选）

### 3.1 目录约定

所有 skill 仓统一放在 `~/.hermes/profiles/huiben/skills/` 下：
- `creative/`（创意类）
- `social-media/`（社媒类）

### 3.2 必装 2 仓

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills

# 1. seedance2.0-tool（视频底层工具 · Volcengine Seedance API）
mkdir -p $HUIBEN_SKILLS/creative
git clone https://github.com/leonluo2008-ops/seedance2.0-tool.git \
    $HUIBEN_SKILLS/creative/seedance2.0-tool

# 2. picturebook-video（本仓 · v4.0 v8 导演分镜稳定版）
git clone -b v4.0 https://github.com/leonluo2008-ops/picturebook-video.git \
    $HUIBEN_SKILLS/creative/picturebook-video
```

> ⚠️ **Git HTTPS TLS 间歇失败兜底**（v4.0 体检实测 · 部分网络环境 GnuTLS recv error）：
> 如果 `git clone https://...` 报 `GnuTLS recv error (-110)`，切 SSH：
> ```bash
> # 一次性：上传 SSH 公钥到 GitHub（https://github.com/settings/keys）
> cat ~/.ssh/id_rsa.pub   # 没的话先 ssh-keygen
>
> # 然后用 SSH URL：
> git clone git@github.com:leonluo2008-ops/seedance2.0-tool.git $HUIBEN_SKILLS/creative/seedance2.0-tool
> git clone -b v4.0 git@github.com:leonluo2008-ops/picturebook-video.git $HUIBEN_SKILLS/creative/picturebook-video
> ```

### 3.3 可选 2 仓

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills

# 3. lark-cli（飞书云盘/消息/文档 - 用到飞书时必装）
git clone https://github.com/leonluo2008-ops/lark-cli.git \
    $HUIBEN_SKILLS/lark-cli

# 4. douyin-ops（抖音数据调研 + 内容发布）
git clone https://github.com/leonluo2008-ops/douyin-ops.git \
    $HUIBEN_SKILLS/social-media/douyin-ops
```

### 3.4 相关但非依赖（与本 skill 业务上下游不直接相关）

| 仓 | 用途 | 是否必装 |
|---|---|---|
| `picturebook-creator` | 绘本前期（从 0 创作角色 + 生图）| ❌ **非依赖**——本 skill 接收现成图片 + 旁白，不需要从 0 创作。如有外部图源（飞书 tar 包 / 本地）= 不必装 |

### 3.5 验证 skill 仓

```bash
# 必装 2 仓应都在
ls $HUIBEN_SKILLS/creative/
# 预期输出：picturebook-video  seedance2.0-tool

# 每个仓都应有 SKILL.md
for d in picturebook-video seedance2.0-tool; do
    if [ -f $HUIBEN_SKILLS/creative/$d/SKILL.md ]; then
        echo "✅ $d/SKILL.md"
    else
        echo "❌ $d/SKILL.md 缺失"
    fi
done
```

---

## 4. 配置环境变量

### 4.1 创建 `.env` 文件

```bash
# seedance2.0-tool 仓自带 .env 模板
SEEDANCE_DIR=~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool
ls $SEEDANCE_DIR/.env.example 2>/dev/null && cp $SEEDANCE_DIR/.env.example $SEEDANCE_DIR/.env || true

# 编辑 .env 填入真实凭据
nano $SEEDANCE_DIR/.env
```

### 4.2 必填环境变量（替换占位字符串）

```bash
# === seedance2.0-tool/.env ===
# Volcengine Ark API Key（视频生成）
ARK_API_KEY=<YOUR_ARK_API_KEY_HERE>
```

> **注意**：**不再需要** `CHEVERETO_API_KEY`。本地图片上传改用 uguu.se 兜底路线（无需任何 env 配置，详见 `references/uguu-fallback-route.md`）。

> **2 套加载路径**（v4.0 体检实测）：
> - **CLI 路径**（手动跑 `seedance.py`）：用 `source .../.env` 注入 shell 环境变量
> - **MCP 路径**（AI agent 自动调 `mcp_seedance_*` 工具）：由 `bin/seedance-mcp-wrapper.sh` 自动从 skill 仓的 `.env` 加载（**无需 source**）
>
> **同一份 `.env` 服务 2 套路径**——只填一次 = CLI + MCP 都通

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
set -a
source ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env
set +a

# 验证（注意：用 echo 会暴露真实 key，用 ${VAR:+set} 测试）
if [ -n "$ARK_API_KEY" ] && [ "$ARK_API_KEY" != "<YOUR_ARK_API_KEY_HERE>" ]; then
    echo "✅ ARK_API_KEY 已配置（长度 ${#ARK_API_KEY}）"
else
    echo "❌ ARK_API_KEY 未配置或还是占位字符串"
fi

# 注：CHEVERETO_API_KEY 不再必填 = uguu 兜底路线自动处理
echo "✅ 图床走 uguu 兜底（无需 env）"
```

---

## 5. 依赖图与安装顺序

```
hermes-agent (主框架)
    └── picturebook-video v4.0（本仓 · 调度中枢）
        └── seedance2.0-tool（必装 · 视频生成 CLI）

可选扩展（按需）：
  ├── lark-cli（飞书云盘/消息）
  ├── douyin-ops（抖音数据）
  └── feishu-channel-quirks（飞书 quirks）

注意：picturebook-creator（绘本前期创作）非本 skill 依赖
```

**安装顺序原则**：

1. 系统依赖（Python / ffmpeg / git）
2. hermes-agent
3. 必装 skill 仓：seedance2.0-tool → picturebook-video
4. env 变量
5. 验收测试（跑通一个 5s 视频）
6. 可选 skill 仓（按需）

---

## 6. 验收测试（必跑 · 5 分钟内完成）

### 6.1 单 Clip 端到端测试

**目的**：验证 2 必装 skill 仓 + env 变量全部正确配置。

```bash
# 创建测试目录
mkdir -p /tmp/pic_install_test
cd /tmp/pic_install_test

# 准备 1 张测试图（任意 JPG）
curl -sLo test.jpg https://picsum.photos/800/600

# 准备 1 句测试旁白
cat > narration.txt <<'EOF'
A cat sitting on a chair, looking at the camera.
EOF

# 跑 1 个 Clip（5s 整数档）
PROMPT="A cute cartoon cat@Image1 (orange tabby with green eyes) sitting on a wooden chair, looking at the camera with curious eyes, paper craft collage style, simple background, 5 second test clip."

set -a
source ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env
set +a

python3 ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py create \
    --ref-images /tmp/pic_install_test/test.jpg \
    --prompt "$PROMPT" \
    --duration 5 \
    --ratio 16:9 \
    --resolution 720P \
    --model doubao-seedance-2-0-fast-260128 \
    --watermark false \
    --generate-audio true

# 应输出：
# ✅ Task created: cgt-XXXXXXXX-XXXX
# Use 'seedance.py status <task_id>' to check progress.
```

### 6.2 等待任务完成

```bash
TASK_ID="cgt-XXXXXXXX-XXXX"  # 替换为上一步输出的 task_id
for i in $(seq 1 20); do
    STATUS=$(python3 ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py status $TASK_ID 2>&1)
    if echo "$STATUS" | grep -q succeeded; then
        echo "✅ Round $i: SUCCEEDED"
        VIDEO_URL=$(echo "$STATUS" | grep -oE '"video_url":\s*"[^"]+"' | head -1 | sed 's/"video_url":\s*"//;s/"$//' | sed 's/\\u0026/\&/g')
        curl -sLo /tmp/pic_install_test/test-output.mp4 "$VIDEO_URL"
        echo "✅ 视频已下载：/tmp/pic_install_test/test-output.mp4"
        break
    elif echo "$STATUS" | grep -q failed; then
        echo "❌ Round $i: FAILED"
        echo "$STATUS" | tail -20
        break
    fi
    echo "⏳ Round $i: 轮询中..."
    sleep 15
done
```

### 6.3 验证视频

```bash
# 检查文件存在 + 时长
ls -lh /tmp/pic_install_test/test-output.mp4
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \
    /tmp/pic_install_test/test-output.mp4
# 预期：约 5.0-5.5 秒（seedance 自动 ceiling）

# 如有 ffmpeg 抽帧工具，看一眼 t=0.5s 是否正常
ffmpeg -y -ss 0.5 -i /tmp/pic_install_test/test-output.mp4 -frames:v 1 /tmp/pic_install_test/frame.jpg
ls -lh /tmp/pic_install_test/frame.jpg
```

### 验收通过标准

| 检查项 | 通过条件 |
|---|---|
| 任务创建 | 输出 Task ID 无报错 |
| API 调用成功 | status = succeeded（不是 failed）|
| 视频下载 | mp4 文件 > 100KB |
| 时长正确 | 5-6 秒范围 |
| env 配置正确 | `ARK_API_KEY` 已配置且不是占位 |

**全部通过** → 安装完成。**任一失败** → 跳到第 7 节故障排查。

---

## 7. 故障排查

### 7.1 `ARK_API_KEY not found`

**症状**：调用 seedance.py 时报 `KeyError: 'ARK_API_KEY'` 或 `ARK_API_KEY=<YOUR_ARK_API_KEY_HERE>`

**修复**：
```bash
# 1. 检查 .env 文件存在
ls -la ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env

# 2. 检查占位符已替换
grep "YOUR_ARK_API_KEY" ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env
# 如有输出 = 占位符还没替换

# 3. 替换为真实 key（从 https://console.volcengine.com/ark 获取）
nano ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env
```

### 7.2 `Chevereto upload failed`（已废弃场景）

> **v1.0.3+pic13 起**：本 skill 已迁移到 **uguu 兜底路线**，不再依赖 Chevereto。
>
> 如旧版 seedance.py 仍报 Chevereto 错误：
>
> ```bash
> # 升级 seedance2.0-tool 到最新版（v2.0+）
> cd ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool
> git pull origin main
>
> # 或用 uguu 兜底脚本
> # 详见 picturebook-video/references/uguu-fallback-route.md
> ```
>
> 测试图床上传：
> ```bash
> # uguu 测试
> curl -sF 'files[]=@/tmp/pic_install_test/test.jpg' https://uguu.se/upload.php
> # 预期返回 JSON：{"files":[{"url":"https://n.uguu.se/xxxxx.jpg",...}]}
> ```

### 7.3 ffmpeg 抽帧失败

**症状**：`ffmpeg: command not found` 或 `no such file`

**修复**：
```bash
# Ubuntu
sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# 验证
ffmpeg -version
```

### 7.4 skill 仓 SKILL.md 缺失

**症状**：调用 skill 时报 `skill not found`

**修复**：
```bash
# 检查目录结构
ls ~/.hermes/profiles/huiben/skills/creative/
ls ~/.hermes/profiles/huiben/skills/creative/picturebook-video/SKILL.md

# 重新克隆（如缺失）
rm -rf ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git clone -b v4.0 https://github.com/leonluo2008-ops/picturebook-video.git \
    ~/.hermes/profiles/huiben/skills/creative/picturebook-video
```

### 7.5 hermes-agent 找不到 skill 仓

**症状**：AI 说 `skill picturebook-video not found`

**修复**：
```bash
# 1. 检查 profile 路径
ls ~/.hermes/profiles/huiben/skills/creative/picturebook-video/SKILL.md

# 2. 路径必填 ~/.hermes/profiles/huiben/skills/（不是 ~/.hermes/skills/）
# 全局 ~/.hermes/skills/ 会带进 apple/gaming/mlops 等无关 skill
```

### 7.6 视频生成任务一直 running 不结束

**症状**：status 一直是 `running`，25 轮轮询都没 succeeded

**修复**：
```bash
# 1. 检查 seedance API 限额
# 2. 减小并发（≤2/批 + 主 agent 续跑）
# 3. 简化 prompt 长度（< 2000 字符）
# 4. 减少时长（4-7s 短档优先）
```

### 7.7 验收测试任务失败（status = failed）

**症状**：验收测试跑出 failed

**修复**：
```bash
# 1. 看完整错误信息
python3 ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py status $TASK_ID 2>&1

# 2. 检查错误类型
# - 401 Unauthorized = ARK_API_KEY 错
# - 400 Bad Request = prompt 有敏感词 / 时长超 15s
# - 429 Too Many Requests = API 限流，稍后重试
# - 500 Server Error = Seedance 服务问题
```

---

## 8. 升级与回滚

### 8.1 升级 picturebook-video

```bash
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git fetch origin
git checkout v4.0  # 或更新版本（查 https://github.com/leonluo2008-ops/picturebook-video/tags）

# 重启 hermes-agent 让 skill 重新加载
```

### 8.2 回滚到旧版本

```bash
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git checkout v3.0  # 或已知稳定的旧 tag
```

### 8.3 查看 tag 列表

```bash
git ls-remote --tags https://github.com/leonluo2008-ops/picturebook-video.git
```

当前稳定 tag：
- `v4.0`（v8 导演分镜 · 2026-06-16 · 推荐）
- `v3.0`（4 元方法论 + 20 铁律 · 2026-06-14）
- `v2.0`（领读绘本稳定版 · 2026-06-08）

---

## 9. 子 skill 联动验收

如果装了 lark-cli + douyin-ops，跑全链路测试：

```bash
# 测试 1：lark-cli 飞书消息
python3 ~/.hermes/profiles/huiben/skills/lark-cli/lark.py send \
    --target feishu \
    --message "✅ picturebook-video v4.0 安装完成"

# 测试 2：douyin-ops 抖音数据
python3 ~/.hermes/profiles/huiben/skills/social-media/douyin-ops/douyin.py search_user \
    --keyword "儿童绘本"
```

> **注**：picturebook-creator（绘本前期创作）与本 skill 无强业务联动，验收跳过。

---

## 10. 维护说明

- 本文档随 picturebook-video v4.0 同步发布
- 验收测试必跑 · 不通过 = 安装未完成
- 子 skill 联动验收 = 可选项 · 但建议跑通核心链路
- 故障排查覆盖 7 类常见问题 · 95% 失败可在此解决
