---
name: picturebook-video-clip-rules
description: "绘本视频Clip划分约束：≤3图/Clip等用户硬性规则."
version: 0.1.0
author: Hermes
tags: [Picturebook, Video, Clip, Splitting, Seedance]
---

# 绘本视频 Clip 划分用户硬性规则

> 补充 picturebook-video skill 中 Step 4「旁白优先逐段合并」的用户实测约束。
> picturebook-video 是 bundled skill 不可直接编辑，本 skill 作为用户偏好补丁存在。

## When to Use

- 执行 picturebook-video Step 4 划分 Clip 时
- clip_merger.py 输出合并方案后，人工复核 Clip 内参考图数量

## Hard Constraints

### 约束 #1：单 Clip 最多 3 张参考图（2026-08-01 实测）

**用户原话**：「五张图一个Clip，那很容易崩的」

| 图数 | 判定 | 处理 |
|------|------|------|
| ≤3 张 | ✅ 安全 | 直接合并 |
| 4-5 张 | ❌ 容易崩 | 必须拆分，减少每 Clip 图数 |
| ≥6 张 | ❌ 必崩 | 必须拆分 |

**拆分策略**：clip_merger.py 输出的合并方案如果某 Clip 含 ≥4 张图，手动在该 Clip 内找自然断点（段间停顿 ≥0.8s 或叙事转折点）拆分为 2 个更小的 Clip。

### 约束 #2：总时长对齐（继承 picturebook-video）

- ceil 取整差额（典型 +1~3s）是自然余量，不展开画面
- 用户原话：「严格按 SRT 时长处理，禁止乱加戏」

## Procedure

1. 跑 `clip_merger.py` 获得初始 clip 划分
2. 人工检查每个 Clip 的参考图数量
3. 如有 Clip 含 ≥4 张图 → 在该 Clip 内找段间停顿 ≥0.8s 的位置拆分
4. 拆分后重新计算每个 Clip 的 `suggested_duration`（取整到 [4,15]）
5. 输出最终 clip 方案给用户确认

## Pitfalls

- ❌ clip_merger.py 只按时长合并，不检查图数 → 必须人工复核
- ❌ 拆分后总时长可能略增（多一个 ceil 取整）→ 差额仍为自然余量，不解释
- ✅ 优先拆在段间停顿大的位置（≥0.8s），画面过渡更自然
