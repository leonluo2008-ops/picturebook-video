---
name: picturebook-video
description: 绘本转儿童动画视频一站式调度 skill（**v1.0.3+pic12** · 4 子 agent + 主 agent 减负架构 + Pic4 No 不绘本实战验证）。把绘本简介 + N 张图 + 旁白 → **Step 0.5 场景对位检查** → **Step 1 启动前 7 必问（含 #7 调性预审）** → 调 A 风格识别 + B 旁白量化（主 agent 干 · 并行）→ 调 C 分镜设计（唯一子 agent · 产"原料" JSON · **不写 prompt_draft**）→ 主 agent 填 **v15 4 段骨架模板 11 变量 = 终稿 prompt** → 调 D 视频执行（**主 agent 干 · ≤2/批 + 续跑模式** · uguu 兜底路线）→ 汇总发飞书（**附完整证据链防 send_message 串扰**）。**v1.0.3+pic12 实战新增**：v5 节奏公式（朗读完最低 3s + 末帧静默 ≥ 2s）+ v6 整数时长铁律（seedance 不生成小数时长）+ 彩色文字全程可见铁律（领读锚点不可一闪而过）+ uguu 兜底路线（chevereto 挂时备用）+ **9 条新铁律**（#63-#71）。**触发词**：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent, picturebook, v15-template, fill-v15, uguu-fallback, send-message-evidence, integer-duration, text-anchored-reading]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool]
    toolkit_role: picturebook-video-orchestrator
    version: 1.0.3
    breaking_changes_from_v1.0.2:
      - "**9 条新铁律（#63-#71）**——Pic4 No 不绘本实战沉淀（v3 情绪温柔化 + v5 节奏两步推导 + v6 整数时长 + 彩色文字全程可见）"
      - "**uguu 兜底路线**——chevereto 图床挂了时备用（uguu.se + 直接 curl 调 ark API）"
      - "**send_message 防串扰**——发视频前必本地 stat+md5+消息里显式打文件名+md5+task_id"
      - "**fill_v15 模板脚本统一**——fill_v15_v3.py / v5.py / v6.py 归一为 scripts/fill_v15_template.py（含 _parse_en_color 数据清洗）"
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

## Step 1 · 启动前 7 必问（必跑）—— 6 必问 + #7 调性预审（v1.0.3+pic12 铁律 #70 强化）

**铁律（用户多次纠错）**：不擅自替用户决定。**但 7 问都走"我打算 X 因为 Y"报你**——你只回"停"或"换 X"就调整（不主动开问卷）。

| # | 必问项 | 默认值 | 为什么这么定 |
|---|---|---|---|
| 1 | **画幅比例** | 16:9 | 抖音/视频号/B 站主流；小红书可改 3:4 |
| 2 | **单 Clip 时长** | **v6 整数公式**（短句 6s / 中句 7s / 长句 8s / 极短 5s）| 按 B 子 agent 算出的朗读时长 + **整数**（铁律 #72：seedance 不生成小数）+ 末帧静默 ≥ 2s（铁律 #74 v5 公式）|
| 3 | **切分方式** | 按图（每张图 1 Clip） | 默认；>15s 走 v15.1 语义块 |
| 4 | **调性** | 等 A 子 agent 识别 | 主 agent 不擅自定 |
| 5 | **范式** | **v6 模板**（v15 4 段 + 文字持续可见段）| 铁律 #77 v6 = 5 段结构 |
| 6 | **约束** | 末帧 ≠ 定格海报 / 文字保留 v3 / 不写隔离句 / **彩色文字全程可见+微动画** | v0.7.1+pic7 沉淀 + 铁律 #73 |
| **7**（v1.0.3+pic12 铁律 #70 新增）| **调性预审**（绘本方选图情绪 vs 用户期望情绪）| **差距大 = 选材问题，建议换绘本** | 见 [references/2026-06-07-pic4-no-v6-final.md](references/2026-06-07-pic4-no-v6-final.md) "v6 三大核心铁律" |

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

**v1.0.2 改：B 改主 agent 干**（铁律 #58）。B 跑在主 agent 上下文里，纯计算+少量 vision，~1-2 min 写完 narration-quantization.json。

```python
# B 在主 agent 干（不调子 agent）
# 1. 读旁白表（已知）
# 2. 1.4 词/秒 兜底公式（无 TTS 音频时）· 或用用户提供 TTS 实测
# 3. 按节奏档位表算每行 tier / shot_count / total_duration_seconds
# 4. 写 narration-quantization.json
```

**⚠️ 串扰风险（2026-06-07 用户警告）**：B 放主 agent 干可能受主 agent thinking 中断/上下文污染影响。**Pic4 暂未验证稳定性**——D 跑完后回看 B 算的档位 vs C 选节奏是否 100% 匹配，如果有错位 = B 串扰实锤，**回滚 B 到子 agent**（v1.0.0 老架构）。

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
| **v1.0.2 Pic4 No 不 实战验证** | `references/2026-06-07-pic4-no-validation.md`（2026-06-07 Pic4 No 不 9 Clip 实战 0 错位 · v1.0.2 完整流程首次端到端跑通 · C 不写 prompt_draft + 主 agent 填 v15 模板 + B 串扰风险警告 · 铁律 #59-#65）|
| **Pic4 No v5 节奏公式重构**（用户两步推导）| `references/2026-06-07-pic4-no-v5-rhythm-formula.md`（2026-06-07 Pic4 v3 跑通后用户反馈"末帧仍太短"，原话两步推导：① 朗读完最低 3s ② + 2s 末帧静默。v5 公式：5/6/7/8s 四档 · 末帧静默 2.9-3.8s · 镜头数 2-3 · 微动元素 4-6 · 铁律 #69）|
| **飞书视频交付与目检反例排查** | `references/视频交付与目检反例排查.md`（2026-06-07 Pic4 clip1 用户目检反例沉淀 · vision_analyze 4 步排查法 · 4 个可能根因 · 完整证据链交付模板 · 决策树）|
| **Pic4 v6 最终实战沉淀** | `references/2026-06-07-pic4-no-v6-final.md`（2026-06-07 Pic4 v6 完整闭环：v1 严肃 → v3 温柔化 → v5 节奏两步推导 → v6 整数+文字全程可见 · 5 版迭代对比表 · v15 4 段→v6 5 段结构升级 · 铁律 #72-#79）|
| **uguu 兜底路线** | `references/uguu-fallback-route.md`（2026-06-07 chevereto 挂时备用图床 · uguu.se + 直接 curl 调 ark API · 4 段 v3/v5 实战验证 · 3 步标准流程 · 铁律 #71）|
| **send_message 防串扰** | `references/send-message-evidence-chain.md`（2026-06-07 Pic4 clip1 send_message 串扰实战 · 4 步排查法 · 完整证据链交付模板 · 飞书 client bug 排查 · 铁律 #76）|
| **v15 填模板脚本** | `scripts/fill_v15_template.py`（v1.0.2 主 agent 必用 · 9 段 prompt 100% 一致 · 0 行 drift · Pic4 实战 5 min 写完 9 段 · **含 _parse_en_color 数据清洗** 修 Pic4 翻车 · **v1.0.3+pic12 待统一 v3/v5/v6 模板变体**）|

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
| **59**（v1.0.3+pic12 实战新增 · 2026-06-07 · **Pic4 实战沉淀**）| **C 子 agent SKILL.md schema 强制不写 prompt_draft**——v1.0.3+pic12 commit 描述里说"C 不写 prompt_draft"，但 SKILL.md 上面的「输入/输出 schema」和「示例」段落**还写 prompt_draft 字段**。Pic4 修复：重写 C 子 agent SKILL.md 的「输出 schema」+「示例」段落，**明确标注"v1.0.3+pic12 新版 · 不写 prompt_draft"**。**根因**：下个 C 子 agent 看到 schema 引导会直接错（schema 是 agent 的第一反应源，不是红线 #9）。**同时**：把 `scripts/fill_v15_template.py` 放进 picturebook-video/scripts/ 目录作为标准填模板工具（9 段 prompt 100% 一致 = 0 行 drift）|
| **60**（v1.0.3+pic12 实战新增 · 2026-06-07 · **B 串扰风险**）| **B 放主 agent 干可能受干扰**——用户 2026-06-07 警告："把B也放入主agent执行的话，可能会受干扰，可能会出现不稳定的情况"。**风险**：主 agent thinking 中断/上下文污染可能影响 B 量化结果（9 段旁白量化在主 agent 上下文里跑 = 不隔离 = 易污染）。**Pic4 暂未验证稳定性**——D 跑完后**必**回看 B 算的档位 vs C 选节奏是否 100% 匹配，如果有错位 = B 串扰实锤，**回滚 B 到子 agent**（v1.0.0 老架构）。**判断口诀**："**D 跑完验证 B 输出 vs C 节奏档位 = 100% 匹配才确认 B 干稳定**" |
| **61**（v1.0.3+pic12 实战新增 · 2026-06-07 · **vision_analyze 汇报流程**）| **vision_analyze 批量调用后必先汇报再下一步**——Pic4 实战翻车：在跑 vision_analyze × 4（2/4/6/8）时**中断**，agent **没在响应里汇报 4 张图的结果**就跳到写 style-recognition.json，用户反馈"2/4/6 都没看到识别成功"。**修复**：每次 vision_analyze 批量调用结束后，**先简短汇报 "X/Y 张已识别"再开始下一步**；vision_analyze 失败的图要明确标 ❌ 不掩盖。**判断口诀**："**vision batch 完 = 先汇报结果 → 再写 JSON**" |
| **62**（v1.0.3+pic12 实战新增 · 2026-06-07 · **fill_v15 模板数据清洗**）| **C 子 agent 输出的 text_position.en_color 是结构化数据，不能直接拼进 prompt**——Pic4 clip1 实战：`tp.en_color = "N=鲜艳红色 / o=橙红色"` 直接拼 f"{en_color_raw} 英文" 出现"1/6 画面的N=鲜艳红色 / o=橙红色 英文"语法断裂。**修复**：`scripts/fill_v15_template.py` 加 `_parse_en_color()` 函数，**只取主色名 + 保证"色"字结尾**（"N=鲜艳红色 / o=橙红色" → "鲜艳红色色"）。**根因**：C 子 agent 倾向把字段填成结构化数据便于检索，但 prompt 模板需要的是**流畅词组**不是结构化标签。**新约定**：C 输出的所有"颜色/位置/特征"字段都应该是**句法片段**（可直接拼入句子的词组），不是**键值对**。**判断口诀**：**"C 产原料 ≠ prompt 词组 · 主 agent 必清洗"** |
| **63**（v1.0.3+pic12 实战新增 · 2026-06-07 · **vision 和人眼观感不一致风险**）| **mp4 → 飞书附件 → 用户手机 = 渲染链不可控**——Pic4 clip1 跑通后 vision_analyze 多次确认视频内容是 No（小熊 Stop 手势 + No/不能），**但用户反馈"看到的是 Welcome"**。**可能的根因（未实锤）**：① 飞书 client 渲染 bug ② 附件预览显示成了历史 pic3 视频 ③ 用户看的是 pic3 历史消息 ④ seedance 实际生成跟 prompt 不一致（vision 看花眼）。**修复方向**：① 主 agent 每次发飞书**附完整证据链**（文件名 + md5 + task_id + 原图 + prompt 文字）让用户能 100% 验证 ② 视频交付不只发飞书，**同时落地磁盘 + 飞书云盘**，用户可从云盘二次下载验证 ③ **vision_analyze 跟人眼观感不一致时，以人眼为准**（vision 是辅助不是真理）。**判断口诀**：**"vision 看多帧 ≠ 用户看到的就是这个"** |
| **64**（v1.0.3+pic12 实战新增 · 2026-06-07 · **B 干 magic number 必标注依据**）| **B 旁白量化的系数（0.71 / 0.95 / 2.14 / 2.86）必须标注公式来源**——Pic3 + Pic4 实战中 B 干多次出现"0.71 系数""0.95 系数""2.86 系数"等 magic number，**没有来源** = 主 agent 凭印象拍板。**风险**：下次不同绘本跑出来的 B 输出可能 magic number 漂移。**修复方向**：① B 干 narration-quantization.json 每个 silence_coefficient / silence_rationale 必填**公式来源**（"朗读 × 0.71 系数 = 0.6 系数 × 1.2 调性调整"这种链式推导）② 主 agent 必查 B 输出是否有 rationale 字段，**没有就拒绝 B 输出** ③ 沉淀标准公式到 `references/旁白朗读时长计算.md`（已有文档但要补"系数计算链"）。**判断口诀**：**"B 输出无 rationale = 主 agent 拒绝用"** |
| **65**（v1.0.3+pic12 实战新增 · 2026-06-07 · **单 Clip 端到端验证发现的内容-渲染不一致**）| **发飞书前单 Clip 端到端验证时，要用户目检 = 必经环节**——Pic4 clip1 跑通后 vision 自检全过但用户目检发现"内容是 Welcome"。**修复方向**：① 单 Clip 跑通 → 不直接发"继续跑剩下 8 段"，**先等用户目检确认** ② 主 agent 必说"我打算：发您单 Clip → 等您目检 → OK 再批量"。**反模式**：单 Clip 跑通就接着批量跑（Pic4 v1.0.2 实战差点触发）。**判断口诀**：**"单 Clip 端到端 = 等用户目检 = 不批量跑"** |
| **66**（v1.0.3+pic12 实战新增 · 2026-06-07 · **绘本情绪基调 = 输入约束，不是 skill 能修的**）| **v15 模板"表情=变量"可驱动 seedance 改表情，但改不了画面骨架**——Pic4 No 绘本 9 段图本身就是"严肃警告"风格（棕熊 Stop 手势+悬崖警告牌+两猫打架+灰机器警告三角），**v15 段 1 主体定义的"表情"变量**可以驱动 seedance 在视频里把"严肃"改成"慈爱/温柔坚定/担心/保护"（Pic4 v3 prompt 9 段手写实战 = 把 5 段负面情绪 100% 替换为温柔），**但改不了**"悬崖警告牌" → "远方风景"。**根因**：seedance 是图生视频，**原图定了视觉骨架**，prompt 只能调"动作/光线/表情/镜头"幅度，不能换场景。**绘本情绪基调** = **绘本方选图时定**的输入约束，**不是 skill 能修的**。**修复方向**：① **绘本选材时必问调性**（启动前 6 必问加 #7 调性预审——绘本方选图情绪 vs 用户期望情绪是否一致）② v15 段 1 表情变量是 **"温度调节器"**（严肃↔温柔），不是"换场景器" ③ 接受现状判定：**绘本方用"威胁"画"为什么不能"** vs **理想 "温柔坚定"** 的差距 = **绘本选材问题**——选材阶段解决，不是 prompt 阶段。**判断口诀**：**"v15 表情变量 = 温度调节器 ≠ 换场景器 · 调性错位 = 选材问题"** |
| **67**（v1.0.3+pic12 实战新增 · 2026-06-07 · **用户对绘本情绪基调的反馈必追问根因**）| **当用户说"情绪不对"时，主 agent 必追问"严肃 vs 温柔的差距是大还是小"**——Pic4 No 绘本 v3 重设计实战中，用户**两轮反馈**才让根因浮出：第一轮"情绪太严肃" → 第二轮"可以通过提示词控制表情" → 才点出 v15 段 1 表情变量的能力。**反模式**：用户说"情绪不对"立即给方案（不追问）→ 给的方案可能不解决根因（v3 实战差点触发——用户原话"不要给我相邻概念"）。**修复方向**：① 用户提"情绪"反馈时必先**情绪诊断表**（9 段每段的严肃/温柔/恐吓判定）② 必问"绘本方选图情绪 vs 你期望情绪差距是大是小" ③ 差距小 → v15 表情变量"温度调节"可救；差距大 → 选材问题。**判断口诀**：**"用户说情绪不对 = 先诊断 + 追问差距大小 = 再给方案"** |
| **68**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v3 重设计 = 必重发 C 子 agent**）| **prompt 重设计（含表情/动作/末帧/风格四联动）= 重发 C 子 agent，主 agent 不手写 9 段 prompt**——Pic4 No 绘本 v3 实战中，主 agent 第一次越界：手写 9 段 v3 prompt（re.sub 批量替换 v1 prompt 加 soften + 占位段 + style 词），用户直接纠错"**写 prompt 应该让子 agent 去做吧**"。**反模式**：① 主 agent 用 re.sub/正则批量改 prompt（容易破坏结构 + 拼出语法断裂）② 主 agent 手写 9 段 prompt 看起来"快"但**违反"看图产分镜"是 C 的核心职责**（v15 段 1 表情 = vision 分析后决定，不是主 agent 凭印象）。**修复方向**：① 用户提"重设计"或"再跑一版"时，**主 agent 必重发 C**（不是手写）② 重发 C 时 brief 必含"v3 设计目标"（表情软化方向 + 动作软化方向 + 末帧软化方向 + style 词追加）③ C 必**重新看 9 张图**（vision_analyze 1-9.jpg）验证原图严肃程度，软化幅度合理（不能完全脱离原图）④ 主 agent 拿到 C v3 JSON 后**走 fill_v15_v3.py**（或修改 fill_v15_template.py 加 v3 入口）填 9 段终稿 prompt。**判断口诀**：**"prompt 重设计 = 重发 C · 不主 agent 手写"** |
| **69**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v5 节奏公式 · 用户两步推导**）| **总时长 = 朗读完最低 3s + 末帧静默 ≥ 2s（用户底线）**——Pic4 No 绘本 v3 跑通后用户反馈"末帧仍然太短"，原话两步推导：①"拆解镜头过后，把旁白的时长包含在里面，3秒是可以把这个旁白讲完的。那么说我们最低就是3秒。" ②"再增加我们预留的用户消化、读者消化的时长，可能要预留2秒。"。**v5 公式**：极短档 5s（0.7s 朗读 + 3s 起步 + 2s 静默）· 短句档 6s（2.1s 朗读 + 4s 起步 + 2s 静默）· 中句档 7s（2.9s + 5s + 2s）· 长句档 8s（3.6s + 6s + 2s）· **末帧静默 2.9-3.8s**（全部 ≥ 2s 底线）· **总时长 56s**（v3 48s +8s）。**与 v3 对比**：末帧静默从 1.5-2.5s 升到 2.9-3.8s（**末帧微动必填 4-6 元素**），镜头数从 3-4 减到 2-3（铺垫"建立+跃入"合并）。**修复方向**：① B 干 narration-quantization.json **silence_rationale 必填**"v5 公式步骤 2 用户底线 ≥ 2s"（铁律 #64 强化）② 主 agent 收到 B 输出后**必查 silence_recommendation_seconds ≥ 2s**（不达 = 重发 B）③ C 干 end_frame_microaction.specific_motion 必填 4-6 个微动元素（2-4s 静默时间有持续微动 = 不定帧）。**判断口诀**：**"v5 = 朗读完最低 3s + 末帧静默 ≥ 2s"** · **"末帧静默 < 2s = 翻车征兆"** · **详细实战数据**见 `references/2026-06-07-pic4-no-v5-rhythm-formula.md` |
| **70**（v1.0.3+pic12 实战新增 · 2026-06-07 · **绘本情绪基调 = 选材约束 · v15 表情变量是温度调节器不是换场景器**）| **v15 段 1 表情变量 ≠ 改场景**——Pic4 No 绘本 v3 实战：原图是"棕熊 Stop 手势+悬崖警告牌+两猫打架+灰机器警告三角"（严肃警告），v3 prompt 把 5 段负面表情软化为"慈爱/温柔坚定/担心/保护"，**但改不了**"悬崖警告牌 → 远方风景"。**根因**：seedance 是图生视频，**原图定了视觉骨架**，prompt 只能调"动作/光线/表情/镜头"幅度，不能换场景。**v15 段 1 表情变量 = 温度调节器**（严肃↔温柔），**不是换场景器**。**绘本情绪基调 = 选材约束**（绘本方选图时定），**不是 skill 能修的**。**修复方向**：① 启动前 6 必问加 #7 调性预审（绘本方选图情绪 vs 用户期望情绪是否一致）② 差距小 → v15 表情变量"温度调节"可救；差距大 → 选材问题。**判断口诀**：**"v15 表情变量 = 温度调节器 ≠ 换场景器 · 调性错位 = 选材问题"** · **"绘本方用威胁画为什么不能 vs 理想温柔坚定 = 选材问题 = 选材阶段解决"** |
| **71**（v1.0.3+pic12 实战新增 · 2026-06-07 · **chevereto 挂了用 uguu + 直接 curl 调 ark API 兜底**）| **seedance.py 硬编码 chevereto = 单点故障**——Pic4 v1 跑通后 chevereto 图床挂了（curl 6 次全 timeout），seedance.py create 内部走 chevereto 上传 = 所有 seedance 调用全失败。**uguu 兜底路线**：① 上传图片到 `https://uguu.se/upload.php`（multipart field 名 `files[]` 带方括号，**不是** `file`）→ 拿 `files[0].url`（直链 `n.uguu.se`）② 直接调 ark API `POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks`（带 Bearer token + JSON body）③ 等 succeeded → 从 `content.video_url` 下载（用 urllib 不用 curl，URL 跟 X-Tos-Signature 时效约 24h）④ 已实测 wrapper：`uguu_ark_wrapper.py`（一次性跑 1 段）+ `run_v3_clip23.py`（批量跑 2 段）跑通。**修复方向**：① 未来 seedance.py 改支持多图床（chevereto + uguu 切换）② 兜底脚本纳入 `seedance2.0-tool/scripts/` 目录（见 `references/public-file-hosting-fallback.md` 已沉淀）③ 主 agent 跑视频前**不依赖** seedance.py 单一图床。**判断口诀**：**"chevereto 挂了 = uguu 兜底 = 直接 curl 调 ark API"** |
| **72**（v1.0.3+pic12 实战新增 · 2026-06-07 · **seedance 整数时长铁律**）| **seedance 不生成小数时长**（用户 2026-06-07 原话）——"生成的实际上是六秒，模型不会生成小数点最后的，比如说五点五秒，它只要超出了五秒，比如五点一秒，它肯定就生成了六秒，所以计算时长的时候必须是整数，精确到整数，没有小数点。" **根因**：seedance API 实际生成时长 = ceiling(设计时长) = 整数。**Pic4 v3 翻车实战**：v3 设计 5.5s 短句档 → 实际跑 6s → 5.5s 装不下 6s 实际内容 → 镜头被压缩 → 末帧静默才 1.5s（远不够 2s 底线）。**修复方向**：① **设计时长必须 = 整数**（5/6/7/8/9/10），**不能用 5.5/4.5/6.5** ② C 子 agent time_breakdown.end_time 必填整数结尾 ③ B 子 agent total_duration_seconds 必填整数 ④ 验证脚本：v6 公式 = 极短 5s / 短句 6s / 中句 7s / 长句 8s（v5 设计 5.5s 错 → v6 全整数对）。**判断口诀**：**"seedance 时长 = ceiling(设计) = 整数"** · **"5.5s → 6s 实跑 = 0.5s 浪费 = 镜头被压缩"** |
| **73**（v1.0.3+pic12 实战新增 · 2026-06-07 · **彩色文字全程可见铁律**）| **领读绘本彩色文字 = 领读锚点，不是装饰**（用户 2026-06-07 原话）——"彩色文字没有保持，一闪而过就没有了，用户根本看不清。大多数情况下，彩色文字可以更长时间的展示，或者说一直出现在画面中都是可以的，当然最好能够给它设计一些动画，这个彩色文字是最好的。你要知道，领读绘本彩色文字参考图片中的彩色文字实际上是很重要的。" **根因**：v3-v5 prompt 写"文字位置锁定在顶部 1/6 画面不要重新生成"——seedance 实际跑**只在前 1-2s 保持**，之后 4-6s 文字消失 = 失去领读锚点。**修复方向**：① 文字**全程可见**（从 t=0 到 t=末帧 5-8s）② 文字有**微动画**：每字轻微呼吸式明暗交替（0.5s/次）+ 字符顺序浮现（按朗读节奏 No→no→X，0.3s/字）③ 颜色+字体+位置全程锁定 ④ v15 模板**新增"文字持续可见段"**（5 段变 6 段结构）⑤ C 子 agent 必填 `text_visibility` 字段（full_clip_visible + micro_animation + position_locked + color_locked）⑥ 主 agent 填 v15 模板时**必加文字持续可见段**（scripts/fill_v15_v6.py 已实现）。**判断口诀**：**"领读绘本文字 = 领读锚点 · 全程可见 + 微动画 = 必填铁律"** |
| **74**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v5 节奏公式 = 用户两步推导**）| **总时长 = 朗读完最低 3s + 末帧静默 ≥ 2s**（用户 2026-06-07 原话两步推导）——"拆解镜头过后，把旁白的时长包含在里面，3秒是可以把这个旁白讲完的。那么说我们最低就是3秒。" + "再增加我们预留的用户消化、读者消化的时长，可能要预留2秒。那么说这个视频可能就是5秒钟。" **v5 公式**：极短档 5s（0.7s 朗读 + 3s 起步 + 2s 静默 = 末帧静默 3.8s）· 短句档 6s（2.1s + 4s + 2s = 2.9s）· 中句档 7s（2.9s + 5s + 2s = 3.1s）· 长句档 8s（3.6s + 6s + 2s = 3.4s）。**修复方向**：① B 子 agent silence_rationale 必填"v5 公式步骤 2 用户底线 ≥ 2s"（铁律 #64 强化）② 主 agent 收 B 输出必查 silence_recommendation_seconds ≥ 2s（不达 = 重发 B）③ C 子 agent end_frame_microaction.specific_motion 必填 4-6 个微动元素（2-4s 静默时间有持续微动 = 不定帧）④ **整数时长铁律**结合（铁律 #72）：v5 公式本身就是整数 = 设计 = 实跑 = 0 浪费。**判断口诀**：**"v5 = 朗读完最低 3s + 末帧静默 ≥ 2s"** · **"末帧静默 < 2s = 翻车征兆"** |
| **75**（v1.0.3+pic12 实战新增 · 2026-06-07 · **fill_v15 模板脚本 = 标准工具**）| **`scripts/fill_v15_template.py` 是主 agent 拼 prompt 的标准工具**——v1.0.2 写就了，但 v3/v5/v6 实战都是临时写 fill_v15_v3/v5/v6.py。**Pic4 实战教训**：每次新增 v3/v5/v6 模板变体都新建一个文件（v1.0.2 → v1.0.3+pic12 共 4 个版本），导致脚本碎片化。**修复方向**：① 统一为 `scripts/fill_v15_template.py`，通过参数 `--version v3|v5|v6` 切换模板变体 ② **含 _parse_en_color 数据清洗函数**（铁律 #62 沉淀：text_position.en_color 必清洗为"主色名+色字结尾"）③ 模板版本号 = JSON 文件后缀（clip1-prompt-v3.txt / clip1-prompt-v5.txt / clip1-prompt-v6.txt）④ 主 agent 必用脚本填，不手写 9 段 prompt（防铁律 #68 主 agent 越界）。**判断口诀**：**"主 agent 填模板 = scripts/fill_v15_template.py · 不手写"** |
| **76**（v1.0.3+pic12 实战新增 · 2026-06-07 · **send_message 防串扰铁律**）| **发飞书视频附件 = 必附完整证据链**——Pic4 clip1 实际生成正确（md5 95323c4e 验证 No 内容）但首次 send_message 用户看到"Welcome"视频（send_message 串扰 / 飞书 client bug / 用户看历史消息）。**根因未实锤**但**修复路径已定**：① **发视频前必本地 stat+md5 校验**（终端 ls -lh + md5sum）② **消息里显式打 文件名 + md5 + task_id + seed + 时长**（让用户能 100% 验证）③ **同时落地磁盘 + 飞书云盘**（用户可从云盘二次下载验证）④ **vision_analyze 跟人眼观感不一致时，以人眼为准**（vision 是辅助不是真理）。**Pic4 验证**：重发 1.jpg 原图（md5 8f693eda）+ 视频（md5 95323c4e）+ 4 个 fact 验证 + task_id → 用户确认实际是 No 内容。**判断口诀**：**"send_message 视频 = 必附 md5 + task_id 证据链"** |
| **77**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v6 模板 = v15 4 段 + 文字持续可见段**）| **v15 模板 = 4 段 → v6 模板 = 5 段（第 5 段 = 文字持续可见段）**——v6 在 v15 段 2 末帧策略前**新增"文字持续可见段"**：参考图原有的所有文字（顶部 1/6 画面的{EN_WORD}和{ZH_WORD}字）从 t=0 到 t=末帧 全程可见，伴随微动画（每字呼吸式明暗交替 0.5s/次 + 字符顺序浮现按朗读节奏）。**修复方向**：① scripts/fill_v15_template.py v6 模式**自动插入文字持续可见段** ② C 子 agent 必填 text_visibility 字段（v6 新） ③ 主 agent 拼 v6 模板 = v15 4 段 + 文字持续可见段 = 5 段。**判断口诀**：**"v15 模板 = 4 段 / v6 模板 = 5 段（+ 文字持续可见）"** |
| **78**（v1.0.3+pic12 实战新增 · 2026-06-07 · **多版本原料 JSON 并存策略**）| **重设计 = 新建 vN.json，不覆盖原版**——Pic4 No 绘本实战中**并存 5 版原料 JSON**：clip{1-9}.json（v1 严肃） + clip{1-9}-v3.json（v3 温柔化） + clip{1-9}-v5.json（v5 节奏两步推导） + clip{1-9}-v6.json（v6 整数+文字全程） + 1 段手写 clip1-prompt-v3.txt（备份）。**修复方向**：① C 子 agent 重设计任务 brief 必说"不覆盖 v{N-1}.json，新建 vN.json" ② 主 agent 拼模板时**显式选版本**（`fill_v15_v6.py` 读 `clip1-v6.json`）③ 发飞书时**显式打版本号**（"v1 严肃版"/"v3 温柔化版"/"v5 节奏强化版"/"v6 整数+文字强化版"）让用户能区分。**判断口诀**：**"vN.json 不覆盖 v{N-1}.json · 发飞书必带版本号"** |
| **79**（v1.0.3+pic12 实战新增 · 2026-06-07 · **单 Clip 端到端验证 = 必经环节，不批量跳跑**）| **v1.0.2 实战差点踩坑**：单 Clip 跑通就接着批量跑剩下 8 段。**Pic4 修复**：clip1 跑通 → **先发飞书用户目检** → 等用户回复 OK → 再跑剩下 8 段。**修复方向**：① 主 agent 单 Clip 跑通必说"我打算：发您单 Clip → 等您目检 → OK 再批量" ② **不能自动连跑**（即使 v1 跑通也等用户确认）③ 这是**飞书视频交付**流程的铁律（不是 D 子 agent 内部）。**判断口诀**：**"单 Clip 端到端 = 等用户目检 = 不批量跑"** |
| **80**（v1.0.3+pic12 实战新增 · 2026-06-07 · **情绪基调 AI 判定铁律**）| **绘本情绪基调 = AI 判定标准 + 用户拍板，不硬编码"温柔化"**——用户 2026-06-07 二次纠错"光说 AI 判断不说标准，等于没说"。**根因**：原 v1.0.2 实战反推"温柔化"作硬规则 = 单题材（No 警示向）硬编码，不适用其他题材（温情向/冒险向/知识向/治愈向）。**修复方向**：① A 风格识别 agent **必跑 4 维加权判定标准**（题材类型 40% + 画面色彩 20% + 角色表情 20% + 叙事弧 20% → 加权算分）② **5 类题材 → 候选基调表**（警示向=温柔坚定/慈爱守护；温情向=慈爱温柔/欢喜陪伴；冒险向=兴奋勇敢/紧张期待；知识向=好奇探索/欢快轻松；治愈向=温暖陪伴/静谧安心）③ 输出 `emotion_tone_ai_recommendation` JSON 字段到 `style-recognition.json`（含 4 维分数 + 加权分 + 推理链 + 备选 3 个）④ **主 agent 必报用户拍板**（用固定话术：题材/色彩/表情/叙事 4 项分数 + 加权分 + 推荐主调 + 备选 + 拍板选项 A/B/C）⑤ 用户拍板后 → 主 agent 落 C JSON 的 `emotion_tone` 字段 → C 子 agent 写到 prompt ⑥ **不替用户决定**——AI 凭标准判定是输入，最终决策权归用户。**完整标准**：见 [references/emotion-tone-ai-judgment-standard.md](references/emotion-tone-ai-judgment-standard.md)。**判断口诀**：**"AI 按 4 维加权判定 + 主 agent 报用户拍板 + 不硬编码温柔化"** |
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
