---
name: picturebook-video
description: 绘本转儿童动画视频一站式调度 skill（v1.0.0 多 agent 架构）。把绘本简介 + N 张图 + 旁白 → 调 A 风格识别 + B 旁白量化（并行）→ 调 C 分镜设计 → 调 D 视频执行 → 汇总发飞书。**主 skill 只做调度 + 启动前 6 必问 + 路由，不直接跑分镜/视频**。触发词：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor]
    toolkit_role: picturebook-video-orchestrator
    version: 1.0.2
    breaking_changes_from_v1.0.1:
      - "Step 4 实测约束：≤3 个/批 仍 timeout（Pic3 实战 9 Clip D 卡在 6/9），改为最佳 2 个/批 + 主 agent 续跑模式"
      - "新增铁律 #55（v15.2 实战验证成功 · Pic3 9 Clip 0 错位）+ 铁律 #56（绘本场景对位检查前置）"
      - "新增 references/2026-06-07-pic3-welcome-validation.md（Pic3 Welcome 欢迎 9 Clip 实战数据）"
---

# picturebook-video · 绘本视频调度中枢（v1.0.2）

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
Step 4 · 调 D（可能 N 次重试 · 2 个/批 + 主 agent 续跑）
   ↓
Step 5 · 汇总 + 决定发不发飞书
```

**Step 0.5 · 绘本场景对位检查（v1.0.2 新增 · 铁律 #56）**

在调 C 之前，**主 agent 必跑**这步（不交子 agent）：

```python
# 用 native vision 抽每张图 t=0.5s 帧，验证：
# 1) 原图场景跟旁白对位（防 pic2 clip6 玩具房当 eat 翻车）
# 2) 收势页是否真的"全员集合"（防 pic2 clip8 误用图书馆当收势）
# 3) 文字是否清晰可读（防 pic2 clip1 文字消失）
```

**判断口诀**：
- ✅ 看到 1/3/5/9/...关键页的场景对位才进 Step 2
- ❌ 发现错位 → **不重做绘本**（绘本方已发布），**接受并标注**（Step 5 报告里说"clip6 玩具房 vs 旁白 eat 不对应，已接受现状"）

**Pic3 实战验证**（2026-06-07）：vision 抽 1/5/9 三帧确认场景对位 → 9 个 Clip 全对位 → 9/9 succeeded 0 错位。

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

**C 600s timeout 实战**（Pic3 2026-06-07）：C 写 9 个 JSON 跑了 600s 没写完主索引 → **主 agent 续写主索引**（用 Python 一次性聚合 clip1-9.json → storyboard-index.json）。

---

## Step 4 · 调 D · 视频执行

**⚠️ 实战约束（铁律 #50 · v1.0.2 强化）**：D 子 agent **禁止一次跑全部 N 个 Clip**。
- Pic2 实战（2026-06-06）：8 个 Clip 一次跑 = 600s timeout × 2
- Pic3 实战（2026-06-07）：D 跑 3 个/批 仍 timeout（6 个 Clip 用了 ~6 分钟，9 个=29 API call=timeout）= **最佳 batch = 2 个/批**
- **极限 = 1 个/批**（端到端验证）
- **C 子 agent 600s 内只能写 9 个 JSON + 聚合 + vision × 9 = 9 个 API call**——超出时主 agent 续跑

**主 agent 续跑模式**（D/C timeout 后 · Pic3 实战验证）：
1. D timeout → 主 agent 直接调 seedance.py 续跑**未提交的 Clip**（不重新调 D）
2. 续跑命令模板（pic3 实战）：
   ```bash
   set -a; source /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env; set +a
   for N in 7 8 9; do
     python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py create \
       --ref-images /path/${N}.jpg \
       --prompt "$(cat /path/clips/clip${N}-prompt.txt)" \
       --duration ${DURATION} --ratio 16:9 --resolution 720P \
       --model doubao-seedance-2-0-fast-260128 \
       --watermark false --generate-audio true \
       --download /path/v1-clip${N}-fixed.mp4 2>&1 | grep "Task ID"
   done
   # 再 wait 每个 task_id（用 shell 变量存）
   ```
3. **task_id 必存**到 `task_ids.txt`（铁律 #30 强化：D timeout 也要存已生成的 ID）

**D 必做 6 件事**（主 agent 必查）：
1. **不 --wait / 不 --download**（Pic2 实测 timeout）
2. 25 轮 × 15s 轮询
3. ffmpeg 抽帧（每秒 1 帧）
4. **vision_analyze 必须 native vision**（不调 mcp_zai_analyze_image）
5. ls -lh 验证（铁律 #30）
6. **单 Clip 端到端先验**（铁律 #50）—— 不一次跑全部，1 个 OK 再 2 个/批次

**D 翻车 → C 修复 → D 重跑**（铁律 #49 · C self_check 错位修复方向）：

| 翻车征兆 | C 修复方向 |
|---|---|
| 镜头一主体完全丢失 | 镜头一加约束"两兔必须完整可见"（不只是"切到全景"）|
| 文字消失/被吃 | 文字保留升级"锁定 top 1/6 画面不重绘" / 改用 `--image` 首帧模式钉死构图 |
| 末帧定格海报 | 末帧微动细化为"末帧 1s 必须含 ≥1 个动作元素"（不只写"画面继续微动"）|
| 末帧完全静止 5s | 同上 |
| 角色外观漂移 | 强化 @ImageN 绑定 + 主体定义加视觉特征详情 |
| task failed | 不重试 D，查 ark list 端点 |
| 角色闭嘴 vs 张嘴 | 接受（绘本调性 = 温柔内敛）|
| **绘本原图场景和旁白错位** | **不重做**！直接接受（绘本方已发布）—— Pic2 clip6 玩具房当 eat 教训 |

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

**Pic3 实战补充**（v1.0.2）：
- 9 个 Clip 全部 succeeded → 决定拼装+发飞书
- 拼接工具：ffmpeg concat demuxer + 旁白 BGM 混音（参考 [references/2026-06-07-pic3-welcome-validation.md](references/2026-06-07-pic3-welcome-validation.md) §"拼装"）
- **不主动抽帧发**（铁律 #29 强化：抽 4 帧 = 6×9 = 54 帧 = 主 agent 上下文污染）

## Step 4.5 · 实战验证 gate（重构/大版本发布前必跑 · 铁律 #51）

**触发条件**：本次任务是**重构/大版本优化/新子 agent 接入**——不是普通跑视频。

**反模式（2026-06-06 差点踩）**：evals 9 维度全胜就开 PR → Pic2 v1.0.0 实战 Clip 1 跑出 5/6 false（主体丢失 + 文字消失 + 末帧定格）。

**实战 gate 5 步**：

```
1. 跑 1 个 Clip 端到端（验证流程跑通）
2. 看视频：末帧是否画面微动？文字是否保留？角色是否完整？
3. 跑 1-2 个完整绘本（8-12 个 Clip 批量）出 mp4
4. 抽 2-3 个 Clip 抽帧自检（不只凭感觉）
5. 全部 OK → 才能开 PR
```

**实战 OK 定义**：
- 至少 1 个 Clip 跑通端到端（A+B+C+D 全跑）
- 至少 1 个 Clip 视频自检 self_check ≥5/6
- 至少 1 个 Clip 末帧画面**真的**微动（不是定格海报）
- 至少 1 个 Clip 文字**真的**完整保留（不是消失）

**实战翻车处理**：
- C self_check 错位（铁律 #49）→ 重发 C 改 prompt 措辞，**不**直接改 evals 评分标准
- D 批量 timeout（铁律 #50）→ 降级为单 Clip 端到端 + 2 个/批次（v1.0.2 强化）
- evals 9 维度全胜但实战翻车 → **evals 评分方法**本身要重写，**不是改 v1.0.0**

**不开 PR 的硬约束**（用户 2026-06-06 原话）：
- "我们都没有实测过，怎么能PR"——evals 通过 ≠ 实战通过
- 任何"看起来 OK"都不算实战 OK，**必须 mp4 视频目检 + 抽帧自检**

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
| C 子 agent 600s timeout | **主 agent 续写**主索引（用 Python 聚合 clip1-9.json → storyboard-index.json） |
| D 子 agent 600s timeout | **主 agent 续跑未提交 Clip**（shell + seedance.py） |
| D 子 agent 部分翻车 | 重发 C 改 prompt → 重发 D 跑该 Clip |
| D 子 agent 全部翻车 | 降级 v0.7.1+pic7 + 报告用户 |
| 用户中途打断 | 接受中断，保存当前状态 |
| **绘本原图场景和旁白错位** | **不重做**！接受现状 + Step 5 报告标注（绘本方已发布，强行改 = 不忠于原书） |

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

| 阶段 | 工具 | 产物 |
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
- ✅ Step 0.5 绘本场景对位检查（v1.0.2 新增）
- ✅ C/D 子 agent timeout 后续跑（v1.0.2 新增）

主 agent **不做**：
- ❌ 拼 prompt（那是 C 的事）
- ❌ 跑视频（那是 D 的事，除非 D timeout 续跑）
- ❌ 抽帧验证（那是 D 的事）
- ❌ 凭印象选节奏（那是 C 的事）

---

## 详细规范位置

- **v15 范式 prompt 4 段骨架**：见 C 子 agent `agents/storyboard-design/SKILL.md`
- **v15.1 长旁白拆分**：见 `references/长旁白拆分规范-v15.1.md`
- **节奏档位表**：见 C 子 agent `agents/storyboard-design/SKILL.md` "决策规则"
- **文字保留铁律 v1v2v3**：见 `references/绘本文字保留铁律-v1v2.md`
- **末帧 ≠ 定格海报**：见 `references/2026-06-06-pic2-mvp-validation.md`
| 视频交付不抽帧 | `references/视频交付工作流-不抽帧.md` |
| 重构根因 | `references/2026-06-06-v1-refactor-rationale.md` |
| **v1.0.1 实战 Pitfall** | `references/2026-06-07-v1.0.1-pitfalls.md`（2026-06-07 Pic2 Clip 8 收势节奏拖慢）|
| **v15 4 段骨架模板**（v1.0.3+pic12）| `references/v15-4段骨架-模板.md`（**用户根本性纠错**："底层核心 = prompt 写法结构"，模板化 v15 4 段，11 个变量必填，**主 agent 填变量 = 终稿 prompt**）|
| **v1.0.2 Pic3 Welcome 实战验证** | `references/2026-06-07-pic3-welcome-validation.md`（2026-06-07 Pic3 Welcome 9 Clip 实战 0 错位 · v15.2 铁律 #54 完整闭环 · C/D 续跑模式沉淀）|

---

## v0.7.1+pic7 → v1.0.0 → v1.0.1+pic10 → v1.0.2 变化清单

| 维度 | v0.7.1+pic7 | v1.0.0 | v1.0.1+pic10 | v1.0.2 |
|---|---|---|---|---|
| SKILL.md 行数 | 568 | ~200 | ~270 | ~280 |
| 主 agent 职责 | 干全部 | 只调度 | 只调度 | 只调度 + 场景对位 + 续跑 |
| 子 agent 数 | 0 | 4 | 4 | 4 |
| 节奏选档 | 凭印象 + 标版必跑 | 档位表强制 | v15.2 强化（不主动加镜）| 同 v1.0.1 |
| 朗读时长 | 凭语感 | B 子 agent 量化 | 同 v1.0.0 | 同 v1.0.0 |
| 末帧策略 | 标版 2-3s 静默 | 调性 × 系数 + 画面微动 | v15.2 收势约束 6s 3 镜头 | 同 v1.0.1 |
| 翻车处理 | 主 agent 自己改 prompt 重跑 | 报告回主 agent → 重发 C 改 | 同 v1.0.0 | + C/D 续跑模式 |
| 并行度 | 串行 | A+B 并行 | 同 v1.0.0 | + Step 0.5 场景对位 |
| 实战绘本 | 0 | Pic2（部分）| Pic2 8 Clip（v1.0.1+pic10）| **Pic3 9 Clip（v1.0.2 · 0 错位）**|

---

## 铁律清单（v1.0.2 精简版）

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
| 47（新）| D 子 agent 不 --wait / 不 --download（Pic2 实测 timeout）|
| **48**（新）| 主 agent 调度子 agent 必传 schema 完整 JSON（不传散文）|
| **49**（v1.0.0 实战新增）| 节奏公式 = 动作成本相加（不硬套模板·"Good afternoon" 1.5s 套 6-7s = 凭空加 4-5s 空镜 = 节奏拖慢）|
| **50**（v1.0.0 实战新增）| **未实战验证不能开 PR**（重构完成 + evals 100% ≠ 实战可用）|
| **51**（v1.0.0 实战新增）| **Cat v15 范式精准度迁移** = 拆 Clip 维度 = 语义块 + 拟声 = 故事动作音 + 画面先讲语义 + 末帧 = 故事动作停留 + 目标词重读窗口 |
| **52**（v1.0.0 实战新增 · 核心三控制）| **画面控制（clip_narrative 故事动作）+ 时间控制（节奏 = 动作成本相加）+ 声音控制（拟声 = 故事动作音 + 朗读强化读音 + 目标词重读窗口）** |
| **53**（v1.0.0+pic9 实战新增）| **末帧消化时间 ≥ 1s 标准 / ≥ 2s 收势** |
| **54**（v1.0.1+pic10 实战新增 · 2026-06-07 · v15.2 强化）| **节奏默认 = 朗读 + 末帧消化（不主动加镜头不加时长）**——"用户没说要 = 不要加" |
| **55**（v1.0.2+pic11 实战新增 · 2026-06-07）| **v15.2 铁律 #54 实战验证成功**——Pic3 Welcome 9 Clip 跑通：clip9 收势 6s 3 镜头**一次到位**（v15.1 套 11s 5 镜头翻车已彻底修复）；9/9 md5 唯一 0 错位（Pic2 6/8 错位教训已闭环）；C 自检 12/12 + D seedance 9/9 succeeded（**C 文本合规 = D 视频合规**，v1.0.0 错位已修复） |
| **56**（v1.0.2+pic11 实战新增 · 2026-06-07）| **绘本场景对位检查前置（Step 0.5）**——主 agent 在调 C 之前，**必**用 native vision 抽 1/3/5/9 等关键页 t=0.5s 帧验证原图场景与旁白对位。Pic2 clip6 玩具房当 eat 翻车教训：绘本方可能用"兔子+通用场景"模板画，**场景 ≠ 旁白**。**对位错则接受现状**（不重做绘本） |
| **57**（v1.0.3+pic12 实战新增 · 2026-06-07 · **底层核心 = prompt 写法**）| **v15 4 段骨架 = 模板 · 主体/动作/拟声/微动 = 变量**——**用户根本性纠错**："底层核心逻辑是提示词的写法结构，所有任何场景都是在这个结构上做微调"。**含义**：v15 4 段骨架（段 1 主体定义 / 段 2 分镜绑定 + 文字保留 / 段 3 分镜描述含拟声 / 段 4 风格 + BGM）= **固定的 4 段写法**，不是"每次从 0 拼"。**所有场景**（绘本/漫剧/故事/广告/动画）= **在模板上做变量微调**（不是"重写 prompt"）。**主 agent 拼 prompt 的职责**：C 子 agent 产"原料"（clip_narrative / time_breakdown / 文字位置 / 视觉特征 / 风格关键词）→ **主 agent 填 v15 模板变量 = 终稿 prompt**（保证 prompt 写法 100% 一致）。**模板沉淀**：见 `references/v15-4段骨架-模板.md`（v1.0.3+pic12 新增）。**判断口诀**："**v15 4 段 = 模板**；**主体/动作/拟声/微动 = 变量**" |
| **58**（v1.0.3+pic12 实战新增 · 2026-06-07 · **子 agent 减负**）| **A+B+D 主 agent 干 · 只 C 子 agent 干**——**用户纠错**："子 agent 执行时长 >> 主 agent" + "视频生成可以由主 agent 执行"。**修复方向**：A+B 改主 agent 干（纯计算/少量 vision，~1-2min/个）+ D 改主 agent 用 `seedance.py` 跑（实时决策不超时）+ **C 唯一子 agent**（看图产"原料" JSON，~5-8min ≤ 600s）。**根因**：子 agent 启动 + 上下文传递 + 多步 vision 调用 = 600s timeout 元凶。**Pic3 实战数据**（用全子 agent）：A 5min + B 8min + C 10min + D 10min = ~33min。**v1.0.3+pic12 改后**（A+B+D 主 agent 干）：A 1-2min + B 1-2min + C 5-8min + D 3-5min/批 = **~12-18min 节省 50%**。**D 退化为参考文档**（不调用）。**C 必做 1 件事**：产"原料" JSON（**不**写 prompt_draft 字段，由主 agent 拼）。**判断口诀**："**A+B+D = 主 agent 干 = 减 5x 时长**" |

## v1.0.2 实战对比（Pic2 vs Pic3 完整数据）

| 维度 | Pic2 (Please) | Pic3 (Welcome) | v15.2 改进 |
|---|---|---|---|
| 页数 | 8 | 9 | — |
| 场景对位 | 6/8 错位（玩具房当 eat）| 9/9 对位 | ✅ Step 0.5 拦截 |
| 节奏档位 | v1.0.1 修复后全对 | 全对 | ✅ 铁律 #54 闭环 |
| clip8/9 收势时长 | v1 11s 5 镜头→v2 6s 3 镜头 | **6s 3 镜头**（一次到位）| ✅ 铁律 #54 + #55 实战 |
| D 任务数 | 8 succeeded | 9 succeeded | ✅ |
| md5 错位 | 6/8 | **0/9** | ✅ 主索引聚合修复 |
| C self_check | 9/9（v1.0.0 错位·v1.0.1 修复）| 12/12 | ✅ 铁律 #55 实战 |
| C 子 agent timeout | 无 | timeout 但 9/9 JSON 写完 | ✅ 主 agent 续写主索引 |
| D 子 agent timeout | 无 | 600s 时 6/9 done | ✅ 主 agent 续跑 3/3 |
| 总时长 | 47s | **45s**（用户 TTS 估算）| ✅ 匹配 |
| 总镜头数 | 33 | 34 | — |

**详细实战数据**：见 [references/2026-06-07-pic3-welcome-validation.md](references/2026-06-07-pic3-welcome-validation.md)

---

## v1.0.0 实战翻车决策树（Pic2 8 Clip 实战沉淀）

**实战发现的核心矛盾**：C 子 agent self_check 9/9（**仅查文本合规**）≠ D 子 agent 实战 self_check 6/6（**查视频合规**）——C 子 agent 看不到 seedance 实际跑出来效果。

**v1.0.2 实战修正**（Pic3 9 Clip）：C self_check 12/12 + D seedance 9/9 succeeded = **C 文本合规 = D 视频合规**（v1.0.0 错位已修复，原因是 v1.0.1+pic10 的实战校准措辞补齐了 seedance 实战细节）。

**主 agent 翻车处理**：

| 翻车征兆 | 主 agent 决策 | 不该做什么 |
|---|---|---|
| frame_01 角色完全丢失 | **重发 C 改 prompt**（镜头一 1.5s）| 不擅自重跑 D |
| 文字消失 / 被吃 | **重发 C 改 prompt**（v3 措辞升级）| 不擅自重跑 D |
| 末帧定格海报 | **重发 C 改 prompt**（画面微动具体化）| 不擅自重跑 D |
| frame_03 镜头未推到特写 | **重发 C 改 prompt**（clip_narrative 必填）| 不擅自重跑 D |
| task failed | 不重试 D | 查 ark list 端点 |
| 角色闭嘴 vs 张嘴 | **接受**（绘本调性 = 温柔内敛，铁律 #42）| 不修 |
| evals 100% 命中 | **不**直接开 PR | **必须实战验证**（铁律 #49）|
| C 子 agent 600s timeout | **主 agent 续写主索引**（Python 聚合 clip1-9.json）| 不重发 C |
| D 子 agent 600s timeout | **主 agent 续跑未提交 Clip**（shell + seedance.py）| 不重发 D |
| **绘本原图场景错位** | **接受现状**（绘本方已发布）| **不重做绘本** |

**核心原则**：C 子 agent self_check 通过 ≠ 视频实际通过。**实测胜于 evals**。

## v1.0.0 实战 Pitfall 库

详见 [references/2026-06-06-v1-real-pitfalls.md](references/2026-06-06-v1-real-pitfalls.md)（6 个 Pitfall 库 + 修复优先级 + v1.1 待办）。

**6 个 Pitfall 速查**：

1. **画面在配音**（反 Cat v15 范式）→ C 子 agent 必填 clip_narrative 字段
2. **短档镜头一 1s 不够时间** → 短档 1-1-3-1 → 1.5-1-3-1.5
3. **C 子 agent self_check 只查文本合规** → C 必填 seedance_visual_checklist
4. **实战翻车不擅自重跑 D**（铁律 #45）→ 报回主 agent
5. **未实战验证不能开 PR**（铁律 #49）→ 实战拍板后再开
6. **视频交付不抽帧**（铁律 #29 强化）→ D 不发飞书 + 主 agent 不主动抽帧发

| **49**（新 · 2026-06-06 实战）| **C self_check ≠ seedance 实际输出合规** — C 检查"prompt 文本合规"，但不验证"seedance 是否真跑出对应效果"。**实战验证**：Pic2 Clip 1 C 9/9 ✓ → D 跑出来 5/6 false。**修复方向**：① 末帧微动细化为"末帧 1s 必须含 ≥1 个动作元素"（不只写"画面继续微动"）② 文字保留升级"锁定 top 1/6 画面不重绘"或改用 `--image` 首帧模式钉死构图 ③ 镜头一"切到全景"加约束"两兔必须完整可见" |
| **50**（新 · 2026-06-06 实战）| **D 子 agent 禁止一次跑全部 N 个 Clip** — Pic2 实测 D 跑 8 个 Clip × 提交+轮询+下载+抽帧+vision × 4 帧 = 600s 直接 timeout。**正确做法**：D 先跑 1 个 Clip 端到端验证，OK 后再批量；批量时限制 ≤3 个/批次（避免 timeout）|
| **51**（新 · 2026-06-06 实战）| **开 PR 前必做实战验证** — 用户原话："现在肯定不能跑 PR，我们都没有实测过，怎么能PR。" 任何重构/优化完成后，**先跑 1-2 个真实绘本出 mp4 看实际效果** → OK 才能开 PR。evals 验出来的 = prompt 草稿质量 ≠ 视频实际质量。**反模式**：evals 9 维度全胜就开 PR（Pic2 v1.0.0 实战翻车就是这个反模式差点触发）|
| **52**（新 · 2026-06-06 实战）| **节奏公式 = 动作成本相加，不是模板套数** — 用户原话："两秒就把话讲完了，那剩下那两秒是不是把节奏给拖慢了呢？"。**核心洞察**：每个节奏数字 = 该镜头动作/朗读/消化的实际成本（不是凭空加的）。`总时长 = 朗读 + 消化（≈朗读 × 1-2 倍）`。强行套模板（如 "Good afternoon" 1.5s 朗读套 6-7s 节奏 = 凭空加 4-5s 空镜 = 节奏拖慢）。**反模式**：把"标版" / 节奏公式当模板（v0.7.1+pic7 时代 v15.1 标版 2-1-3-3-3 套所有 Clip = 浪费）。**正确做法**：见 [references/2026-06-06-rhythm-action-cost.md](references/2026-06-06-rhythm-action-cost.md) — 节奏档位表 4 档（极短/短句/中句/长句），每档时长 = 该档朗读 + 消化实际成本求和 |
| **53**（新 · 2026-06-06 实战）| **Cat v15 范式精准度迁移** — 用户原话："对画面的镜头控制，画面的内容控制，特别是对clip做拆分的时候，那种控制，非常精准"。**Cat v15 范式精准 4 点**（v1.0.0 实战修复方向）= ① 拆 Clip 维度 = **语义块**（不是时间块）② 拟声 = **故事动作音**（pat 一响 = 猫掌落地，不是装饰音）③ 画面 vs 朗读 = **画面先讲语义，朗读强化读音**（不是"嘴巴半张开说 X"）④ 末帧 = **本 Clip 故事动作停留 + 目标词重读窗口 + 画面微动**。**Pic2 clip_narrative 必填**：每 Clip 1 句话描述本 Clip 故事动作，绑定目标词语义。详见 [references/2026-06-06-cat-v15-paradigm-precision.md](references/2026-06-06-cat-v15-paradigm-precision.md) |

---

## 相关 skill

- **子 agent A**：`storyboard-style`（风格识别）
- **子 agent B**：`storyboard-narration`（旁白量化）
- **子 agent C**：`storyboard-design`（分镜设计）
- **子 agent D**：`video-executor`（视频执行）
- **工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`
- **兄弟 skill**：`picturebook-creator`（绘本创作）/ `seedance2.0-tool`（视频底层工具）
