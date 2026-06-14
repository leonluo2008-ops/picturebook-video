---
name: picturebook-video
description: "绘本转儿童动画视频的标准制作流程。接收绘本简介 + 图片 + 旁白 → 通读旁白标叙事弧合并到 3-5 Clip（导演分镜·1 个故事 = 1 个 Clip·不按图分段）→ fill v15/v6 5 段模板（B 档音效默认）→ seedance 提交 `--generate-audio true` + `--ref-images` 多图 → 端到端验证。默认 16:9 · 整数时长 · 视频总时长 = 用户给 TTS + 5s 冗余（不缩短）· 单 Clip ≤ seedance 15s 物理上限 · 静默按故事连贯编排（不是铁律）· vision 必跑全 N 张图 · **绝对不用首尾帧范式**（v7/v3/v8 · `--image`+`--last-frame` = 用户元偏好的绝对约束）。触发词：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, storyboard, fill-v15, seedance, director-cut, ref-images, no-silence-mandatory, vision-all-mandatory, tts-user-priority, no-first-last-frame]
  related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool, picturebook-creator]
  toolkit_role: picturebook-video-orchestrator
---

# picturebook-video · 绘本视频标准制作流程

|> **当前唯一标准做法**——任何绘本按此跑。绘本做完 skill 不变（不在 SKILL.md 加铁律"XX 绘本踩坑"、不开新分支、不绑版本号、不绑绘本名）。

## 📚 长期积累机制（蒸馏法 · 2026-06-14 沉淀 · 必走）

> **核心问题**：绘本踩坑笔记全堆 skill 仓 = 半年后 token 爆炸 + 污染源头 + "建议升级铁律"反复发生。**长期积累 ≠ 业务数据堆仓 = 跨本验证 → 升铁律**。

### 三层架构（业务/work/通用方法论 分层）

| 层 | 位置 | 内容 | 命名 | 寿命 |
|---|---|---|---|---|
| **业务层** | `~/.hermes/profiles/huiben/work/<日期-绘本名>/` | 每本绘本的踩坑、prompt 迭代、vision 笔记 | 含日期+绘本名 | 永远在（**不入** skill 仓）|
| **方法论层** | `references/<通用名>.md` | 跨本验证 ≥ 1 次的通用方法论 | 通用名（**不含**绘本名/日期/vX.X+picN）| 永久 |
| **铁律层** | `SKILL.md` 顶部纠错表 | 跨本验证 ≥ 3 次的硬规律 | 通用名 | 永久 |

### 跨本验证升铁律机制（3 次原则）

```
绘本 A 跑完 → work/A/notes.md 标 "X 规律第 1 次"（业务层）
绘本 B 跑完 → work/B/notes.md 标 "X 规律第 2 次"
绘本 C 跑完 → work/C/notes.md 标 "X 规律第 3 次"
        ↓
跨本验证 ≥ 3 次 = 升 SKILL.md 铁律（铁律名 = 通用名）
        ↓
升铁律时同步：
- 在 references/ 加 1 份 <通用名>.md（记录 A/B/C 实战证据）
- 删除 3 份 work 笔记里的踩坑细节（蒸馏到 references/）
- 0 绘本名 / 0 日期 / 0 vX.X+picN 标签
```

### 反模式（不蒸馏 = 污染）

- ❌ **绘本 A 踩坑 → 直接写 references/A-validation.md** = 业务数据进 skill
- ❌ **单本绘本规律没跨本验证 = 升 SKILL.md 铁律** = 凭印象升级
- ❌ **"v1.0.5+picN" / "2026-06-14-XX 绘本"** 命名 = 业务标签污染通用方法论
- ❌ **绘本做完不写 work 笔记** = 业务数据丢失（下次跑没参考）

### 自检命令（绘本完成时必跑）

```bash
# 0 绘本名残留（除方法论层通用名）
grep -rE "(特定绘本名|2026-\d{2}-\d{2}-[a-z]+|v\d+\.\d+\+pic\d+)" \
  /home/luo/.hermes/profiles/huiben/skills/creative/ \
  --include="*.md" --include="*.py" --include="*.txt" \
  | grep -v "/work/" | grep -v "references/versions/"
# 期望：方法论层文件 = 0 绘本名 / 0 日期 / 0 版本号
```

---

## ⚠️ 用户 7 个根本性纠错（必读）

> 任何绘本进来 = **必读下面 8 条** · 违反任一条 = 翻车 · 详细 + 修复 SOP 见 `references/six-roots-correction.md`（纠错 1-6）+ `references/scene-jump-v7-correction.md`（纠错 7）+ `references/tts-rate-calibration-workflow.md`（纠错 8）

| # | 纠错 | 用户原话（关键） |
|---|---|---|
| 1 | **数字方案必查物理约束** | "**你竟然写出了 18 秒的 clip，这肯定是有问题的，这是一个严重问题**" |
| 2 | **vision 必全 N 张图（不抽样）** | "**必须识别所有的图片，而不是只识别部分图片**" |
| 3 | **画面时长匹配旁白时长** | "**你要保证那句话和画面能够基本上匹配上**" |
| 4 | **静默 = 编排工具不是铁律** | "**应该根据编排的故事来合理的设置有静默或者没有静默，不是每一个都要去静默的**" |
| 5 | **1 个故事 = 1 个 Clip（不按段拆）** | "**应该把参考图和旁白该合并成一个 clip 的，就要合并成一个 clip**" |
| 6 | **家族词组中文 TTS 必算** | "**你在计算家庭词组的时候是不是没有计算中文的阅读时间？**" |
| 7 | **多图参考必拆 Clip**（蒙太奇装不下长旁白）| "**图五对应的是旁白五，你觉得两秒钟可以把旁白五那句话读完吗？**" → 接受拆 Clip = 蒙太奇 2s 末帧装不下 7s 旁白 = 黑场翻车 |
| 8 | **TTS 速率方案必校对**（3-5s 容忍范围 · 差过大重算）| "**如果差别不大，比如多三五秒或刚好，说明计算方式正确。如果差别过大，就需要衡量计算方式**" → 算出总旁白 vs 用户给 TTS，差 3-5s = 正常 · 差 ≥ 5s = 必重算 1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿 速率公式 |
| 9 | **信任参考图 + 关键引导而非过度约束**（2026-06-14 绘本 沉淀）| "**视频模型可以非常好地理解参考图，如果给它参考图，提示词方面只需要做好一些关键引导就可以了，不需要描述得很详细，我们可以相信视频模型，它会自然地根据参考图结合关键指令去生成非常好的画面**" → 关键指令 = 时间点、运镜、声音 + 末帧约束 + 风格词 · 不需要描述每一个细节（每个肢体角度/每秒动作）· 让模型自由组织 |
| 10 | **不把"建议"升级成"红线"**（2026-06-14 绘本 沉淀）| "**模型对时间精确是很稳定的，很准的。这条资料肯定不是官方文档里的吧？**" + "**官方的意思只是不要在同一个时间点强行塞入很多镜头和动作**" → 官方语气分 4 档（必填正文 / 红线红框 / 建议小字 / 示例案例）· "不强制"≠"禁止"· "可能"≠"必然"· 引用官方原话必先回原文档 grep 验证 + 标注 4 维属性（原文+位置+语气+上下文）|
| 11 | **写 prompt 前 = 必先 vision 参考图**（2026-06-14 绘本 沉淀）| "**写提示词时要预测参考图画面接下来可能发生的事情，根据推测顺着画面发展的方向去写，而不是凭空捏造**" → 写前必 vision 全 N 张图 + 列"图里有/没有"清单（写到 image-inventory.md）· prompt 里的每个名词必须在"有"列里· "没有"列里的元素 = 凭空捏造 = 必删|
| 12 | **凡引用官方原文 = 必逐字核对**（漏字根因·2026-06-14 绘本 沉淀）| "**我说的是运镜，不是动作。1 镜多动作 OK**" → 把"**1 种运镜方式**"读成"**1 动作**" = 漏 4 字 = 错全意· 凡引用官方原话 = 必带 4 维属性（原文+位置+语气+上下文）· "漏 1 字 = 错全意 · 缩 1 句 = 断章取义 · 凭记忆 = 翻车"|
| 13 | **跳过有问题的参考图 = 复用 + 描述延伸**（2026-06-14 绘本 沉淀）| "**@image3 本身就有问题……第三个镜头仍然用参考图二，描述这只鸭子在水里游泳就可以了**" → 跳过冲突图 = prompt 里不引用 + ref_images 也不传 + 复用 @ImageM + 描述"自然延伸"（"参考 @ImageM 的同一只鸭子，镜头继续中景跟拍，鸭子从浮水状态开始游动"）· "3 镜头 = 3 张图"是死规则**已废**|
| 14 | **"不要 X 不要 X" = 约束词污染**（2026-06-14 绘本 沉淀）| "**负面的不要什么不要什么不要什么，你根本就没有必要……会污染模型**" → 约束词只对"已知出错元素"用（字幕/Logo/水印 3 类）· 4 词末尾约束（无人声/无歌唱/无配音/无朗读）是绘本专用 = **已确认保留，不开问卷** · 泛泛堆"无 X / 不要 X" = 污染模型|
| 15 | **MCP timeout ≠ 任务失败**（2026-06-14 绘本 5 次跑沉淀）| 5 个版本（v1-v5）每次 `wait_and_download` 都报 `MCP call timed out after 120.0s` · 实际是 seedance 14s 720p 视频生成需要 5-15 分钟 · **status 才是唯一权威**（不是 timeout）· 已发任务 = 已扣费 = 必查 status + 单独 download，**绝不重提交**（同 Seedance 2.0 红线）|

**铁律口诀**：**"凭印象 = 翻车 · 必查必算 = 标准 · 过度约束 = 僵硬 · 信任参考图 = 自然 · 漏字断章 = 错全意 · 建议 ≠ 红线 · 凭空捏造 = 必删 · 不要 X 堆砌 = 污染 · MCP timeout ≠ 任务失败"**

---

## 🎯 3 个必读决策树（2026-06-14 绘本实战沉淀 · 用户明确要）

### 决策树 1 · Clip 时长计算（必按优先级走 · 不凭印象）

```
用户给 TTS 数值？
├─ 是 → 视频总时长 = 用户给 TTS + 5s 冗余（不缩短）
└─ 否 → 兜底公式：1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿
        ↓
每 Clip 时长 = 整数（5/6/7/8/9/10/11/12/13/14/15）· 必查 schema
        ↓
单 Clip ≤ 15s 物理上限（seedance API 硬约束）
        ↓
> 15s 必拆 Clip（拆依据 = image-inventory "场景跳变"列）
        ↓
> 15s 必报"拆 2 个 ≤ 15s"方案 · 不报"18s"方案给用户
```

**反模式**（必避）：凭印象写 Clip 时长 = 写出 18s = 严重违规

### 决策树 2 · Prompt 写法（按事件拆 vs 按秒数拆 · 两种都允许）

```
首次跑（无翻车数据）
└─ 按事件拆（镜头 1 / 镜头 2）= 官方首选 + 命中"少约束"思路

按事件拆翻车了（动作在切点抽搐）
└─ 改按秒数拆（0-3s xxx / 3-6s yyy）= 显式约束模型

按秒数拆也翻车
└─ 回到按事件拆 + **每镜 ≤ 2 动作**（1 主 1 辅）

按秒数拆成功
└─ 沿用 · 不为换而换
```

**关键判断**：翻车真凶 = **动作堆砌**（4 动作一句塞）≠ "按秒数"。两种写法都允许，看实战。

### 决策树 3 · 约束红线（必保留 · 4 类 · 不开问卷）

```
绘本 prompt 末尾约束（必含 4 类 · 4 行精简单行）
├─ 1. 保持无字幕（官方原话 · L1 红线 · 防字幕）
├─ 2. 不要生成水印（官方原话 · L1 红线 · 防水印）
├─ 3. 不要生成 Logo（官方原话 · L1 红线 · 防 Logo）
└─ 4. 无人声、无歌唱、无配音、无朗读（4 词末尾约束 · 绘本专用 · 已确认保留）

约束词只对"已知出错元素"用（字幕/Logo/水印 3 类官方原话）
   ↓
❌ 泛泛堆"无 X / 不要 X / 只保留 Y" = 污染模型 = 必删
   ↓
✅ 4 行末尾约束 = 绘本场景标准 · 不开问卷
```

**判断口诀**：约束词 = "**3 类官方原话 + 4 词绘本专用**" = 4 行 = 标准。其他"无 X" = 必删。

**详见** `references/official-quote-4-levels.md`（4 档分级法 · 凡引用官方原话前必跑 3 问）

**核心方法论**（一句话）：

**通读旁白 → 标叙事弧 → 合并到 3-5 Clip（导演分镜）→ fill v15/v6 模板（关键引导为主，不堆细节）→ seedance 跑出视频**

**信任参考图原则**（2026-06-14 绘本沉淀 · 元纠错 #9）：

视频模型能非常好地理解参考图。**prompt 只需要做好关键引导**（时间点、运镜、声音、末帧约束、风格词），**不需要描述每一个细节**。

- **必须约束**（关键引导）：① 镜头运动（推/拉/摇/切，每镜 1 种）② 末帧微动（不变成定格海报）③ 声音策略（无 BGM / 拟声）④ 文字保留 / 风格锁 ⑤ 大动作（鸭子游动 / 起飞 / 张嘴）
- **让模型自由组织**（不约束）：① 角色每个肢体的具体动作（翅膀朝后还是朝前、几度、几秒）② 表情的微变化 ③ 头发/羽毛/水花的物理细节 ④ 镜头内具体的秒数切分（官方原话："模型对精确时间支持不稳定"）

**反模式**：prompt 写 5+ 句动作描述塞 1 个镜头 = 5 个动作里必有 2 个跟参考图姿态冲突 = 模型二选一时抽 = 动作僵硬 / 抽搐 / 跟参考图姿态对不上

**修复**：每镜头 1-2 个核心动作（"鸭子继续向前游"）+ 让模型照参考图自己组织细节 = 自由发挥 = 自然连贯

**官方背书**（seedance doc2 §1.3 · line232-237）："**模型对精确时间（如 0–3 秒）的支持不稳定，强行限制时长可能导致生成结果异常**" + 实战案例 line320-389 官方案本**根本不写秒数** = 印证"信任参考图 + 让模型自由组织"是官方推荐写法

详见 `references/prompt-minimalist-principle.md`（2026-06-14 沉淀 · 5 个反模式 + 5 个修复 + 官方原话 4 处）

**6 个反直觉点**（必记 · 不重复于上方纠错表）：
1. **不按图分段**（8 张图 ≠ 8 Clip）· 通读旁白后按叙事弧合并（导演分镜）
2. **绝对不用首尾帧范式**（v7/v3/v8 范式 · `--image`+`--last-frame` = 用户元偏好"绝对不用"）= 默认 v15 4 段 / v6 5 段 + `--ref-images` 多图参考
3. **整数时长 + 视频总时长 = TTS + 5s 冗余**（不缩短）· 单 Clip 不超过 seedance 15s 物理上限
4. **画面时长 = 旁白 TTS 总和**（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿 · 必算 + 必跟用户给 TTS 校对 · 差 3-5s = 正常 · 差过大 = 重算速率）
5. **静默 = 编排工具不是铁律**（按故事连贯性决定 · 故事连贯 = 0 静默 · 视觉断点 = 短静默 · 不硬塞 ≥ 2s）
6. **绘本做完 skill 不动** · 全部产物在工作目录（`~/.hermes/profiles/huiben/work/<日期-绘本名>/`）

---

## 7 步标准流程

```
Step 1 · 接收需求（绘本简介 + 图片 + 旁白 + 目标平台 + TTS 数值）
   ↓
Step 2 · **2.0 必先列"图里有/没有"清单**（写到 image-inventory.md）+ 2.1 vision 自检全 N 张图（必全·不是抽样）+ 通读旁白 + 标叙事弧
   ↓
Step 3 · 合并到 3-5 Clip（导演分镜·1 故事 = 1 Clip）+ 算 TTS 时长 + 整数时长分配
   ↓
Step 4 · 写 11 维 JSON（≤ 4 Clip 主 agent 直干 / > 4 Clip 调 C 子 agent）
   ↓
Step 5 · fill v15/v6 模板（段 4 B 档默认 + @Image 空格语法 + char_floats 动态）
        ↓
        **5.5 · 必跑 `scripts/verify_filled_prompts.py <clips_dir>` 验证 4 项**（不靠"上次我修过"记忆）
   ↓
Step 6 · seedance 提交（--generate-audio true + --ref-images 多图 + 整数时长）
   ↓
Step 7 · 端到端验证 → 发飞书 + 完整证据链
```

---

## Step 1 · 接收需求

**必收 4 件事**：
1. **绘本简介**（故事简介 + 旁白文本）
2. **绘本图片**（本地路径 / 飞书云盘链接 / 附件 · PNG/JPG 都行）
3. **目标平台**（抖音 / 小红书 / 视频号 / B 站）
4. **TTS 数值**（用户给 = 视频总时长基准 = 必收；不给 = 兜底公式 1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）

**文件用途澄清**（不解就问，不假设）：
- `*.mp3` → 问"TTS 干声 / 完整音频 / 不用？"
- `*.xlsx` → 读 schema 确认结构
- `0.jpg` → 问"封面 / logo / 不用？"
- `readme.txt` → 读内容，不当数据源（GBK 编码常见，必 force decode）

---

## Step 2 · vision 自检 + 通读旁白（**必全 N 张图**）

**2.0 image-inventory 必含"有/没有"两列**（**2026-06-14 绘本 元教训 #11 强化版**）：

```markdown
# 图 | 风格 | **有** | **没有**（警告·prompt 误写会翻车）| 文字 | 动作 | 场景跳变
1 | 3D 折纸 | 1 只黄鸭·草地·纸艺 | 小鸭·荷叶·水·歪头·水花 | 顶部大字 | 站草地 | 草（独立）
2 | 3D 折纸 | 1 只黄鸭·水面静态蓝圈波纹 | 小鸭·荷叶·水花·歪头 | 顶部大字 | 浮水面·转头 | 水（连续）
3 | 3D 折纸 | 1 只黄鸭·踏浪姿态·蓝色水花 | 小鸭·荷叶·游泳·歪头 | 顶部大字 | 踏浪/跑步 | 水（连续·但姿态跟"游泳"主题冲突·**#13 跳过此图**）
```

**判定**：
- prompt 里**每个**名词必须在"有"列里 = 不凭空捏造
- "没有"列是**警告**——写 prompt 时**必**避免出现
- 任何"有"列元素都被某镜头引用 = 0 浪费

**反模式**（绘本 v1 v2 翻车）："4 只鸭立荷叶"——4 只鸭 / 荷叶 / 歪头 都不在"有"列 = 凭空捏造 = 必删

**2.1 vision 必跑·必全**（native vision·**全 N 张图必看光**）：

| vision 状态 | 动作 |
|---|---|
| 全成功 | 继续 |
| 部分失败 | 立即重试失败的 1 张验证（临时过载 vs 真挂） |
| 全部失败 | **立即降级**——不依赖 vision，凭简介+兜底描述走主 agent 直干 |

**⚠️ 必看全 = 全部 N 张图 = 标准**（不是抽样 1/N/中/末）。**只识别部分图 = 凭印象拼 prompt = 翻车征兆**。收到 8 张图 = vision 8 次 · 1 张都别跳。

**每图必看的 7 维**（缺 = prompt 拼错）：
1. 风格类型（彩纸拼贴 / 水彩 / 平面矢量 / 3D 毛毡 / 2D 卡通 / 3D 折纸拼贴）—— 决定 prompt 风格词
2. 主体数量（1 颗 / 2 颗 / 1+鸟 / 1+3 小 / 1+truck）—— 决定主体描述
3. 背景色调（米黄 / 青绿 / 草绿 / 蓝水 / 混合）—— 决定 prompt 背景描述
4. 文字是否在画面（顶部 1/2 居中 / 1/6 / 散落 / 角字卡 / 无文字）—— 决定是否让字母动画
5. **主体动作**（duck 游 / 跳 / 站 / 排队 / 看 truck / 张嘴 quack）—— 决定是否需要拟声
6. **场景跳变**（水 → 陆 = 跳变 · 同色系 = 连续）—— 决定是否拆 Clip
7. **主体对位**（多图合并时多主体关系：duck vs truck / 大鸭 vs 3 小鸭）—— 决定段 2 镜头拆分

**合并前必记表**（写到 `~/.hermes/profiles/huiben/work/<项目>/image-inventory.md`）：

```markdown
# 图 | 风格 | 主体 | 背景 | 文字 | 动作 | 场景跳变
1 | 3D 折纸 | 4 鸭家族 | 蓝水 | 顶部大字 | 站荷叶 | 水
2 | 3D 折纸 | 1 大鸭 | 蓝水+柳 | 右下字卡 | 单立 | 水
3 | 3D 折纸 | 1 大鸭 | 蓝水+浪 | 左上字卡 | 向右游 | 水
4 | 3D 折纸 | 1 大鸭 | 蓝水 | 顶部字 | 准备动作 | 水
5 | 3D 折纸 | 1 鸭+1 truck | 草地+土路 | 左上字卡 | 并排 | **陆（跳变）**
6 | 3D 折纸 | 1 大+3 小 | 蓝水 | 左上字卡 | **排队跟随** | 水
7 | 3D 折纸 | 4 词字卡 | 浅色 | 4 词大字 | 展示 | 字卡
8 | 3D 折纸 | 3 鸭戏水 | 蓝水+荷叶 | 顶部大字 | 戏水 | 水（收势）
```

**2.2 通读旁白 1 遍**：

把整本旁白读一遍，**标出叙事弧**（故事起伏）· 不要看图分段（**通读优先于按图**）。

**叙事弧模板**（3 弧）：
- 唤醒+观察 → 感知+行动 → 反馈+情感
- 引入 → 冲突 → 解决
- 看到 → 想到 → 做到

---

## Step 3 · 标叙事弧 → 合并到 3-5 Clip（**导演分镜**·核心步骤）

**3.1 合并决策树**：

```
通读旁白 → 标叙事弧
   ↓
弧的数量 = N（N 通常 2-4）
   ↓
每个弧 = 1 个 Clip（每 Clip 装 1-3 张图）
   ↓
N=3 → 3 Clip（最常见·甜区）
N=4 → 4 Clip
N=2 → 2 Clip（极简绘本）
N>5 → 合并叙事弧到 5 Clip 以内
   ↓
   ↓
Step 3.2 算 TTS 时长（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿·用户给 TTS 优先）
   ↓
Step 3.3 整数时长分配（每 Clip 时长 = 装得下对应故事段 TTS + 视觉延展）
   ↓
**每 Clip 时长硬上限 ≤ 15s**（seedance duration 物理上限·API 拒收 > 15s）
**> 15s 必拆**（拆成 2 个 ≤ 15s Clip）· 拆依据看 image-inventory 的"场景跳变"列
   ↓
**视频总时长 = 用户给 TTS + 5s 冗余**（不缩短·按用户原则）
   ↓
静默按故事连贯性编排（不是每段必塞 ≥ 2s 末帧静默）
```

**3.2 算 TTS 时长（**必算**·用户原话 6 个根本性纠错）**：

| 速率 | 公式 | 用途 |
|---|---|---|
| **用户给 TTS** | 必收· = 视频总时长基准 | **优先级最高**·视频总时长 = TTS + 5s 冗余 |
| **自然速率**（兜底）| **1.0 词/秒（英文）+ 3 字/秒（中文）** | 每段 TTS 估算 = 词数/1.0 + 字数/3.0 |
| **词间停顿** | **0.5s/词间隔**（家族词组 4 词 = 6 个 0.5s = 3s 停顿）| 必加在家族词组 / 多词集合段 |
| ~~1.4 词/秒 兜底~~ | ~~不用~~ | ~~过快估=漏算中文+漏算停顿=实际 TTS 翻 1.5-2 倍~~ |

**计算示例**（8 段旁白 · 用户给 TTS 50s · 真实算）：

| 段 | 英 | 中 | 词 | 字 | 词间停顿 | TTS(自然) |
|---|---|---|---|---|---|---|
| 1 | DUCK! | 鸭子 DUCK！ | 1 | 4 | 0 | 1.67s |
| 2 | A yellow duck. | 黄色的鸭子 | 3 | 4 | 0 | 4.67s |
| 3 | The duck swims. | 鸭子在游泳 | 3 | 4 | 0 | 4.67s |
| 4 | The duck quacks! | 鸭子嘎嘎叫 | 3 | 4 | 0 | 4.67s |
| 5 | A duck and a truck. | 鸭子和小卡车 | 5 | 5 | 0 | 7.00s |
| 6 | Ducklings follow the duck. | 小鸭子跟着鸭妈妈 | 4 | 7 | 0 | 6.67s |
| 7 | duck, truck, luck, buck | 鸭子 duck 的 UCK 家族，duck、truck、luck、buck 大集合！ | 8 (4+4 重复) | 8 | 6 (0.5s × 6) | **13.67s** |
| 8 | Count the ducks! | 数数鸭子 | 3 | 4 | 0 | 4.33s |
| **总和** | — | — | — | — | — | **47.35s** |

**3.3 整数时长分配**：

| 段 | TTS | 拟时长 | 冗余 |
|---|---|---|---|
| 1+2+3 | 11.01s | 12s | +0.99s（故事开头） |
| 4+5 | 11.67s | 13s | +1.33s（押韵词对过渡） |
| 6 | 6.67s | 8s | +1.33s（家庭情感收） |
| 7（UCK 家族）| 13.67s | 15s（物理上限）| +1.33s（领读末帧）|
| 8 | 4.33s | 7s | +2.67s（收势延展）|
| **总和** | **47.35s** | **55s** | +7.65s（≈ 5s 冗余）|

**55s = 用户给 50s + 5s 冗余** · 全部 ≤ 15s ✅ · 整数时长 ✅

**⚠️ 数字方案必查物理约束**（用户元偏好 · 严重违规红线）：
- 写"X 时长 Clip"前**必查** seedance duration schema（`minimum=4, maximum=15`）
- 凭印象编数字 = 严重违规 = 必自查
- 例：算出来某 Clip 需 18s = 必拆成 2 个 ≤ 15s · **不**报"18s"方案给用户

**⚠️ 场景跳变 = 拆 Clip 规则**（image-inventory 第 6 列必查）：
- **同色系同背景**（连续水/连续陆/连续字卡）= 可合并
- **场景跳变**（水 → 陆 / 陆 → 字卡 / 水 → 字卡）= **必拆**（镜头跳变感强 = 不适合合并）
- 例：图 4（水）+ 图 5（陆 = 跳变）+ 图 6（水）= 拆 2 个 Clip（图 4+5 跨场景 / 图 6 独立家庭队列）= 不强求合并

**实拍案例**（8 张图 8 段旁白 → 5 Clip 合并）：

| Clip | 涉及图 | 叙事弧 | 时长 | 场景 | 声音档 |
|---|---|---|---|---|---|
| 1 | 1+2+3 | 唤醒+观察+游动 | 12s | 蓝水（连续）| B |
| 2 | 4+5 | 行动+认知 | 13s | 水+陆（跳变合并）| B |
| 3 | 6 | 家庭情感（ducklings 队列独立）| 8s | 蓝水+队列 | B |
| 4 | 7 | UCK 家族 4 词集合 | 15s（物理上限）| 字卡（独立）| **C** |
| 5 | 8 | 数数收势 | 7s | 蓝水+3 鸭戏水 | B |
| **总计** | 8 张全用 | — | **55s** | — | — |

| 7 类必走（不可省）

## Step 4 · 写 11 维 JSON

**Clip ≤ 4**：主 agent 直干（不调子 agent）
**Clip > 4**：调 C 子 agent 产原料 JSON

**11 维 JSON 必填字段**（每 Clip 一个）：

```json
{
  "clip_id": 1,
  "image_files": {
    "first_frame": "1.jpg",
    "last_frame": "3.jpg"
  },
  "narration_text": {"en": "Mango! Look!", "zh": "芒果！看！"},
  "image_index": "1+2+3",
  "subject_definition": "single yellow mango character with smiling face",
  "background_description": "warm cream background with soft yellow gradient",
  "style_keywords": "2D cartoon, webtoon style, high saturation, warm colors",
  "shot_sequence": [
    {"start": 0.0, "end": 4.0, "shot": "camera holds on the smiling mango, gentle breathing pulse"},
    {"start": 4.0, "end": 8.0, "shot": "camera slowly pushes in, the mango waves a tiny hand"},
    {"start": 8.0, "end": 10.0, "shot": "final frame: the mango smiles brightly, soft warm light glows"}
  ],
  "end_frame_microaction": "the mango keeps gently breathing with a soft smile for 2s",
  "text_visibility": {
    "en_word": "Mango",
    "zh_word": "芒果",
    "color_en": "bright red",
    "color_zh": "鲜艳红色",
    "full_clip_visible": true,
    "micro_animation": "breathing pulse 0.5s/cycle + character-order float (M→a→n→g→o)"
  },
  "sound_strategy": "B"
}
```

**sound_strategy 档位**（声音维度分支·不破坏 4 维核心）：

| 档位 | 触发 | seedance 参数 | 段 4 写法 |
|---|---|---|---|
| **A** | 不使用（**不推荐·全静音翻车**）| `--generate-audio false` | — |
| **B 默认** | 普通短句/单词 | `--generate-audio true` | 无 BGM + 允许并保留画面元素动作音效 |
| **C** | 家族词组（≥3 同字母家族）/ 长句（words_en≥5）| `--generate-audio false` + `--audio tts.mp3` | 不发音·保留 TTS 音轨占位·时长匹配 |

---

## Step 5 · fill v15/v6 模板

**v15 4 段骨架**（默认·无文字持续可见需求）：

```
段 1 · 主体定义（含 @ImageN 引用 + 风格锚定词）
段 2 · 分镜绑定（@Image1 + @Image2 + @Image3 多图参考）
段 3 · 分镜描述（含拟声 + 镜头运动 + 末帧微动）
段 4 · 风格 + BGM（B 档默认 = 无 BGM + 允许音效 + 无朗读人声）
```

**v6 5 段骨架**（有顶部文字·领读型）：

```
段 1 · 主体定义
段 2 · 分镜绑定
段 3 · 分镜描述
段 4 · 风格 + BGM
段 5 · 文字持续可见段（全程可见 + 呼吸动画 + 字符顺序浮现）
```

**标准工具**：`scripts/fill_v15_template.py`（主 agent 必用·不手写 prompt）

**约束词精简铁律**（**2026-06-14 绘本 元教训 #14 · 绘本末尾约束标准**）：

末尾约束**只**写 3 类官方原话 + 4 词绘本专用 = **4 行精简单行**：

```python
# ✅ 标准末尾约束（4 行 · 必按此写）
保持无字幕。
不要生成水印。
不要生成 Logo。
无人声、无歌唱、无配音、无朗读。

# ❌ 泛泛堆砌（污染模型 · 必删）
保持无字幕、无水印、无 Logo，无人声、无歌唱、无配音、无朗读。
音效只保留环境细节：水花声、纸页翻动等短促物理声。
全程无背景音乐。
```

**判定**：约束词只对"已知出错元素"用（字幕/Logo/水印 3 类）· 泛泛"无 X / 不要 X" = 必删 · 4 词末尾约束 = **已确认保留，不开问卷**

**4 词末尾约束的官方背书**（doc2 §5 · "常用约束词模板"）：官方原话是 4 类（字幕/Logo/水印）+ 1 句"全程无 BGM"——绘本场景 BGM 红线（不生成）= 默认 · 但**不**写进 prompt 末尾约束段

**fill 完必查 4 项**（防止 fill 脚本 bug）：

| 检查 | 期望 |
|---|---|
| 0 双重前缀 | `grep -c "@Image@Image" clip*-prompt.txt` = 0 |
| @Image 空格语法 | `grep "@Image1 + @Image2 + @Image3" clip*-prompt.txt` ✅ |
| 段 4 B 档音效版 | 找 "无 BGM" + "音效" 字样（不是 A 档"无任何背景音乐、无旁白人声、无哼唱"）|
| char_floats 动态 | `grep "M(0.3s) → a(0.6s)" clip*-prompt.txt` ✅ 按 en_word 字母数生成 |
| **@ImageN 引用数 = ref_images 实际传图数**（**2026-06-14 绘本 元教训 #13 强化**）| `grep -oE "@Image[0-9]" clipN-prompt.txt \| sort -u` 的结果数 ≤ `len(ref_images)`（不引用未传的图 = 不凭空捏造）|
| **末尾约束 ≤ 4 行**（**2026-06-14 绘本 元教训 #14 强化**）| 末尾约束段不超过 4 行（"保持无字幕。不要生成水印。不要生成 Logo。无人声、无歌唱、无配音、无朗读。"）· 泛泛"音效只保留环境细节" / "全程无背景音乐" = 必删|

**一键验证脚本**（**主 agent 必用·不手敲 4 个 grep**）：

```bash
python3 ~/.hermes/profiles/huiben/skills/creative/picturebook-video/scripts/verify_filled_prompts.py <clips_dir>
```

退出码 0 = 4/4 全过 · 1 = 任 1 项失败。详细检查项 + 修复路径见 `references/verify-filled-prompts.md`。

---

## Step 6 · seedance 提交

**每 Clip 必传参数**：

```python
mcp_seedance_generate_video(
  prompt=<fill 出的 prompt 文本>,
  ref_images=["/abs/path/1.jpg", "/abs/path/2.jpg", "/abs/path/3.jpg"],
  duration=<整数 · 5-15>,
  ratio="16:9",
  watermark="none",
  generate_audio=True,  # B 档·B 档默认必传 true
  resolution="720p",
  model="doubao-seedance-2-0-fast-260128"
)
```

**关键约束**：

| 约束 | 规则 |
|---|---|
| 整数时长 | 设计时长 = 整数（5/6/7/8/9/10/11/12/13/14/15）· seedance 不生成小数 |
| 单 Clip 上限 | ≤ 15s（seedance 物理上限） |
| 视频总时长 | = 用户给 TTS + 5s 冗余（不缩短·用户原则）|
| @Image 语法 | `@ImageN + @ImageM` 带空格（不带空格 = 错） |
| 多图参考 | `--ref-images`（**绝对不用** `--image`+`--last-frame` 首尾帧范式·除非用户明确指定 · 用户元偏好的绝对约束）|

**单 Clip 端到端验证**（必走·铁律）：
1. 提交 1 个 Clip
2. 等 succeeded
3. 下载 + 本地 `md5sum` 验证
4. 发飞书用户目检
5. **等用户确认 OK** → 再批量跑剩下

**反模式**：
- ❌ 跑完 1 个 Clip 自动连跑剩下（没用户目检 = 翻车无拦截）
- ❌ 8 个 Clip 一次跑（D timeout 风险）
- ❌ 视频 < TTS（音频多出没画面 = 黑场翻车）
- ❌ **用首尾帧范式**（`--image`+`--last-frame` = 用户元偏好"绝对不用" · 用 v15/v6 多图参考 = 拆 Clip 单图独立）

---

## Step 7 · 端到端验证 + 发飞书

**发飞书前必查**：

```bash
# 1. 本地 stat + md5
ls -lh clips/clip*.mp4
md5sum clips/clip*.mp4

# 2. 验证整数时长（ffprobe）
for f in clips/clip*.mp4; do
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f"
done
```

**发飞书模板**：

```
[绘本名] 视频已生成：

[MEDIA:/abs/path/clips/clip1.mp4]
[MEDIA:/abs/path/clips/clip2.mp4]
[MEDIA:/abs/path/clips/clip3.mp4]

📊 元数据：
• 总时长：55s（5 个 Clip · TTS 50s + 5s 冗余）
• md5 唯一 0 错位
• 整数时长 100% 命中
• 涉及图：8 张全用
• 声音档：1/2/3/5 = B（普通短句）· 4 = C（UCK 家族）

需要我改什么吗？
```

**核心原则**：
- ✅ 一次发完整组视频（不拆开发）
- ✅ 必附完整证据链（md5 + task_id + 涉及图）
- ✅ 不主动抽帧自检（vision 是辅助不是真理·等用户目检）
- ❌ 不发飞书云盘兜底链接（用户没要求）

---

## 7 类必走（不可省）

| # | 步骤 | 不可省原因 |
|---|---|---|
| 1 | **vision 全 N 张图必看光**（不抽样）| 防止主体数量/背景色/文字位置/动作/场景跳变 凭印象拼错（用户原话"必须识别所有的图片"）|
| 2 | **通读旁白 + 标叙事弧** | 防止按图分段=8 Clip 翻车 / 按段机械拆=段数 ≠ Clip 数 |
| 3 | **算 TTS 时长（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿·用户给 TTS 优先）** | 防止家族词组中文漏算（"你明显没有把时长计算进去"）|
| 4 | **主 agent fill 完必查 @Image 语法 4 项** | 防止双重前缀 + char_floats 硬编码 + 段 4 误用 A 档 |
| 5 | **提交 seedance 必传 `--generate-audio true`** | 防止 v1 全静音翻车（B 档默认）|
| 6 | **单 Clip 端到端验证 + 用户目检** | 防止跑完 4 个 Clip 才发现在 v1 错 |
| 7 | **视频总时长 = 用户给 TTS + 5s 冗余**（不缩短）| 防止黑场翻车（铁律·硬底线）|

---

## 7 类反模式（必避·用户 6 个根本性纠错沉淀）

| 反模式 | 触发 | 修复 |
|---|---|---|
| ❌ 8 张图 = 8 Clip | 收到绘本直接按图分 | 通读旁白 → 标叙事弧 → 合并到 3-5 Clip |
| ❌ **画面时长脱离旁白时长** | 写方案时凭印象算 Clip 时长 · 不查 TTS · 不算中文 | **Clip 时长 = 对应故事所有段 TTS 自然朗读总时长（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）· 视频总时长 = 用户给 TTS + 5s 冗余（不缩短）** |
| ❌ **每段硬塞末帧静默 ≥ 2s** | 凭印象套 v5 公式 = 把"经验值"当"铁律" = 节奏拖慢 | **静默 = 编排工具不是铁律**（按故事连贯性决定 · 故事连贯 = 无静默 · 视觉断点 = 短静默 · 不硬塞 ≥ 2s）|
| ❌ **按"段"机械拆 Clip** | 把 8 段旁白 = 8 Clip · 没按"故事"合并 | **1 个故事 = 1 个 Clip**（视觉连续 + 朗读连贯 = 合并）· 段数 ≠ Clip 数 |
| ❌ **Clip 时长 > 15s**（数字方案物理约束）| 算时长凭印象 = 写出 18s Clip = 严重违规 | 写 Clip 时长前**必查** seedance schema（duration maximum=15）· > 15s 必拆 2 个 |
| ❌ **家族词组中文漏算** | 把"UCK 家族 4 词集合"当说明文字 = 0s | **TTS 真要读的 = 必算**（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）|
| ❌ **场景跳变 + 长旁白走 v15 多图参考** | 蒙太奇末帧 2s 装不下 7s 旁白 = 黑场翻车 | **拆 Clip = 单图独立**（v15 单图参考）· **绝对不用首尾帧范式**（v7/v3/v8 · 用户元偏好的绝对约束）· 详见 `references/scene-jump-v7-correction.md`（v2 修订版）|
| ❌ **vision 抽样不抽全** | 收到 8 张图只 vision 3 张 = 凭印象拼 prompt = 翻车 | **全 N 张图必看光**（不抽样 1/N/中/末）· 写 image-inventory.md |
| ❌ 视频 < TTS | 按范式默认档位算总时长 | 视频总时长 = 用户给 TTS + 5s 冗余（不缩短）|
| ❌ 全静音翻车 | fill 脚本段 4 写"无 BGM/无人声/无哼唱" | 改 B 档默认："无 BGM + 有音效" |
| ❌ `@Image@Image1+2` 双重前缀 | fill 脚本拼错 | 查 4 项 · 空格语法 · 必删双重前缀 |
| ❌ `@Image1+@Image2` 无空格 | 拼 ref 时漏空格 | 带空格：`@Image1 + @Image2 + @Image3` |
| ❌ 5.5s/4.3s 小数时长 | 按朗读时长反推 Clip 时长 | 整数（5/6/7/8/9/10/11/12/13/14/15）· seedance 不生成小数 |
| ❌ 跑完 1 个 Clip 自动连跑 | 没等用户目检 | 单 Clip → 发飞书 → 等目检 → OK 再批量 |
| ❌ **prompt 描述过度细节**（每动作都精确到"翅膀角度/脚蹼几度/几秒切一次"）| prompt 5+ 句动作描述塞 1 镜头 = 必跟参考图姿态冲突 = 模型抽 | **每镜头 1-2 核心动作**（"继续向前游" / "翅膀展开"） + **让模型照参考图自己组织** = 信任参考图 = 自然 · 详见 `references/prompt-minimalist-principle.md` |
| ❌ **场景跳变走 v7 首尾帧范式**（用户元偏好"绝对不用"）| "图 4 + 图 5 跨场景拼一起很跳 = 改用首尾帧过渡" | **拆 Clip 单图独立**（v15 单图参考）· 不用首尾帧范式 |
| ❌ **凭空捏造参考图没有的元素**（2026-06-14 绘本 v1/v2）| 没 vision 参考图就写 prompt = "4 鸭+荷叶+歪头" 凭空加 = 跟原图完全对不上 | **写前必 vision 全 N 张图 + 列"图里有/没有"清单**（写到 image-inventory.md）· prompt 每个名词必须在"有"列里 |
| ❌ **漏字读偏官方原话**（2026-06-14 绘本）| "1 种运镜方式"漏"运镜"4 字 → 读成"1 动作" → 建议用户 1 镜 1 动作 = 违反官方原意 | **凡引用官方原话 = 必 grep 原文档验证 + 标注 4 维属性**（原文+位置+语气+上下文）· 漏 1 字 = 错全意 |
| ❌ **泛泛堆"不要 X"约束词**（2026-06-14 绘本 v4）| 末尾约束写"无字幕、无水印、无 Logo，无人声、无歌唱、无配音、无朗读，音效只保留环境细节，全程无背景音乐" = 6 个"无 X" + 2 个"只保留" + 1 个"全程无" = 污染模型 | **约束词只对"已知出错元素"用**（字幕/Logo/水印 3 类官方原话）· 4 词末尾约束 = 绘本专用 = **已确认保留** · 泛泛"不要 X" = 必删 |
| ❌ **冲突参考图强行用**（2026-06-14 绘本 v3）| @Image3 跟"鸭子游泳"主题冲突（踏浪跑步姿态）= 强行写 prompt 让模型"游" = 末帧仍是踏浪 | **跳过冲突图 = prompt 不引用 + ref_images 不传 + 复用其他 @ImageM + 描述"自然延伸"**（"参考 @ImageM 的同一只鸭子，镜头继续中景跟拍"）|
| ❌ **MCP timeout = 任务失败**（2026-06-14 绘本 5 次跑）| 看到 `wait_and_download` 120s timeout → 重提交 = 重复扣费 | **status 才是唯一权威**（不是 timeout）· 已发任务 = 已扣费 = 用 `check_task` 查 status → running 就再 `wait_and_download`，succeeded 读 output_path · **绝不重提交**（红线·同 seedance2.0-tool 红线 v1）|

---

## 调性 / 范式 / 约束（默认 vs 备选）

| 项 | 默认 | 备选 | 触发备选 |
|---|---|---|---|
| 画幅 | 16:9 | 3:4（小红书） | 用户说小红书 |
| 范式 | v15 4 段（叙事型）| v6 5 段（领读型·有文字持续可见）| 顶部 1/6 有彩色文字 |
| 范式 | v15 4 段 | ~~v7 首尾帧~~（**已删除**·用户元偏好"绝对不用"）| ~~场景跳变 + 长旁白~~ → **拆 Clip 单图独立**（v15 单图参考）|
| 声音档位 | B（普通短句） | C（家族词组/长句）| ≥3 同字母家族词 或 words_en≥5 |
| 段 4 BGM | 无 BGM + 有音效 | 有 BGM（用户指定）| 用户说"要 BGM" |
| 整数时长档位 | 6/7/8/10/12/13/14/15 | 5/9/11 | 短句 5s / 长句 ≤ 15s |
| 视频总时长 | 用户给 TTS + 5s 冗余 | 严格匹配 TTS | 用户说"视频=TTS 严格匹配" |
| Clip 数 | 3-5（甜区） | 2-6 | 极简绘本 2 / 大绘本 6 |

---

## 绘本做完 = 不动 skill（最重要·元教训）

> 用户原话（2026-06-13）："**绘本做完不要在 skill 里加版本号**" + "**绘本做法规范到 skill 里作为标准的制作流程**" + "**不要有太多分支/版本**" + "**不要再开新分支**"

**绘本完成 = 全部产物在工作目录（`~/.hermes/profiles/huiben/work/<日期-绘本名>/`）· skill 不变**：

- ❌ **不**在 SKILL.md 加铁律"v1.0.5+picXX · XX 绘本踩坑"
- ❌ **不**在 references/ 加 `2026-06-XX-绘本名-validation.md`
- ❌ **不**修改 fill 脚本（除非发现通用 bug）
- ❌ **不**开新 git 分支
- ❌ **不**在 SKILL.md / fill 脚本注释 / 铁律名出现特定绘本名
- ✅ **可以**在 work/<日期-绘本名>/ 加本绘本专属笔记（业务文档·不入 skill）
- ✅ **可以**清理 work 旧绘本残留（每绘本完成一周后）

**反问自检**："这个铁律是因为某本绘本踩坑，还是因为通用方法论？"
- **通用方法论** → 加铁律（不绑绘本名）
- **某本绘本踩坑** → work/<日期-绘本名>/ 写笔记，不加 skill

---

## 与子 agent 的关系

主 agent **必做**：
- ✅ 验证子 agent 输出 schema
- ✅ 持久化子 agent 输出到磁盘
- ✅ 翻车时决定重发哪个子 agent
- ✅ 接受/降级决策
- ✅ 端到端验证 + 用户目检
- ✅ **vision 全 N 张图必跑**（不抽样）
- ✅ **必算 TTS 时长**（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）

主 agent **不做**：
- ❌ 拼 prompt（用 `scripts/fill_v15_template.py` 填模板）
- ❌ 跑视频（用 `seedance.py` 或 `mcp_seedance_generate_video`）
- ❌ 抽帧验证（vision 是辅助不是真理·等用户目检）
- ❌ **凭印象算 Clip 时长**（不查 TTS = 严重违规）
- ❌ **用首尾帧范式**（`--image`+`--last-frame` = 用户元偏好"绝对不用"）

**4 个子 agent**（不直接调，记下来即可）：

| Agent | 职责 | Skill |
|---|---|---|
| **A · 风格识别** | 调性 + 节奏倾向 + 风格锚定词 | `storyboard-style` |
| **B · 旁白量化** | 朗读时长 + 复杂度 + 静默推荐 | `storyboard-narration` |
| **C · 分镜设计** | 节奏公式 + 镜头表 + 11 维 JSON | `storyboard-design` |
| **D · 视频执行** | seedance 跑 + 抽帧 + vision 自检 | `video-executor` |

**默认调用规则**：
- Clip ≤ 4：主 agent 直干（不调 C）
- Clip > 4：调 C 子 agent
- A + B 始终主 agent 干（纯计算/少量 vision）

---

## 工具位置

- **fill 模板脚本**：`scripts/fill_v15_template.py`（v15 4 段 / v6 5 段自动切换）
- **fill 后必跑验证**：`scripts/verify_filled_prompts.py`（4 项关键检查·一键验证·**v2 修过段 4 区域定位 bug**）
- **TTS 速率方案校对**：`scripts/tts_rate_calculator.py`（**Step 3 必跑**·8 段旁白 → 多种速率对比 → 差 vs 用户给 TTS → 判定 0/1）
- **时长校验**：`scripts/validate_durations.py`（整数时长 + 末帧静默阈值）
- **敏感词检查**：`scripts/check_sensitive_words.py`（`OutputVideoSensitiveContentDetected` 防护）
- **seedance 调用**：MCP `mcp_seedance_generate_video` / 兜底 `seedance2.0-tool/seedance.py`
- **图床**：uguu.se 优先（chevereto 兜底·已挂）

---

## 维护陷阱（绘本完成后必看）

| 陷阱 | 反模式 | 修复 |
|---|---|---|
| 1. skill 装绘本"版本号" | `**#110**（v1.0.5+pic32 实战新增 · 绘本踩坑 ...）` | 铁律以通用方法论命名·不绑绘本名·反问自检 |
| 2. v6 整段不分镜（v15 修复） | 1 Clip = 1 长段不分镜 | v15 必做"按事件分镜"·**别按"段"机械拆** |
| 3. 5s 5 镜头 | 5s 硬塞 5 镜头 | 5s=2-3 / 12s=4-5 / 14s=5-6 镜头数算法 |
| 4. 段 4 末尾约束偷懒 | 4 段 prompt 只 1 段写末尾约束 | 每段**必**重复约束（**不**共享）|
| 5. 1 Clip = 1 张图 | 单图当参考 = 风格漂移 | 多图参考（`--ref-images`）= 必走 |
| 6. 数字方案凭印象 | "12s 是最长"猜 | **必查 skill 仓**+ duration 4-15s 都是合法 |
| 7. vision 抽样 | 只看 1 帧（5s/末帧）| **必跑全 N 张图**·3 帧起步 |
| 8. TTS 漏算家族词组 | 1.0 词/秒 + 3 字/秒 | 1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿 |
| 9. 静默铁律 | 硬塞静默 = 断裂 | 静默是编排工具·连贯=0 静默 |
| 10. 视频总时长凭印象 | 视频总时长 = TTS（不冗余）| 视频总时长 = TTS + 5s 冗余·**不缩短** |
| 11. 1 故事 = 拆 N Clip | 1 故事 1 Clip 该合不合 | 1 故事=1 Clip·**该合并就合并**（不按图分段）|
| 12. TTS 必缩短 | 1.4 词/秒公式硬套 | **TTS 优先**·绘本专用值·**不缩短** |
| 13. **把 L3 软建议当 L1 红线**（2026-06-14 绘本 v2） | "按秒数拆是错的"= 强推 | "按事件/按秒数"是优先级，**两种都行**，看实战 |
| 14. **动作堆砌翻车甩锅给"按秒数"**（2026-06-14） | 4 动作一句塞 = 抽搐 → 怪"按秒数" | 真凶是动作堆砌·每镜 ≤2 动作（1 主 1 辅）|
| 15. **MCP timeout = 任务失败**（2026-06-14） | `wait_and_download` 120s 超时 → 重提交 | check_task 查 status → running 就再 wait·succeeded 读 output_path |
| 16. **凭印象引用官方原话**（2026-06-14） | "1 镜 1 运镜"漏"运镜"4 字 → 读成"1 动作" → 推给用户 = 违反官方原意 | **凡引用官方原话 = 必 grep 原文档验证 + 标注 4 维属性**（原文+位置+语气+上下文）· "漏 1 字 = 错全意" |
| 17. **没 vision 参考图就写 prompt**（2026-06-14） | 凭印象 + 抄 v1 prompt = "4 鸭+荷叶+歪头"凭空加 = 跟原图对不上 | **写前必 vision 全 N 张图 + 列"图里有/没有"清单**（写到 image-inventory.md）|
| 18. **冲突参考图强行用**（2026-06-14） | @Image3 跟"鸭子游泳"主题冲突 = 强行让模型"游" = 末帧仍是踏浪 | **跳过冲突图 = prompt 不引用 + ref_images 不传 + 复用 @ImageM + 描述"自然延伸"** |
| 19. **泛泛堆"不要 X"约束词**（2026-06-14） | 末尾约束写 6 个"无 X" + 2 个"只保留" + 1 个"全程无" = 污染模型 | **约束词只对"已知出错元素"用**（字幕/Logo/水印 3 类官方原话）· 4 词末尾约束 = 绘本专用 = **已确认保留** |
| 20. **不把"建议"升级成"红线"**（2026-06-14） | 官方"小字说明/建议"读成"红线" = 包装成"官方依据"强推 = 过度推论 | **官方语气分 4 档**（必填正文/红线红框/建议小字/示例案例）· 引用前必标注语气 |
| 2. 开新 git 分支做"实验" | 每本绘本 = 新分支（`{绘本名}-Nclip-{vX.X+picN}` 模式）| 沿用现有 fix/feature 分支累加 commit |
| 3. 1 个 commit = 1 个完整变更单元 | N 个半成品 commit | 本轮工作 = 1 个 commit·message 列出铁律+bug+章节 |
| 4. 子 agent 累积未提交修改 | `git status` 满屏 `M` / `??` | 开工前必先 `git status`·要么 commit 要么 stash |
| 5. fill 脚本 "state reverts" 翻车 | 信任"上次我已修过"记忆 = 这次跑出来 `char_floats 硬编码 "参/考/图/原/考"` | **每 session 必跑** `scripts/verify_filled_prompts.py <clips_dir>` 验证 4 项（不靠记忆）|
| 6. 12 个 untracked 一把 `git add -A` | 误把 6 个含绘本名 references + 2 个含绘本名 scripts + 2 个业务数据目录 add 进 commit | 跑 `git status` 后**先分类**再 `git add`（见下方 3-way 分类法）|
| 7. **数字方案凭印象写** | 写出 18s Clip · 没查 seedance duration 物理上限 | **写任何数字前必查 schema 硬约束**（seedance duration 4-15s · 4-15 整数）|
| 8. **vision 抽样 1/N/中/末** | 收到 8 张图只看 3 张 = 凭印象拼 prompt = 翻车 | **全 N 张图必看光**（不抽样）|
| 9. **TTS 时长凭兜底公式估** | 用 1.4 词/秒估 = 过快估 = 漏算中文 + 漏算停顿 = 实际 TTS 翻 1.5-2 倍 | **1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿** + **用户给 TTS 优先** |
| 10. **画面时长脱离旁白时长** | 凭印象写 Clip 时长 = 不算 TTS | **Clip 时长 = 对应故事所有段 TTS 自然朗读总时长**（算完再写）|
| 11. **每段硬塞末帧静默 ≥ 2s** | 凭印象套 v5 公式 = 把经验值当铁律 | **静默 = 编排工具不是铁律**（按故事连贯性）|
| 12. **家族词组中文漏算** | 把中文"UCK 家族 4 词集合"当说明文字 = 0s | **TTS 真要读的 = 必算**（不漏中文）|
| 13. ~~**场景跳变 + 长旁白走 v15 多图参考**~~ | ~~蒙太奇末帧 2s 装不下 7s 旁白 = 黑场翻车~~ | ~~**必走 v7 首尾帧范式**~~（**已修订** · v2 · 用户元偏好"绝对不用首尾帧" = **改为拆 Clip 单图独立** · 详见 `references/scene-jump-v7-correction.md` v2 修订版）|
| 14. **verify_filled_prompts 段 4 区域定位 bug** | 旧版 `text[-quarter:]`（最后 1/4）= 实际看到的是段 5 文字持续可见段 = 误判 B 档缺失 = 误报 | **改用 `find("段 4 · BGM 段")` 标记定位**（v6 模板里 60-80% 位置）= 精准取段 4 = 不误报 |
| 15. **verify_filled_prompts v7 范式误判 A 档** | v7 模板末尾"No background music, no human voice, no narration, no singing"= 触发 A 档正则全文匹配 = 误报为 A 档翻车 | **加 v7 范式识别**（"storyboard reference image sequence" 关键字）= v7 范式跳过 A 档判定 + 跳过 char_floats 检查（v7 没段 5 文字持续可见段）|
| 16. **fill_v15_template.py 11 维 JSON schema 字段名不匹配** | 主 agent 凭印象编字段名（`subject_definition` / `text_visibility` / `sound_strategy`）= 跟脚本要的不一致（要 `characters[]` / `text_position` / `style_keywords` 数组 / `time_breakdown`）= 脚本运行 KeyError | **必查 `scripts/fill_v15_template.py fill_template()` 函数要的字段**（实际是 C 子 agent 风格 schema）= 必查不靠印象 |

### 维护陷阱 #5 详解 · fill 脚本 state reverts

**触发条件**（实测翻车 2026-06-13）：`scripts/fill_v15_template.py` 的 `_build_text_visibility_segment` 函数曾有"char_floats 硬编码 参/考/图/原/考" bug · 之前 session 修过 · 本 session 跑时 grep 发现 bug 还在。

**根因**：agent 凭"我之前修过"记忆直接填 prompt = **没验证填出来的结果**。`fill_v15_template.py` 实际状态可能在跨 session 期间被回滚 / 外部编辑 / 子 agent 改过 = 记忆失效。

**修复**（必跑 · 不能省）：

```bash
# 跑完 fill_v15_template.py 后必跑验证脚本
python3 scripts/verify_filled_prompts.py <clips_dir>

# 4 项检查：
#   1. 0 双重前缀（@Image@Image）
#   2. @Image 空格语法（@Image1+@Image2 带空格·不是 @Image1+@Image2）
#   3. 段 4 B 档音效版（不是 A 档"无 BGM/无人声/无哼唱"全静音）
#   4. char_floats 动态按 en_word 字母数生成（不是硬编码"参/考/图/原/考"）
# 退出码 0 = 4/4 全过 · 1 = 失败（CI 可拦截）
```

**判断口诀**：**"fill 完 ≠ 验证过 · 跑 verify_filled_prompts.py = 唯一权威"**。

### 维护陷阱 #6 详解 · untracked 残留 3-way 分类法

**触发条件**：skill 仓 `git status` 出现 N 个 untracked 文件（references/scripts/templates/ 子目录 + `_inbox/` + `data/`）= 准备 commit 时**不知道该不该 add**。

**反模式**：直接 `git add -A` = 误把绘本名污染 + 业务数据一并 commit = 违反铁律 #116 / #117。

**3-way 分类法**（commit 前必跑）：

| 类别 | 判定标准 | 动作 |
|---|---|---|
| ✅ **应 commit** | 在 `references/` / `scripts/` / `templates/` 下 + **0 绘本名**（grep 不到 Mango/Kangaroo/Horse/Cherry/Bird/Cow/No/Banana 等）+ 是**通用方法论** | `git add <file>` |
| ❌ **绘本名污染** | 文件名或内容含特定绘本名 = 违反铁律 #117 绘本名不绑 | `rm <file>` · 内容可重写到 `work/<日期-绘本名>/` 业务笔记 |
| ❌ **业务数据** | 在 `_inbox/` / `data/` / `work/` 目录下 = 业务产物 = 违反铁律 #116 不入 skill 仓 | `rm -rf <dir>` · 或保持 untracked（不入 commit）|

**操作流程**：

```bash
# 1. 看未跟踪
git status

# 2. 对每个 untracked 文件做判定
for f in $(git status --porcelain | grep '^??' | awk '{print $2}'); do
  case "$f" in
    # 业务数据 → 删
    _inbox/*|data/*|work/*) echo "❌ 业务数据·删: $f" ;;
    # 绘本名污染 → 删
    *mango*|*kangaroo*|*horse*|*cherry*|*bird*|*cow*|*banana*)
      echo "❌ 绘本名污染·删: $f" ;;
    # references/scripts/templates 通用方法论 → 检查内容是否含绘本名
    references/*|scripts/*|templates/*)
      if grep -lE "Mango|Kangaroo|Horse|Cherry|Bird|Cow|No\.|Banana" "$f" >/dev/null 2>&1; then
        echo "❌ 内容含绘本名·删: $f"
      else
        echo "✅ 通用方法论·add: $f"
      fi ;;
    *) echo "⚠️ 未知类别·人工判断: $f" ;;
  esac
done

# 3. 执行 add / rm（按上面输出操作）
```

**判断口诀**：**"`git add -A` 永远错 · 3-way 分类必跑一遍"** ·  **"通用方法论 = commit · 绘本名 = 删 · 业务数据 = 删/不 commit"**

**自检命令**（绘本完成后必跑 0 残留验证）：

```bash
# 1. SKILL.md 内 0 绘本名残留
grep -E "特定绘本名" SKILL.md scripts/*.py references/*.md templates/*.md assets/example-prompts/*.txt
# 期望：无任何输出

# 2. SKILL.md 内 0 v\d+\.\d+\+pic\d+ 标签
grep -E "v[0-9]+\.[0-9]+\+pic[0-9]+" SKILL.md scripts/*.py references/*.md templates/*.md
# 期望：无任何输出（反例占位也用 `v\d+\.\d+\+pic\d+` 通用占位符）
```

**反例教学的正确写法**（示范）：

```markdown
# ❌ 错：绑了具体绘本名和版本号
**#110**（v1.0.5+pic32 实战新增 · 某绘本踩坑 ...）
每本绘本 = 新分支（`某绘本-4clip-v1.0.5+pic37` 等）

# ✅ 对：用通用占位符
**#110**（绘本踩坑实战新增）
每本绘本 = 新分支（`{绘本名}-Nclip-{vX.X+picN}` 模式）
```

---

## 相关 skill

- **绘本创作**：`picturebook-creator`（静态绘本）
- **分镜子 agent**：`storyboard-style` / `storyboard-narration` / `storyboard-design` / `video-executor`
- **视频工具**：`seedance2.0-tool`（底层 seedance 兜底脚本）
- **4-skill 工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`

## 📚 引用 references

- `references/six-roots-correction.md` · **6 个根本性纠错详细 + 修复 SOP**（2026-06-13 沉淀）
- `references/scene-jump-v7-correction.md` · **第 7 个根本性纠错：场景跳变 + 长旁白 = 必拆 Clip 单图独立 · 绝对不用首尾帧范式**（v2 修订版 · 2026-06-13 沉淀 · 跟用户元偏好"绝对不用"对齐）
- `references/tts-rate-calibration-workflow.md` · **第 8 个根本性纠错：TTS 速率方案必校对**（3-5s 容忍范围 · 多种速率对比 · 5 类常见根因 · 一键校对脚本 · 2026-06-13 绘本实战沉淀）
- `references/prompt-minimalist-principle.md` · **元纠错 #9 · 信任参考图 + 关键引导而非过度约束**（2026-06-14 沉淀 · 5 反模式 + 5 修复 + 4 处官方原话背书 + 8 项自检清单）
- `references/prompt-overconstraint-pitfalls.md` · **元纠错 #10-#15 · prompt 过度约束翻车沉淀**（不把"建议"读成"红线" / 写前必 vision + 列"图里有/没有" / 凡引用官方原文必逐字核对 / 跳过冲突图 = 复用+延伸 / "不要 X"= 约束词污染 + MCP timeout 元教训）
- `references/official-quote-4-levels.md` · **官方原话 4 档分级法**（2026-06-14 沉淀 · L1 红线 / L2 强建议 / L3 软建议 / L4 描述 · 凡引用官方原话前必跑 3 问 = grep 验证 + 标 5 维属性 + 实战数据 · "按事件 vs 按秒数"决策表 · "1 镜 1 运镜"漏字案）
- `references/standard-flow-mango-validation.md` · 标准绘本工作流验证（Mango 实战）
- `references/director-cut-merge-recipe.md` · 导演分镜合并配方
- `references/tts-duration-merge-recipe.md` · TTS 时长合并配方
- `references/verify-filled-prompts.md` · verify 脚本详细说明（含 v2 bugfix · 见下）
- `references/v6-5段骨架-模板.md` · v6 5 段骨架模板
- `references/v15-4段骨架-模板.md` · v15 4 段骨架模板
- `references/standard-picturebook-workflow-5steps.md` · 标准工作流 5 步速查

## 🔧 配套 scripts（**主 agent Step 3 必跑**）

- `scripts/tts_rate_calculator.py` · **TTS 速率方案校对脚本**（8 段旁白 → 多种速率对比 → 差 vs 用户给 TTS → 判定 0/1）— 见 `references/tts-rate-calibration-workflow.md`
