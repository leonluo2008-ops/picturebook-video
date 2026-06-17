---
name: v8-workflow-7steps
description: v8 写法 7 步工作流 — Step 1 收需求 → Step 2 vision 自检 → Step 3 时长分配 → Step 4 Clip 划分 → Step 5 prompt 写 → Step 6 提交 → Step 7 验证。整合了 standard-picturebook-workflow-5steps + narration-shot-mapping + clip-pacing + director-cut-merge 4 个老 references 的核心方法论。
license: Apache-2-2
metadata:
  hermes:
    tags: [v8, workflow, 7-steps, storyboard, 2026-06-16]
  related_skills: [picturebook-video, seedance2.0-tool]
---

# v8 写法 7 步工作流

> **整合**：5 步工作流 + 旁白-镜头映射（#M3）+ 整本节奏 + 合并配方
> **每步必跑** = 漏 1 步 = 翻车
> **Step 5 prompt 写法** = 见 `v8-prompt-template.md`

---

## 整体框架

```
Step 1: 收需求（4 件：简介 / 图片 / 平台 / TTS）
  ↓
Step 2: vision 自检（全 N 张图 + 标 5 项）
  ↓
Step 3: 时长分配（用户 TTS 优先 + 5 档对比 + 整数化）
  ↓
Step 4: Clip 划分（5 项一致性 = 合并 / 不一致 = 必拆）
  ↓
Step 5: prompt 写（v8 4 段骨架 + 故事弧 + 方向锚点）
  ↓
Step 6: seedance 提交（ref_images + 整数时长 + B 档音效）
  ↓
Step 7: 端到端验证（md5 + 时长 + 画面目检）+ 发飞书
```

---

## Step 1 · 收需求（4 件）

| 必收 | 形式 |
|---|---|
| 绘本简介 | 故事简介.txt 或用户口述 |
| 绘本图片 | 本地路径 / 飞书云盘 / 附件（PNG/JPG）|
| 目标平台 | 抖音 / 小红书 / 视频号 / B 站（= 决定画幅）|
| TTS 数值 | 用户给 = 视频总时长基准 / 不给 = 兜底公式 1.0 词/秒 + 3 字/秒 |

---

## Step 2 · vision 自检（5 项必查）

### ⚠️ 用户硬性元偏好（**2026-06-16 爷爷 Grandpa 绘本踩坑**）

> **用户原话**："看图你不要跟我确认，直接全看"

**核心**：拿到 N 张参考图 = **必 1 次性 vision 全 N 张看完 + 边看边写到 image-inventory = 不分批中断 + 不中途跟用户确认**。

**禁止反模式**：

- ❌ 看完前 3 张后停下来发"已 vision 3 张，是否继续看剩下 5 张？"
- ❌ 看完一批后发"是否开始写 prompt？"
- ❌ 任何把"流程内部节点"伪装成"决策点"反问用户的行为
- ❌ 1 张图 vision 后问"这张是什么风格？"
- ❌ 任何"我打算 X 因为 Y"式询问（报告 ≠ 询问）

**正确范式**（**流程内不确认·只有跑视频后目检才让用户介入**）：

```
收到 N 张图
   ↓
1 次性把 N 张 vision 完（按 ≤ 3 张/批拆批，**不**在批间跟用户确认）
   ↓
直接写到 image-inventory.md（含 5 项 + 有/没有两列 + 叙事弧）
   ↓
直接进 Step 3 算 TTS（不确认）
   ↓
Step 4 划完 Clip（不确认）
   ↓
Step 5 写完 N 个 prompt（不确认）
   ↓
Step 5.5 跑完 4 项 grep 兜底（不确认）
   ↓
Step 6 提交第 1 个 Clip → 等用户目检（**这才是真正该问的节点**）
```

**根因**（用户偏好底层逻辑）：

- 用户来 = 让我做事，**不是让我做问卷**
- vision / TTS 算 / Clip 划 / prompt 写 = **流程内部** = 不可逆程度低 = **不确认**
- 提交视频后**目检反馈** = **流程外** = 用户该介入的节点

**判定口诀**（"什么时候该跟用户确认？"）：

```
1. 我要确认的事 = 流程内还是流程外？
   ├─ 流程内（vision / TTS / Clip 划 / prompt 写）→ 不确认 · 直接做
   └─ 流程外（提交后目检 / 不可逆决策）→ 等用户拍板

2. 我要确认的事 = 可逆还是不可逆？
   ├─ 可逆（再跑一个 Clip 也行）→ 直接做 + 报告
   └─ 不可逆（删数据 / 关服务）→ 一次性问清楚

3. 我有没有"问错了的代价"？
   ├─ 问错了代价低（凭印象写 1 段 prompt）→ 不问
   └─ 问错了代价高（删业务数据）→ 一次性问
```

**跨 skill 适用**（不只绘本视频）：

- ✅ 绘本视频（Step 2 vision 全 N 张必看光 = 不确认）
- ✅ 漫剧分镜（角色图 + 场景图 = 全看完才进 prompt）
- ✅ 任何"批量输入 + 流程化处理"任务（多文件 / 多图 / 多数据源）

### 5 项必查（每张图）

| # | 必查 | 写到 prompt 哪里 |
|---|---|---|
| 1 | 主体在画面哪个位置（左/中/右/上下） | 段 1 主体定义 |
| 2 | 主体朝向（侧身/正面/背面 + 朝左/朝右） | 段 1 + 段 4 运镜 |
| 3 | 景别（全身/中景/半身/特写） | 段 4 运镜（**参考图原景别 = 起点**）|
| 4 | 主体姿态（手/脚/头的具体位置） | 段 1 主体定义 |
| 5 | 招牌/文字位置（顶部/中央/右侧/角落） | 段 4 文字保留 + 段 4 运镜 |

### vision 调用规范

```bash
# 1 批 ≤ 3 张（避免 multi-image-eviction）
for batch in 1 2 3; do
  case $batch in
    1) imgs="1.jpg 2.jpg 3.jpg" ;;
    2) imgs="4.jpg 5.jpg 6.jpg" ;;
    3) imgs="7.jpg 8.jpg" ;;
  esac
  mcp_zai_analyze_image "${imgs[@]}" "..."
done
# **不**在批间跟用户确认 · **不**发"已看完前 3 张，是否继续？"
```

### ⚠️ 5 项 = 启发性参照 ≠ 枷锁

**允许**（用户原话级）：

- 跑出画面（往画面外跑 = 镜头有方向感）
- 转弯往回跑（动态 = 有变化）
- 跑 1-2 秒再换动作（动态 = 节奏点）
- 姿态一直在变（动画感来源）
- 多镜头/单镜头/多机位（时长能容纳）
- 镜头推进拉远切换角度（自由运镜）

**禁止**（v1-v4 误用 = 翻车根因）：

- 把参考图当枷锁（5 项必查"严格匹配"= 僵化）
- "必须保持参考图的整体构图...不重新设计画面布局"
- "固定原景别不做推拉"
- "跑步动作循环"
- "保持跑步姿态"

---

## Step 3 · 时长分配（用户 TTS 优先）

### 3 步走

1. **5 档语速对比**（必跑）= 详见 `v8-tts-rate.md`
2. **选物理意义最强 + 跟用户 TTS 差 ≤ 5s 档**（如 1.4/4.0 领读型）
3. **整数化**（API 拒绝 7.5s = 8s）

### 旁白-时长映射（#M3）

```
1 段旁白 = 1 镜头 = N 秒（TTS 计算）
N 段旁白 = N 镜头 = 总 TTS + 5s 冗余（默认）/ 严格匹配（用户说）
```

### TTS 兜底公式

```
英文 = 1.0 词/秒（用户给 = 1.4 词/秒）
中文 = 3.0 字/秒（用户给 = 4.0 字/秒）
词间停顿 = 0.5s
```

### Step 3.5 · 必走 · 确认点 1 · Clip 时长划分/合并策略确认（v5.0.5 新增）

**⚠️ 必走**（铁律 #30 强约束 · 违反 = 红线违规）：

**做法**：Step 3 + Step 4 算完 → 输出纯文本让用户看 Clip 时长划分和合并策略 → 收到 "OK" → 才进 Step 5。

```bash
# ⚠️ 必先发飞书让用户确认（纯文本 + 标题 + 列表，不用表格）
send_message action=send target=feishu message="## 确认点 1 · Clip 时长划分方案

绘本：[绘本名] · [N] 页 · TTS [Xs]

时长划分（5 档对比后选 [X.X/Y.Y] 档）：
- Clip 1：[Xs] · 单图 · [主体]
- Clip 2：[Xs] · 单图 · [主体]
- ...（共 N 个）

合并策略：
- 单镜单图 [N] 个 / 单镜 N 图 [N] 个（5 项一致性检查后）

总时长：[Xs] · [N] Clip · 合并方案 [描述]

回复 OK / 不通过 + 修改意见。"
```

**反模式**：
- ❌ 不等用户确认直接进 Step 5 写 prompt
- ❌ 用表格输出（飞书渲染问题，详 SKILL.md 铁律 #32）

详见 SKILL.md 铁律 #30。

---

## Step 4 · Clip 划分（5 项一致性 = 合并 / 必拆）

### 合并决策（5 项一致性）

| 检查 | 一致 | 不一致 |
|---|---|---|
| 主体位置 | 可合并 | 必拆 |
| 主体朝向 | 可合并 | 必拆 |
| 景别 | 可合并 | 必拆 |
| 主体姿态 | 可合并 | 必拆 |
| 招牌位置 | 可合并 | 必拆 |

**判定口诀**：

- N 张图 5 项全一致 = 可合并到 1 个 Clip
- 任 1 项不一致 = 必拆 Clip

### 合并数量（甜区）

| 数量 | 适用 |
|---|---|
| 1 镜 1 图 | **v8 默认**（最安全）|
| 1 镜 N 图（N≤3）| 多图多旁白 1 Clip（5 项全过）|
| N 镜 N 图 | 故事弧需要（v8 推这种）|

### 反模式

- ❌ 1 镜 4 图（4 个不同主体 = 视频"瞬移"）
- ❌ 1 镜 N 旁白 + N 主体（旁白和主体都变 = 错位）
- ❌ 1 镜 7+ 张参考图（违反 seedance 多图参考限制）

---

## Step 5 · prompt 写（v8 4 段骨架）

详见 `v8-prompt-template.md`。

### Step 5.5 · 必走 · 确认点 2 · 每个 Clip 中文 prompt 确认（v5.0.5 新增）

**⚠️ 必走**（铁律 #30 强约束 · 违反 = 红线违规）：

**做法**：Step 5 写完 N 段 prompt → **翻译/列出每段中文 prompt** → 发飞书让用户确认 → 收到 "OK" → 才进 Step 6。

```bash
# ⚠️ 必先发飞书让用户确认（纯文本 + 标题 + 列表，不用表格）
# 注意：prompt 用 v8 4 段骨架写了 @ImageN · 这里给用户看的是"中文翻译版"
send_message action=send target=feishu message="## 确认点 2 · 每个 Clip 中文 prompt 方案

绘本：[绘本名] · [N] Clip

Clip 1 · [Xs] · @Image1（[主体]）：
中文描述：[主体外观 + 核心动作 + 1 组情绪外化 + 1 运镜 + 方向锚点]
关键引导：[时间点/运镜/声音/末帧约束/风格词]

Clip 2 · [Xs] · @Image2（[主体]）：
...

（共 N 段）

自检结果（v8-prompt-template.md 检查 1-5）：
- 检查 1 方向锚点：✅
- 检查 2 末帧冗余：✅ 0 命中
- 检查 3 情绪词：✅ 0 命中
- 检查 4 @ImageN 必含：✅
- 检查 5 多图覆盖：✅（单图 Clip 跳过）

回复 OK / 不通过 + 修改意见。"
```

**反模式**：
- ❌ 不等用户确认直接进 Step 6 提交
- ❌ 只列英文 prompt 不翻译成中文（用户看不懂英文）
- ❌ 用表格输出（飞书渲染问题，详 SKILL.md 铁律 #32）
- ❌ 跳过 v8 自检 5 项（铁律 #29 强约束）

详见 SKILL.md 铁律 #29 + #30。

### ⚠️ `@ImageN` 必含铁律（2026-06-17 多图 Clip 翻车沉淀 · 主 agent 路径必读）

- **每段 prompt = 必以 `from X.Xs to Y.Ys @ImageN is the ... shot, ...` 开头**
- `@ImageN` = 唯一参考帧绑定（N = 该镜头对应的图编号）
- 多图 Clip = 每个 `@ImageN` 都必带该图独有的视觉特征（详见 `v8-prompt-template.md` 多图覆盖规则）
- **反模式**：❌ prompt 0 处 `@Image` = 模型不知道哪张是参考图 = 必翻车

### 多镜头范式（v8 默认 = 1 段 prompt 1 镜头）

```
prompt = 主体定义 + 核心动作 + 情绪外化（1 组动作）+ 运镜 + 方向锚点
+ 末段简洁约束（1 句不堆砌）
```

**注意**：1 段 prompt = 1 镜头 = 1 段旁白（v8 不堆砌 3 镜到 1 段）。

---

## Step 6 · seedance 提交（含 4 确认点流程 · v5.0.5 修订）

### Step 6.0 · 必走 · spike clip 单测（4 确认点中的确认点 3 + 4）· 2026-06-17 云服 8 并行翻车沉淀

**⚠️ v5.0.5 修订**：`#30` 从"单测必跑"修订为"4 确认点流程"·本节是确认点 3（提交前）和确认点 4（跑完后）的具体执行段。

#### 确认点 3 · spike 提交前参数确认（必走 · 主 agent 强约束）

**做法**：准备 spike 参数 → 输出纯文本让用户确认 → 收到 "OK" → 才提交。

```bash
# 1. 准备 spike 参数（参考下方"spike clip 推荐配置"）
SPIKE_PROMPT="$CLIP1_PROMPT"
SPIKE_REFS="$CLIP1_REFS"
SPIKE_MODEL="doubao-seedance-2-0-fast-260128"
SPIKE_DURATION=4
SPIKE_RESOLUTION=480p

# 2. ⚠️ 必先发飞书让用户确认参数（纯文本 + 标题 + 列表，不用表格）
send_message action=send target=feishu message="## 确认点 3 · 准备跑 spike 单测

绘本：[绘本名] · Clip 1（8 Clip 中的第 1 个）

参数：
- model: doubao-seedance-2-0-fast-260128（fast 档）
- duration: 4 秒
- resolution: 480p（最低费用）
- ratio: 16:9
- generate_audio: false（spike 只验视觉）
- watermark: none

prompt 摘要：[前 100 字]

回复 OK / 不通过 + 修改意见。"

# 3. ⚠️ 必等用户回复 OK 才进步骤 4 = 不许自判 / 不许沉默默认
# （如用户说"全自动"/"静默跑"= 跳过此确认点）
```

**反模式**：
- ❌ 不等用户确认直接调 `mcp_seedance_generate_video`
- ❌ 用表格输出确认信息（飞书渲染问题，详 SKILL.md 铁律 #32）

#### ① 跑 1 条 spike clip（收到确认后才执行）

```bash
# 用 Clip 1 跑 spike（480p + 最短时长 4s + 无 BGM = 最低费用）
# 单图 Clip 用 1 个 ref，多图 Clip 用对应数量的 ref
mcp_seedance_generate_video \
  --prompt "$SPIKE_PROMPT" \
  --ref_images "$SPIKE_REFS" \
  --model "$SPIKE_MODEL" \
  --duration "$SPIKE_DURATION" \
  --ratio 16:9 \
  --resolution "$SPIKE_RESOLUTION" \
  --generate_audio false \
  --watermark none

mcp_seedance_wait_and_download --task_id <task_id> --output_path clip1-spike.mp4 --timeout_sec 300
```

**spike clip 推荐配置**（最低费用范式）：
- `model = doubao-seedance-2-0-fast-260128`（fast 档）
- `resolution = 480p`（不是 720p）
- `duration = 4`（最小整数）
- `generate_audio = false`（绘本有声场景也先 false，spike 阶段只验视觉）
- `watermark = none`

#### 确认点 4 · spike 跑完后视觉质量 + 批量 1 次确认（必走）

**做法**：spike 跑完 → 验证元数据 → 发飞书带 MEDIA 附件让用户目检 → 用户回复"OK"= **同时意味视觉 OK + 可以批量 2 件事** → 才进 Step 6.1。

```bash
# 1. 验证 spike 元数据
md5sum clip1-spike.mp4
SPIKE_MD5=$(md5sum clip1-spike.mp4 | awk '{print $1}')
SPIKE_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 clip1-spike.mp4)

# 2. ⚠️ 必先发飞书让用户目检（纯文本 + MEDIA 附件，不用表格）
send_message action=send target=feishu message="## 确认点 4 · Spike 单测跑完，请目检

绘本：[绘本名] · Clip 1

时长：${SPIKE_DURATION}s
md5：${SPIKE_MD5}
文件：MEDIA:/path/clip1-spike.mp4

回复 OK = 视觉 OK + 可以批量 2 件事。
回复 修改意见 = 重提新任务（铁律 #19 已发任务不重复提交）。"

# 3. ⚠️ 必等用户回复才进 Step 6.1 批量 = 不许自判 / 不许沉默默认
# （如用户说"全自动"= 跳过此确认点直接批量）
```

**反模式**：
- ❌ spike 跑完自判"应该 OK"不确认（自判 = 翻车）
- ❌ 用户没回复就当默认通过（沉默 ≠ 确认）
- ❌ spike 跑完后不存 md5 / 不发飞书（用户没法看）
- ❌ 用表格输出确认信息（飞书渲染问题）

详见 SKILL.md 铁律 #30 + #32。

---

### Step 6.1 · 批量提交 · 每轮 ≤ 3 并发（2026-06-17 云服 8 并行翻车沉淀）

**核心约束**：seedance 个人用户最大并发 = 3（官方限流 · `references/seedance-official-docs/1-Doubao_Seedance_2.0_系列教程.docx` line 143）。企业用户 = 10。**绘本场景默认按个人用户 3 并发**。

**3 步必走**：

```bash
# 把 N 个 Clip 拆成 ceil(N/3) 轮
# 例：8 个 Clip = 3 + 3 + 2 = 3 轮
N_CLIPS=8
ROUNDS=$(( (N_CLIPS + 2) / 3 ))
echo "总轮数: $ROUNDS"  # 期望 3

for round in 1 2 3; do
  # 每轮提交 3 个（或最后一轮 < 3 个）
  for clip in $(get_clips_for_round $round); do
    mcp_seedance_generate_video \
      --prompt "${CLIP_PROMPTS[$clip]}" \
      --ref_images "${CLIP_REFS[$clip]}" \
      --model doubao-seedance-2-0-fast-260128 \
      --duration "${CLIP_DURATIONS[$clip]}" \
      --ratio 16:9 \
      --resolution 720p \
      --generate_audio true \
      --watermark none
  done

  # 每轮提交后必 wait_and_download 全部完成（Step 6 wait_and_download 红线 · v5.0.3 沉淀）
  for task_id in $(get_task_ids_for_round $round); do
    mcp_seedance_wait_and_download --task_id "$task_id" --output_path "clip$round-$(basename $task_id).mp4" --timeout_sec 300
  done

  # 下一轮提交前必查 status（确保本轮无 failed 任务 = 有就停下汇报用户）
  if has_failed_task $round; then
    echo "❌ 本轮有 failed 任务，停下汇报用户"
    break
  fi
done
```

**反模式（必避）**：
- ❌ 8 个 Clip 一次性并行（超限流 = 部分任务卡死/失败 = 云服多图 Clip 翻车原文）
- ❌ "并发越多越快"（并发受官方限流约束）
- ❌ 单轮提交后不等 wait_and_download 完成就开下一轮（叠加并发 = 超限）
- ❌ 企业用户按 10 并发（绘本场景默认个人用户 = 3）

详见 SKILL.md 铁律 #31。

---

### Step 6.2 · 参数规范

| 参数 | v8 默认 | 备注 |
|---|---|---|
| model | `doubao-seedance-2-0-fast-260128` | 默认 fast |
| duration | 整数 [4, 15] | 用户 TTS ÷ Clip 数 = 向上取整 |
| ratio | 16:9（绘本）/ 9:16（抖音）/ 1:1（朋友圈）| 平台决定 |
| generate_audio | **true**（绘本有声场景）| user-pinned 不可覆盖 |
| watermark | `none`（绘本）| 不加 AI 水印 |
| resolution | 720p（生产）/ 480p（spike）| spike 用 480p 省钱 |
| ref_images | 单图 Clip = 1 个路径 / 多图 Clip = N 个路径（必 = image_index 图数量）| **红线**：缺任一路径 = 不提交（v5.0.3 沉淀）|

### 提交后处理

> ⚠️ **红线（2026-06-17 多图 Clip 翻车沉淀）**：提交获得 task_id 后 = **必立即调 `wait_and_download` 同步等待 + 下载** · 禁止只调 `generate_video` 拿 task_id 停手等用户催 · 兜底（wait_and_download timeout 后）= `check_task` 查 status + curl video_url -o clipN.mp4（铁律 #19 已含）

```bash
# 1. wait_and_download 同步等待 + 下载
mcp_seedance_wait_and_download --task_id <task_id> --output_path clip1-v8.mp4 --timeout_sec 300

# 2. 验证元数据
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 clip1-v8.mp4
md5sum clip1-v8.mp4
ls -lh clip1-v8.mp4

# 3. verify 4 项（必走手动 grep，verify 脚本有误报）
grep -E "末帧定格|末帧微动|不得成为定格海报|1s 内至少 1 个动作元素" clip1-v8-prompt.txt
# 期望 0 命中
```

---

## Step 7 · 端到端验证 + 发飞书

### 验证清单

| 项 | 命令 | 期望 |
|---|---|---|
| 时长 | `ffprobe -show_entries format=duration` | 跟 duration 一致 |
| md5 | `md5sum` | 全 Clip 唯一 |
| 大小 | `ls -lh` | < 20M/clip |
| 画幅 | `ffprobe -show_entries stream=width,height` | 跟 ratio 一致 |
| 画面 | 用户目检 | 流畅 + 方向感 + 故事弧 |

### 发飞书

```
send_message action=send target=feishu message="[绘本名] N 个 Clip 全部生成：MEDIA:... MEDIA:... ..."
```

---

## 决策树（整本绘本）

```
N 张参考图 + M 段旁白
  ↓
M 段旁白总 TTS = 用户给 TTS（30s / 28s / 60s 等）
  ↓
M 段 ÷ 故事弧 4 步 = N Clip（1 Clip = 1 段 prompt = 1 镜 1 图）
  ↓
每个 Clip 走 Step 2-7 = N 个 mp4
  ↓
ffmpeg concat + 整数化 = 整本视频
```

---

## 整本节奏（#M1 核心）

| 维度 | 规则 |
|---|---|
| Clip 总数 | 绘本 N 段旁白 = N Clip（**不**按段拆细分）|
| Clip 时长 | 1 段旁白 TTS = 1 Clip 时长（整数化）|
| Clip 故事弧 | 多镜头 Clip 必走 出现→转折→高潮→收尾 |
| 静默 | 不硬塞 ≥ 2s 末帧静默（铁律 #27）|
| 收尾 | 末段必留下一个"画面有动感"的余韵 = 故事感 |

---

## 跟元方法论的对应

| 元方法论 | 7 步工作流哪步 |
|---|---|
| #M1 整本节奏 | Step 3-4（时长 + Clip 划分）|
| #M2 规则推导 | Step 5（不靠记忆写 = 5 项必查）|
| #M3 旁白-镜头映射 | Step 3 + Step 5（1 段旁白 = 1 镜头）|
| #M4 蒸馏治理 | 整个流程（业务/work/方法论/铁律 3 层）|

---

## 自检命令

```bash
# Step 2 vision 5 项必查
echo "1. 主体位置: $(grep -c 'left\|right\|center' clip*-vision-notes.txt)"
echo "2. 主体朝向: $(grep -c 'side\|front\|back\|facing' clip*-vision-notes.txt)"
echo "3. 景别: $(grep -c 'close-up\|medium\|wide\|full' clip*-vision-notes.txt)"
echo "4. 主体姿态: $(grep -c 'posture\|sitting\|standing\|running' clip*-vision-notes.txt)"
echo "5. 招牌位置: $(grep -c 'top\|center\|corner' clip*-vision-notes.txt)"

# Step 3 时长
echo "TTS 5 档对比见 v8-tts-rate.md"

# Step 4 Clip 划分
echo "5 项一致性检查 = 5/5 一致才可合并"

# Step 5 prompt 自检
grep -E "toward|exits|off-screen|left to right" clip*-prompt.txt
# 期望 ≥ 1 命中 / 镜头

# Step 6 提交后
md5sum clip*.mp4 | awk '{print $1}' | sort -u | wc -l
# 期望 = Clip 数（md5 唯一）
```
