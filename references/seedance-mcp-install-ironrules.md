# Seedance MCP 跨电脑安装铁律（v5.0.19 沉淀 · 2026-08-24）

> **沉淀来源**: 2026-08-24 云服 Seedance 渠道从官方火山切换到第三方 `aigc.learningcat.cn` 后 MCP 持续 401，最终根因是 wrapper.sh 只加载 `ARK_API_KEY`、漏 `SEEDANCE_BASE_URL`/`SEEDANCE_MODEL`，且硬编码 `/home/luo` 路径。**修复后实测 INSTALL_TEST.sh 端到端出片。**
>
> **核心结论**: 任何电脑装 Seedance MCP，**只 clone 1 个 picturebook-video 仓 = 完整可用**，但必须满足以下 3 条铁律，否则必踩 401 / 找不到 task / 路径错三坑。

---

## 铁律 1 · wrapper.sh 必须完整加载 3 变量（只载 key = 401）

`bin/seedance-mcp-wrapper.sh` 必须从 `.env` 加载并 export **全部 3 个变量**：

```bash
ARK_API_KEY        # 渠道 API Key
SEEDANCE_BASE_URL  # 渠道 base URL
SEEDANCE_MODEL     # 模型 ID（必须带版本后缀）
```

**坑的机制**：`mcp_server.py` 用 `os.environ.get("SEEDANCE_BASE_URL", 官方火山默认)`。如果 wrapper 只 export 了 `ARK_API_KEY`（旧版 bug），则 base URL 落到官方 `ark.cn-beijing.volces.com`，而 key 是第三方渠道的 → **HTTP 401 "API key status is not active"**。

**判断**：`grep -c "SEEDANCE_BASE_URL\|SEEDANCE_MODEL" bin/seedance-mcp-wrapper.sh` 应为 ≥2。只 `grep ARK_API_KEY` 不够——base URL 是另一条腿。

**换渠道 = 只改 `.env` 3 变量，不碰代码**。`.env` 已被 `.gitignore` 保护，key 不会误提交。

---

## 铁律 2 · 路径必须自动探测（不硬编码用户名/机器）

wrapper.sh 和 INSTALL_TEST.sh 都**禁止硬编码 `/home/<user>`**。跨用户/跨主机必挂（云服 `ubuntu`、本地 `luo`）。

**正确做法（wrapper）**：向上找含 `hermes-agent/` 的目录定位 HERMES_ROOT，再从多候选找 `seedance_mcp/`：

```bash
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
HERMES_ROOT=""; _D="$SCRIPT_DIR"
for _i in 1 2 3 4 5 6; do
  [ -d "$_D/hermes-agent" ] && HERMES_ROOT="$_D" && break
  _D="$(dirname "$_D")"
done
[ -z "$HERMES_ROOT" ] && HERMES_ROOT="$HOME/.hermes"
```

**正确做法（INSTALL_TEST.sh）**：同样向上找 hermes-agent（兼容两种结构）：
- A) `~/.hermes/profiles/<p>/skills/creative/picturebook-video/`（profiles 结构）
- B) `~/.hermes/skills/creative/picturebook-video/`（根 skills 结构）

> ⚠️ 旧版用「固定 5 次 dirname」只兼容结构 A，结构 B 下会把 HERMES_ROOT 错判成 `/home`。**必须向上找 hermes-agent，不能数 dirname 次数。**

**自检**：`bash INSTALL_TEST.sh 2>&1 | head -4` 的 `HERMES_ROOT=` 应为真实 `.hermes` 绝对路径。

---

## 铁律 3 · 改 `.env` 后必须重启 gateway（MCP server 是常驻进程）

MCP server 由 Hermes gateway 启动时 spawn，**`.env` 只在启动时读一次**。改 `.env` 不重启 = 进程内存里还是旧配置。

- 症状：curl 用新 key 直接 POST 成功，但 MCP 工具仍 401。
- 验证：`ps aux | grep mcp_server` 看启动时间是否在改 .env 之后。
- 修复：**重启 Hermes gateway**（gateway 重新 spawn MCP server，wrapper 从最新 `.env` 加载）。

> ⚠️ 手动 `kill` watchdog 子进程**不会**让 gateway 自动重建——必须重启 gateway 进程本身。

---

## 附加坑：verify_api_key 假阴性 + 第三方渠道只开 POST

- **`verify_api_key` 走 GET list 端点**（`{base}?page_size=1`）。第三方网关 `aigc.learningcat.cn` 只开了 POST 提交端点 → 返回 **HTTP 405/401 = 假阴性**。
- **判断可用性看 `generate_video` 能否返回 task_id**，不是看 verify_api_key。
- 第三方网关的 fast 模型**不认 `resolution` 参数**（报 InvalidParameter）→ 提交时省略 resolution。
- 视频任务实际要 ~90-180s 才 succeeded，INSTALL_TEST.sh 的 wait `timeout_sec` 要够（180s 通常 OK）。

---

## 安装自检（新电脑装完必跑）

```bash
# 1. wrapper 三变量齐全
grep -c "SEEDANCE_BASE_URL\|SEEDANCE_MODEL" bin/seedance-mcp-wrapper.sh   # ≥2
# 2. 无硬编码路径
grep -c "/home/luo\|/home/ubuntu" bin/seedance-mcp-wrapper.sh             # 0
# 3. .env 三变量已填
grep -E "SEEDANCE_BASE_URL|SEEDANCE_MODEL|ARK_API_KEY" seedance_mcp/.env
# 4. 端到端验收（真实出片）
bash INSTALL_TEST.sh   # 全 7 步过 = 安装成功
```

---

## 相关文件

- `bin/seedance-mcp-wrapper.sh`（跨电脑通用 · 三变量完整加载）
- `INSTALL_TEST.sh`（路径自动探测 + 三变量传递 + 端到端验收）
- `INSTALL.md` §4.2（三变量配置说明）· §7.2（去硬编码排查）
- `seedance_mcp/.env.example`（三变量模板）
- `references/install-script-autodetect.md`（路径自动探测范式）
