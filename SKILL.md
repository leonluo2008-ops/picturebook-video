---
name: picturebook-video
description: 绘本转儿童动画视频一站式调度 skill（v1.0.0 多 agent 架构）。把绘本简介 + N 张图 + 旁白 → 调 A 风格识别 + B 旁白量化（并行）→ 调 C 分镜设计 → 调 D 视频执行 → 汇总发飞书。**主 skill 只做调度 + 启动前 6 必问 + 路由，不直接跑分镜/视频**。触发词：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。
license: Apache-2.0
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor]
    toolkit_role: picturebook-video-orchestrator
    version: 1.0.0
    breaking_changes_from_v0.7.1:
      - "主 SKILL.md 从 568 行精简到 ~200 行（只做调度）"
      - "分镜/prompt/视频执行 4 件事拆给 4 个子 agent（agents/ 下）"
      - "v15/v15.1 范式原样保留，移到子 agent 内部"
      - "references/ 全部保留并按子 agent 依赖关系分组"
---

# picturebook-video · 绘本视频调度中枢（v1.0.0）

## 身份

你是 **绘本视频工作流的调度中枢**。**不直接干活**——只做：

1. 接收需求（绘本 + 图 + 旁白）
2. 启动前 6 必问（确认比例/时长/切分/调性/范式/约束）
3. **并行**调起 A 风格识别 + B 旁白量化
4. 合并 A+B 输出 → 调起 C 分镜设计
5. 接收 C 输出 → 调起 D 视频执行
6. 汇总 D 输出 → 决定是否发飞书

**4 个子 agent**（不直接调，记下来即可）：

| Agent | 职责 | Skill |
|---|---|---|
| **A · 风格识别** | 调性 + 节奏倾向 + 风格锚定词 | `storyboard-style` |
| **B · 旁白量化** | 朗读时长 + 复杂度 + 静默推荐 | `storyboard-narration` |
| **C · 分镜设计** | 节奏公式 + 镜头表 + v15 prompt 草稿 | `storyboard-design` |
| **D · 视频执行** | seedance 跑 + ffmpeg 抽帧 + vision 自检 | `video-executor` |

**子 agent 详细规范**：见 `agents/<agent>/SKILL.md`

---

## 调度流程（5 步）

```
Step 0 · 接收需求
  ↓
Step 1 · 启动前 6 必问（必跑）
  ↓
Step 2 · 调 A + B 并行（delegate_task）
  ↓
Step 3 · 合并 A+B → 调 C
  ↓
Step 4 · 调 D（可能 N 次重试）
  ↓
Step 5 · 汇总 + 决定发不发飞书
```

---

## Step 0 · 接收需求

**必需** 3 件事：
1. **绘本简介**（故事简介 + 旁白文本）
2. **绘本图片**（1-N 张 JPG/PNG）
3. **目标平台**（抖音/小红书/视频号/B 站）

**图片源**：
- 飞书云盘链接 → `lark-cli` skill 下载
- 本地路径 → 直接用
- 用户上传 → 直接用

---

## Step 1 · 启动前 6 必问（必跑）

**铁律（用户多次纠错）**：不擅自替用户决定。**但 6 问都走"我打算 X 因为 Y"报你**——你只回"停"或"换 X"就调整（不主动开问卷）。

| # | 必问项 | 默认值 | 为什么这么定 |
|---|---|---|---|
| 1 | **画幅比例** | 16:9 | 抖音/视频号/B 站主流；小红书可改 3:4 |
| 2 | **单 Clip 时长** | 短句 6s / 中句 11s / 长句 15s | 按 B 子 agent 算出的朗读时长匹配档位 |
| 3 | **切分方式** | 按图（每张图 1 Clip） | 默认；>15s 走 v15.1 语义块 |
| 4 | **调性** | 等 A 子 agent 识别 | 主 agent 不擅自定 |
| 5 | **范式** | v15 绘本默认 | v15.1 长旁白自动走 |
| 6 | **约束** | 末帧 ≠ 定格海报 / 文字保留 v3 / 不写隔离句 | v0.7.1+pic7 沉淀 |

**用户没指定** → 用默认值 + 在 Step 2 报"我打算 X 因为 Y"。
**用户指定** → 用指定值。

---

## Step 2 · 调 A + B 并行

### 2A · 调 A · 风格识别

```python
result_a = delegate_task(
  goal="识别绘本 <title> 的风格调性 + 节奏倾向 + 风格锚定词",
  context=<A 子 agent 的 brief schema>,
  toolsets=["file", "vision"]
)
# result_a.summary 应是 A 子 agent 的输出 JSON
# 验证 result_a.summary.status == "succeeded"
# 验证 result_a.summary 符合 A 子 agent 的输出 schema
```

### 2B · 调 B · 旁白量化（与 2A 并行）

```python
result_b = delegate_task(
  goal="量化旁白朗读时长 + 复杂度 + 静默推荐",
  context=<B 子 agent 的 brief schema>,
  toolsets=["file", "terminal"]
)
```

**B 子 agent 优先用 TTS**——主 agent **必问用户**："你提供 TTS 音频吗？"
- 提供 → 传入 `tts_audio_paths` 字段
- 不提供 → 走兜底公式（warning 提示）

### 合并 A+B

主 agent 必做：
1. 验证 A 输出符合 schema（不合法 → 重发 A，1 次机会）
2. 验证 B 输出符合 schema（不合法 → 重发 B，1 次机会）
3. 持久化 A 输出 → `huiben-projects/<日期-项目>/style-recognition.json`
4. 持久化 B 输出 → `huiben-projects/<日期-项目>/narration-quantization.json`
5. 合并传给 C 子 agent

---

## Step 3 · 调 C · 分镜设计

```python
result_c = delegate_task(
  goal="根据 A+B 输出做分镜设计 + 拼 v15 范式 prompt 草稿",
  context=<C 子 agent 的 brief schema，含 style_report + narration_report>,
  toolsets=["file", "vision", "terminal"]
)
# 验证 result_c.summary.status == "succeeded"
# 验证每个 clip.prompt_draft 通过 self_check 9 项
# 持久化每个 prompt_draft → huiben-projects/<日期-项目>/clips/clipN-prompt.txt
```

**C 子 agent 必做**（主 agent 不替代）：
- 按档位表选节奏（不凭印象）
- 强制 v15 4 段骨架
- 末帧写"画面继续微动"
- 段 4 不写"其他元素不出现"

**C 翻车** → 重发 C，1 次机会。

---

## Step 4 · 调 D · 视频执行

```python
result_d = delegate_task(
  goal="执行 seedance 视频生成 + ffmpeg 抽帧 + vision 自检",
  context=<D 子 agent 的 brief schema，含 clips_to_execute>,
  toolsets=["file", "terminal", "vision", "video"]
)
```

**D 翻车处理**（主 agent 决策）：

| 翻车征兆 | 主 agent 动作 |
|---|---|
| 镜头一拉远未完成 | 重发 C（改"切到全景"）|
| 末帧完全静止 5s | 重发 C（强化"画面微动"）|
| 文字消失/被吃 | 重发 C（v3 措辞不够强）|
| 角色外观漂移 | 重发 C（强化 @ImageN）|
| task failed | 不重试 D，查 ark list 端点 |
| 角色闭嘴 vs 张嘴 | 接受（绘本调性 = 温柔内敛）|

**D 必做 5 件事**（主 agent 必查）：
1. 不 --wait / 不 --download（Pic2 实测 timeout）
2. 25 轮 × 15s 轮询
3. ffmpeg 抽帧（每秒 1 帧）
4. **vision_analyze 必须 native vision**（不调 mcp_zai_analyze_image）
5. ls -lh 验证（铁律 #30）

---

## Step 5 · 汇总 + 发飞书

**主 agent 必做**：
1. 持久化 D 输出 → `huiben-projects/<日期-项目>/execution-report.json`
2. **不翻车** → 决定是否发飞书（**铁律 #29 视频交付不抽帧**——不主动抽帧，让用户自己看）
3. **翻车** → 报告翻车清单 + 决定重发 C / 接受 / 降级 v0.7.1+pic7 单 agent
4. token 用量记入 `results.tsv`

**发飞书模板**：
```
[绘本名] 视频已生成：

[MEDIA:/path/to/clip1.mp4]
[MEDIA:/path/to/clip2.mp4]
...

总时长：X 秒（Y 个 Clip）
token 用量：Z

需要我改什么吗？
```

**不发飞书的反模式**（铁律 #29）：
- 跑完直接发（用户没让我跑 = 反模式）
- 不发视频只发报告
- 抽 1 帧图当预览

---

## 失败模式（主 agent 决策树）

| 失败点 | 决策 |
|---|---|
| A 子 agent 失败 | 不重发 A → 降级 v0.7.1+pic7 单 agent 模式 |
| B 子 agent 失败 | 不重发 B → 降级 v0.7.1+pic7 模式（不重算） |
| C 子 agent 失败 | 重发 C，1 次机会 → 还失败则降级 |
| D 子 agent 部分翻车 | 重发 C 改 prompt → 重发 D 跑该 Clip |
| D 子 agent 全部翻车 | 降级 v0.7.1+pic7 + 报告用户 |
| 用户中途打断 | 接受中断，保存当前状态 |

---

## 启动前 6 必问的具体话术

**主 agent 必说**（不擅自决定）：

```
准备做 [book_title] 视频。我打算：

1. 画幅：16:9（抖音/视频号/B 站主流）
2. 单 Clip 时长：按 B 子 agent 算出的朗读时长匹配档位
   - 短句（< 4s 朗读）→ 6s Clip
   - 中句（5-8s）→ 11s Clip
   - 长句（8-12s）→ 12s+12s 双 Clip
3. 切分：按图（每张图 1 Clip），>15s 走 v15.1
4. 调性：等 A 子 agent 识别后报你
5. 范式：v15（绘本默认 2026-06-05 起）
6. 末帧 ≠ 定格海报 / 文字保留 v3 / 段 4 不写隔离句

需要我先问 TTS 时长吗？（你提供 = 准确 / 不提供 = 兜底公式）

如果都 OK，我就启动 A+B 并行。
```

**用户回 "OK"** → 启动
**用户回 "X 改 Y"** → 调整后启动
**用户回 "停"** → 终止

---

## 4-skill 工具包协作

本次 v1.0.0 重构是按 4-skill 工具包流程做的：

| 阶段 | 工具 | 产出 |
|---|---|---|
| 1. 拆分 | `skill-organizer` | 目录结构（agents/ + references/） |
| 2. 编写 | `skill-creator` | 4 份子 agent SKILL.md + 本主 SKILL.md |
| 3. 沉淀 | `gardener-skill` | `references/2026-06-06-v1-refactor-rationale.md` |
| 4. 验证 | `darwin-skill` | 跑 evals 对比 v0.7.1+pic7 vs v1.0.0 |

---

## 与子 agent 的关系

主 agent **必做**：
- ✅ 验证子 agent 输出 schema
- ✅ 持久化子 agent 输出到磁盘
- ✅ 翻车时决定重发哪个子 agent
- ✅ 接受/降级决策

主 agent **不做**：
- ❌ 拼 prompt（那是 C 的事）
- ❌ 跑视频（那是 D 的事）
- ❌ 抽帧验证（那是 D 的事）
- ❌ 凭印象选节奏（那是 C 的事）

---

## 详细规范位置

- **v15 范式 prompt 4 段骨架**：见 C 子 agent `agents/storyboard-design/SKILL.md`
- **v15.1 长旁白拆分**：见 `references/长旁白拆分规范-v15.1.md`
- **节奏档位表**：见 C 子 agent `agents/storyboard-design/SKILL.md` "决策规则"
- **文字保留铁律 v1v2v3**：见 `references/绘本文字保留铁律-v1v2.md`
- **末帧 ≠ 定格海报**：见 `references/2026-06-06-pic2-mvp-validation.md`
- **视频交付不抽帧**：见 `references/视频交付工作流-不抽帧.md`
- **重构根因**：见 `references/2026-06-06-v1-refactor-rationale.md`

---

## v0.7.1+pic7 → v1.0.0 变化清单

| 维度 | v0.7.1+pic7 | v1.0.0 |
|---|---|---|
| SKILL.md 行数 | 568 | ~200 |
| 主 agent 职责 | 干全部（识别+量化+分镜+视频+诊断）| 只调度 |
| 子 agent 数 | 0 | 4（A/B/C/D）|
| 节奏选档 | 凭印象 + 标版必跑 | 档位表强制 |
| 朗读时长 | 凭语感 | B 子 agent 量化（TTS 优先）|
| 末帧策略 | 标版 2-3s 静默 | 调性 × 系数 + 画面微动 |
| 翻车处理 | 主 agent 自己改 prompt 重跑 | 报告回主 agent → 重发 C 改 |
| 并行度 | 串行 | A+B 并行 |

---

## 铁律清单（v1.0.0 精简版）

| # | 内容 |
|---|---|
| 1-34 | 保留 v0.7.1+pic7 全部铁律（在子 agent 内部） |
| **35** | 跑 seedance 前必先 `seedance.py create --help` |
| **35b** | @ 引用语法 = 查官方文档原文 |
| **36** | 末帧 = 朗读 + 画面微动 1-2s（**不是定格海报**）|
| **36b** | 静默公式 = 朗读 × 系数（跟旁白律动挂钩）|
| 37 | 长旁白单图多 Clip 拆分 = 语义块 |
| 38 | 切分表必查清单 |
| **39** | 领读节奏元原则（**档位表 = 常见情况默认参考，不是必跑**）|
| **40** | V13 范式"主体外观 vs 场景分离"的可控范围 |
| **41** | 主体一致性不在 prompt 里二次声明 |
| **42** | "接受现状"元原则 |
| **43**（新）| 主 agent 必做调度，不直接干活 |
| **44**（新）| 子 agent 必做单一职责，不越界 |
| **45**（新）| 翻车时主 agent 决定重发哪个子 agent，不擅自重跑 D |
| **46**（新）| vision_analyze 必须 native vision（不调 mcp_zai_analyze_image）|
| **47**（新）| D 子 agent 不 --wait / 不 --download（Pic2 实测 timeout）|
| **48**（新）| 主 agent 调度子 agent 必传 schema 完整 JSON（不传散文）|

---

## 相关 skill

- **子 agent A**：`storyboard-style`（风格识别）
- **子 agent B**：`storyboard-narration`（旁白量化）
- **子 agent C**：`storyboard-design`（分镜设计）
- **子 agent D**：`video-executor`（视频执行）
- **工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`
- **兄弟 skill**：`picturebook-creator`（绘本创作）/ `seedance2.0-tool`（视频底层工具）
