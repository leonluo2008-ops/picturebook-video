# picturebook-video

静态绘本转儿童动画视频工作流。

输入任意数量静态图 + 旁白，输出完整动画视频。整合即梦（Dreamina/Seedance）官方 9 阶段 SOP + 导演模式多镜头时间线 + 段间尾帧接力，覆盖从分镜到成片全链路。

---

## 核心能力

- **导演模式多镜头时间线**：一个 prompt 写多段 `[00-05s] Shot 1` + `[05-10s] Shot 2`，模型自动转场衔接
- **段间尾帧接力**：用 `--return-last-frame` 取 Clip N 尾帧 → 作为 Clip N+1 的 `--last-frame` 接入，物理保证连贯
- **Clip 衔接设计**：每个 clip 必须写出「出动作/入动作」，不允许静置开场

---

## 适用场景

已有静态绘本图片 + 旁白，需要转换为动画视频。

**输入**：静态图（≥1张）+ 旁白
**输出**：可播放动画视频

---

## 工作流概览（6步）

```
Step 1 · 图片分析（Vision）
Step 2 · 旁白与图片匹配
Step 3 · 分镜脚本设计
    ├─ script-chunk   分镜切分
    ├─ shots-timing  时长计算
    ├─ shots-assembly 合并为 clip
    └─ scene-reflection 连贯性校验
Step 4 · 视频生成（并行）
Step 5 · 成片剪辑
Step 6 · 交付与反馈
```

---

## 快速开始

### 触发词

当用户说以下关键词时调用本 skill：
- `制作绘本动画`
- `绘本转视频`
- `静态图转动画`

### 输入要求

- 静态绘本图片（≥1张，任意数量）
- 对应旁白（文字或 MP3）
- 可选：BGM 音乐

### 主要约束

| 参数 | 限制 |
|------|------|
| 单 Clip 时长 | **4s ≤ 时长 ≤ 15s**，绝对不能超 |
| 时长计算 | 字数 × 0.3 秒/字 |
| `--duration` | 必须是**整数**，向上取整 |
| 生成方式 | 所有 Clip **并行提交**，不串行 |

---

## 目录结构

```
picturebook-video/
├── SKILL.md                          # 主工作流
├── references/
│   ├── video-sop.md                 # 即梦官方视频创作 SOP（9阶段）
│   ├── script-chunk.md               # 分镜切分技能
│   ├── shots-timing.md               # 分镜计时技能
│   ├── shots-assembly.md             # 分镜组合技能
│   ├── scene-reflection.md           # 连贯性校验技能
│   ├── video-prompt.md               # 分镜生视频技能
│   └── clip-continuity.md            # 衔接问题实战诊断（模式A/B/C）
├── README.md                         # 本文件
└── CHANGELOG.md                      # 开发日志
```

---

## 参考文档说明

`references/` 目录中的文档来自即梦官方 skill 体系和实战验证：

| 文档 | 来源 | 用途 |
|------|------|------|
| `video-sop.md` | 即梦官方 | 9阶段 SOP 框架 |
| `script-chunk.md` | 即梦官方 | 分镜切分规范 |
| `shots-timing.md` | 即梦官方 | 时长计算规则 |
| `shots-assembly.md` | 即梦官方 | Clip 合并规范 |
| `scene-reflection.md` | 即梦官方 | 连贯性校验规范 |
| `video-prompt.md` | 即梦官方 | Prompt 编写规范 |
| `clip-continuity.md` | 实战验证 | 衔接问题根因 + 三种解决模式 |

这些文档同时被 `seedance2.0-tool` skill 共享，保持同步更新。

---

## 关键教训

> 以下每条都从实战踩坑中提取，调用时必须遵守。

1. **图片分析不能省略**：没有分析就凭旁白设计，结果与图片不符
2. **时长计算用 0.3s/字**：不是估算，是字速标准
3. **duration 必须是整数**：`--duration 7.5` 会报错，向上取整
4. **衔接必须在生成前设计**：Clip 生成完再补救是补救不了的
5. **即梦 API 上限是物理约束**：导演时间线单次上限约 10-15s，超时分段 + 尾帧接力
6. **尾帧图必须用 --return-last-frame 生成**：不接受手动上传尾帧图片
7. **并行生成，不串行**：同一阶段多个任务必须一次性提交
8. **交付必须发实际文件**：不能只发链接或文字描述

---

## 与 seedance2.0-tool 的关系

- `picturebook-video`：专注绘本转视频场景，跳过 Phase 0-4，直奔分镜到成片
- `seedance2.0-tool`：通用即梦视频生成工具，包含 CLI 命令和导演模式完整指南

两者共享 `references/` 中的参考文档。

---

## 维护说明

本项目采用持续维护模式，每次实战中发现的问题和解决方案都会更新到 CHANGELOG.md。

如发现问题或有不连贯的 clip 生成结果，记录具体 clip 编号和现象，更新到工作流规范中。