# v7 范式 Clip 提示词自动生成脚本（实测模板）

> 来源：2026-06-03 Ok 好的绘本视频实战沉淀。
> 用途：**已就绪 8 张图 + 8 段旁白** → 自动产出 4 个 Clip 的 v7 范式 prompt + JSON + 11 项自检。
> 配合 `picturebook-video` skill Phase 5 步骤 1-4 自动化原则使用。

---

## 跑法

```bash
python3 /path/to/build_clips.py
# 输出 clips-prompt.json（含 4 个 Clip 完整 prompt）+ 控制台打印自检结果
```

## 输入数据结构（CLIPS 列表）

每个 Clip 含：

| 字段 | 说明 | 示例 |
|---|---|---|
| `id` | 1-4 | `1` |
| `duration` | 4-15s（绘本版 v7 公式：8/9/9/10）| `8` |
| `image_start` / `image_end` | 绑定图号（@Image1, @Image2）| `1` / `2` |
| `narration_1` / `narration_2` | 双段旁白（合并的 2 段）| `"Ok. 好的 Ok。"` |
| `shot_1.time` | `"0.0s to 3.5s"` | 第一段时序窗 |
| `shot_1.content` | 画面描述（基于图 1）| `"a small round bear stands center stage..."` |
| `shot_1.motion` | shot 内部动作（v7 关键）| `"in this shot the small bear's paw raises slowly..., then holds steady for the rest of this shot"` |
| `shot_1.sfx` | 音效副词（嵌入视觉句）| `"gentle paper-landing tap-tap-tap as the thumbs-up pose settles"` |
| `shot_2.*` | 同 shot_1，但绑定图 2 | |
| `shot_3.*` | 收势段（`final frame:` + motion + sfx + 收势词）| |

## v7 prompt 8 段固定结构（**不能漏**）

| 段 | 必含 | 来源 |
|---|---|---|
| 1 | 引导句 | 固定：`This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video` |
| 2 | shot_1 视觉分镜 | `from {s1.time} @Image1 as the opening frame, {s1.content}, {s1.motion}, {s1.sfx}` |
| 3 | shot_2 视觉分镜 | `from {s2.time} transitions seamlessly to @Image2 as the second half, {s2.content}, {s2.motion}, {s2.sfx}` |
| 4 | final frame 收势 | `from {s3.time} final frame: {s3.content}, {s3.motion}, {s3.sfx}, no fade, no dissolve, holds to the last frame` |
| 5 | Storyboard Audio Description | `[{t1}] {s1.sfx}; [{t2}] {s2.sfx}; [{t3}] {s3.sfx}` |
| 6 | No 禁令 | `No background music, no human voice, no narration, no singing` |
| 7 | 风格锚点 | `Children's picture book illustration style, ...`（动态，从图片观察提炼）|
| 8 | 句号收尾 | `.` |

## 11 项自检（必跑）

| # | 检查项 | 期望 |
|---|---|---|
| 0 | 段 1 = 引导句 | ✅ 不可漏 |
| 1 | 分号数 ≥ 3 | ✅ |
| 2 | `holds to the last frame` 收势词 | ✅ |
| 3 | `no fade, no dissolve` 收势指令 | ✅ |
| 4 | 无独立 `[Sound effect: ...]` 块 | ✅ |
| 5 | 视觉段无 `no speech / no narration / No BGM` | ✅ |
| 6 | `0.0s to` 时序窗 | ✅ |
| 7 | `from` 出现 ≥ 3 次（3 shot） | ✅ |
| 8 | `@Image1` + `@Image2` 都存在 | ✅ |
| 9 | `Storyboard Audio Description` 段 | ✅ |
| 10 | `No background music` 禁令段 | ✅ |
| 11 | `Children's picture book` 风格锚点 | ✅ |
| 12 | `duration` 在 4-15s 范围 | ✅ |

## 已知 bug 教训

1. **build script 漏字段**：拼接 f-string 时**易漏 `motion` 字段**到 final frame 段——自检脚本只看关键词字符串会**误判通过**。**修复**：用段数 + 字段名双重检查（v7 = 8 段，每段必含字段白名单）。
2. **段 1 引导句漏写**：v7 模板强制要求段 1 引导句 `This is a storyboard reference image sequence...`，**漏掉 = 模型把 2 图当 1 段独立运镜，时序窗失效**。**修复**：把引导句作为必含字符串纳入 build script（**不允许覆盖**）。
3. **数字缩写误判为句号**：`1.2s/8.0s` 里的 `.` 不是句号——自检脚本要把 `X.Xs` 正则排除。

## 时长公式（绘本领读型 · 4 Clip 标准）

| 段落位置 | 推荐时长 | 理由 |
|---------|---------|------|
| Clip 1（开头）| 8s | 标题+主形象登场，需要稳 |
| Clip 2-N-1（中间）| 8-9s | 均匀推进，节奏稳定 |
| Clip N（结尾）| 10s | 情感核心（All is Ok），给足余韵 |

**总时长 ≈ 段落数 × 8-10s**，向上对齐到 8/9/10s 整数值。

**示例**（Ok 好的 · 4 Clip）：`8 + 9 + 9 + 10 = 36s` ✅
