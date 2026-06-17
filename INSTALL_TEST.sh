#!/usr/bin/env bash
# picturebook-video 安装验收测试（v5.0 单仓验证）
# ============================================
# 目的：验证 picturebook-video 单仓安装 = 完整可用
#       不依赖任何外部仓（包括 seedance2.0-tool）
# 跑通 = picturebook-video v5.0+ 在新机器上能跑视频生成
# 失败 = 看每个 step 的输出

set -e

# ===== 配置 =====
# v5.0.2: 自动检测 HERMES_ROOT，不硬编码用户名（云服是 ubuntu，本地是 luo）
# 策略：从 INSTALL_TEST.sh 自己所在的绝对路径反推（最可靠）
#   /path/to/.hermes/profiles/huiben/skills/creative/picturebook-video/INSTALL_TEST.sh
#   → HERMES_ROOT = /path/to/.hermes
SCRIPT_PATH="$(readlink -f "$0")"
SKILL_DIR="$(dirname "$SCRIPT_PATH")"
HERMES_ROOT="$(dirname "$(dirname "$(dirname "$(dirname "$(dirname "$SKILL_DIR")")")")")"
PROFILE_BIN="$HERMES_ROOT/profiles/huiben/bin"
TEST_DIR="/tmp/picturebook_install_test_$$"

# Python 解释器：优先用 hermes-agent 的 venv，找不到就退化到系统 python3
if [ -x "$HERMES_ROOT/hermes-agent/venv/bin/python3" ]; then
  PY="$HERMES_ROOT/hermes-agent/venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "❌ 找不到 python3"
  exit 1
fi

# 调试输出（让用户知道检测到啥）
echo "  SCRIPT_PATH=$SCRIPT_PATH"
echo "  SKILL_DIR=$SKILL_DIR"
echo "  HERMES_ROOT=$HERMES_ROOT"
echo "  PY=$PY"
echo ""

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "================================================="
echo "picturebook-video v5.0 安装验收测试"
echo "================================================="
echo ""

# ===== Step 1: skill 仓存在 =====
echo -e "${YELLOW}[1/7] 检查 skill 仓结构...${NC}"
if [ ! -d "$SKILL_DIR/seedance_mcp" ]; then
  echo -e "${RED}❌ 缺失: $SKILL_DIR/seedance_mcp/${NC}"
  echo "   修复: 重新 git clone picturebook-video v5.0+"
  exit 1
fi
if [ ! -d "$SKILL_DIR/references" ]; then
  echo -e "${RED}❌ 缺失: $SKILL_DIR/references/${NC}"
  exit 1
fi
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo -e "${RED}❌ 缺失: $SKILL_DIR/SKILL.md${NC}"
  exit 1
fi
echo -e "${GREEN}✅ skill 仓结构完整${NC}"
echo ""

# ===== Step 2: .env 配置 =====
echo -e "${YELLOW}[2/7] 检查 .env 配置...${NC}"
if [ ! -f "$SKILL_DIR/seedance_mcp/.env" ]; then
  echo -e "${YELLOW}⚠️  .env 不存在,自动创建模板:${NC}"
  cp "$SKILL_DIR/seedance_mcp/.env.example" "$SKILL_DIR/seedance_mcp/.env"
  echo -e "${RED}❌ 请编辑后重跑:${NC}"
  echo "   nano $SKILL_DIR/seedance_mcp/.env"
  echo "   替换 ARK_API_KEY=<YOUR_ARK_API_KEY_HERE> 为真实 key"
  exit 1
fi

# 提取 ARK_API_KEY（跳过注释行 + 占位符检查）
ARK_KEY=$(grep '^ARK_API_KEY=' "$SKILL_DIR/seedance_mcp/.env" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d ' ')
if [ -z "$ARK_KEY" ] || [ "$ARK_KEY" = "<YOUR_ARK_API_KEY_HERE>" ]; then
  echo -e "${RED}❌ ARK_API_KEY 还未替换为真实值${NC}"
  echo "   nano $SKILL_DIR/seedance_mcp/.env"
  exit 1
fi
echo -e "${GREEN}✅ ARK_API_KEY 已配置 (长度 ${#ARK_KEY})${NC}"
echo ""

# ===== Step 3: wrapper.sh 已部署 =====
# v5.0.2: wrapper 可能部署在两个常见位置（看用户选择）
#   A) $HERMES_ROOT/profiles/huiben/bin/  ← INSTALL_TEST.sh 首选
#   B) $HERMES_ROOT/bin/                  ← v5.0 升级文档推荐
# 策略：先 A 后 B，找到后 echo 实际位置 + 对比 config.yaml
echo -e "${YELLOW}[3/7] 检查 MCP wrapper.sh...${NC}"
WRAPPER=""
for CAND in "$PROFILE_BIN/seedance-mcp-wrapper.sh" "$HERMES_ROOT/bin/seedance-mcp-wrapper.sh"; do
  if [ -f "$CAND" ]; then
    WRAPPER="$CAND"
    break
  fi
done

if [ -z "$WRAPPER" ]; then
  echo -e "${YELLOW}⚠️  wrapper.sh 未部署,自动复制到 $PROFILE_BIN/:${NC}"
  mkdir -p "$PROFILE_BIN"
  cp "$SKILL_DIR/bin/seedance-mcp-wrapper.sh" "$PROFILE_BIN/seedance-mcp-wrapper.sh"
  chmod +x "$PROFILE_BIN/seedance-mcp-wrapper.sh"
  # patch SKILL_DIR 路径
  sed -i "s|/skills/creative/seedance2.0-tool|/skills/creative/picturebook-video/seedance_mcp|g" "$PROFILE_BIN/seedance-mcp-wrapper.sh"
  sed -i "s|spikes/001-mcp-uguu-server/mcp_server.py|mcp_server.py|g" "$PROFILE_BIN/seedance-mcp-wrapper.sh"
  WRAPPER="$PROFILE_BIN/seedance-mcp-wrapper.sh"
  echo -e "${GREEN}✅ wrapper.sh 已部署到 $WRAPPER${NC}"
else
  # 检查是否指向新路径
  if grep -q "seedance2.0-tool" "$WRAPPER"; then
    echo -e "${YELLOW}⚠️  wrapper.sh 仍指向 seedance2.0-tool 旧路径,自动修正:${NC}"
    sed -i "s|/skills/creative/seedance2.0-tool|/skills/creative/picturebook-video/seedance_mcp|g" "$WRAPPER"
    sed -i "s|spikes/001-mcp-uguu-server/mcp_server.py|mcp_server.py|g" "$WRAPPER"
  fi
  echo -e "${GREEN}✅ wrapper.sh 已就位: $WRAPPER${NC}"
fi

# 交叉验证：与 config.yaml 的 seedance.command 一致？
if [ -f "$HERMES_ROOT/config.yaml" ] && command -v grep >/dev/null 2>&1; then
  CFG_CMD=$(grep -A3 "seedance:" "$HERMES_ROOT/config.yaml" 2>/dev/null | grep -E "^\s*command:" | head -1 | sed 's/.*command:[[:space:]]*//' | tr -d '"' | tr -d "'" | xargs)
  if [ -n "$CFG_CMD" ] && [ "$CFG_CMD" != "$WRAPPER" ]; then
    echo -e "${YELLOW}⚠️  config.yaml 指向 $CFG_CMD 与实际 wrapper $WRAPPER 不一致${NC}"
    echo "   建议：保持一致（改 config.yaml 或重部署 wrapper.sh）"
  elif [ -n "$CFG_CMD" ]; then
    echo -e "${GREEN}✅ config.yaml 与 wrapper 路径一致${NC}"
  fi
fi
echo ""

# ===== Step 4: Python 依赖 =====
echo -e "${YELLOW}[4/7] 检查 Python 依赖...${NC}"
cd "$SKILL_DIR/seedance_mcp" && $PY -c "
import mcp, httpx
try:
    from dotenv import dotenv_values
    print('✅ mcp / httpx / python-dotenv 全部可用')
except ImportError as e:
    print(f'❌ 缺依赖: {e}')
    print('   pip install python-dotenv')
    raise SystemExit(1)
"
echo ""

# ===== Step 5: API key 有效性 =====
echo -e "${YELLOW}[5/7] 验证 API key 有效性（不扣费）...${NC}"
cd "$SKILL_DIR/seedance_mcp" && ARK_API_KEY="$ARK_KEY" $PY -c "
import asyncio, sys, json
sys.path.insert(0, '.')
import seedance_uploads as U

async def main():
    try:
        result = await U.ark_request_async('GET', 'https://ark.cn-beijing.volcsandbox.com/api/v3/contents/generations/tasks?page_size=1', timeout=15)
        print('✅ API key 有效 · response keys: ' + str(list(result.keys()) if isinstance(result, dict) else type(result).__name__))
    except Exception as e:
        print(f'❌ API key 无效: {e}')
        sys.exit(1)

asyncio.run(main())
" 2>&1 | tail -3
echo ""

# ===== Step 6: uguu.se 图床 =====
echo -e "${YELLOW}[6/7] 验证图床 uguu.se 可用...${NC}"
mkdir -p "$TEST_DIR"
curl -sLo "$TEST_DIR/test.jpg" https://picsum.photos/800/600 2>&1 >/dev/null
UGUU_RESP=$(curl -sF "files[]=@$TEST_DIR/test.jpg" https://uguu.se/upload.php 2>&1)
UGUU_URL=$(echo "$UGUU_RESP" | $PY -c "import sys,json; d=json.load(sys.stdin); print(d.get('files',[{}])[0].get('url',''))" 2>/dev/null || echo "")
if [ -n "$UGUU_URL" ]; then
  echo -e "${GREEN}✅ uguu.se 上传成功: $UGUU_URL${NC}"
else
  echo -e "${RED}❌ uguu.se 上传失败${NC}"
  echo "   response: $UGUU_RESP"
  exit 1
fi
echo ""

# ===== Step 7: 端到端视频生成 =====
echo -e "${YELLOW}[7/7] 端到端视频生成测试（5s clip）...${NC}"
echo "  提交任务..."
TASK_ID=$(cd "$SKILL_DIR/seedance_mcp" && ARK_API_KEY="$ARK_KEY" $PY -c "
import asyncio, sys, json
sys.path.insert(0, '.')
sys.path.insert(0, '$TEST_DIR')
import mcp_server
from mcp_server import call_tool

PROMPT = '''A cute cartoon cat sitting on a wooden chair, looking at the camera with curious eyes, paper craft collage style, simple background, 5 second test clip.

保持无字幕。
不要生成水印。
不要生成 Logo。
无人声、无歌唱、无配音、无朗读。'''

async def main():
    result = await call_tool('generate_video', {
        'prompt': PROMPT,
        'image': '$UGUU_URL',
        'duration': 5,
        'ratio': '16:9',
        'watermark': 'none',
        'generate_audio': False,
    })
    text = result[0].text
    data = json.loads(text)
    if 'task_id' in data:
        print(data['task_id'])
    else:
        print('ERROR: ' + text, file=sys.stderr)
        sys.exit(1)

asyncio.run(main())
" 2>&1 | tail -1)

if [ -z "$TASK_ID" ] || [[ "$TASK_ID" == ERROR* ]]; then
  echo -e "${RED}❌ 任务提交失败: $TASK_ID${NC}"
  exit 1
fi
echo "  task_id: $TASK_ID"

echo "  等待完成（最长 180s）..."
cd "$SKILL_DIR/seedance_mcp" && ARK_API_KEY="$ARK_KEY" $PY -c "
import asyncio, sys, json
sys.path.insert(0, '.')
import mcp_server
from mcp_server import call_tool

async def main():
    result = await call_tool('wait_and_download', {
        'task_id': '$TASK_ID',
        'output_path': '$TEST_DIR/test-output.mp4',
        'timeout_sec': 180,
        'poll_interval_sec': 15,
    })
    print(result[0].text)

asyncio.run(main())
" 2>&1 | tail -3

if [ -f "$TEST_DIR/test-output.mp4" ]; then
  SIZE=$(ls -lh "$TEST_DIR/test-output.mp4" | awk '{print $5}')
  DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TEST_DIR/test-output.mp4" 2>/dev/null || echo "?")
  echo -e "${GREEN}✅ 测试通过: 视频已生成 ($SIZE · ${DURATION}s)${NC}"
  echo ""
  echo "================================================="
  echo -e "${GREEN}picturebook-video v5.0 安装验收完成 ✅${NC}"
  echo "================================================="
  echo ""
  echo "单仓可用 · 不依赖 seedance2.0-tool 仓"
  echo ""
  echo "测试产物: $TEST_DIR/test-output.mp4"
  echo "（可手动 rm -rf $TEST_DIR 清理）"
  exit 0
else
  echo -e "${RED}❌ 视频文件未生成${NC}"
  exit 1
fi
