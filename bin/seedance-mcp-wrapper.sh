#!/usr/bin/env bash
# seedance MCP server wrapper (v5.0.3 — 跨电脑通用 · 自动探测路径)
# 作用：从 seedance_mcp/.env 加载 Seedance 配置，然后 exec mcp_server.py
# 设计：
#   1. 不修改 mcp_server.py（保持原样）
#   2. 不在 ~/.hermes/config.yaml 明文注入 key（防误 commit）
#   3. key 走 .env 文件（已是 .gitignore 规则）
#   4. exec（不是 source+run）—— PID 1 = python，信号转发干净
#   5. 路径自动探测 —— 不硬编码用户名，跨用户/跨主机可用

set -e

# ===== Step 1: 反推 HERMES_ROOT（不硬编码用户名）=====
# wrapper 可能部署在 $HERMES_ROOT/bin/ 或 $HERMES_ROOT/profiles/<p>/bin/
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

HERMES_ROOT=""
_D="$SCRIPT_DIR"
for _i in 1 2 3 4 5 6; do
  if [ -d "$_D/hermes-agent" ]; then HERMES_ROOT="$_D"; break; fi
  _D="$(dirname "$_D")"
done
[ -z "$HERMES_ROOT" ] && HERMES_ROOT="$HOME/.hermes"

# ===== Step 2: 定位 seedance_mcp 目录（多候选）=====
SKILL_DIR=""
# 候选 A：profiles/<任意profile>/skills/creative/picturebook-video/seedance_mcp
for _p in "$HERMES_ROOT"/profiles/*/; do
  _cand="$_p/skills/creative/picturebook-video/seedance_mcp"
  if [ -f "$_cand/mcp_server.py" ]; then SKILL_DIR="$_cand"; break; fi
done
# 候选 B：$HERMES_ROOT/skills/creative/picturebook-video/seedance_mcp
if [ -z "$SKILL_DIR" ] && [ -f "$HERMES_ROOT/skills/creative/picturebook-video/seedance_mcp/mcp_server.py" ]; then
  SKILL_DIR="$HERMES_ROOT/skills/creative/picturebook-video/seedance_mcp"
fi

if [ -z "$SKILL_DIR" ]; then
  echo "[seedance-mcp-wrapper] FATAL: 找不到 seedance_mcp 目录（HERMES_ROOT=$HERMES_ROOT）" >&2
  exit 1
fi

# .env 存在性检查（fail fast 比静默好）
if [[ ! -f "$SKILL_DIR/.env" ]]; then
    echo "[seedance-mcp-wrapper] FATAL: $SKILL_DIR/.env 不存在" >&2
    exit 1
fi

# ===== Step 3: 从 .env 加载全部 Seedance 配置 =====
# ARK_API_KEY / SEEDANCE_BASE_URL / SEEDANCE_MODEL
# 一次读三个变量，避免只 export key 导致 base URL 落回官方 → 401
# 用 hermes venv python（有 dotenv）；找不到则回退系统 python3
PY="${HERMES_ROOT}/hermes-agent/venv/bin/python3"
if [ ! -x "$PY" ]; then PY="$(command -v python3)"; fi
if [ -z "$PY" ]; then
  echo "[seedance-mcp-wrapper] FATAL: 找不到 python3" >&2
  exit 1
fi

CONF=$("$PY" -c "
import sys
try:
    from dotenv import dotenv_values
except ImportError:
    sys.exit(2)
d = dotenv_values('$SKILL_DIR/.env')
print(d.get('ARK_API_KEY',''))
print(d.get('SEEDANCE_BASE_URL',''))
print(d.get('SEEDANCE_MODEL',''))
") || {
  echo "[seedance-mcp-wrapper] FATAL: dotenv 不可用，请 pip install python-dotenv" >&2
  exit 1
}

# 逐行读回三个变量（第一行 ARK_API_KEY，第二行 BASE_URL，第三行 MODEL）
mapfile -t CONF_LINES <<< "$CONF"
ARK_API_KEY="${CONF_LINES[0]}"
SEEDANCE_BASE_URL="${CONF_LINES[1]}"
SEEDANCE_MODEL="${CONF_LINES[2]}"

if [[ -z "$ARK_API_KEY" ]]; then
    echo "[seedance-mcp-wrapper] FATAL: .env 里没有 ARK_API_KEY" >&2
    exit 1
fi
if [[ -z "$SEEDANCE_BASE_URL" ]]; then
    echo "[seedance-mcp-wrapper] WARN: .env 里没有 SEEDANCE_BASE_URL，将回落官方火山引擎" >&2
fi
if [[ -z "$SEEDANCE_MODEL" ]]; then
    SEEDANCE_MODEL="doubao-seedance-2-0-fast-260128"
fi

# ===== Step 4: export + exec =====
# PYTHONPATH 让 mcp_server.py 能 import 同目录的 seedance_uploads.py
export PYTHONPATH="$SKILL_DIR"
export ARK_API_KEY="$ARK_API_KEY"
export SEEDANCE_BASE_URL="$SEEDANCE_BASE_URL"
export SEEDANCE_MODEL="$SEEDANCE_MODEL"

exec "$PY" "$SKILL_DIR/mcp_server.py"
