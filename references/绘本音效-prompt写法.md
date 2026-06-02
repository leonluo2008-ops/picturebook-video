---
name: 绘本音效-prompt写法
description: 绘本动画里音效（拟声/环境音）的 prompt 写法规范。从 2026-06-02 Red 绘本 v1→v2→v3 三轮实测中提炼，修复画面切快+收势失败两个具体问题。明确 Seedance 内容风控白名单（仅警察/军队/枪/武器等敏感题材触发，机械/警笛类拟声可正常使用）。
triggers:
  - 绘本音效
  - 音效写法
  - 拟声
  - --generate-audio
  - 绘本 prompt
---

# 绘本音效 · Prompt 写法三铁律

> **核心结论**：绘本视频**默认带音效**（拟声+环境音），不是全静音。但写法不对会出现「画面切快」+「收势失败」两个连锁问题。
> 来源：2026-06-02 Red 绘本 v1（无音效）→ v2（音效写错，画面切快+结尾没收住）→ v3（修复后通过）。

## 0. 绘本音频三件事

绘本视频里音频**有三件事**，**互不替代**，必须先分清再写 prompt：

| 类型 | 是否需要 | 写进 prompt | 由谁生成 |
|------|---------|------------|---------|
| **旁白朗读**（人声念 "A red apple"） | ✅ 需要 | **否**——prompt 里不出现朗读文字 | 后期 TTS 单独合成 |
| **BGM 背景音乐**（持续音乐铺底） | ❌ 不要（绘本默认） | **否**——prompt 里不出现 BGM 词 | 不加 |
| **音效**（拟声+环境音，配合画面动作） | ✅ 需要 | **是**——短促拟声、卡点环境音 | Seedance `--generate-audio true` 同步生成 |

**绘本默认配置**：`--generate-audio true` + prompt 里**只写音效动作描述**。

常见音效举例：

| 场景 | 音效写法（嵌入视觉句） |
|---|---|
| 标题页字母 RED 出现 | `... paper-landing tap-tap-tap as the three letters settle into place` |
| 红苹果 | `... soft plop as the apple gently appears, like a fruit placed on a table` |
| 红色小汽车 | `... soft gentle chime as the small car rolls in`（绘本风格更温柔；写 `beep-beep` 也安全，见 §5.2） |
| 红色消防车 | `... soft gentle chime as the fire truck rolls in`（绘本风格更温柔；写 `siren/wee-oo` 也安全，见 §5.2） |
| 红色瓢虫 | `... a tiny soft flutter as the ladybug's wings beat, then soft landing on leaf` |
| 红鱼游过 | `... gentle water-bubble bloop-bloop as the fish swims across` |
| 集合页 Everything red! | `... a warm chime cascades, soft children's giggle 'wow~'` |
| 收尾定格 | `... quiet warm chime settles`（要短促，不能盖过画面定格感） |

## 1. v1 → v2 → v3 实战对比

### v1（无音效，画面 OK）

```python
prompt = """@Image1 as the opening frame, the bold collaged letters 'RED' ...
the camera slowly pushes in with a warm light bloom sweeping across the scene ...
transitions seamlessly to @Image2 as the second half, a red paper-collaged apple ...
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame.
Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel."""

generate-audio = false
# ✅ 画面：稳。✅ 收势：定住。❌ 静音（用户反馈：绘本需要音效）。
```

### v2（加音效，写法错 → 画面切快 + 收势失败）

```python
prompt = """@Image1 as the opening frame, ... soft white background.
[Sound effect: gentle paper-landing 'tap-tap-tap' as the three letters settle into place].   ← 句号1
The camera slowly pushes in with a warm light bloom sweeping across the scene ...    ← 句号2
transitions seamlessly to @Image2 as the second half, ...    ← 句号3
[Sound effect: soft 'plop' as the apple gently appears, like a fruit placed on a table].   ← 句号4
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame.    ← 句号5
[Sound effect: quiet, brief warm chime settling].   ← 句号6 ⚠️ 覆盖收势词
Children's picture book collage illustration style, ...
No speech, no narration, no background music — only short picture-book sound effects synced to the visual action."""  ← 否定句干扰

generate-audio = true
# ❌ 画面：切快（句号切碎视觉）。❌ 收势：没收住（尾部音效块覆盖收势词）。✅ 音效：有，但代价是画面崩坏。
```

### v3（修复 → 画面稳 + 收住 + 音效在）

```python
prompt = """@Image1 as the opening frame, the bold collaged letters 'RED' in red, blue and yellow paper stand on a yellow paper strip, a small white rabbit looks up at them, soft white background, gentle paper-landing tap-tap-tap as the three letters settle into place;    ← 分号
the camera slowly pushes in with a warm light bloom sweeping across the scene, paper textures become more vivid, soft plop as the apple gently appears, transitions seamlessly to @Image2 as the second half, a red paper-collaged apple with green stem and brown leaf sits in the center, handcrafted paper-cut style throughout;    ← 分号
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame, quiet warm chime settles.    ← 收势词在最末！音效描述嵌入为副词
Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel."""  ← 删除否定句

generate-audio = true
# ✅ 画面：稳（分号保单段连续）。✅ 收势：定住（收势词不被覆盖）。✅ 音效：在。
```

## 2. 三铁律

### 铁律 1 · 句号切分视觉，音效描述必须用分号 / 逗号

**现象**：v2 用句号 `.` 把视觉流程切成了 6 段（起始段、音效块、推进段、过渡段、音效块、收势段），模型把每段当成独立小节执行。

**修复**：视觉描述用**分号 `;`** 连接，音效描述**嵌入视觉句中间**（用**逗号 `,`** 串接）→ 整段保持单段连续语义。

```
❌ 错误：起始段. 音效块. 推进段. 收势段. 音效块. 风格段.
✅ 正确：起始段含音效副词, 推进段含音效副词; 收势段含收尾音效; 风格段.
```

### 铁律 2 · 收势词（final frame / camera locks / holds）放最后一句，后面不追加任何内容

**现象**：v2 收势词后面又追加了 `[Sound effect: quiet warm chime settling]` → 模型把视觉定格指令当成"中间过渡"，把尾部音效当成收尾 → 画面继续动。

**修复**：收势词必须**是 prompt 的最后一句有意义的画面描述**。如果想加收尾音效，用逗号串接在收势句内部，**不再开新句**。

```
❌ 错误：final frame: ... holds to the last frame. [Sound effect: chime settling]. 风格段.
✅ 正确：final frame: ... holds to the last frame, quiet warm chime settles. 风格段.
```

### 铁律 3 · 否定性指令（no speech / no narration / no BGM）放末尾会干扰视觉模型

**现象**：v2 末尾加 "No speech, no narration, no background music..." 否定句 → 视觉模型不擅长"反向作画"，这句会变成无效描述，反而把最后一段从"画面定格指令"变成了"文字说明"。

**修复**：删除否定句。**正向描述已经够了**——只要 prompt 里不出现朗读文字、不出现 BGM 词，模型自然就不会生成这些。

```
❌ 错误：风格段. No speech, no narration, no background music — only sound effects.
✅ 正确：风格段.
```

## 3. 完整 prompt 模板（v3 范式）

```python
prompt_template = """@Image1 as the opening frame, {起始画面描述}, {起始音效副词};
{camera 运镜描述 + 中段音效副词}, transitions seamlessly to @Image2 as the second half, {结束画面描述};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame, {收尾音效副词}.
{风格锁定句}."""
```

**3 个分号，1 个句号（收尾），0 个 `[Sound effect: ...]` 独立块，0 个否定句**。

**红苹果示例**（直接可复用）：

```python
prompt_template.format(
    起始画面描述="the bold collaged letters 'RED' in red, blue and yellow paper stand on a yellow paper strip, a small white rabbit looks up at them, soft white background",
    起始音效副词="gentle paper-landing tap-tap-tap as the three letters settle into place",
    运镜="the camera slowly pushes in with a warm light bloom sweeping across the scene, paper textures become more vivid",
    中段音效副词="soft plop as the apple gently appears",
    结束画面描述="a red paper-collaged apple with green stem and brown leaf sits in the center, handcrafted paper-cut style throughout",
    收尾音效副词="quiet warm chime settles",
    风格锁定句="Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel",
)
```

## 4. 与单测门 SOP 的关系

音效是**视觉 + 音频双轨验证**：

单测门单测 clip 必看 4 项 → 5 项（新增）：

1. 风格锁定（跟原图拼贴+手绘一致吗）
2. 镜头运镜（推进+暖光过渡自然吗）
3. 收势（结尾稳定定格，无渐隐/淡出/动作截断）
4. 无穿帮/崩坏
5. **音效**：
   - 有没有人声念旁白？（应该没有）
   - 有没有 BGM 持续铺底？（应该没有）
   - 有没有拟声/环境音跟画面卡点？（应该有）
   - 音效是否短促不抢戏？（应该 0.5-1.5s/段，不延绵）

如果音效不卡点 / 太抢戏 → 调整音效描述用词（不要加 "BGM" / "music" / "song" 词，不要用长句描述音效）。
如果画面切快 / 收势失败 → 检查 prompt 是不是用了句号切分 + 收势词后追加内容（**回到三铁律**）。
如果**任务 failed with OutputVideoSensitiveContentDetected** → 检查 prompt 是否出现"警察/军人/枪/武器/暴力"等**敏感题材本体**（不是机械/警笛类拟声，那些安全）。

## 5. 音效写作用词白名单 / 黑名单

### 5.1 模型生成白名单（用这些词描述音效，模型能生成）

| 类别 | 推荐词 |
|------|--------|
| 通用 | `sound effect`, `gentle`, `soft`, `quiet`, `warm`, `brief` |
| 拟声 | `tap-tap-tap`, `plop`, `pop`, `click`, `whoosh`, `bloom` |
| 环境 | `chime`, `splash`, `bubble`, `rustle`, `swoosh`, `hum`, `buzz` |
| 情绪 | `cascading`, `settling`, `rising`（描述音效"怎么来怎么去"） |

### 5.2 内容风控（2026-06-02 用户最终纠正 · 修正版）

> ⚠️ **旧版（错）**：vroom/horn/siren/警笛/鸣笛 等机械警笛类拟声触发风控
> ✅ **用户最终纠正**："只有警察、军队等敏感词汇容易风控，机械/车辆视觉动作这些是可以使用的"
> 旧版的"黑名单"全部作废。**绘本消防车/汽车/警车/军车的视觉动作 + 警笛/喇叭/vroom/siren 等拟声**全部可以正常使用。

| 类别 | 状态 | 说明 |
|------|------|------|
| 警察/军人/枪支/武器/暴力 | ❌ 触发风控 | API 返回 `OutputVideoSensitiveContentDetected` |
| 机械/车辆类拟声（vroom/horn/siren/alarm/engine） | ✅ 全部安全 | 绘本消防车、汽车、警车、军车等视觉动作 + 拟声全部可以写 |
| 警笛/鸣笛/wee-oo/beep-beep | ✅ 全部安全 | 跟视觉动作叠加写也没事（之前是误判） |
| chime/rustling/plop/tap-tap-tap/bubble/sparkle/flutter/whoosh/bloom/settle | ✅ 安全 | 绘本风格自然声，依然推荐（温柔卡点，不是风控要求） |

**消防车场景的安全写法（修正版）**：

```
✅ 安全：a distant 'wee-oo wee-oo' siren as the fire truck rolls in     → task succeeded
✅ 安全：a friendly 'beep-beep' as the small car rolls in                → task succeeded
✅ 安全：soft engine 'vroom' as the car starts                           → task succeeded
✅ 安全：soft gentle chime as the fire truck rolls in                    → task succeeded（绘本风格更温柔）
✅ 安全：soft gentle chime as the small car rolls in                     → task succeeded
```

**唯一真正禁忌**：明确出现"警察/军人/枪/武器/暴力"等敏感题材本体。**绘本里消防车、警车、军车的警笛/喇叭视觉动作 + 拟声**全部可以正常使用。

绘本风格调性建议（不是风控要求）：绘本对童趣有克制，`chime` 替代警笛`是一种**风格选择**，不是安全妥协。

### 5.3 BGM/人声黑名单（不会触发风控，但会让模型生成"绘本不该有的东西"）

| 词 | 风险 |
|---|---|
| `BGM`, `background music`, `musical score`, `soundtrack` | 会触发持续音乐铺底 |
| `song`, `melody`, `rhythm`, `beat` | 会触发儿歌/旋律生成 |
| `voiceover`, `narrator says`, `speaks`, `reads aloud` | 会触发人声朗读 |
| `cheerful melody`, `playful tune`, `happy music` | 同 BGM |
| `loud`, `dramatic`, `intense` | 会让音效变 BGM 化 |

## 6. 风险与权衡

**风险 1**：把音效描述降级为"视觉句的副词"后，模型对音效的"卡点"可能不如独立 `[Sound effect]` 块精准。

**应对**：
- 音效描述用「**动词 + 时间副词**」加强卡点感：`as the apple appears`（果出现时）/ `as the letters settle`（字母落位时）
- 必要时**升级为"分号独立短句"**（但仍不用句号切断视觉）：`; the sound of a soft plop fills the air as the apple lands.`

**风险 2**：每张图的具体音效（"消防车警笛呜——" vs "汽车嘀嘀"）在 prompt 模板里是变量，不是固定的——必须按图片实际主体配。

**应对**：用 `{音效副词}` 占位符预留，由本项目 Phase 5 Step 1 阶段生成。机械/车辆类主体的拟声（vroom/horn/siren/beep 等）现在全部安全，可以根据画面真实需求自由选择。**绘本风格调性**建议优先 chime/rustling 等温柔卡点（属于风格选择，不是风控规避）。

## 7. 关联 skill 章节

- `picturebook-video/SKILL.md` Phase 8 · 绘本场景音频策略 + 参数默认值表（已嵌入三铁律 + 默认配置）
- `picturebook-video/SKILL.md` 关键教训 #15（v1→v2→v3 修复沉淀）
- `references/领读型合并-双图连续运镜.md` · 时长公式 + 4 段式 prompt 模板（需配合三铁律改写）
