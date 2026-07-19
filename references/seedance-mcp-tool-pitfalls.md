---
name: seedance-mcp-tool-pitfalls
description: picturebook-video Step 6 调用 mcp__seedance__generate_video 时的踩坑清单 · 含 2026-07-13 Rose 绘本实测沉淀。覆盖 fast 模型拒绝 service_tier、duration 参数被空 audio_refs 吞掉 2 个真实 bug + 修复策略。
license: Apache-2.2
metadata:
  hermes:
    tags: [picturebook-video, seedance, mcp, generate_video, pitfall, step-6]
    related_skills: [picturebook-video]
---

# Seedance MCP 工具踩坑清单 · picturebook-video Step 6 实战沉淀

> **触发位置**：Step 6 提交 seedance 视频生成任务。
> **优先级**：高（这 2 个 bug 都不报错信息直接告诉你哪里错了，容易让人以为是网络问题然后反复重提 = 反复扣费）。
> **来源**：2026-07-13 Rose 绘本实测 · 已扣费的任务绝不能再提，必须用对的参数组合。

---

## 1. Fast 模型拒绝 `service_tier` 参数

**症状**：
```
HTTP 400: the specified parameter service_tier is not supported for model
doubao-seedance-2-0-fast in r2v, must be empty
Request id: 02178392968871514cea4691e83c1d7ab80acdae8752ced82b842
```

**根因**：
- `seedance2.0-tool` SKILL.md 列出的参数表里有 `service_tier`（"default 在线 / flex 离线，便宜 50%"），看起来通用。
- 但 **fast 模型 (`doubao-seedance-2-0-fast-260128`) 的 r2v 路由根本不接受这个参数**，只接受空值。
- API 错误信息已经明确说 "must be empty"，但人容易误判为 "参数值错了" → 反复切 default/flex → 反复 400 → 反复被网关拒收（虽然没真扣费，但浪费 4 次提交机会）。

**check_task 验证未扣费**：
```
error: API Error (HTTP 404): The specified resource `...` is not found.
```
→ 任务 ID 不存在 = 网关层参数校验拒绝 = 没创建真任务 = 没扣费。

**修复策略**：
- 调用 fast 模型时 **直接省略 `service_tier` 参数**，根本不要传这个 key。
- 高质量模型 `doubao-seedance-2-0-260128` 才支持 `service_tier`。
- 写代码时把 `service_tier` 设为可选，仅对非 fast 模型传入。

**口诀**：**fast 模型 + 不传 service_tier** = 永远 PASS；fast 模型 + 传 service_tier = 永远 400。

---

## 2. `duration` 参数被空 `audio_refs`/`video_refs` 吞掉

**症状**：
```
Input validation error: 'duration' is a required property
```

明明 prompt 里写了 `duration: 14`，MCP 工具的参数也明确传了 `14`，但校验器报 "duration 是必需属性"。

**根因（实测推断）**：
- 当 `audio_refs` 或 `video_refs` 传成空数组 `[]` 时，部分 MCP wrapper 实现会把它包装成嵌套对象，导致 JSON Schema 验证失败。
- 验证器抛错说 "duration 缺失"，其实根本原因是空数组字段导致整个对象解析异常。
- 在本会话观察到：传 `audio_refs: []` + `ref_images: [4 个文件]` → 报 duration 缺失；不传 `audio_refs`/`video_refs`（直接不写这两个 key）→ 通过。

**修复策略**：
- **不要传空的 `audio_refs=[]` 或 `video_refs=[]`** —— 根本不要写这两个 key。
- 只在真正有参考视频/音频时才传这两个参数。
- `ref_images` 用扁平数组（`[file1, file2, file3, file4]`），不要嵌套。

**对比**：

```python
# ❌ 错误（duration 被吞）
mcp__seedance__generate_video(
  audio_refs=[],           # ← 空数组惹的祸
  video_refs=[],
  duration=14,
  ref_images=[img1, img2, img3, img4],
  ...
)

# ✅ 正确（不传空的 audio_refs/video_refs）
mcp__seedance__generate_video(
  duration=14,
  ref_images=[img1, img2, img3, img4],
  generate_audio=True,
  ...
)
```

---

## 3. 完整可工作的 Clip 提交样板（fast 模型 + 4 参考图）

```python
mcp__seedance__generate_video(
  duration=14,                                  # 整数 [4, 15]
  generate_audio=True,                           # 路径 A：有 SRT
  model="doubao-seedance-2-0-fast-260128",       # fast 模型
  prompt="...",                                  # 完整 v8.1 5 段 prompt
  ratio="16:9",                                  # 绘本横屏
  ref_images=[img1, img2, img3, img4],           # 扁平数组
  resolution="720p",                             # fast 只支持 720p
  watermark="none",                              # 永远不要 seedance_ai 水印
  # ❌ 不要传 service_tier（fast 模型拒绝）
  # ❌ 不要传空的 audio_refs / video_refs
  # ❌ 不要传 image / last_frame（绘本场景禁用首尾帧）
)
```

---

## 4. 验证清单（Step 6 提交前自检）

- [ ] 模型 = `doubao-seedance-2-0-fast-260128` → 省略 `service_tier`
- [ ] 模型 = `doubao-seedance-2-0-260128`（高质量慢）→ 可以传 `service_tier`
- [ ] `ref_images` 是扁平数组，不嵌套
- [ ] 没有传空的 `audio_refs=[]` 或 `video_refs=[]`
- [ ] `duration` 是整数 4-15
- [ ] `watermark="none"`（绘本场景必填）
- [ ] prompt 末尾含"无背景音乐"（v5.0.13 硬约束 #0）
- [ ] generate_audio 跟 SRT 路径匹配：有 SRT → True；无 SRT → 仍 True（v5.0.13 默认）

---

## 5. 错误码速查

| 错误码 | 原因 | 修复 |
|--------|------|------|
| HTTP 400 service_tier not supported | fast 模型 + 传了 service_tier | 省略 service_tier |
| Input validation error: 'duration' required | 空 audio_refs/video_refs 嵌套污染 | 不传空的 audio_refs/video_refs |
| HTTP 404 task not found | 参数校验拒绝，没创建真任务 | 修参数重提（未扣费） |
| HTTP 401 API key not active | MCP server 缓存旧 key | `hermes gateway restart` |
| OutputVideoSensitiveContentDetected | seedance 偶发内容审核误判 | 不要重提同 task_id（已扣费），用完整 prompt 重发新 task_id |

---

## 6. 跟用户 profile 的兼容性

- user profile "严禁自作主张改脚本" → 本文档只记录 MCP 工具的实战坑，**不修改 MCP server 源代码**。
- 修复策略都是改调用方的参数组合，不动 wrapper / server。
- 如果某个 bug 是 MCP server 的代码缺陷 → 通过 `references/` 记录 + 报告用户，由用户决定是否升级 wrapper。

---

## 版本

v1.0 (2026-07-13 实测沉淀 · 来自《Rose 玫瑰》绘本 Step 6 提交失败 debug)