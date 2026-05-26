---
name: picturebook-video
description: 静态绘本转儿童动画视频工作流。输入任意数量静态图+旁白，输出完整动画视频。整合即梦官方9阶段SOP + 导演模式多镜头时间线 + 段间尾帧接力，覆盖分镜到成片全链路。
triggers:
  - 制作绘本动画
  - 绘本转视频
  - 静态图转动画
---

# picturebook-video · 绘本动画制作工作流

> 将静态绘本图片转换为儿童动画视频的完整工作流。
> 整合即梦官方 SOP（9阶段）和实战衔接方案，确保 clip 衔接流畅、风格一致。
> 输入：静态图（≥1张）+ 旁白；输出：可播放动画视频。

---

## 定位说明

本 skill 针对「已有静态绘本图片+旁白」的半成品素材，跳过 Phase 0-4（创意/大纲/剧本/素材挖掘），直接进入分镜设计→视频生成→成片剪辑。

**核心能力**：导演模式多镜头时间线 + 段间尾帧接力，保证 clip 衔接流畅。

---

## 完整工作流（6步）

```
Step 1 · 图片分析（Vision）
  → 分析每张图：场景/人物/构图/色彩/氛围/关键元素
  → 输出一张汇总表
  
Step 2 · 旁白与图片匹配
  → 将旁白匹配到对应图片，形成 1→1 或 1→N 关系
  → 输出匹配表
  
Step 3 · 分镜脚本设计（含衔接设计）
  → script-chunk：拆分为单个分镜
  → shots-timing：计算每镜时长
  → shots-assembly：合并为 4-15s 的 clip
  → scene-reflection：校验一致性
  → 【关键】每个 clip 必须写出「出动作/入动作」
  
Step 4 · 视频生成（并行）
  → video-prompt：编写导演模式 prompt
  → 每个 clip 并行提交，不串行
  → 段间用 --return-last-frame / --last-frame 接力
  
Step 5 · 成片剪辑
  → ffmpeg 拼接 + BGM 合并
  → 输出最终视频
  
Step 6 · 交付与反馈
  → 发送实际文件给用户
  → 记录问题反馈到下一步
```

---

## Step 1 · 图片分析（Vision）

**必须先做，不能省略，不能用旁白反推画面。**

对每一张图执行 Vision 分析，输出：

```
| 图号 | 场景 | 人物/关键元素 | 色彩/氛围 |
|------|------|-------------|-----------|
| 1.jpg | 白天梯田村庄 | 10+人穿民族服饰，白墙红门，远景 | 绿/白/红，明亮开阔 |
```

分析维度：
- **场景**：地点/时间/光感/整体氛围
- **人物**：主要角色外观特征（服装/发型/动作状态）
- **构图**：景别/主体位置/画面重心
- **色彩**：主色调/光感/冷暖
- **关键元素**：重要道具/动作状态/情绪

> ⚠️ 教训：绝对不能用旁白反推画面描述。图里有什么才能写什么，硬加图没有的内容会导致视频生成结果不符预期。

---

## Step 2 · 旁白与图片匹配

将每段旁白匹配到对应图片（不是按序号硬套）。

匹配原则：
- 看图实际场景是否贴合旁白内容
- 同一场景顺序连接自然
- 避免「图说不到一块」

输出：匹配表

```
| 图号 | 旁白 | 匹配原因 |
|------|------|---------|
| 1.jpg | 夏天到来时... | 白天多人民族服饰场景，开场交代 |
```

---

## Step 3 · 分镜脚本设计

这是**最关键的一步**，包含4个子步骤，按顺序执行：

### 3.1 script-chunk · 分镜切分

将旁白+图片匹配结果拆分为单个分镜，每个分镜标注：

| 字段 | 内容 |
|------|------|
| 镜号 | 从1开始连续编号 |
| 景别 | 远景/全景/中景/中近景/近景/特写 |
| 画面描述 | 当前镜头中看到的内容，必须完全基于图片 |
| 台词/音效 | 对应本镜头的旁白或环境音效 |

> 拆分技巧：每句对话对应一个分镜（近景/特写聚焦说话者）；连贯动作放同一分镜；关键动作转折处拆分。

### 3.2 shots-timing · 分镜计时

计算每个分镜的合理时长：

| 类型 | 计算方式 |
|------|----------|
| 台词镜头 | 字数 × 0.3 秒/字 |
| 最低保底 | 每镜 ≥1 秒 |
| 情绪节奏 | 快节奏1-3秒，情感戏3-8秒，空镜2-4秒 |
| 景别影响 | 远景/全景偏长（3-6秒），近景/特写偏短（1-4秒） |

> ⚠️ `--duration` 参数必须是整数，向上取整。`--duration 7.5` 会报错。

### 3.3 shots-assembly · 分镜组合

将分镜合并为适合 AI 生成的 clip 片段：

**硬约束**：每个 clip **4s ≤ 时长 ≤ 15s**，绝对不能超

合并步骤：
1. 从第一个分镜开始累加时长，直到接近但不超过 15s
2. 超过 15s 时，当前累加段作为 clip 结束
3. 从下一个分镜开始新的累加
4. 检查每个 clip，确保都 ≥4s（不足则与相邻 clip 合并）
5. 给每个 clip 编号，整理成 clip 表

输出格式：

```
# {故事名}Clip表

| Clip编号 | 包含镜号 | 总时长(秒) | 镜号-景别-画面（精简） |
|----------|----------|------------|-------------------------|
| 1 | 1-3 | 12.5 | 1.全景-...；2.特写-...；3.中景-... |
| 2 | 4-7 | 10.0 | ... |

## 总信息
**总Clip数：** N个
**总时长：** XX.X 秒
```

### 3.4 scene-reflection · 连贯性校验

从五个维度检查每个 clip：

| 维度 | 检查内容 |
|------|----------|
| 人物一致性 | 服装/外观/位置/动作衔接 |
| 道具一致性 | 存在性/位置/外观 |
| 场景一致性 | 光线/天气/陈设 |
| 逻辑连贯性 | 情节/时间/物理规则 |
| 色调统一性 | 整体色调风格统一 |

**发现问题时的修复优先级**：
1. 最小修改原则：只改有问题的部分
2. 添加说明：在问题分镜描述中加「需要保持与前一Clip一致」
3. 拆分调整：适当调整 clip 拆分边界

输出：
- 校验结果说明（发现的问题+修复方式）
- 修复后的 clip 表
- 一致性注意事项汇总

### 3.5 衔接设计（核心重点）

每个 clip 必须在脚本里写清楚：

```
Clip N
├─ 开头：承接 Clip N-1 结尾 → 【具体动作描述】
├─ 中段：【当前场景核心动作】
└─ 结尾：【出动作】→ Clip N+1 开头要从这个动作接
```

**禁止**：人物站好静置开场、场景从头渲染
**必须**：clip 开头是「上一段动作的延续」，clip 结尾是「下一段动作的起点」

**三种衔接模式**：

| 模式 | 做法 | 适用场景 |
|------|------|----------|
| **导演时间线**（模式B） | 一个 prompt 写多段 `[00-05s] Shot 1` + `[05-10s] Shot 2` | clip 内部多镜接、场景连贯 |
| **尾帧接力**（模式C） | Clip N 尾帧 → Clip N+1 的 `--last-frame` | 跨 15s 上限、长故事接续 |
| **模式B+C结合** | 时间线内拼接 + 段间尾帧接力 | 总时长超过 15s |

---

## Step 4 · 视频生成

### 4.1 video-prompt · prompt 编写规范

每个 clip 的 prompt 必须包含（按顺序）：

1. **参考主体引用**：`@Image1`（首帧图片）
2. **场景描述**：当前 clip 所在场景，要求与图片一致
3. **分镜动作描述**：按时间线写 `[00-02.5s]` + 镜头描述
4. **台词/音效说明**：本片段对应的旁白或音效提示
5. **风格一致性说明**：整体风格与参考素材保持一致

**Prompt 格式示例**：

```
[00-02.5s] Wide establishing shot, terraced fields cascade down green mountains,
villagers in colorful ethnic clothing gather near white houses. Warm sunset lighting.
[02.5-05s] Medium shot, young girl lifts torch above her head, flame flickering in night wind.
[05-07.5s] Tracking shot slowly pulls back, revealing the gathering crowd.
Style: flat 2D cartoon illustration, warm lighting, consistent ethnic characters,
cinematic camera movement.
```

### 4.2 工具选择规则

| 情况 | 命令 |
|------|------|
| 纯文生视频 | `text2video` |
| 有首帧参考图 | `image2video` |
| 多参考素材（角色+场景+动作） | `multi_modal2video` |

### 4.3 导演模式时间线写法

```bash
python3 seedance.py create \
  --image image_N.jpg \
  --prompt "[00-05s] Medium close-up, young girl lifts torch above her head, flame flickering in night wind. [05-10s] Wide shot, she walks forward leading the procession, sunset glow in background.
  Style: warm illustration, consistent with reference image, cinematic camera movement." \
  --duration 10 \
  --ratio 16:9 \
  --model doubao-seedance-2-0-fast-260128 \
  --return-last-frame \
  --download ./output
```

### 4.4 尾帧接力用法

Clip N 生成完成后：
1. 从输出中获取尾帧图片（`--return-last-frame` 返回 URL）
2. Clip N+1 使用 `--last-frame <尾帧URL>` 接入

```bash
# Clip N+1 接入 Clip N 尾帧
python3 seedance.py create \
  --image image_N+1.jpg \
  --last-frame <ClipN尾帧URL> \
  --prompt "Continuing from the previous clip: the girl holds the torch high..." \
  --duration 10 \
  --ratio 16:9 \
  --model doubao-seedance-2-0-fast-260128 \
  --return-last-frame \
  --download ./output
```

> ⚠️ `--image`（first_frame）和 `--ref-images` **互斥**：同时使用会触发 API 报错 `first/last frame content cannot be mixed with reference media content`

### 4.5 并行生成规则

所有 clip **一次性并行提交**，不串行分批。

---

## Step 5 · 成片剪辑

### 5.1 ffmpeg 拼接

```bash
# 1. 列出所有 clip 文件（按顺序）
ls -v ./output/*.mp4 > clips.txt

# 2. 生成拼接文件
cat clips.txt | while read f; do echo "file '$f'"; done > concat.txt

# 3. ffmpeg 拼接
ffmpeg -f concat -safe 0 -i concat.txt -c copy concat_raw.mp4
```

### 5.2 BGM 合并

```bash
ffmpeg -i concat_raw.mp4 -i "bgm.mp3" -shortest -c:v copy -c:a aac output_final.mp4
```

---

## Step 6 · 交付与反馈

- 最终视频文件必须发送给用户，不能只发链接
- 检查视频是否流畅、衔接是否自然
- 如有问题：记录具体 clip 编号和现象，反馈到 Step 3 改进

---

## 执行检查清单

```
Step 1 ✅ 每张图都分析了，没有省略，没有用旁白反推
Step 2 ✅ 旁白和图片匹配合理
Step 3 ✅ script-chunk：分镜拆分完整
Step 3 ✅ shots-timing：时长计算正确（0.3s/字）
Step 3 ✅ shots-assembly：clip 在 4-15s 内，合并合理
Step 3 ✅ scene-reflection：五个维度都检查了
Step 3 ✅ 衔接设计：每个 clip 有出/入动作
Step 4 ✅ prompt 包含全部5个要素
Step 4 ✅ 全部并行生成，没有串行
Step 4 ✅ 尾帧接力已设计
Step 5 ✅ ffmpeg 拼接 + BGM 合并完成
Step 6 ✅ 最终视频已交付用户
```

---

## 关键教训（从实战提取）

1. **图片分析不能省略**：没有分析就凭旁白设计，结果与图片不符
2. **时长计算用 0.3s/字**：不是估算，是字速标准
3. **duration 必须是整数**：向上取整，`7.5` 会报错
4. **衔接必须在生成前设计**：clip 生成完再补救是补救不了的
5. **即梦 API 上限是物理约束**：导演时间线单次上限约 10-15s，超时分段 + 尾帧接力
6. **尾帧图必须用 --return-last-frame 生成**：不接受手动上传尾帧图片
7. **并行生成，不串行**：同一阶段多个任务必须一次性提交
8. **交付必须发实际文件**：不能只发链接或文字描述
9. **云盘文件必须全部读完再出成品**：当云盘文件标记为「非常重要」时，读取所有文件+完整理解后才能开始写 skill，不能读了部分就出骨架

---

---

## 参考文档

| 文档 | 来源 | 访问方式 |
|------|------|----------|
| `seedance2.0-tool/references/director-mode.md` | 即梦官方 | 本地共享 |
| `seedance2.0-tool/references/clip-continuity.md` | 实战验证 | 本地共享 |
| 即梦官方 SOP 系列（video-sop / script-chunk / shots-timing / shots-assembly / scene-reflection / video-prompt 等11个文件） | 即梦官方 | 飞书云盘 `lark-cli drive +download`，见下方清单 |

> ⚠️ **重要**：references/ 目录中不要复制这些上游文档的本地副本。上游文档由 aistar-work.feishu.cn 管理，每次使用时通过 lark-cli 读取最新版本。本 skill 的 references/ 只存放本 skill 独有的实战验证文档（如 clip-continuity.md）。

### 即梦官方 SOP 云盘文件清单

飞书云盘文件夹 token: `NlaRfWdU9lgn29dYs6DceyPjnZb`

| 文件名 | 内容 |
|--------|------|
| `jimeng-2026-05-26-2894-video-sop.md` | 即梦视频创作标准工作流程（9阶段） |
| `jimeng-2026-05-26-1840-video-prompt.md` | 分镜生视频 prompt 规范 |
| `jimeng-2026-05-26-6742-script-chunk.md` | 分镜切分规范 |
| `jimeng-2026-05-26-3727-shots-timing.md` | 分镜计时规则 |
| `jimeng-2026-05-26-5414-shots-assembly.md` | 分镜组合规范 |
| `jimeng-2026-05-26-4972-scene-reflection.md` | 连贯性校验规范 |
| `jimeng-2026-05-26-4798-ref-extract.md` | 素材挖掘规范 |
| `jimeng-2026-05-26-1766-story-ref-gen.md` | 故事参考素材生成 |
| `jimeng-2026-05-26-6845-story-idea.md` | 故事大纲创作 |
| `jimeng-2026-05-26-9174-story-script.md` | 故事剧本创作 |
| `jimeng-2026-05-26-2894-ecom-idea.md` | 营销广告创意构思 |
| `jimeng-2026-05-26-3029-ecom-ref-gen.md` | 营销参考素材生成 |

> 即梦官方 SOP 完整 Phase 应从云盘读取最新版本，不要使用本地缓存副本。