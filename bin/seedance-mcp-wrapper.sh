#!/usr/bin/env bash
# seedance MCP server wrapper
# 作用：从 skill 仓的 .env 自动加载 ARK_API_KEY，然后 exec mcp_server.py
# 设计：
#   1. 不修改 mcp_server.py（spike 代码保持 throwaway 状态）
#   2. 不在 ~/.hermes/config.yaml 明文注入 key（防误 commit）
#   3. key 走 .env 文件（已是 .gitignore 规则）
#   4. exec（不是 source+run）—— PID 1 = python，信号转发干净

set -e

# 仓根（profile 仓）
SKILL_DIR="/home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool"

# .env 存在性检查（fail fast 比静默好）
if [[ ! -f "$SKILL_DIR/.env" ]]; then
    echo "[seedance-mcp-wrapper] FATAL: $SKILL_DIR/.env 不存在" >&2
    exit 1
fi

# 从 .env 加载 ARK_API_KEY（用 python-dotenv，比手工 parse 鲁棒）
ARK_API_KEY=$(/home/luo/.hermes/hermes-agent/venv/bin/python3.11 -c "
from dotenv import dotenv_values
print(dotenv_values('$SKILL_DIR/.env').get('ARK_API_KEY', ''))
")

if [[ -z "$ARK_API_KEY" ]]; then
    echo "[seedance-mcp-wrapper] FATAL: .env 里没有 ARK_API_KEY" >&2
    exit 1
fi

# PYTHONPATH 让 mcp_server.py 能 import 仓根的 seedance_uploads.py
export PYTHONPATH="$SKILL_DIR"
export ARK_API_KEY="$ARK_API_KEY"

# exec（PID 1 替换为 python，stdin/stdout/stderr 全透传，信号处理干净）
exec /home/luo/.hermes/hermes-agent/venv/bin/python3.11 \
    "$SKILL_DIR/spikes/001-mcp-uguu-server/mcp_server.py"
