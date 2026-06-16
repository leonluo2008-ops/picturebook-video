# seedance MCP timeout 兜底下载（curl + video_url）

## 场景

绘本/漫剧批量提交 5+ 个 seedance 任务时，`wait_and_download` 工具会**部分 timeout**（默认 120s），但实际任务还在 `running` 状态，最后才到 `succeeded`。

- 现象：`MCP call failed: TimeoutError: MCP call timed out after 120.0s (configured timeout: 120.0s)`
- 任务真实状态：`running` → `succeeded`（不在 timeout 时确认）
- 损失：`wait_and_download` 没把 mp4 落盘，但任务已扣费、已成功

## 修复路径（3 步）

**第一步：`check_task` 确认状态**

```python
mcp_seedance_check_task(task_id="cgt-20260616095348-f7dqd")
# 返回 succeeded → 第二步
# 返回 running  → 等 30s 重试 check_task
# 返回 failed   → 改 prompt 重提新 task（**绝不重提交同 task_id**）
```

**第二步：从 succeeded 返回里拿 `video_url`**

```json
{
  "task_id": "cgt-20260616095348-f7dqd",
  "status": "succeeded",
  "video_url": "https://ark-acg-cn-beijing.tos-cn-beijing.volces.com/...mp4?X-Tos-Algorithm=...&X-Tos-Signature=...",
  "_note": "video_url 24h 有效，及时下载。过期调 check_task 拿新 URL。"
}
```

**URL 24h 有效**——24h 内重复下载都行。过期了再调 `check_task` 拿新 URL（官方不会失效数据，只换签名）。

**第三步：`curl` 兜底下载**

```bash
curl -sL "${video_url}" -o /path/to/clips/clipN.mp4
```

- `-sL` = silent + follow redirects（cos/tos URL 通常带 302）
- `-o` = 指定输出路径（必传，curl 不传就用 stdout）
- 跨环境通用：不依赖 MCP / 不依赖额外 SDK / 不依赖账号认证（URL 自带签名）

## 实测案例（2026-06-16 I love you 绘本）

5 个 task 并行 `wait_and_download`：
- clip4 / clip5 / clip6：wait_and_download 同步成功（120s 内跑完 720p 短视频）
- clip2 / clip3：wait_and_download timeout 120s

**修复过程**：
1. 调 `check_task` 5 个 task_id → 全部 succeeded
2. clip2 / clip3 返回里带 `video_url`
3. `curl -sL URL -o clip2.mp4` + `curl -sL URL -o clip3.mp4` → 2 个 mp4 落盘成功
4. md5 验证：6 个 mp4 md5 全部唯一 ✅

**耗时**：curl 兜底 vs 重提新 task = **省 5-10 分钟 + 2 段重提费**。

## 反模式（必避）

- ❌ wait_and_download timeout → 重提交同 task_id → **已扣费重复扣费**
- ❌ wait_and_download timeout → 改 prompt 重提新 task → **浪费一段成本**
- ❌ check_task 返回 succeeded → 不拿 video_url 直接重跑 wait_and_download → **可能再 timeout**
- ✅ check_task 拿 video_url → curl 兜底下载 → md5 + ffprobe 验证

## 跟 Step 6 应变表的配合

| 行 | 触发 | 行动 |
|---|---|---|
| MCP timeout | wait_and_download 120s timeout | ① check_task 拿状态<br>② succeeded → curl video_url 兜底下载<br>③ running → 等 30s 重试 check_task<br>④ failed → 改 prompt 重提新 task |
| 已发任务 = 已扣费 | 任何"重试"想法 | **绝不重提交同 task_id**（红线） |

## 跨 skill 适用

- ✅ 绘本视频（picturebook-video）
- ✅ 漫剧分镜（ai-drama）
- ✅ 任何 seedance MCP 批量任务场景（短视频 / 广告 / 教学视频 / 产品演示）

## 关键参数

- `curl -sL` = silent + follow 302 redirects（必需，tos URL 经常 302）
- 24h URL TTL = 24 小时内同一 task 可重复 curl
- `video_url` 含 `X-Tos-Signature` 鉴权签名 → URL 本身 = 凭据 → 不可泄漏给无关方

## 不写进 skill 的内容

- ❌ 具体绘本名 / 工作目录路径（业务数据 → 留 work/ 目录）
- ❌ task_id 列表（会过期）
- ❌ curl 之外的下载工具（curl 是 Linux 默认都有，最稳）
