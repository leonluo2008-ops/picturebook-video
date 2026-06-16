# 实战案例 · 并行 wait_and_download 模式（2026-06-14 绘本 clip2-5 跑沉淀）

> **触发场景**：跑 ≥ 4 个独立 seedance task · 4 个 prompt 互不依赖（不同 ref_images / 不同时长）· 想最大化并行度。
> **不是新增元方法论** = 只是 #M3 旁白-镜头映射法落地时遇到的一个工程技巧。

---

## 实战场景

绘本 Donkey 驴：5 个 clip · clip1 v1 单独跑（用户目检 OK）后跑 v2（重提）· 接下来 4 个 clip（clip2/3/4/5）4 个独立 task 并行提交。

```
4 个 task 同时跑（doubao-seedance-2-0-fast 720p）
- clip2 10s · cgt-20260614142119-mm4sb
- clip3 7s  · cgt-20260614142126-q28v2
- clip4 10s · cgt-20260614142131-d5kbr
- clip5 6s  · cgt-20260614142141-7ckcs
```

## MCP timeout 4/4 现象

`wait_and_download` 默认 120s timeout，**4 个 task 全部 timeout**：

```
MCP call failed: TimeoutError: MCP call timed out after 120.0s (configured timeout: 120.0s)
```

## 按铁律 #19 处理（status 唯一权威）

**不重提交原 task_id**（已扣费）= 必查 status。结果：

| task | status |
|---|---|
| clip2 | running（→ succeeded 第二次）|
| clip3 | succeeded |
| clip4 | succeeded |
| clip5 | succeeded |

**关键发现**：MCP timeout ≠ 任务失败。seedance 实际生成时间 = 5-15 分钟，**远超 120s**。

## 3 步恢复流程（重试 wait_and_download 拿到视频）

```
1. 4 个 task 全部 check_task → 3 个 succeeded + 1 个 running
2. 重试 wait_and_download 跑成功的 3 个 → 直接拿到 mp4 + md5
3. clip2 running → 等 30-60 秒 → check_task → succeeded → 重试 wait_and_download → 拿到
```

## 关键经验

| # | 经验 | 原因 |
|---|---|---|
| 1 | **`wait_and_download` 的 `timeout_sec=300` 参数实际无效** | MCP 客户端 120s 就 timeout，pass 更大值也救不了 |
| 2 | **succeeded 的 task 重新调 wait_and_download = 100% 能拿到** | 视频已落地 ark CDN · 24h 有效 URL · 客户端只下载 |
| 3 | **running 的 task 必须先 check_task → succeeded 再 wait_and_download** | 否则仍会 timeout（5-15 分钟还没跑完）|
| 4 | **check_task 的 succeeded 响应含 video_url** = 24h 有效，可作为兜底下载通道 | `https://ark-acg-cn-beijing.tos-cn-beijing.volces.com/...mp4?...&X-Tos-Expires=86400` |
| 5 | **4 个 task 并行 wait_and_download（不是并行 submit）= 仍是 4 个独立 MCP 调用，按 task 各自进度返回** | 不会因为 1 个 timeout 影响其他 |

## 反模式（不要做）

- ❌ 看到 4/4 timeout → 重提交 = **4 次重复扣费 + task_id 冲突**
- ❌ 单 Clip 跑完等用户目检 OK 后再跑下一条（4 个独立 task 完全可以并行）
- ❌ 4 个 task 顺序 wait_and_download（浪费时间 = 一个接一个等 120s timeout）

## 最佳实践（绘本/漫剧多 Clip 跑流程）

```
Step 1 · 4-5 个 task 同时 submit（每个独立 task_id）
Step 2 · 同时 wait_and_download（接受 4/4 timeout，**不重提交**）
Step 3 · check_task 逐个确认 status
Step 4 · 对 status=succeeded 的 task 重新 wait_and_download 拿到 mp4
Step 5 · 对 status=running 的 task 循环 check_task + wait_and_download（5-15 分钟内必 succeed）
Step 6 · 全部 5 个 mp4 落地后统一 md5sum + ffprobe 验时长 + 一次性发飞书
```

## 跟 #M3 旁白-镜头映射法的关系

**不属于 #M3 方法论本身** = 只是落地时的工程技巧。#M3 关注"镜头序列怎么设计"，本文件关注"多个 clip 怎么高效生成"。

属于"多 Clip 落地的工程模式" = 跟 seedance MCP 工具的 timeout 行为强相关 = 不属于 #M3 范畴。

## 跨 skill 适用

- ✅ **绘本视频**（本场景·5 Clip 并行）
- ✅ **漫剧**（每集多镜头 · 跨集可并行）
- ✅ **AI 短剧**（多场景 · 多 task 并行）
- ✅ **任何 seedance 跑多 Clip 的场景**

## 沉淀决策

**不升级为铁律** = 只是工程技巧，不是创作方法论。用户原话没针对这点纠错过。
**不升 references 顶层** = 是 narration-shot-mapping.md 实战案例下的子文档。
**保留为 references/ 文件** = 未来跑多 Clip 的 session 直接查阅。
