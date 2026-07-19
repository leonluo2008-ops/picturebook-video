# seedance Sensitive Content Retry 决策树（v5.0.19+）

> **来源**：2026-07-11 Morning 早上绘本 Clip 2 实测 · OutputVideoSensitiveContentDetected 错误码处理

## 1. 错误码识别

```json
{
  "error": "task failed: {'code': 'OutputVideoSensitiveContentDetected', 'message': 'The request failed because the output video may contain sensitive information. Request id: ...'}",
  "tool": "wait_and_download",
  "arguments": {"output_path": "clip_2.mp4", "task_id": "cgt-..."}
}
```

**核心特征**：
- 错误码 = `OutputVideoSensitiveContentDetected`
- task_id 标记 failed
- **但已扣费**（最关键的坑）

## 2. 重试决策树

```
[seedance 返回 OutputVideoSensitiveContentDetected]
         ↓
[检查 task_id 是否已扣费] → ✅ 是（已扣费）
         ↓
[绝不重提交同 task_id]（task_id 已被服务端标记 failed，重提必失败）
         ↓
[检查 prompt 是否截断] → 用 read_file 查 prompt 文件完整性
         ↓
[Yes 截断 → 用完整 prompt 提交新 task_id]
[No 未截断 → 考虑是否触发敏感词]
         ↓
[检查 prompt 中可能触发敏感词的描述]
  - 人物姿态："被子隆起（小孩坐起）" / "身体弯曲" / "近距离接触" → 可能误判
  - 食物相关："咀嚼" / "张嘴" / "吞咽" → 可能误判
         ↓
[Yes 敏感词 → 改用更抽象的描述重提新 task_id]
[No 不确定 → 直接用完整 prompt 重提新 task_id（偶发性错误）]
         ↓
[新 task_id 成功后立即 rm 旧 failed 文件]
         ↓
[按"重发=顺带清"模式确认目录干净]
```

## 3. 实战案例（2026-07-11 Morning Clip 2）

**失败情况**：
- task_id: `cgt-20260711185843-4qjmx`
- 错误：OutputVideoSensitiveContentDetected
- 原因：**prompt 截断**（手抖 send 时只发了前 1000 字，丢了被子隆起之后的镜头描述）
- 扣费：✅ 已扣费

**重发流程**：
1. ✅ 读完整 prompt 文件 `/tmp/morning/clip_2_prompt.txt`
2. ✅ 用完整 prompt 提交新 task_id `cgt-20260711190254-gvq9l`
3. ✅ wait_and_download 成功（10.10s，md5 `da22fc044d9400092d32619206b5e623`）
4. ✅ 重命名为 `clip_2_v2.mp4`
5. ✅ `rm /tmp/morning/clip_2.mp4`（旧 failed 文件不存在因为下载就失败，但留个 rm 兜底）

## 4. wait_and_download 5 分钟超时处理（同期 Morning Spike 实测）

**症状**：
- 任务确实在跑（check_task 返回 running）
- 但 wait_and_download 5 分钟超时
- 没有错误码，只是 TimeoutError

**正确处理**：
```python
# ❌ 错误：超时后重 submit
mcp__seedance__wait_and_download(timeout_sec=300)  # 超时
mcp__seedance__generate_video(...)  # 重新提交 → 已扣费 2 次

# ✅ 正确：超时后二次 wait_and_download
mcp__seedance__wait_and_download(timeout_sec=300)  # 超时
mcp__seedance__check_task(task_id="...")  # 确认 status=running
mcp__seedance__wait_and_download(timeout_sec=300)  # 二次等，多半 succeed
```

**根因**：seedance 任务在排队时，5 分钟 wait_and_download 不够长。但任务确实在跑（已扣费），重 submit 会扣两次费。

## 5. 反模式总结

| 反模式 | 后果 | 修复 |
|---|---|---|
| 重提交同 task_id | 必失败，且再扣一次费 | 用新 task_id |
| 重 submit 替代 wait_and_download | 已扣费 2 次（任务原本 succeed） | 二次 wait_and_download |
| 保留 failed 文件 | 最终目录混淆 | 重发成功后立即 rm 旧 failed 文件 |
| 不知道是 prompt 截断 | 重发同一截断 prompt 必再失败 | 必读完整 prompt 文件再重发 |
| 跳过"重发=顺带清" | 目录残留 v1/v2 多个版本 | 立即 rm 旧版本 |

## 6. 重发成本控制

按 user profile 第 5 条"重跑/批量提交前必先确认（2026-06-26 Beet Pepper 重跑教训）"：

**重发 Clip 单价 ≈ 0.4 元（fast 模型 10s clip）**

**重发前必跟用户确认**：
- 是 prompt 截断？（高概率修复）
- 是敏感词？（可能需要改描述）
- 是偶发错误？（可能跟 server 状态有关）

**避免盲目重发**：
- 如果第一次失败原因不明，先看一次服务端日志
- 必要时 curl seedance task list 看 task 详情
- 不要"已扣费就发出去"——先告诉用户失败原因，让用户决策

## 7. 与"重发=顺带清"协同

按 SKILL.md §Step 7 末尾：
> **v5.0.19 强化 · "重发=顺带清"模式**：任何 prompt 重跑导致文件版本更新时，立即 `rm <旧文件>` 避免最终目录残留多个混淆版本

**Step 6 重发成功后的清理脚本**：
```bash
# 假设 clip_2.mp4 是旧 failed（重命名为 clip_2_v2.mp4 之前）
# 或者旧版本是 clip_2_v1.mp4
rm /tmp/<绘本名>/clip_2.mp4 2>/dev/null
mv /tmp/<绘本名>/clip_2_v2.mp4 /tmp/<绘本名>/clip_2.mp4  # 归一化命名（可选）
```

**最终交付前**：
```bash
ls -la /tmp/<绘本名>/clip_*.mp4
# 应该只有 clip_1_*.mp4, clip_2_*.mp4, clip_3_*.mp4（每个 clip 一份）
```