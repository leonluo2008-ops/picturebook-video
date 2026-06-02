---
name: 分镜时序-prompt范式-v7
description: 用「显式分镜时序表 + @ImageN 时间窗绑定 + shot 内部动作描述 + Storyboard Audio Description 段 + 音频禁令句」让 Seedance 在指定时段精准切换画面+精准执行动作+精准控制音频（卡点音效 / 零人声 / 零 BGM）。来源：2026-06-02 Cactus 仙人掌绘本 8 图分 4 Clip 实测沉淀。
triggers:
  - 分镜时序
  - storyboard 提示词
  - 精准切换
  - 精准动作
  - 精准音效
  - from Xs to Ys
  - @Image1 @Image2
  - 分镜图时序
  - Storyboard Audio Description
  - v7 范式
---

# 分镜时序 Prompt 范式（v7 · 领读型绘本 + TTS 后期卡点）

> 本文档解决：**如何用 prompt 让 Seedance 在指定秒数精准切换画面 + 精准执行动作 + 精准控制音频**。
> 模式来源：2026-06-02 Cactus 仙人掌绘本 8 图分 4 Clip 实测。
> 模式提取（不绑定具体内容）：**「显式分镜时序表 + @ImageN 时间窗绑定 + shot 内部动作描述 + Storyboard Audio Description 段 + 音频禁令句」**。

**范式状态**：✅ **v7 是当前唯一推荐范式**（2026-06-02 后）。早期版本（v5 纯静态=绘本翻页感、v6 嵌入式音效=持续音+人声）已废弃，**不要再用 v5/v6 写法**。

---

## 核心原理

**用户的金句（2026-06-02 二大爷）**：
> "能让画面在目标时段精准切换，并静止，那么也可以让画面在目标时段动起来，是吧"

**✅ 答：是的。** 同一机制反过来用：
- v5：用 `stays perfectly still + holds steady within its time window` → **精准静态**
- v6：用 `in this shot [动作描述]` + `holds steady for the rest of this shot` → **精准动画**

---

## 与既有范式的差异

| 维度 | 双图连续运镜（v3） | 带时间锚点 TTS 匹配（v3+锚点） | **分镜时序精准动作（v5+v6，本文档）** |
|------|------------------|---------------------------|---------------------------------|
| **画面切换时机** | 模型自动决定 | 触发式动作（"as the camera X begins"） | **显式时间窗**（"from 0.0s to 1.2s @Image1"） |
| **TTS 后期匹配** | 难精准对齐 | 中（触发式不严格遵守） | **容易精准对齐**（时间窗硬约束） |
| **动作精度** | 模糊（散文叙述） | 模糊（触发式） | **精准**（shot 内部动作 + holds steady for the rest） |
| **Prompt 复杂度** | 3 字段 | 6 字段 | 5 字段（storyboard 头 + N 段 shot + 风格 + 收势） |
| **模型自由度** | 高 | 中 | **低**（按时间窗+shot 切分） |
| **适合场景** | 氛围型、不要求卡点 | 需要 TTS 后期卡点 | **需要精准控制画面+动作的 TTS 卡点** |

**关键差异**：本范式是**唯一**能让画面在**指定秒数**（不是"as the camera X begins"这种软触发）切换并执行的写法。

---

## 适用判断

**同时满足才用本范式**：
- 绘本类型 = 领读型（弱情节、靠画面+旁白推）
- **用户需要 TTS 后期精准卡点**（不是氛围型）
- 需要**画面切换+动作**双重精准（不是纯静态展示）
- 旁白单段中等长度（5-20 字中文 + 2-8 词英文）

**不适用**：
- 故事型绘本（强情节、起承转合）→ 用 1图=1Clip 标准模式
- 不需要 TTS 卡点 → 用双图连续运镜（v3）
- 旁白 < 4s/段 → 走 1图=1Clip 标准模式

---

## Prompt 模板（v7 · 分镜时序 + 精准动画 + 精准音频控制）⭐

> v7 是当前推荐范式。v5/v6 见后文子节。

```python
PROMPT_TEMPLATE_V7 = """This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from {t1_start:.1f}s to {t1_end:.1f}s @Image{img1} is the {shot1_name} shot, in this shot {action1_verb}, then {state1_hold};
from {t2_start:.1f}s to {t2_end:.1f}s @Image{img2} is the {shot2_name} shot, in this shot {action2_verb}, then {state2_hold};
final frame: the camera locks completely, paper textures crisp and vivid, the scene holds its final pose;
Storyboard Audio Description: {audio_segment_1_t_start:.1f}s to {audio_segment_1_t_end:.1f}s {audio_1_description}, then ambient silence, {audio_segment_2_t}s {audio_2_description}, {audio_segment_2_t}s to {total_duration:.1f}s minimal ambient silence, a single brief warm chime at the very end;
No background music, no human voice, no narration, no singing;
{style_sentence}."""
```

**8 段固定结构**（分号 7 个，句号 1 个在风格段尾）：

| 段 | 内容 | 性质 |
|---|------|------|
| 1 | `This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video` | 分镜引导（固定） |
| 2 | `from X.Xs to Y.Ys @ImageN is the ... shot, in this shot [动作], then [稳态]` | shot 1 视觉分镜 |
| 3 | `from X.Xs to Y.Ys @ImageN is the ... shot, in this shot [动作], then [稳态]` | shot 2 视觉分镜 |
| 4 | `final frame: the camera locks completely, ...` | 收势词 |
| 5 | `Storyboard Audio Description: X.Xs to Y.Ys [音效1]...` | 音频描述（分时段） |
| 6 | `No background music, no human voice, no narration, no singing` | 音频禁令 |
| 7 | `{style_sentence}` | 风格锁定 |
| 8 | `.` | 句号收尾 |

### 字段说明（Cactus Clip 1 v7 真实示例）

| 字段 | 含义 | Cactus Clip 1 v7 实际值 |
|------|------|----------------------|
| `t1_start` / `t1_end` | 第 1 段画面时间窗 | `0.0` / `1.2` |
| `img1` | 第 1 段画面绑定图 | `1`（@Image1） |
| `shot1_name` | 第 1 段画面定位词 | `opening` |
| `action1_verb` | 第 1 段动作描述 | `the colorful paper-collaged letters 'CACTUS' bounce into the frame from the edges and land in the center, settling into place one by one to spell CACTUS` |
| `state1_hold` | 第 1 段动作完成后稳态 | `then they hold steady for the rest of this shot` |
| `t2_start` / `t2_end` | 第 2 段画面时间窗 | `1.2` / `8.0` |
| `img2` | 第 2 段画面绑定图 | `2`（@Image2） |
| `shot2_name` | 第 2 段画面定位词 | `second` |
| `action2_verb` | 第 2 段动作描述 | `a green saguaro cactus slowly grows up from the yellow desert sand with paper layers unfolding` |
| `state2_hold` | 第 2 段动作完成后稳态 | `then it stands tall and sways gently in a warm breeze for the rest of this shot` |
| `audio_segment_1_t_start` / `_end` | 第 1 段音效时间窗 | `0.0` / `1.2` |
| `audio_1_description` | 第 1 段音效 | `a single paper-landing tap-tap as the CACTUS letters settle` |
| `audio_segment_2_t` | 第 2 段音效触发时间 | `1.2` |
| `audio_2_description` | 第 2 段音效 | `a quick soft whoosh as the cactus grows up` |
| `audio_segment_2_t_end` | 第 2 段剩余时间窗 | `1.2` / `8.0` |
| `style_sentence` | 风格锁定句 | `Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel` |

### v7 关键句式（5 件套）

1. **分镜引导**：`This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video`
   - 让模型知道是"分镜时序"任务，不是单图转视频

2. **shot 时间窗 + 动作 + 稳态**：`from 0.0s to 1.2s @Image1 is the opening shot, in this shot [动作], then [稳态]`
   - 显式时间窗是硬约束
   - `in this shot` 显式声明"本 shot 做什么"
   - `then [状态] hold steady for the rest of this shot` 显式声明"动作完成后稳态停留"

3. **收势词**：`final frame: the camera locks completely, paper textures crisp and vivid, the scene holds its final pose`
   - 在**段 4**（音频段之前）
   - 三铁律 2 要求：收势词是 prompt 的最后一句有意义的画面描述

4. **音频描述**：`Storyboard Audio Description: X.Xs to Y.Ys [音效1] then ambient silence, Xs [音效2], X.Xs to Y.Ys minimal ambient silence, a single brief warm chime at the very end`
   - 在**段 5**（收势词之后，禁令段之前）
   - 关键发现：参考示例的"Storyboard Audio Description"分段模式被 Seedance **完美遵守**——分时段精确控制音效

5. **音频禁令**：`No background music, no human voice, no narration, no singing`
   - 在**段 6**（音频段之后，风格段之前）
   - ⚠️ 跟三铁律 3 的视觉段"不能用否定句"**不冲突**——音频禁令段 Seedance 实际会听（参考示例验证）

### v7 必跑自检（11 项）

| # | 检查项 | 期望 |
|---|--------|------|
| 1 | 段数 = 8 | ✅ |
| 2 | 分号数 = 7 | ✅ |
| 3 | 句号数 ≤ 9（数字缩写如 `1.2s/8.0s` 不计入） | ✅ |
| 4 | 段 4 含 `final frame` | ✅ |
| 5 | 段 5 以 `Storyboard Audio Description:` 开头 | ✅ |
| 6 | 段 6 以 `No background music` 开头 | ✅ |
| 7 | 段 7 以 `Children's picture book` 开头 | ✅ |
| 8 | 段 7 末尾有 1 个句号收尾 | ✅ |
| 9 | 视觉段（段 2-4）无 `no / no BGM / no speech` | ✅ |
| 10 | 整段无独立 `[Sound effect: ...]` 块 | ✅ |
| 11 | 收势词在最后一句**画面描述**里（不是音频/禁令/风格段） | ✅ |

### 完整 v7 真实示例（Cactus Clip 1）

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 1.2s @Image1 is the opening shot, in this shot the colorful paper-collaged letters 'CACTUS' bounce into the frame from the edges and land in the center, settling into place one by one to spell CACTUS, then they hold steady for the rest of this shot;
from 1.2s to 8.0s @Image2 is the second shot, in this shot a green saguaro cactus slowly grows up from the yellow desert sand with paper layers unfolding, then it stands tall and sways gently in a warm breeze for the rest of this shot;
final frame: the camera locks completely, paper textures crisp and vivid, the scene holds its final pose;
Storyboard Audio Description: 0.0s to 1.2s a single paper-landing tap-tap as the CACTUS letters settle then ambient silence, 1.2s a quick soft whoosh as the cactus grows up, 1.2s to 8.0s minimal desert ambient silence, a single brief warm chime at the very end;
No background music, no human voice, no narration, no singing;
Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel.
```

**4-5 个分号 + 1 个句号**（收尾风格段）。

> ⚠️ **关于 v5/v6 的处理**：v5（纯静态=绘本翻页感）和 v6（嵌入式音效=持续音+人声）已被 v7 完全替代。**v5 验证了"分镜时序精准切换"能力，v6 验证了"in this shot 精准动作"能力**——这两点被 v7 继承。**不要再用 v5/v6 写法**（v5 太静态，v6 音效段会变持续音）。

---

## 8 段旁白 → 8 个动作的映射（Cactus 范式）

| 旁白 | 画面动作 | 起始时点 |
|------|---------|---------|
| 1. Cactus! | 彩色字母从四周蹦到中央拼成 CACTUS | 0-1.2s |
| 2. A green cactus. | 绿色仙人掌从沙地长出（叶子展开） | 1.2-4.5s |
| 3. 仙人掌有刺 | 黑色刺一根根从仙人掌身上长出 | 4.5-7.2s |
| 4. 仙人掌上有粉色的花 | 粉色花苞在仙人掌顶部绽放 | 7.2-11.7s |
| 5. 仙人掌住在沙漠里 | 镜头从近景拉远展示沙漠全景 | 11.7-15.9s |
| 6. 仙人掌有手臂 | 仙人掌的两只手臂从身体伸出来 | 15.9-18.9s |
| 7. 仙人掌高高的 | 镜头仰拍/仙人掌长高顶天 | 18.9-21.9s |
| 8. 仙人掌很坚强 | 暖光充满画面，6 株仙人掌聚成家庭 | 21.9-24.6s |

**配对原则**：把动作关联的旁白就近配对（每个 Clip 内做 2 个动作）。
- Clip1 = 1+2（标题蹦出 + 仙人掌长出）→ 1.jpg 起，2.jpg 收，时长 8s
- Clip2 = 3+4（刺长出 + 花绽放）→ 3.jpg 起，4.jpg 收，时长 9s
- Clip3 = 5+6（镜头拉远 + 手臂伸出）→ 5.jpg 起，6.jpg 收，时长 10s
- Clip4 = 7+8（仙人掌长高 + 家庭聚光）→ 7.jpg 起，8.jpg 收，时长 10s

---

## 注意事项

1. **`from X.Xs to Y.Ys` 是硬时间窗** —— Seedance 会严格遵守，**这是 v7 范式的核心能力**。
2. **shot 内部动作时长** —— 动作应该在该 shot 时间窗内完成（前 50% 时间做动作，后 50% 时间稳态停留），不要让动作跨 shot 边界。
3. **2 图=1 Clip 合并**仍然适用本范式 —— 跟 v3 范式一样用 `--image` + `--last-frame`，但 prompt 内部用显式时间窗切分。
4. **不要写"at 1.2 seconds the camera X"**这种**散文时间戳** —— 改用**显式时间窗**（`from 1.2s to 8.0s`）才精准。
5. **`@Image1` `@Image2` 是写给模型看的标记** —— 实际调用靠 `--image` + `--last-frame` 传参绑定。
6. **风格段必须** —— 领读绘本风格一致性靠这句话锁。
7. **buffer 不要留太长** —— 1-1.5s 是上限。再长会显得画面"在等"，破坏节奏。
8. **音频段和视觉段同样重要** —— 视觉段只写"动作"（不写音效词，避免触发持续音），音效全部集中在 `Storyboard Audio Description` 段。

---

## 关联 skill 章节

- `picturebook-video/SKILL.md` Phase 5 Step 1-4：分镜设计四步走
- `picturebook-video/SKILL.md` Phase 8 必读 · 绘本 prompt 三铁律 + 范式选择决策树
- `picturebook-video/SKILL.md` Phase 8 必读 · 单测门 SOP（v7 范式专项检查 ⑥⑦⑧）
- `picturebook-video/references/绘本音效-prompt写法.md` §7 · Storyboard Audio Description 模式（v7 范式音频段写法）

---

## 实测 pitfall（v7 范式 · 演化教训）

> v5/v6 的失败原因已在文件顶部"范式状态"段说明。**下面只记录 v7 范式本身的坑**。

1. **数字缩写"1.2s"被三铁律自检误判为句号** → 自检脚本需要把 `\d+\.\d+s` 排除出句号统计（v7 范式的已知限制，不影响生成）。

2. **v7 关键发现**（里程碑）：**音频模型"会听否定句"**——这是 v6 → v7 的最大突破。视觉模型不擅长"反向作画"（三铁律 3），但**音频模型对 `No X / No Y` 的禁令是遵守的**（参考示例验证 + Cactus 4 段实测通过）。**这意味着音频控制可以用否定句，视觉控制不能用**。

3. **"final frame" 位置在段 4**（音频段之前）→ v7 范式固定位置（视觉段 2-3、收势段 4、音频段 5、禁令段 6、风格段 7）。**收势词永远在音频段之前**——符合三铁律 2（收势词是最后一句画面描述）。

4. **音频段不要嵌入视觉句** → 三铁律 1 在视觉段是金科玉律（分号/逗号串接），但**音频段需要独立**——Seedance 看到 `Storyboard Audio Description: X.Xs to Y.Ys [音效]...` 这种**带时间窗的音频段**会精准执行，但看到嵌入视觉句的"soft chime"会当成**持续环境音**处理。

5. **v7 验证的"精准音频控制"** → 用 `Storyboard Audio Description` 段 + `No X` 禁令段 = 精准卡点音效 + 零人声零 BGM。**这是 v7 里程碑的核心**。
