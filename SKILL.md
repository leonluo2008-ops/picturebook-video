---
name: picturebook-video
description: "绘本转儿童动画视频标准流程（v5.0.13 音频路由 · 2026-06-26）。**单仓含 seedance_mcp/ 集成（uguu + Ark API + MCP 协议壳）** = 克隆 1 仓 = 完整可用，不依赖 seedance2.0-tool 仓。v8.1 动作模板（按事件分镜 · 替代 v8 运镜模板 · Potato BUG 修复） + 7 步流程 + 5 硬约束（含硬约束 #1 = 永远无 BGM） + 7 案例 + SRT 驱动工作流 + 音频路由（路径 A 有 SRT = 旁白+音效 / 路径 B 无 SRT = 纯音效 / 路径 C/D spike/静默）。Step 1 接收需求 + SRT → Step 2 vision 自检（5 项必查）→ Step 3 解析 SRT 真实时间戳 + 反推速率 → Step 4 旁白优先逐段合并（按真实秒数 [4,15] + suggested_duration 整数保证）→ Step 5 v8.1 动作模板（主体本身动 + 按事件分镜 + 不凝固收尾 + 段 5 音频描述）→ Step 6 seedance 提交（v5.0.13 路由规则）→ Step 7 端到端验证。**安装**：`git clone -b v5.0` + 拷 wrapper.sh + 填 .env + 跑 INSTALL_TEST.sh。触发词：绘本视频、绘本转视频、绘本动画、v8.1 写法、按事件分镜、SRT 驱动、动作模板、单仓安装、音频路由、generate_audio。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, storyboard, fill-v15, seedance, director-cut, ref-images, no-silence-mandatory, vision-all-mandatory, tts-user-priority, no-first-last-frame, audio-routing-v5.0.13, no-bgm-mandatory]
  related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool, picturebook-creator]
  toolkit_role: picturebook-video-orchestrator
---

# picturebook-video · 绘本视频标准制作流程 v5.0.13

> **核心**: 旁白优先 · 画面跟随旁白走 · 不凑时长 · 不抢画面 · 装不下就拆。v5.0.13 = SRT 驱动 + v8.1 动作模板 + 音频路由（默认有声 + 永远无 BGM）。

## 0. 这是什么

绘本转儿童动画视频的 7 步标准流程。**单仓集成** v5.0 = 自带 `seedance_mcp/`(uguu 上传 + Ark API + MCP 协议壳),克隆 1 仓 = 完整可用,不依赖 `seedance2.0-tool`。**v5.0.10 起 SRT 是必走路径** — 用户从剪映导出 SRT → 直接喂给制作 agent(详见 §8)。**v5.0.13 起音频路由默认有声**(详见 §1 硬约束 #1 = 永远无 BGM)。

**触发词**: 绘本视频、绘本转视频、绘本动画、v8.1 写法、SRT 时间戳、动作模板、单仓安装、音频路由、generate_audio、无 BGM、有声视频。

**v5.0.10.1 核心修复**(用户 Potato SRT 实测翻车驱动):
- **clip_merger 整数时长 < SRT 跨度翻车** → v5.0.10 用 `int()` 向下取整 vs 实际 SRT 跨度 6.166s/7.633s。v5.0.10.1 强制 `ceil()` + `suggested_duration` 字段 + `duration_ok` 校验 + 任何 srt_span > 15s 必 WARNING 拆 clip。
- **v8.1 强时间锁违反官方** → v5.0.10 段 2 强制 `00:00.0-00:01.0` 100ms 精度违反 Seedance 官方"模型对精确时间不稳定"原则。v5.0.10.1 改为按事件分镜 (`镜头 1/2/3`), 段 3 改"念到 X 词时 Y 动作"事件对应。
- **verify_prompt R1/R4 FAIL 误判** → v5.0.10 强制必含 `MM:SS.mmm` 时间戳让 4 个按事件分镜 prompt 全 fail。v5.0.10.1 降级为 WARN(跟官方对齐)。

**v5.0.13 核心改动**(用户 Beet Pepper SRT 实测翻车驱动):
- **默认音频路由翻车** → v5.0.12 规则下"领读型=false / 有声绘本=true"二分法容易选错。Beet Pepper v1 给 SRT 但直接发视频场景误判为 false → 4 个 Clip 全无声。
- **v5.0.13 新规则**: 默认 generate_audio=true,通过路径 A/B/C/D 路由决策,通过段 5 内容区分旁白 vs 音效。
- **硬约束 #1 = 永远无 BGM**: 任何 prompt 末尾约束必须包含"无背景音乐"——音效 + 旁白 OK,BGM ❌。
- **案例 #38** 新增: 默认音频路由翻车记录。

**必读**: `manifest.json` / `INSTALL.md` / `references/clip-划分方法论.md`(**Step 4 唯一权威依据**)。

**官方文档兜底**: 当 skill 规则不够明确、遇到新场景、或 seedance 实际效果与预期不符时，**必查以下两套官方文档**（详见 §7）:
- `references/seedance-official-docs/` — Seedance 2.0 官方教程（3 篇：教程/提示词指南/视频生成教程）
- `references/ai-drama-sop/` — 即梦(Dreamina)官方工作流 SOP（9 篇：从创意发散到成片全流程）

## 1. 6 条硬约束（v5.0.13 加 #0 = 永远无 BGM）

> **v5.0.13 新增硬约束 #0**: 任何 prompt 末尾约束必须包含"无背景音乐"。音效 + 旁白 OK,BGM ❌。这条优先级最高,不受其他规则影响。

| # | 约束 | 触发场景 | 对应案例 / 脚本 |
|---|---|---|---|
| **0** | **永远无 BGM · 硬约束 #1** | Step 5 prompt 末尾约束 | 案例 #38 / v5.0.13 路由规则 |
| 1 | **参考图是起点不是限制** | Step 2-5 prompt 设计 | 案例 #26 / `scripts/verify_prompt.py` |
| 2 | **4 确认点流程 · 默认开启 · 用户说"全自动"才静默** | Step 3 后 / Step 5 后 / Step 6.0 / Spike 后 | 案例 #30 |
| 3 | **seedance ≤3 并发 · 多轮分批** | Step 6 提交 | 案例 #31 |
| 4 | **末尾约束按参考图分 2 类** | Step 5 prompt 末尾 | 案例 #36 |
| 5 | **readme 文字 vs vision 视觉冲突 = 默认按 readme 文字** | Step 1 角色对位 | 案例 #23 |

**注意**: v5.0.9 删除了 v5.0.8 的 18 条铁律段。v5.0.13 在原 5 条基础上**新增 #0(永远无 BGM)** = 共 6 条硬约束 + 案例库(§4)+ 权威文档(§3 Step 4)。

**元方法论状态**: `#M1 整本节奏` **降级为参考原则**(优先级 = 最低),被权威文档"旁白优先"覆盖。`#M2 #M3 #M4` 保留为参考方法论,不作为硬约束。

## 2. 7 步标准流程

### Step 1 · 接收需求(绘本简介 + 图片 + 旁白 + 目标平台 + TTS 数值)

- 必收 `user_tts_seconds` = 视频总时长基准
- 必收 `readme.txt`(若有)→ 角色对位优先级 = readme > vision(约束 5)
- 必收所有 N 张图 + 旁白文件(中文列含嵌入英文 = 领读型)
- **⚠️ SRT 前置校验(case #39)**: 有 SRT 时，解压后先通读 SRT 文本，核对目标词是否与图片一致、内容是否与绘本主题匹配。目标词对不上 = 立即告知用户，不进入 Step 2-3。口诀:"解压先读 SRT，目标词对得上才往下走。"

### Step 2 · vision 自检 + 通读旁白(必全 N 张图)

**5 项必查**:
1. 主体位置(左/中/右/上下)
2. 主体朝向(侧身/正面/背面)
3. 景别(全身/中景/半身/特写)
4. 主体姿态(手/脚/头位置)
5. 文字元素(位置/颜色/类型/是否装饰性 → 决定末尾约束分流)

**输出**: `image-inventory.md`(主体分类 + 文字元素列)

### Step 3 · 逐段计算旁白朗读时长

**v5.0.10 优先 SRT 路径** — 用户从剪映导出 SRT 文件后,**必走 SRT 路径**(精确到毫秒)。无 SRT 才回落估算。

**路径 A · SRT 优先**(v5.0.10 推荐):
1. 跑 `python3 scripts/srt_parser.py <srt_file> --out timeline.json` → JSON 时间轴(含每段精确起止 + 段间停顿)
2. 跑 `python3 scripts/clip_merger.py timeline.json --user-tts <用户TTS秒数>` → clip 划分(用真实秒数,不需要估算)
3. 对齐检查 = `--align-tolerance 1.0`(v5.0.10 精确模式,v5.0.9 是 5s)

**路径 B · TTS 估算回落**(无 SRT 时):
- 公式:`每段 TTS = 中文字数 / 中文速率 + 英文词数 / 英文速率 + 词间停顿`
- 速率档位(必跑 `scripts/tts_rate_calculator.py`):

| 档位 | 中文速率 | 英文速率 | 适用 |
|---|---|---|---|
| 慢估 | 3.0 字/秒 | 1.0 词/秒 | 长句 + 复杂词 |
| **领读短句档** | **4.0 字/秒** | **1.4 词/秒** | **绘本短句 + 双语领读(默认)** |
| 偏快档 | 4.0 字/秒 | 1.5 词/秒 | 极短单词开篇 |

- 判定: 选物理意义最强 + 跟用户给 TTS 差 ≤ 5s 的档位

**v5.0.10 关键改进**: SRT 路径下**反推真实速率**(剔除停顿)→ 不再依赖假设的速率档。比如生菜 SRT 反推 = 1.78 字/秒(v5.0.9 默认 4.0 字/秒**严重偏差**)→ 用真实速率校准 prompt 时间锚点。

### Step 4 · 旁白优先逐段合并 ⚠️ 权威文档 v1.0

> **本节是 SKILL.md 唯一权威依据,优先级最高,覆盖 #M1 整本节奏 / 5 项一致性合并 / 任何旧版规则**。
> 完整版: `references/clip-划分方法论.md`

**5 步标准流程**:

1. **逐段计算旁白朗读时长**(Step 3 输出)
2. **累加相邻段** = 从段 1 开始累加 + 下一段 ≤ 15s? 是 → 继续合并;否 → 当前组 = 1 clip
3. **向上取整** = 每组取整到 [4, 15] 整数
4. **总和 vs 用户 TTS 对齐** = 差 ≤ 5s ✅ / 超出 → 调整拆分策略
5. **图跟随旁白段分配** = 画面跟随旁白走

**判定口诀**: **"逐段算 → 累加合并 → 取整 → 对齐 TTS → 图跟随"**

**4 个反模式**(必避):

| 反模式 | 后果 |
|---|---|
| 先按图分组再凑时长(3 图 = 1 clip) | clip 时长 < 旁白实际时长 → TTS 画面错位 |
| 以叙事弧决定 clip 数(3 弧 = 3 clip) | 弧内旁白段太多 = 超时 |
| 总时长均分到 N 个 clip(31s / 4 = 7.75s) | 不考虑各段旁白长短差异 |
| 以图数量决定 clip 数量(8 图 = 4 clip) | 旁白段长短不一 = 有的装不下、有的空废 |

**3-clip 对齐超容差修复模式(2026-06-26 Luffa 实测)**: clip_merger 输出 3 clips 但 `within_tolerance=false`(+1.5s) → 人工检查每个 clip 的 `srt_span` vs `suggested_duration`,**把 7-8s 的 clip 强制压到 [4, 区间]下界**(speech_duration < srt_span 才可压)→ 重新求和差 ≤1s。判别口诀: **"speech + tail_pause < suggested 时才允许降一档"**。

### Step 5 · v8.1 动作模板手写 prompt

|> **v5.0.10 核心改动** — 从 v8 运镜模板 → v8.1 动作模板。**问题**: v8 模板让画面"几乎静止"(生菜 SRT 实测翻车)。**修复**: 主体本身动 + 按事件分镜 + 禁凝固语。
>
> **v5.0.10.1 核心修正** — Potato 实测发现 v5.0.10 强时间锁(`00:00.0-00:01.0`)违反 Seedance 官方"模型对精确时间不稳定"原则。改为"按事件分镜"(镜头 1/2/3),时间戳降级为 WARN。

> 完整模板: `references/v8-action-template.md`(v5.0.10 新增, v5.0.10.1 按事件分镜修正)

**4 段结构(v8.1 动作版 · v5.0.10.1 按事件分镜 · v5.0.12 蓝本约束)**:
- **段 1 · 主体+视觉基底**: 主体 + 景别 + `@ImageN` + 视觉特征
- **段 2 · 主体动作序列(核心)**: 按事件分镜(`镜头 1 / 镜头 2 / 镜头 3`),**主体本身动**(不只镜头动),**不卡秒数**(官方"不强制限制每段时长")
- **段 3 · 关键节点对照**: "念到 X 词时 Y 动作" 事件对应(**不写精确 SRT 时间戳**, v5.0.10.1 修正)
- **段 4 · 收尾(不凝固)**: `镜头 N(收尾):` 按事件分镜 + **保持运动状态** + 跟起始状态呼应
- **段 5 · 音频描述**(generate_audio=True 时,v5.0.13 路由规则):
  - **路径 A(SRT)**: `人声旁白:"{SRT原文}"` + `音效:{具体音效}`(v5.0.12 新增)
  - **路径 B(无 SRT)**: **只写** `音效:{具体音效}`(不写人声旁白,seedance 无 SRT 时不知道说什么)
  - **路径 C/D(spike/静默)**: 整段省略,generate_audio=false 不需要

**5 条强制段约束(v5.0.11 R6-R9 视觉 + v5.0.12 R10 音频)** — 全部 FAIL 级 verify_prompt.py 硬规则:

| 规则 | 段 | 强制要求 | 为什么 |
|------|----|----------|--------|
| **R6** | 段 1 | 多图 Clip 每张 `@ImageN` **必须分别描述视觉基底**（位置/景别/视觉特征/文字元素），多图之间用 **"接着"** 衔接 | seedance 需要逐图差异才能做镜头切换,只写 `@Image1 @Image2` 不分别描述 = 画面模糊 |
| **R7** | 段 2 | 每个镜头必须用 `镜头 N（@ImageN + 段 N 旁白）：` 格式**显式绑定**参考图和旁白段 | seedance 需要知道每个镜头对应哪张参考图、对应哪段旁白,不绑定 = 画面动作和旁白不同步 |
| **R8** | 段 3 | 必须用 `段 N 念"完整旁白文本"：动作映射` 格式,**逐段列出完整旁白原文** + 动作映射 | seedance 需要旁白原文才能直接对照,只写"念到 X 词时"太模糊 = 对不上 |
| **R9** | 段 4 | 必须用 `镜头 N 末尾：` 指明位置 + **具体微动描述**,不可用"回到开场状态"等抽象语 | seedance 需要精确知道收尾在哪个镜头之后、做什么动作,抽象语 = 画面趋向凝固 |
| **R10** | 段 5 | **generate_audio=True 时**必须新增**段 5 · 音频描述**,逐段写 `人声旁白："{SRT原文}"` + `音效：{具体音效}` | seedance generate_audio=True 会自动生成音频,不写音频描述段 → 自己猜旁白内容和节奏 → 不可控 |

**完整蓝本参考**: `references/v8-action-template-blueprint.md`(v5.0.12 更新 · 5 个 Clip 模板含 R10 音频段 + Lettuce 反例对照)

- **v5.0.10 反模式**(verify_prompt.py 硬规则, v5.0.10.1 调整):
- ❌ 段 2 只写"运镜"无主体动作 → 画面静止(主体本身需要动: 摆动/摇晃/光斑/水珠/伸手等 50+ 关键词,见 `scripts/verify_prompt.py` SUBJECT_ACTION_KEYWORDS)
- ❌ 段 2 用"持续 X 秒"含糊 → 时间锚点丢失
- ❌ 段 4 用"持续循环/保持稳定/画面自然流动" → 画面凝固(v5.0.9 旧收尾语,见 FROZEN_LANGUAGE_PATTERNS)
- ⚠️ 段 3 强写 `MM:SS.mmm` 精确时间戳 → 官方反模式(模型对精确时间不稳定),v5.0.10.1 降级为 WARN, 改用"念到 X 词时 Y 动作"事件对应
- ❌ 段 1 缺 `@ImageN` → 主体跟参考图脱钩

**文字元素动效分流(2026-06-26 Luffa 用户偏好 · 默认开启)**:
> 领读型绘本**几乎每张图都含文字**(英文目标词+中文),用户偏好让文字元素也"活起来"——默认按参考图类型分流:
> **A. 静态文字图片(默认)**: 在段 1 视觉基底里**显式写**文字元素 + 动效关键词。已验证 6 种安全动效: `轻微弹跳` / `轻微摇摆` / `轻微闪烁光效` / `缩放呼吸` / `轻微摇曳` / `波浪浮动`。
> **B. 静态文字但用户没要求**: 保留"保留参考图中的 X 文字作为画面元素"原写法(不动)。
> **判别口诀**: 用户说"文字也动一下"/"文字也加感觉"/"字母弹跳"等 → 走 A;用户没提 → 走 B。
> **反模式**: ❌ 强写"字母依次出现"/"打字机效果"/"逐字缩放"等复杂时序 → seedance 容易跑飞成"文字乱码"。

**反模式根因诊断**(踩坑记录 · 2026-06-23 生菜 SRT + 2026-06-24 Potato SRT 实测):
- "运镜思维" vs "动作思维" 是 v8 → v8.1 升级的本质。镜头在动 ≠ 主体在动,seedance 输出的画面如果只有运镜就趋向静止
- "凝固语" 是 v5.0.9 旧收尾典型写法("持续循环不切断"等)→ 让模型输出"循环不切断"动作 = 画面被冻结
- "强时间锁" 是 v5.0.10 修正过头(100ms 精度)→ 违反官方"模型对精确时间不稳定"原则,v5.0.10.1 改为按事件分镜
- **"逐图混写"** 是 v5.0.11 新增根因(2026-06-24 Potato vs Lettuce 实测对比发现):Lettuce 把多图混在一段写不分别描述 = seedance 不知道两张图区别 = 镜头切换不自然
- **"旁白-动作脱节"** 是 v5.0.11 新增根因:只写"念到 X 词时 Y 动作"不列完整旁白原文 = seedance 不知道整段旁白是什么 = 时间点对不齐

**末尾约束分流**(约束 4 · v5.0.13 硬约束 #1 = **永远无 BGM**):

> **最高优先级**: 所有 prompt **必须包含** `无背景音乐` 4 个字——不论路径 A/B/C/D,任何情况下都不允许生成 BGM(背景音乐/插曲/主题曲)。音效 + 旁白 OK,BGM ❌。

| 参考图类型 | 末尾约束 | 附加 |
|------------|----------|------|
| **无文字元素** | `无字幕、无 Logo、无水印、无背景音乐` | 4 项全写 |
| **含装饰性文字** | `无水印、无背景音乐` | 2 项 + prompt 文字镜头段显式说"保留参考图中的 X 文字作为画面元素" |

**v5.0.13 新增硬约束**: 即使参考图是纯蔬菜、纯风景、纯动物,**也必须**写"无背景音乐"——BGM 是绘本禁忌(盖旁白、盖音效、容易让宝宝烦躁)。

**Step 5.5 强制**:
- ✅ 必跑 `scripts/verify_prompt.py`(硬规则 v5.0.9 的 8 项 + v5.0.10 新增 3 项, v5.0.10.1 调整 R1/R4 降 WARN, v5.0.11 新增 R6-R9, v5.0.12 新增 R10 音频 · **v5.0.13 调整**: R10 改为"音效必写,人声旁白仅路径 A 必写") + `--generate-audio` 开关
- ✅ 必调 `agents/prompt-reviewer/`(L3 视觉逻辑审查)
- 任意失败 → 修 → 重跑 → 直到 ok=True → 才进 Step 6

### Step 6 · seedance 提交(mcp_seedance_* 工具)

- 整数时长 [4, 15]s
- ≤ 3 并发(约束 3)
- 每轮 submit 后必 `wait_and_download` 全部完成 → 才开下一轮
- N 个 Clip 拆成 `ceil(N / 3)` 轮串行
- 单轮提交前必查 status(确保本轮无 failed 任务 = 有就停下汇报用户)

**generate_audio 参数 — v5.0.13 路由规则**(2026-06-26 Beet Pepper 实测沉淀):

> **核心原则**: 默认情况下所有视频都有音频(音效 + 旁白),**永远没有 BGM**(硬约束 #1 · 最高优先级)。

| 路径 | 用户输入 | generate_audio | 段 5 · 音频描述 | 用途 |
|------|----------|----------------|-----------------|------|
| **A · SRT 路径** | 给了 SRT 文件 | `true` | 写 `人声旁白:"{SRT原文}"` + `音效:{具体音效}` | 有声+旁白+音效 |
| **B · 无 SRT 路径** | 没给 SRT | `true` | **只写** `音效:{具体音效}` (不写人声旁白) | 有声+音效(无旁白) |
| **C · spike 测试** | 用户说"先测一下"/"spike" | `false` | 省略段 5 | 静默,只验视觉 |
| **D · 强制静默** | 用户明确说"不要声音"/"纯视频" | `false` | 省略段 5 | 静默,特殊场景 |

**决策口诀**: "有 SRT → 旁白+音效;无 SRT → 纯音效;spike/特殊 → 静默"——**永远不生成 BGM**。

**历史变更**:
- v5.0.12 旧规则: "领读型=false,有声绘本=true"——**默认不一致,容易翻车**(本会话 Beet Pepper v1 无声翻车就是这个原因)
- v5.0.13 新规则: **始终 true**(除非 spike/强制静默),通过段 5 内容区分旁白 vs 音效

**强制约束**:
- ⚠️ **必须显式传 generate_audio 参数**(不依赖默认值)——API 默认值漂移会失控
- ⚠️ **永远不传 `watermark='seedance_ai'`** —— 不要 AI 水印
- ⚠️ **末尾约束永远包含"无背景音乐"**——硬约束 #1,任何 prompt 不准漏

**4 确认点**(约束 2):
1. Step 3 后 → clip 时长划分/合并策略确认
2. Step 5 后 → 每个 Clip 中文 prompt 确认
3. Step 6.0 提交 spike 前 → 单测参数确认
4. Spike 跑完后 → 视觉质量 + 批量 1 次确认

**输出纪律**: 跟用户确认 = 必用纯文本 + 标题 + 列表,严禁 GFM 表格(飞书渲染问题)。

**Polling pitfall ⚠️ 2026-06-25 firefighter 实测踩坑**:
- ❌ **不要循环调用 `mcp_seedance_check_task`** — 一次任务需要 30+ 次轮询才能完成(每个任务 ~2-3 分钟),既浪费 token 又触发 loop 警告
- ✅ **正确做法**: submit 多个任务后,**直接调一次 `wait_and_download` 等待全部完成**(`poll_interval_sec=30`, `timeout_sec=600`)。wait_and_download 内部已实现智能轮询,返回就是下载好的 mp4
- ✅ 极端情况(spike 单测想立刻看):可以调 1-2 次 `check_task` 探进度,看到 succeeded 后立即 `wait_and_download` 下载,**不要超过 5 次轮询**
- 三个并发任务 → 三个并行 `wait_and_download` → 都返回 = 都下载完成 → 进入 Step 7

**发飞书 pitfall ⚠️ 2026-06-25 firefighter 实测踩坑**:
- ❌ **不要先提取视频封面再发送** — `lark-cli drive +cover` 在 video 文件刚上传后报 HTTP 404(预览未生成),且多次尝试 -spec default/icon/big 都失败
- ❌ **不要用 `lark-cli drive +upload --video --video-cover`** — v1.0.53 的 drive +upload 不支持 video 子命令,只支持 +cover 单独流程(但 +cover 也失败)
- ✅ **正确做法**: 直接用 `send_message` + `MEDIA:/path/to/video.mp4`,Hermes 原生支持 Feishu 视频消息,自动 inline 渲染
- 用户偏好(2026-06-25):"不需要你提取封面，直接把视频发给我" — 视频就用 MEDIA: 直接发,不要中间夹任何 cover 提取步骤

### Step 7 · 端到端验证 → 发飞书 + 完整证据链

- md5 + 时长 + 视觉效果确认
- 必发飞书 + 完整证据链(md5 / duration / 截图)
- 文件名 = ASCII(数字/英文/拼音)· 严禁中文(防 zip UTF-8 / GBK 乱码)

**视频交付纪律（2026-06-29 反复发错视频沉淀 · 核心规则）**:

> **根本原因**: 多个项目视频缓存在本地不同目录(`/tmp/*_huiben/`, `~/.hermes/cache/documents/*_extract/`, `~/asparagus/` 等),上下文压缩后 agent 残留旧路径,凭残留路径发送 = 发错视频。同一会话连续发错 3 次(he→stop→再次 he clip1 错误)。

**核心规则: 不缓存、用完即弃、task_id 为准**:

| 规则 | 说明 |
|------|------|
| **❌ 不缓存视频到本地持久目录** | 不要 `wait_and_download` 到 `/tmp/` 或 home 目录长期保留,多个项目文件混杂 = 发错根源 |
| **✅ 交付流程** | `wait_and_download` → **立即** `send_message MEDIA:` 发飞书 → 删除本地副本 |
| **✅ 用户说"发错"时** | 用 `check_task(task_id)` 拿 `video_url` → `curl` 重新下载到临时路径 → 发送 → 删除。**不要在本地翻找旧文件** |
| **✅ 会话/项目结束后** | 清理所有中间产物(`rm -rf /tmp/*huiben* /tmp/*unzip/` 等残留目录),避免下次会话翻旧文件 |
| **✅ 保留的文件** | 仅用户上传的源素材包(.7z/.zip)在 `~/.hermes/cache/documents/`,不保留解压后的 mp4/jpg |

**反模式**:
- ❌ 上下文压缩后凭残留路径发视频(路径可能指向上一个项目)
- ❌ 用户说"发错视频"后不搜索、不确认、直接重发同一批错误文件
- ❌ 多个项目视频共存于 `/tmp` 不同子目录,发前不校验项目名匹配

## 3. 脚本守门

| 脚本 | 用途 | 检查项 |
|---|---|---|
| `scripts/srt_parser.py` | SRT → JSON 时间轴(v5.0.10 新) | 段起止毫秒精度 + 段间停顿 + 反推真实速率 |
| `scripts/clip_merger.py` | 时间轴 → clip 划分(v5.0.10 新) | 真实秒数合并 + [4,15] 区间 + 对齐用户 TTS |
| `scripts/verify_prompt.py` | v8.1 prompt 硬规则 | v5.0.9 8 项(#29/#28/#26/#33/#21+#27+#37 等) + v5.0.10 新增 3 项 + **v5.0.10.1 调整**: R1/R4 时间锚点从 FAIL 降级为 WARN(跟官方"不强制限制每段时长"对齐) · R3 凝固语 · WARN R1 主体动作 · v5.0.11 R6-R9 Potato 蓝本结构 · **v5.0.12 R10 音频描述**(generate_audio=True 时, `--generate-audio` 开关) |
| `scripts/tts_rate_calculator.py` | TTS 速率方案校对(路径 B fallback) | 5 档对比 + 总和 vs 用户 TTS 差 ≤ 5s |
| `scripts/skill-changes-check.sh` | 守门 SKILL.md 铁律改动 | 检测铁律新增/删除 + 编号连续性 |
| `scripts/validate_durations.py` | 时长校验 | 总时长对齐用户 TTS |
| `agents/prompt-reviewer/` | L3 视觉逻辑审查 | `@ImageN` 必含 / 视觉覆盖 / 时长差 / 旁白映射 |

## 4. 案例库(7 个 · references/cases/)

每个案例 ≤ 300 字,**只列反复触发的隐性陷阱**。完整内容见 `references/cases/{name}.md`。

> **元注释**(用户偏好 · 2026-06-23 反复确认): "反对铁律泛滥 / 案例不超 6 个"。v5.0.9 已删 18 条铁律,v5.0.10 只新增 1 个 case (#37)。**规则不超 5 条,案例不超 7 个,超出 = 搬到 references/**。这是用户长期偏好,不是临时约束。

| 案例 # | 名称 | 反复触发 |
|---|---|---|
| #23 | readme 文字 vs vision 视觉 | ✅ |
| #26 | 参考图是起点不是限制 | ✅ v1→v8 反复翻车 |
| #30 | 4 确认点流程 | ✅ workflow 结构性 |
| #31 | 3 并发限流 | ✅ seedance 官方硬约束 |
| #33 升级版 | 旁白优先逐段合并 | ✅ 权威文档 v1.0 |
| #34 | 文档/代码 3 处对齐 | ✅ 防"全静音"类翻车 |
| #36 | 末尾约束分 2 类 | ✅ seedance 文字元素陷阱 |
| **#37 (v5.0.10)** | **画面静止反例(运镜思维 → 动作思维)** | ✅ **生菜 SRT 实测翻车** |
| **#38 (v5.0.13)** | **默认音频路由翻车(generate_audio 默认值不一致)** | ✅ **Beet Pepper SRT 实测翻车** |
| **#39 (v5.0.13)** | **SRT 文件发错(目标词/主题不匹配)** | ✅ **Truck 实测 · Step 1 前置校验** |

**12 条 v5.0.8 旧铁律已删**(记录在 CHANGELOG.md v5.0.9 段):
- #21 TTS 严格匹配 → 脚本 tts_rate_calculator.py 覆盖
- #22 大小主体装饰 → 合并到 #26 案例
- #24 文件名 ASCII → INSTALL.md 已说明
- #25 verify_filled_prompts 误报 → 一次性 bug 修订
- #27 不为饱满凑数 → 脚本覆盖
- #28 v8 简洁收尾 → verify_prompt.py 已编码
- #29 @ImageN 必含 → verify_prompt.py 已编码
- #32 飞书表格禁用 → 其他 skill 通用,本 skill 不专属
- #35 领读型双列 → 一次性 case,不专属
- #37 单镜头 2-4s → verify_prompt.py 警告

## 5. workflow 节点(强制 hook)

| 节点 | 必走 | 阻塞 |
|---|---|---|
| Step 3 后 | 调 `srt_parser.py` + `clip_merger.py`(SRT 路径)/ 调 `tts_rate_calculator.py`(路径 B fallback) + 跟用户确认 4 确认点 #1 | 不确认不进 Step 4 |
| Step 4 后 | 跟用户确认 4 确认点 #1(clip 时长划分/合并) | 不确认不进 Step 5 |
| Step 5.5 | 跑 `verify_prompt.py`(v5.0.10.1 共 11 项硬规则: 6 FAIL + 5 WARN, R1/R4 时间锚点降 WARN) + delegate `agents/prompt-reviewer/` | 任意 FAIL → 修 → 重跑 |
| Step 5 后 | 跟用户确认 4 确认点 #2(每个 Clip 中文 prompt) | 不确认不进 Step 6 |
| Step 6.0 spike 前 | 跟用户确认 4 确认点 #3(单测参数) | 不确认不提交 |
| Spike 跑完后 | 跟用户确认 4 确认点 #4(视觉质量 + 批量) | 不确认不批量 |
| 任何 SKILL.md 改动 | 跑 `scripts/skill-changes-check.sh` | 有铁律改动 = 必用户拍板 |

**开新分支踩坑**(2026-06-23 实测):
- 本地 `master` 分支 ≠ 上游 `master`!上游默认分支可能是 v5.0.8,而最新工作在 `fix/runtime-stability-2026-06-23` 之类的 fix/feat 分支
- 开新分支前**必查**:`git branch -a` + `git log --all --oneline | head -10` 确认 HEAD 在哪个版本
- 推荐从最新 production 版本(v5.0.9 / v5.0.10 等)的 fix/feat 分支拉新分支,而不是从 master

**"合并到 main" 必先验证祖先关系 + 5 步标准 SOP**(2026-06-24 Potato 4 BUG 修复后踩坑 · 重要):

**踩坑根因**:本地 install 仓的起点 commit(`23fd594 "picturebook-video official install (dev branch)"`)**不在** 远程 `origin/main`(v3.0)或 `origin/dev`(v5.0.11)上 → 三条线**完全独立 commit 历史**。v5 系列产品本地 install 仓和远程 `dev` 分支的 v5.0.x 是**两套独立演进**,同名不同源 → 跨线合并只能 cherry-pick,不能 ff。

**5 步强制 SOP**(用户说"合并到 main" / "推到 origin/X" / "覆盖 remote X" 任何一种措辞时,必走):

1. **`git fetch origin --prune`** — 同步真实远程分支状态(避免本地缓存过期误判)
2. **`git branch -r`** — 列出全部远程分支,**不**假设远程"只有 main"或"只有 dev"
3. **`git log origin/<branch> --oneline -3`** — 看目标远程分支 HEAD 状态(版本号 / commit message / 起点 author)
4. **`git merge-base --is-ancestor <my-HEAD> origin/<branch>`** — 验证祖先关系(是祖先 → 可 ff;不是 → 只能 cherry-pick,不可直接 push)
5. **选操作模式**:
   - **A · ff merge**(祖先关系 ✅) → `git checkout <X>` + `git merge --ff-only <my-HEAD>` + `git push origin <X>`(无 --force)
   - **B · cherry-pick**(非祖先,跨线合并) → 大量冲突(尤其 SKILL.md/manifest),逐文件手动解冲突,**预期会修整版本号**
   - **C · 强制覆盖**(用户明确授权"直接覆盖"/"随便推") → `git push --force-with-lease`(比 `--force` 安全,会先检查 remote 没被别人改过)
   - **D · 本地软合并**(临时方案) → 本地新建分支,不推远程

**任何 `git push origin <branch>` 前必先做前 4 步**,**不**把本地独立 install 仓的工作直接当 ff merge 推到远程(本会话曾创建过孤儿 `origin/master` 分支 = 跟远程 main/dev 零 commit 共享的独立线,后被 --delete 删掉)。

**用户授权"直接覆盖"执行模板**:
```bash
# 1. 在 v5.0.10.1 HEAD 起本地 main(注意: 不叫 master,叫 main 跟远程对齐)
git branch -f main HEAD
git checkout main
# 2. 强制 push(用户授权)
git push --force-with-lease origin main
# 3. 删其他分支
git push origin --delete dev fix/runtime-stability-2026-06-23
git branch -D feature/srt-driven-clip-v5.0.10 master
# 4. 同步远程 HEAD
git remote set-head origin main
```

**多 profile 同步**(主 + huiben 独立副本):
- huiben profile 落后主 profile 1+ commit 时 → `git pull --ff-only` 不行(diverging) → 用 `git reset --hard origin/main` 强制同步
- 同步前**必先确认 origin/main 是用户授权覆盖的最终版本**(否则会丢 huiben 本地独有工作)
- huiben 备份分支(如 `backup-before-v5.0.10-*`)如用户表态"都不需要" → `git branch -D` 全删
- 验证两边一致:`diff <(git log main --oneline -1) <(git log origin/main --oneline -1)` 必须相同

**反射**:本会话 2 次踩坑(①没 ff 验证就 push origin master 创孤儿 ②huiben 落后 1 commit 用 pull 而非 reset),都已沉淀到 SOP。跟 `cross-profile-shared-facility` 第 19 段同源(那边侧重"main 是歧义词"原理,这边侧重"5 步 SOP"操作)。

## 6. 子 agent 列表

| Level | 名称 | 角色 | 触发 |
|---|---|---|---|
| L2-A | `agents/storyboard-style/` | 风格定义 | Step 1 后 |
| L2-B | `agents/storyboard-narration/` | 旁白量化 | Step 1 后 |
| L2-C | `agents/storyboard-design/` | 分镜设计(11 维 JSON) | Step 2 后(主 agent 决定 delegate 还是直干) |
| L2-D | `agents/video-executor/` | seedance 提交执行 | Step 6 |
| **L3** | **`agents/prompt-reviewer/`(v5.0.9 新)** | **v8 prompt 视觉逻辑审查** | **Step 5.5 必调** |

**delegate vs 直干判定**(v5.0.9 修订):
- 1-2 Clip = 主 agent 直干
- ≥ 3 Clip = delegate C 子 agent + L3 审查
- 任何规模 = 必走 `verify_prompt.py` 硬规则检查

## 7. 官方文档查询指南(兜底机制)

**原则**: skill 规则是第一优先级，官方文档是兜底。**遇到以下情况必须主动查阅，不要猜测或跳过。**

### 7.1 Seedance 2.0 官方文档

路径: `references/seedance-official-docs/`

| 遇到什么情况 | 查哪个文件 | 搜什么关键词 |
|---|---|---|
| prompt 写法不灵，v8 模板兜不住 | `2-Doubao_Seedance_2.0_系列提示词指南.md` | "提示词结构" / "镜头" / "风格" / "运镜" |
| seedance 实际跑出来效果跟 prompt 不一致 | `1-Doubao_Seedance_2.0_系列教程.md` | "参数" / "duration" / "ratio" / "resolution" |
| 新场景(漫剧/广告/教学视频)不知道 seedance 怎么用 | `3-视频生成教程.md` | "场景" / "风格" / "转场" / "角色一致性" |
| 视频生成失败/报错/参数不支持 | `1-系列教程.md` + `3-视频生成教程.md` | "error" / "limit" / "参数限制" |
| 不确定某个参数/功能是否存在 | `1-系列教程.md` 先查，查不到 → `3-视频生成教程.md` | 功能名 / 参数名 |

> 注: 每篇都有 `.docx`（原始排版/图片）和 `.md`（便于 grep/read_file）。Agent 用 `.md` 格式搜索。

### 7.2 即梦(Dreamina)官方工作流 SOP

路径: `references/ai-drama-sop/`

| 遇到什么情况 | 查哪个文件 | 说明 |
|---|---|---|
| 不清楚整体流程该怎么走 | `1-video-sop.md` | 9 阶段主流程框架（创意→成片全链路） |
| 不知道怎么发散/确认创意 | `2-story-idea.md` | 创意生成方法论 |
| 剧本/旁白写作不确定 | `3-story-script.md` | 剧本创作标准 |
| 参考素材提取/挖掘 | `4-ref-extract.md` | 素材挖掘方法 |
| 分镜切分/时长/组合 | `5-script-chunk.md` + `6-shots-timing.md` + `7-shots-assembly.md` | 分镜设计 3 步 |
| 分镜连贯性/视觉一致性问题 | `8-scene-reflection.md` | 连贯性校验方法 |
| 分镜 prompt 写法不确定 | `9-video-prompt.md` | 视频提示词生成 |
| 故事/角色/场景参考 | `10-story-ref-gen.md` | 故事参考生成 |

> **ai-drama-sop 是即梦官方工作流**，对视频创作全流程有极高参考价值。尤其是分镜设计（Phase 5 的 4 步子流程）和连贯性校验，与 picturebook-video 的 Step 2-5 高度互补。

### 7.3 查询纪律

- **先查 skill 规则 → 再查官方文档**。skill 规则（§1-§6）是第一优先级，官方文档是兜底参考
- **查到后如实告知用户**: "我在 Seedance 官方文档中找到了 X 规则，跟当前 skill 规则 Y 有一致/不一致之处，建议…"
- **官方文档与 skill 规则冲突时**: 以 skill 规则为第一优先级，但必须把冲突点报告给用户决策
- **不要假设**: 遇到参数/功能不确定 → 查官方文档确认 → 不要靠记忆或猜测
- **§8 SRT 驱动是 v5.0.10+ 的硬性工作流** — 用户给 SRT 时必走 SRT 路径(详见 §8),不要 fallback 到路径 B 估算

## 8. SRT 驱动工作流(v5.0.10 核心新增)

> **核心改动**: 用户从剪映导出 SRT 文件 → **直接喂给制作 agent** 作为编排依据。SRT 提供毫秒级时间戳,替换 v5.0.9 的估算路径,精度从秒级提升到毫秒级。

### 8.1 为什么需要 SRT

**v5.0.9 估算路径的 3 个根本问题**:
1. **速率假设偏差大** — 默认 4.0 字/秒,生菜 SRT 实测 1.78 字/秒(偏差 125%)
2. **时间锚点缺失** — prompt 写"持续 5s",但 5s 里到底哪个时间点对应旁白哪个字?不知道
3. **段间停顿丢失** — 领读型的段间停顿是设计意图,估算路径完全忽略

**SRT 路径的根本改进**:
- 时间锚点精确到毫秒(`00:00:01,200 --> 00:00:04,500`)
- 段间停顿显式化(`pause_after: 1.133s`)
- 反推真实速率(剔停顿后)
- prompt 运镜时长跟旁白时间点 1:1 对齐

### 8.2 完整工作流

```
[用户从剪映导出 SRT]
         ↓
[Step 3 路径 A]
python3 scripts/srt_parser.py <srt> --out timeline.json
         ↓
python3 scripts/clip_merger.py timeline.json --user-tts <TTS秒数>
         ↓
[获得 clips.json: 每个 clip 含精确起止 + 段列表 + 内部停顿]
         ↓
[Step 5 v8.1 模板手写 prompt]
- 段 1: 主体+视觉基底+@ImageN
- 段 2: 主体动作序列 (按事件分镜, 镜头 1/2/3, 不卡秒数)
- 段 3: 关键节点对照 (念到 X 词时 Y 动作, 不写精确时间戳)
- 段 4: 收尾不凝固 (镜头 N 收尾: 保持运动 + 呼应开场)
         ↓
[Step 5.5 验证]
python3 scripts/verify_prompt.py  # v5.0.9 8 项 + v5.0.10 新增 3 项
         ↓
delegate agents/prompt-reviewer/  # L3 视觉逻辑审查
         ↓
[Step 6 seedance 提交]
```

### 8.3 速率反推示例(生菜 SRT)

```
v5.0.9 默认: 4.0 字/秒 + 1.4 词/秒(领读短句档)
v5.0.10 反推(剔除停顿后): 1.78 字/秒 + 0.36 词/秒

偏差 125% — v5.0.9 估算路径严重失真!
v5.0.10 SRT 路径直接用真实速率校准 → prompt 时间锚点跟旁白 1:1 对齐
```

### 8.4 段间停顿语义(v5.0.10 修正)

**v5.0.9 假设**: pause_after >= 0.8s = "画面切换点"

**v5.0.10 修正**: 段间停顿只是朗读节奏,不是画面切换信号。生菜 SRT 7 个段间停顿全 >= 0.8s,但都是"领读型设计意图",不应自动当切换点。

**正确语义**:
- < 0.3s: 紧接(段间无间隔)
- 0.3-0.8s: 呼吸停顿(主体可微动过渡)
- >= 0.8s: 段间停顿(主体可微动 / 镜头可微摇 / 保持运动感)

**不**自动作为"画面切换点"。画面切换由 `clip_merger.py` 根据 [4,15] 区间和段间停顿**综合判断**。

### 8.5 跟 v5.0.9 的兼容性

- **有 SRT**: 走路径 A(v5.0.10 精确模式, 容差 1s)
- **无 SRT**: 走路径 B(v5.0.9 估算模式, 容差 5s)— 仅作为 fallback
- **v8 → v8.1**: 4 段结构不变,但段 2/段 4 必须按 v8.1 新写法(动作序列 + 不凝固收尾)
- **反模式 R1-R5**: verify_prompt.py 新硬规则,v8.1 prompt 必走检查