---
name: 分镜时序-prompt范式-v9
description: v8 按 shot 切 BGM 导致 clip 内部 BGM 断层（用户反馈"分成小段小段"令人不适）。v9 修正：整 Clip 一段 BGM 主题贯穿 + `mood shift / softly evolves` 软描述调性变化，**不按 shot 切 BGM**。v8 vs v9 关键差异：段 5 音频描述从"每 shot 一段 BGM 调性词"变为"整 Clip 一段 BGM 主题 + 持续标记 + 软调性变化"。来源：2026-06-03 Eat 吃绘本 8 图分 4 Clip 实测（AI 量化 -22~-34dB 持续平滑曲线，3.5s 边界无断层）。
triggers:
  - 分镜时序 v9
  - 整 Clip BGM
  - 调性渐变
  - 防止 BGM 断层
  - BGM 不切太碎
  - mood shift
---

# 分镜时序-prompt 范式 v9 · 整 Clip 一致 BGM 版

> **v7 / v8 / v9 三范式并存**（按绘本调性选）：
> - **v7** 静默氛围型（Cactus 沙漠孤独）—— 无 BGM
> - **v8** 调性匹配型（Red/Ok 好的 单 Clip 多情绪）—— 按 shot 切 BGM（**已知有 clip 内部断层问题**）
> - **v9** 整 Clip 一致型（Eat 吃 同主题 BGM 渐变）—— 整 Clip 一段 BGM + 调性渐变

---

## 1. v9 出现的根因

**v8 已知问题**（2026-06-03 用户反馈）：

> "虽然同一个 clip 里视频画面是分段的，但实际上画面之间也是合理切分，他们之间也是有转场衔接的。同一个 clip 时间本来就不长，如果 BGM 切换太频繁，会信人不适。"

**v8 写法**（问题版）：

```
Storyboard Audio Description: [Shot1 BGM: ukulele] throughout this shot, [t1] [拟声1]; [Shot2 BGM: 吉他钢琴] throughout this shot, [t2] [拟声2]; [t3] [收尾];
```

**结果**：3.5s 边界 ukulele 戛然而止 + 吉他钢琴突然开始——**clip 内部 BGM 断层**。

**v9 修正**：

```
Storyboard Audio Description: [整 Clip BGM 主题] continues throughout the entire clip, with [mood shift 描述] during the second half; [t1] [拟声1]; [t2] [拟声2]; [t3] [收尾];
```

**结果**：整 Clip 一段 BGM 主题（ukulele），3.5s 边界不切 BGM，只调情绪（mood shift）。

---

## 2. v9 完整 prompt 范式（8 段结构）

### 2.1 8 段结构

| 段 | 内容 | 关键写法 |
|---|---|---|
| 1 | 引导句 | `This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video` |
| 2 | Shot 1 视觉 | `from X.Xs to Y.Ys @Image1 is the opening shot, in this shot [动作], then [稳态]` |
| 3 | Shot 2 视觉 | `from X.Xs to Y.Ys @Image2 is the second shot, in this shot [动作], then [稳态]` |
| 4 | 收势 | `final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame` |
| **5** | **音频描述（整 Clip 一段 BGM 主题 + 拟声卡点）** | **`[整 Clip BGM 主题] continues throughout the entire clip, with [mood shift 描述]; [t1] [拟声1]; [t2] [拟声2]; [t3] [收尾];`** |
| 6 | 禁令（只禁人声）| `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling` |
| 7 | 风格 | `Children's picture book ... style, ...` |
| 8 | 句号收尾 | `.` |

### 2.2 段 5 音频描述完整写法（v9 核心）

**格式**：

```
Storyboard Audio Description: [整 Clip BGM 主题 + 乐器 + 调性 + 情绪] continues throughout the entire clip, with [mood shift / transition / softly evolves 软描述] during the second half; [t1] [拟声1]; [t2] [拟声2]; [t3] [收尾];
```

**示例（Eat 吃 Clip 1 v9 实际跑通）**：

```
Storyboard Audio Description: playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the apple; [0.0s] soft excited bubble as the small bear greets the food, gentle tap as a strawberry lands on the plate; [3.5s] soft plop as the apple is lifted, gentle whoosh as the camera pushes in; [7.0s] quiet warm chime settles;
```

**关键**：

- 整 Clip **只有一段 BGM 主题**（不按 shot 切）
- 必含 `continues throughout the entire clip`（持续标记）
- 调性变化用 `with a gentle mood shift toward X during the second half` 软描述
- 末尾接拟声卡点（`[t] 拟声`）

---

## 3. v9 调性词参考库（整 Clip 写法）

| 场景情绪 | 整 Clip BGM 调性词 | mood shift 软描述 |
|---|---|---|
| 吃东西+情绪渐变 | `playful cheerful warm ukulele pizzicato melody continues throughout the entire clip` | `with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the apple` |
| 出发+回家 | `bright adventurous pizzicato and light flute melody continues throughout the entire clip` | `with a warm homecoming softening during the second half as the scene transitions to the doorway` |
| 森林+共读 | `playful adventurous melody continues throughout the entire clip` | `with a calm warm piano softening during the second half as the scene shifts indoors` |
| 玩耍+结束 | `lively accordion and light percussion melody continues throughout the entire clip` | `with a hopeful uplifting tone building in the final seconds` |
| 晚安+彩虹 | `soft tender lullaby with music box continues throughout the entire clip` | `with a hopeful uplifting warm orchestra rising in the second half as the rainbow appears` |

**写作规则**：

- 必含 3 个要素：**乐器**（ukulele / piano / strings / guitar / accordion / xylophone / flute / bells）+ **调性形容词**（playful / gentle / warm / soft / bouncy / tender / uplifting）+ **场景情绪**（celebratory / curious / hungry / bedtime）
- 用 `,` 分隔三个要素
- 末尾加 `continues throughout the entire clip`（持续标记）
- mood shift 用 `with a gentle mood shift toward X during the second half`（软描述，不切 BGM）

---

## 4. 段 6 禁令段（v9 必读，与 v8 完全相同）

```
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
```

**绝对不要写**：

- ❌ `No background music`（会让 Seedance 完全不生成 BGM）
- ❌ `No music` / `No melody`（同上）

**禁人声铁律**：BGM 必须是纯音乐，**绝对不能有人声**。

---

## 5. v7 / v8 / v9 三范式对比

| 项 | v7（静默氛围型） | v8（调性匹配型） | **v9（整 Clip 一致型）** |
|---|---|---|---|
| **适用场景** | 安静 / 治愈 / 睡前 / 单色系 / 沙漠 | 多情绪 / 暖色 / 活泼 / 故事化 / 复杂调性 | **同主题多动作 / 一致性 > 复杂度** |
| **段 5 音频描述** | 只写拟声卡点 | **每 shot 一段 BGM 调性词** | **整 Clip 一段 BGM 主题 + mood shift** |
| **BGM 主题数 / Clip** | 0 | 2（按 shot 切）| **1（整 Clip 一致）** |
| **shot 边界 BGM** | 无 BGM 不切 | **硬切（用户反馈断层）** | **平缓渐变（不切）** |
| **段 6 写法** | `No background music, no human voice, no narration, no singing` | `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling` | **同 v8** |
| **实测案例** | Cactus（4 段静默）| Red 苹果 / Ok 好的（4 段多情绪）| **Eat 吃（4 段同主题渐变）** |

---

## 6. 决策树（v7 / v8 / v9 选择）

```
绘本调性需求？
├── 安静治愈 / 睡前 / 单色系 / 氛围为主
│   └── 选 v7（静默氛围型）
│       - 段 6: No background music, no human voice, no narration, no singing
│       - 段 5: 只写拟声卡点
│       - 实测: Cactus
│
├── 多情绪场景 / 暖色 / 活泼 / 复杂调性 / 按 shot 切 BGM 可接受
│   └── 选 v8（调性匹配型）
│       - 段 5: 每 shot 一段 BGM 调性词
│       - 段 6: 删 No background music
│       - 实测: Red 苹果、Ok 好的
│       - ⚠️ 已知问题: shot 边界 BGM 硬切
│
└── 同主题多动作 / 一致性优先 / 怕 BGM 断层
    └── 选 v9（整 Clip 一致型）✅ 推荐
        - 段 5: 整 Clip 一段 BGM 主题 + mood shift 软描述
        - 段 6: 同 v8（删 No background music）
        - 实测: Eat 吃
```

**关键判断信号**：

- 用户说"安静的"/"沙漠"/"治愈" → v7
- 用户说"复杂的"/"多情绪" + 能接受 BGM 在 shot 边界切 → v8
- 用户说"连贯的"/"统一的"/"不要 BGM 切换太频繁" → **v9** ✅
- 用户没说 → **默认 v9**（2026-06-03 起绘本默认走 v9，v8 作为备选）

---

## 7. 11 项自检脚本（v9 专用）

| # | 检查项 | v7 通过 | v8 通过 | **v9 通过** |
|---|---|---|---|---|
| 1 | 段 1 引导句 `storyboard reference image sequence` | ✅ | ✅ | ✅ |
| 2 | 段 2-3 显式时序 `from X.Xs to Y.Ys @ImageN` | ✅ | ✅ | ✅ |
| 3 | 段 4 收势 `final frame: ... holds to the last frame` | ✅ | ✅ | ✅ |
| 4 | 段 5 `Storyboard Audio Description:` | ✅ | ✅ | ✅ |
| 5 | 段 5 BGM 调性词 | ❌ | ✅ `throughout this shot` | ✅ **`continues throughout the entire clip`** |
| 6 | 段 5 mood shift 软描述 | ❌ | ❌ | ✅ `mood shift` 必含 |
| 7 | 段 6 必禁 `No background music` | ✅ 必须有 | ❌ 不能有 | ❌ 不能有 |
| 8 | 段 7 风格锚点 `Children's picture book` | ✅ | ✅ | ✅ |
| 9 | 视觉段无 `no / no BGM / no speech` | ✅ | ✅ | ✅ |
| 10 | 无独立 `[Sound effect: ...]` 块 | ✅ | ✅ | ✅ |
| 11 | 收势词在最后一句画面描述 | ✅ | ✅ | ✅ |

**v9 关键检查项**：第 5 项（`continues throughout the entire clip`）+ 第 6 项（`mood shift`）。

---

## 8. seedance.py 调用（v9 完整命令）

```bash
python3 seedance.py create \
  --image ./1.jpg \
  --last-frame ./2.jpg \
  --prompt "<上面 v9 完整 prompt>" \
  --duration 8 \
  --ratio 16:9 \
  --watermark false \
  --generate-audio true \
  --wait \
  --download ./output/clip1-v9.mp4
```

**v9 关键参数**：

- `--watermark false`（绘本默认无水印）
- `--generate-audio true`（v9 必须有 BGM 音频流）

---

## 9. Eat 吃绘本 v9 实际跑通示例

### Clip 1 v9（8s，图 1+2）—— 整 Clip BGM 首测

**完整 prompt 文本**：

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 3.5s @Image1 is the opening shot, a small round teddy bear sits at a wooden dining table in a warm cozy kitchen with arms raised in a happy welcoming gesture, surrounded by a colorful spread of fruits and bread on the table, the bear's mouth is open with a joyful expression, in this shot the bear holds the welcoming arms-up pose with warm kitchen light glowing, then the bear holds the pose for the rest of this shot;
from 3.5s to 7.0s @Image2 is the second shot, the small bear holds a red apple in both paws with a delighted expression, the kitchen background stays warm and cozy, the camera slowly pushes in toward the apple, in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose for the rest of this shot;
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the apple; [0.0s] soft excited bubble as the small bear greets the food, gentle tap as a strawberry lands on the plate; [3.5s] soft plop as the apple is lifted, gentle whoosh as the camera pushes in; [7.0s] quiet warm chime settles;
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
Children's picture book illustration style, Eric Carle paper-cut collage with watercolor wash, round Q-version teddy bear character, warm color palette of cream, brown, orange, red, paper texture with visible torn edges, handcrafted feel, the word 'EAT' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays.
```

**AI 量化验证**（v8 vs v9 音量曲线对比）：

| 时间 | v8（按 shot 切） | **v9（整 Clip 一致）** |
|---|---|---|
| 0.0s | -inf | -inf |
| 0.5-3.0s | -52 ~ -34 dB（稀疏）| **-27 ~ -33 dB（持续）** |
| **3.5s（边界）** | **-15 ~ -25 dB（突然出现）** | **-24 dB（平缓延续）** |
| 4.0-7.0s | -16 ~ -23 dB | **-23 ~ -29 dB（持续）** |
| 整 Clip 评价 | shot 边界 BGM 硬切 | **一条平滑曲线贯穿 0.5s-7.5s** |

**关键成功**：**3.5s shot 边界 BGM 没有断层**——`mood shift` 调性渐变带来自然音量起伏（-33 dB → -23 dB → -29 dB），不是硬切。

---

## 10. 4 Clip 整 Clip BGM 调性词表（Eat 吃 v9）

| Clip | Shot 数 | 整 Clip BGM 主题 | mood shift 描述 |
|---|---|---|---|
| 1 | 1+2 (图 1+2) | playful cheerful warm ukulele pizzicato melody | gentle mood shift toward curious warm tone during second half as bear explores apple |
| 2 | 3+4 (图 3+4) | bouncy happy xylophone and pizzicato strings | rhythm gently brightening during second half as bear discovers carrot |
| 3 | 5+6 (图 5+6) | warm cozy acoustic guitar with soft piano | tender lullaby-like softening during second half as scene shifts to bread |
| 4 | 7+8 (图 7+8) | joyful celebratory warm bells and pizzicato orchestra | building to hopeful uplifting tone in final seconds as bear celebrates eating everything |

**4 段不同 BGM 主题，段内 mood shift 自然渐变**——Seedance 一次生成整 Clip 同主题 BGM。

---

## 11. 关键教训（2026-06-03 v8 → v9 沉淀）

### 11.1 v8 失败根因

v8 按 shot 切 BGM 是基于"每段画面情绪不同"的直觉，但忽略了：

- **shot 边界是 Seedance 自动切分**（不是用户切的）
- **每 shot BGM 都是独立生成**（Seedance 不跨 shot 共享 BGM 上下文）
- **结果**：shot 边界 BGM 硬切，不自然

### 11.2 v9 成功根因

v9 反直觉：让 Seedance 生成"整 Clip 一段 BGM"——这意味着 Seedance 在 0.5s 就"知道"整段 BGM 走向，靠：

- `continues throughout the entire clip` 持续标记
- `with a mood shift toward X during the second half` 软描述调性变化
- **不切 BGM 主题**——只用 mood 词描述变化

### 11.3 工作方法论教训（用户反馈驱动）

> 用户原话："**听用户原话要听场景，不要脑补到相邻概念**"

**我之前误读**：把"clip 内部 BGM 断层"脑补成"clip 之间 BGM 衔接"
**用户原意**：同一个 Clip 内 8-10s 内 BGM 不要切太碎（一个 Clip 一段 BGM 主题）
**根因**：用户描述时只说"断层"，我脑补到"衔接"这个相邻概念，没回到用户原始场景

**修复**：

- 用户反馈模糊概念时**先问"是哪个范围"**（clip 之间 / clip 内部 / shot 之间）
- 不要直接给出"相邻概念"的方案
- **让用户澄清**比"猜一个并错下去"成本低

---

## 12. 反模式（v9 必避）

| ❌ 反模式 | 后果 | 修复 |
|---|---|---|
| 段 6 写 `No background music` | Seedance 不生成 BGM | 删除（v9 让 BGM 自由）|
| 段 5 只写拟声不写 BGM 主题 | 只生成稀疏音效 | 加 BGM 主题 + `continues throughout the entire clip` |
| 段 5 写 `play BGM` / `play music` | 模型自由发挥 | 用 `[乐器] + [调性形容词] + [场景情绪] continues throughout the entire clip` |
| **段 5 每 shot 一段 BGM 调性词**（v8 写法）| **shot 边界 BGM 硬切** | **合并为整 Clip 一段 + mood shift 软描述** |
| 段 5 缺 `continues throughout the entire clip` | BGM 不持续铺底 | 加 `continues throughout the entire clip` |
| 段 5 缺 `mood shift` 软描述 | 整 Clip 同调性无聊 | 加 `with a gentle mood shift toward X during the second half` |
| 用 MiniMax 生成 BGM 后期铺 | 用户禁止 | v9 走 Seedance 自带 BGM |

---

## 13. v7+v8+v9 三范式并存说明

**三个范式不冲突，适用不同场景**：

| 范式 | 适用 | 段 5 BGM 写法 | 段 6 写法 | 决策信号 |
|---|---|---|---|---|
| **v7 静默氛围型** | 安静 / 治愈 / 单色系 | 只写拟声 | `No background music, ...` | "安静"/"沙漠" |
| **v8 调性匹配型** | 多情绪 / 暖色 / 复杂调性 | 每 shot 一段 BGM | `No human voice, ...`（删 BGM 禁令）| "复杂"/"多情绪" |
| **v9 整 Clip 一致型** | 同主题多动作 / 一致性优先 | 整 Clip 一段 + mood shift | 同 v8 | "连贯"/"不要切太碎" / 默认 |

**默认**：绘本启动 → **v9**（除非用户明确要 v7 静默型或 v8 调性匹配型）。

**切换范式方法**：

- v7 → v8：段 5 加 BGM 调性词 + 段 6 删 `No background music` + 段 6 加 `no dialogue, no vocal, no humming, no whistling`
- v8 → v9：段 5 合并每 shot BGM 调性词为整 Clip 一段 + 加 `continues throughout the entire clip` + 加 `mood shift` 软描述
- v7 → v9：跳过 v8 直接升级

**选择记录**：每次绘本启动把范式版本号写进 `clips-prompt.json` 的 `version` 字段（如 `"v9-20260603"`）。

---

## 14. 关键产物路径

| 文件 | 路径 | 用途 |
|---|---|---|
| v7 范式文档 | `references/分镜时序-prompt范式-v7.md` | Cactus 等静默型绘本参考 |
| v8 范式文档 | `references/分镜时序-prompt范式-v8.md` | Red/Ok 等多情绪绘本参考（已知有 clip 内部断层问题）|
| **v9 范式文档（本文）** | `references/分镜时序-prompt范式-v9.md` | **Eat 吃等整 Clip 一致性绘本参考 ✅ 推荐** |
| v7 真实示例 | `assets/example-prompts/cactus-clip1-v7.txt` + `cactus-clips-2-3-4-v7.txt` | v7 范式参考 |
| v8 真实示例 | `assets/example-prompts/ok-clips-1-4-v8.txt` | v8 范式参考 |
| **v9 真实示例** | `assets/example-prompts/eat-clips-1-4-v9.txt` | **v9 范式参考（本任务产出）** |
| **v9 自动化脚本** | `scripts/build_v9_clips.py` | **v9 自动化生成（本任务产出）** |

---

## 15. 自动化产物（Eat 吃绘本 2026-06-03）

**项目目录**：`/home/luo/huiben-projects/20260603-eat-picbook/`

**v9 prompt 文件**：`clips-prompt.json`（4 Clip prompt 结构化 + v9 标记）

**v9 视频文件**：

- `output/clip1-v9.mp4`（单测 ✅ 通过）
- `output/clip2-v9.mp4` / `clip3-v9.mp4` / `clip4-v9.mp4`（待用户确认后批量）

**v9 自动化脚本**：`build_clips.py`（含 v9 专属 11 项自检）
