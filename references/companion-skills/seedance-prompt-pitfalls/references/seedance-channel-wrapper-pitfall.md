# Seedance MCP 渠道 wrapper 陷阱（2026-08-24 实测沉淀）

> **适用**：任何部署 seedance MCP server 的机器（单仓 `picturebook-video/seedance_mcp/` 或 `seedance2.0-tool`）。
> **触发**：换渠道后 `mcp_seedance_*` 工具报 401 / `verify_api_key` 假阴性 / 其它电脑安装后生成失败。

---

## 核心陷阱：wrapper 只加载 `ARK_API_KEY`，漏 `SEEDANCE_BASE_URL` / `SEEDANCE_MODEL`

`mcp_server.py` 用 `os.environ.get("SEEDANCE_BASE_URL", 官方火山默认)` 读 base URL。如果
wrapper.sh 只 `export ARK_API_KEY` 而没有 `export SEEDANCE_BASE_URL` + `SEEDANCE_MODEL`，则：

- MCP 仍连**官方火山地址** `ark.cn-beijing.volces.com`
- 但 key 是第三方渠道的 → **HTTP 401 "API key status is not active"**
- 症状跟"旧 key 缓存"完全一样，但**重启 gateway 也修不好**（重启后 wrapper 仍只 export 了 key）

**这是 2026-08-24 实测根因**：`.env` 已配好第三方渠道三变量，curl 直接 POST 拿得到 task_id，
但 MCP 工具一直 401 —— 因为 wrapper 漏 export 了另外两个变量。

### 修复（wrapper 必须完整加载并 export 三变量）

```bash
CONF=$("$PY" -c "
from dotenv import dotenv_values
d = dotenv_values('$SKILL_DIR/.env')
print(d.get('ARK_API_KEY',''))
print(d.get('SEEDANCE_BASE_URL',''))
print(d.get('SEEDANCE_MODEL',''))
")
mapfile -t CONF_LINES <<< "$CONF"
ARK_API_KEY="${CONF_LINES[0]}"
SEEDANCE_BASE_URL="${CONF_LINES[1]}"
SEEDANCE_MODEL="${CONF_LINES[2]}"
export ARK_API_KEY SEEDANCE_BASE_URL SEEDANCE_MODEL
```

`SEEDANCE_BASE_URL` 缺省回落官方火山；`SEEDANCE_MODEL` 缺省 `doubao-seedance-2-0-fast-260128`
（必须带版本后缀，无后缀 404）。

---

## verify_api_key 假阴性（第三方网关）

- `verify_api_key` 走 `GET {base}/?page_size=1`（list 端点）。
- 第三方网关（如 `aigc.learningcat.cn`）可能**只开 POST 提交端点** → list 返回 405/401 = **假阴性**。
- **判断渠道可用性的唯一可靠方法**：`generate_video` 能否返回 `task_id`。能 = 渠道通。

---

## 跨电脑自动探测（不硬编码用户名）

单仓 wrapper 必须自动定位，否则其它电脑安装必失败：

1. **HERMES_ROOT**：从脚本路径向上找含 `hermes-agent/` 的目录（兼容
   `profiles/<p>/skills/creative/picturebook-video/seedance_mcp` 和
   `<root>/skills/creative/picturebook-video/seedance_mcp` 两种结构）。
2. **seedance_mcp 目录**：`$HERMES_ROOT/profiles/*/skills/creative/picturebook-video/seedance_mcp`
   优先，回退 `$HERMES_ROOT/skills/...`。
3. **PY**：`$HERMES_ROOT/hermes-agent/venv/bin/python3` 优先，回退系统 `python3`。

同理 `smoke_test.py` 用 `Path(__file__).resolve().parent` 定位 `.env`，不写死 `/home/luo/...`。
`INSTALL_TEST.sh` 的 HERMES_ROOT 也从"固定 5 次 dirname"改为"向上找 hermes-agent"
（profiles 结构和根 skills 结构 dirname 次数不同，固定次数必错）。

---

## .env 三变量模板（换渠道 = 只改这里，不碰代码）

```
ARK_API_KEY=<渠道 key>
SEEDANCE_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
SEEDANCE_MODEL=doubao-seedance-2-0-fast-260128
```

- 官方火山 / 第三方网关都适用，改这三行即可。
- 改 `.env` 后**必须重启 Hermes gateway** 才生效（MCP server 是常驻进程，只在启动时读一次 .env）。
- `.env` 和 `.env.bak*` 都要在 `.gitignore`（含 key，**绝不** commit）。
- fast 模型经第三方网关**不认 `resolution` 参数**（报 InvalidParameter），省略即可。

---

## 其它电脑安装检查清单

1. `bin/seedance-mcp-wrapper.sh` 是否为**跨电脑自动探测版**（无 `/home/luo` 硬编码 + 完整 export 三变量）。
2. `.env.example` 是否含三变量模板。
3. `INSTALL_TEST.sh` HERMES_ROOT 是否"向上找 hermes-agent"。
4. `smoke_test.py` 是否用 `__file__` 定位（无硬编码路径）。
5. 跑通 `INSTALL_TEST.sh` 端到端（能出 5s 视频 = 渠道 OK）。
