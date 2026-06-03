---
name: 分镜时序-prompt范式-v8
description: 在 v7 范式基础上，给 Storyboard Audio Description 段增加「BGM 调性词前缀」+ 「throughout this shot」后缀，让 Seedance 2.0 在每个 shot 持续铺一段纯音乐 BGM（与场景调性相符），同时保留卡点拟声 + 零人声。**v7+v8 双范式并存**：v7 静默氛围型（无 BGM）/ v8 调性匹配型（每 Clip 一首 BGM）。来源：2026-06-03 Ok 好的绘本 8 图分 4 Clip 实测沉淀（v3 prompt，音频音量 -15~-25dB BGM 持续铺底）。
triggers:
  - 分镜时序 v8
  - 调性匹配 BGM
  - 每 Clip 配 BGM
  - BGM 自由生成
  - 绘本 BGM
  - 调性匹配型
---

# 分镜时序-prompt 范式 v8 · 调性匹配型 BGM 版

> **v7 与 v8 并存**：v7 = 静默氛围型（Cactus 默认）/ v8 = 调性匹配型（Red/Ok 好的默认）。**根据绘本调性选范式**（见 §6 决策树）。

---

## 1. 范式核心差异（v7 vs v8）

| 项 | v7（静默氛围型） | v8（调性匹配型） |
|---|---|---|
| **适用场景** | 安静 / 治愈 / 睡前 / 单色系 / 沙漠夜景 | 多情绪 / 暖色 / 活泼 / 故事化 / 多 Clip 不同调性 |
| **段 6 写法** | `No background music, no human voice, no narration, no singing` | `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling`（**删除 `No background music`**）|
| **段 5 音频描述** | 只写拟声卡点 | 写 **BGM 调性词 + 持续标记 + 拟声卡点** |
| **实测案例** | Cactus 仙人掌坚强（4 段静默） | Red 红苹果（4 段温馨）、Ok 好的（4 段多情绪）|

**v8 关键新增**：段 5 音频描述每 shot 加 BGM 调性词前缀 + `throughout this shot` 后缀。

---

## 2. v8 完整 prompt 范式（8 段结构）

### 2.1 8 段结构

| 段 | 内容 | 关键写法 |
|---|---|---|
| 1 | 引导句 | `This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video` |
| 2 | Shot 1 视觉 | `from X.Xs to Y.Ys @Image1 is the opening shot, in this shot [动作], then [稳态]` |
| 3 | Shot 2 视觉 | `from X.Xs to Y.Ys @Image2 is the second shot, in this shot [动作], then [稳态]` |
| 4 | 收势 | `final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame` |
| **5** | **音频描述（BGM + 拟声）** | **每 shot：BGM 调性词 throughout this shot + 关键时间点 [t] 拟声** |
| 6 | 禁令（只禁人声）| `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling` |
| 7 | 风格 | `Children's picture book ... style, ...` |
| 8 | 句号收尾 | `.` |

### 2.2 段 5 音频描述完整写法（v8 核心）

**格式**：
```
Storyboard Audio Description: [BGM调性词1] throughout this shot, [t1] [拟声1]; [BGM调性词2] throughout this shot, [t2] [拟声2]; [t3] [收尾拟声];
```

**示例（Ok 好的 Clip 1 v3 实际跑通）**：
```
Storyboard Audio Description: playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood throughout this shot, [0.0s] gentle paper-landing tap-tap-tap as the thumbs-up pose settles; gentle warm acoustic guitar, tender send-off mood with soft piano throughout this shot, [3.5s] soft morning whoosh as the door swings open, gentle whoosh as golden sunlight pours in; [7.0s] quiet warm chime settles;
```

**关键**：
- 每个 shot **先写 BGM 调性词**（乐器 + 调性 + 情绪 + throughout this shot）
- 之后写**关键时间点的拟声**（`[t] 拟声描述`）
- 段与段用 `;` 分隔
- **BGM 调性词不要写 `play BGM` / `music`**——直接写乐器名（ukulele / piano / strings）+ 调性形容词（playful / gentle / warm）

---

## 3. 段 5 BGM 调性词参考库

| 场景情绪 | BGM 调性词 | 期望 BGM |
|---|---|---|
| 舞台/聚会/鼓掌 | `playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood` | 欢快活泼 |
| 送别/挥手/出门 | `gentle warm acoustic guitar, tender send-off mood with soft piano` | 温馨柔和 |
| 森林/出发/冒险 | `playful adventurous pizzicato and light flute melody, bright cheerful mood` | 轻快明亮 |
| 室内/共读/理解 | `gentle warm piano with soft strings, calm understanding mood` | 平静温暖 |
| 餐桌/吃饭/流口水 | `happy hungry bouncy xylophone and pizzicato strings, joyful excited mood` | 欢快跳跃 |
| 户外/玩耍/奔跑 | `playful lively accordion and light percussion, energetic outdoor mood` | 活泼动感 |
| 卧室/晚安/亲吻 | `soft tender lullaby with music box and soft piano, gentle loving bedtime mood` | 温柔安静 |
| 彩虹/结束/圆满 | `uplifting hopeful warm orchestra with strings and gentle bells, all-is-well ending mood` | 升华希望 |

**写作规则**：
- 必含 3 个要素：**乐器**（ukulele / piano / strings / guitar / accordion / xylophone / flute / bells）+ **调性形容词**（playful / gentle / warm / soft / bouncy / tender / uplifting）+ **场景情绪**（celebratory / send-off / hungry / bedtime）
- 用 `,` 分隔三个要素
- 末尾加 `throughout this shot`（让 BGM 持续整个 shot 而非卡点）

---

## 4. 段 6 禁令段完整写法（v8 必读）

**v8 禁令段**（**只禁人声，**不**禁 BGM**）：
```
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
```

**禁词清单**（v8 必含）：
- ✅ `No human voice`（人声）
- ✅ `No narration`（旁白叙述）
- ✅ `No singing`（歌唱）
- ✅ `No dialogue`（对话）
- ✅ `No vocal`（嗓音/声乐）
- ✅ `No humming`（哼唱）
- ✅ `No whistling`（口哨）

**绝对不要写**（v8 vs v7 关键差异）：
- ❌ **`No background music`**（会让 Seedance 完全不生成 BGM）
- ❌ **`No music`**（同上）
- ❌ **`No melody`**（同上）

---

## 5. v8 调性匹配型 BGM 控制三铁律

> 用户原话 2026-06-03："BGM 一定是纯音乐，不要有人声，这是绝对禁止"

| 铁律 | 规则 | 原因 |
|---|---|---|
| **1. 必须禁人声** | 段 6 含 `no human voice / no singing / no vocal / no humming / no whistling` | BGM 必须是纯音乐，**绝对不能有人声** |
| **2. 段 5 写 BGM 调性词** | 段 5 每 shot 加 `[乐器] + [调性形容词] + [场景情绪] throughout this shot` | 让 Seedance 知道要生成持续 BGM 配画面调性 |
| **3. 不在视觉段写 `play BGM / music`** | 视觉段只写画面 + 调性情绪词 | 模型看到"music"会自由发挥，**画面段已写清楚情绪词足够驱动 BGM 调性** |

---

## 6. 决策树（v7 vs v8 选择）

```
绘本调性需求？
├── 安静治愈 / 睡前 / 单色系 / 氛围为主
│   └── 选 v7（静默氛围型）
│       - 段 6: No background music, no human voice, no narration, no singing
│       - 段 5: 只写拟声卡点
│       - 实测: Cactus 仙人掌
│
└── 多情绪场景 / 暖色 / 活泼 / 故事化 / 多 Clip 不同调性
    └── 选 v8（调性匹配型）
        - 段 6: 只禁人声（删 No background music）
        - 段 5: BGM 调性词 + 持续标记 + 拟声卡点
        - 实测: Red 红苹果、Ok 好的
```

**关键判断信号**：
- 用户说"安静的绘本"/"治愈"/"沙漠"/"夜晚" → v7
- 用户说"活泼的"/"多情绪"/"每段不同调性"/"故事化" → v8
- 用户没明说 → **默认 v8**（2026-06-03 起绘本默认走 v8）

---

## 7. 11 项自检脚本（v8 专用）

| # | 检查项 | v7 通过条件 | v8 通过条件 |
|---|---|---|---|
| 1 | 段 1 引导句 | ✅ `storyboard reference image sequence` | ✅ 同 v7 |
| 2 | 段 2-3 shot 时序 | ✅ `from X.Xs to Y.Ys @ImageN` | ✅ 同 v7 |
| 3 | 段 4 收势词 | ✅ `final frame: ... holds to the last frame` | ✅ 同 v7 |
| 4 | 段 5 音频描述 | ✅ `Storyboard Audio Description:` | ✅ 同 v7 |
| 5 | 段 5 BGM 调性词（v8 专属）| ❌ 不需要 | ✅ `throughout this shot` |
| 6 | 段 6 禁令 | ✅ `No background music, no human voice, no narration, no singing` | ✅ `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling` |
| 7 | 段 6 必禁 `No background music`（v8 专属）| ✅ 必须有 | ❌ **绝对不能有**（v8 让 BGM 自由生成）|
| 8 | 段 7 风格锚点 | ✅ `Children's picture book` | ✅ 同 v7 |
| 9 | 视觉段无 `no / no BGM / no speech` | ✅ 必须 | ✅ 必须 |
| 10 | 无独立 `[Sound effect: ...]` 块 | ✅ 必须 | ✅ 必须 |
| 11 | 收势词在最后一句画面描述 | ✅ 必须 | ✅ 必须 |

**v8 vs v7 第 7 项是反的**——这是范式分叉点。

---

## 8. seedance.py 调用（v8 完整命令）

```bash
python3 seedance.py create \
  --image ./1.jpg \
  --last-frame ./2.jpg \
  --prompt "<上面 v8 完整 prompt>" \
  --duration 8 \
  --ratio 16:9 \
  --watermark false \
  --generate-audio true \
  --wait \
  --download ./output/clip1-v8.mp4
```

**v8 关键参数**：
- `--watermark false`（绘本默认无水印，2026-06-03 用户偏好）
- `--generate-audio true`（v8 必须有 BGM 音频流）

---

## 9. Ok 好的绘本 v3 实际跑通示例

### Clip 1 v3（8s，图 1+2）—— BGM 调性匹配首测

**完整 prompt**：
```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 3.5s @Image1 is the opening shot, a small round bear stands center stage on a circular wooden stage with a warm celebratory atmosphere, surrounded by small forest animal audience clapping, paper-collage crafted theater with warm orange-yellow curtain backdrop, in this shot the small bear raises its right paw to give a thumbs-up with warm light bloom expanding, then the bear holds the thumbs-up pose for the rest of this shot;
from 3.5s to 7.0s @Image2 is the second shot, a warm cozy doorway scene at sunrise with a tender send-off mood, golden sunlight pouring in from the open wooden door onto a yellow tiled floor, a mama bear on the right waves goodbye with her left paw, a small bear with a blue-yellow backpack stands on the left stepping through the doorway, in this shot the small bear steps forward through the doorway with the thumbs-up pose, then the small bear holds the pose for the rest of this shot;
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood throughout this shot, [0.0s] gentle paper-landing tap-tap-tap as the thumbs-up pose settles; gentle warm acoustic guitar, tender send-off mood with soft piano throughout this shot, [3.5s] soft morning whoosh as the door swings open, gentle whoosh as golden sunlight pours in; [7.0s] quiet warm chime settles;
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
Children's picture book illustration style, paper-cut collage with watercolor wash, round Q-version cartoon animals, warm color palette of orange, yellow, brown, paper texture with visible torn edges, handcrafted feel, bright primary colors, the word 'OK' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays.
```

**AI 量化验证**：

| 指标 | Red v3 参考 | Ok v3 |
|---|---|---|
| 视频大小 | 12.4 Mbps | 3.6 Mbps |
| 音频平均音量 | -29 ~ -33 dB | **-15 ~ -25 dB（更响）** |
| BGM 持续性 | ✅ 持续 | ✅ 持续 |
| 水印 | 无 | 无 |

**用户验证反馈**（2026-06-03）：
> "OK，这次效果很不错，这是一次非常成功的探索。"

---

## 10. 4 Clip 调性词表（Ok 好的 v3）

| Clip | Shot 1 调性词 | Shot 2 调性词 |
|---|---|---|
| 1 (8s, 图 1+2) | playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood | gentle warm acoustic guitar, tender send-off mood with soft piano |
| 2 (9s, 图 3+4) | playful adventurous pizzicato and light flute melody, bright cheerful mood | gentle warm piano with soft strings, calm understanding mood |
| 3 (9s, 图 5+6) | happy hungry bouncy xylophone and pizzicato strings, joyful excited mood | playful lively accordion and light percussion, energetic outdoor mood |
| 4 (10s, 图 7+8) | soft tender lullaby with music box and soft piano, gentle loving bedtime mood | uplifting hopeful warm orchestra with strings and gentle bells, all-is-well ending mood |

**调性多样性验证**：4 个 Clip 用了 8 段不同 BGM 调性（不要求系列统一——用户原话"我不要求 Clip 1、Clip 2、Clip 3、Clip 4 保持统一的调性，只需要每一组、每一个 Clip 生成的 BGM 和画面的场景相符就可以了"）。

---

## 11. 关键教训（2026-06-03 Ok 好的绘本 v1→v2→v3 沉淀）

1. **v1 失败原因**：写了 `No background music` 禁令段（v7 写法）→ Seedance 完全不生成 BGM
2. **v2 失败原因**：删除 `No background music` 但段 5 音频描述只写拟声卡点 → Seedance 仍然不生成 BGM（只生成稀疏音效）
3. **v3 成功原因**：段 5 音频描述**每 shot 加 BGM 调性词前缀** + `throughout this shot` 持续标记 → BGM 持续铺底成功

**v7 → v8 范式升级的关键洞察**：
- 段 6 删 `No background music` 是**必要条件**（v1 失败就因有这词）
- 段 5 加 BGM 调性词 + `throughout this shot` 是**充分条件**（v2 失败就因没加）
- 两者**同时满足** → Seedance 才会生成持续 BGM

---

## 12. 反模式（v8 必避）

| ❌ 反模式 | 后果 | 修复 |
|---|---|---|
| 段 6 写 `No background music` | Seedance 完全不生成 BGM | 删除（v8 让 BGM 自由）|
| 段 5 只写拟声不写 BGM 调性词 | 只生成稀疏音效无 BGM | 每 shot 加 BGM 调性词前缀 |
| 段 5 写 `play BGM` / `play music` | 模型自由发挥，BGM 调性不可控 | 改用 `[乐器] + [调性形容词] + [场景情绪] throughout this shot` |
| 段 5 写 `BGM = X.mp3` | Seedance 不知道是文件名还是 BGM 类型 | 不要写文件名，只写乐器 + 调性 |
| 视觉段加 `BGM: X` 标记 | 模型自由发挥，破坏 v8 段 5 范式 | 视觉段只写画面 + 调性情绪词 |
| 段 5 缺 `throughout this shot` | BGM 只在卡点附近出现，不持续铺底 | 每 shot BGM 调性词后加 `throughout this shot` |
| 用 MiniMax 生成 BGM 后期铺 | 用户禁止（绘本场景禁用 MiniMax BGM）| v8 走 Seedance 自带 BGM |

---

## 13. v7+v8 双范式并存说明

**两个范式不冲突，适用不同场景**：
- **v7 静默氛围型**（Cactus 默认）：绘本调性整体安静/治愈/单色系
- **v8 调性匹配型**（Red/Ok 默认）：绘本多情绪/暖色/活泼/多 Clip 不同调性

**skill 系统设计原则**：
- 不要合并 v7+v8 → **范式选择是绘本调性决定的，硬合并会让用户失去灵活度**
- 每次绘本启动时**先选范式**（v7 还是 v8）→ 再按范式写 prompt
- 范式选择记录在 `clips-prompt.json` 的 `version` 字段（如 `"v7"` 或 `"v8"`）

**切换范式的方法**：
- v7 → v8：段 5 加 BGM 调性词 + 段 6 删 `No background music` + 段 6 加 `no dialogue, no vocal, no humming, no whistling`
- v8 → v7：段 5 删 BGM 调性词 + 段 6 删 `no dialogue, no vocal, no humming, no whistling` + 段 6 加 `No background music`

**默认**：绘本启动 → **v8**（除非用户明确要 v7 静默氛围型）。

---

## 14. 关键产物路径

| 文件 | 路径 | 用途 |
|---|---|---|
| v7 范式文档 | `references/分镜时序-prompt范式-v7.md` | Cactus 等静默型绘本参考 |
| **v8 范式文档（本文）** | `references/分镜时序-prompt范式-v8.md` | Red/Ok 等调性匹配型绘本参考 |
| v7 真实示例 | `assets/example-prompts/cactus-clip1-v7.txt` + `cactus-clips-2-3-4-v7.txt` | v7 范式参考 |
| **v8 真实示例** | `assets/example-prompts/ok-clips-1-4-v8.txt` | **v8 范式参考（本任务产出）** |
| v8 自动化脚本 | `scripts/build_v8_clips.py` | **v8 自动化生成（本任务产出）** |

---

## 15. 自动化产物（Ok 好的绘本 2026-06-03）

**脚本路径**：`/home/luo/huiben-projects/20260603-feishu-test/build_clips.py`

**v3 prompt 文件**：`/home/luo/huiben-projects/20260603-feishu-test/clips-prompt.json`

**v3 视频文件**（首批单测 + 批量）：
- `output/clip1-v3.mp4`（单测）
- `output/clip2-v3.mp4` / `clip3-v3.mp4` / `clip4-v3.mp4`（批量）

---

## 16. v8 已知问题 + v9 修正方向（2026-06-03 用户反馈）

### v8 已知问题：Clip 内部 BGM 断层

**现象**：v8 按 shot 切 BGM（如 Clip 1 Shot 1 = 0-3.5s ukulele → 3.5s 切 Shot 2 = 吉他钢琴），**shot 边界 BGM 突然切换太频繁令人不适**。

**用户原话**：
> "虽然同一个 clip 里视频画面是分段的，但实际上画面之间也是合理切分，他们之间也是有转场衔接的。同一个 clip 时间本来就不长，如果 BGM 切换太频繁，会信人不适。"

**v9 修正方向**（**待 v9 验证**）：

| v8（错） | v9（对） |
|---|---|
| 段 5 每 shot 一段 BGM 调性词 | 段 5 整 Clip 一段 BGM 主题贯穿 |
| Clip 1: `ukulele shot 1, guitar shot 2`（3.5s 硬切）| Clip 1: `playful ukulele BGM continues throughout entire clip, with gentle mood shift during the second half as the scene transitions to the doorway`（同主题渐变）|
| 4 段不同 BGM = 4 Clip × 2 shot = 8 段切换 | 4 段不同 BGM = 4 Clip（**整 Clip 一致**）|

**v9 改法**：
1. **BGM 主题按整 Clip 分配**（不是按 shot）—— 一段 BGM 主题贯穿整个 Clip 8-10s
2. **调性变化用"mood shift / transition / softly evolves"软描述**——不切 BGM 主题
3. **段 5 简化为一段**（不是 2 段 shot）

**v9 探索步骤**（下次新绘本时）：
1. 改 `build_clips.py` 的 `bgm_mood_1` / `bgm_mood_2` 合并为 `bgm_mood` 一段
2. prompt 段 5 改为：`Storyboard Audio Description: [整 Clip BGM 主题] continues throughout the entire clip, with [mood shift 描述] during the second half; [t1] [拟声1]; [t2] [拟声2]; [t3] [收尾];`
3. 单测 Clip 1 看 BGM 是否"整 Clip 一致 + 渐变"——不再有 3.5s 硬切

**v9 调研前不要下结论**——单测效果为准。

