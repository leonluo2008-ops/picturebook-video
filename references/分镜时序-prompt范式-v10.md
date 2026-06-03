---
name: 分镜时序-prompt范式-v10
description: v9 解决"clip 内部 BGM 断层"，但**clip 互相不知道对方存在**——clip 1 用 ukulele 主题，clip 2 AI 自由发挥生成为 xylophone 主题，**clip 边界调性跳变**。v10 修正：clip 1 自由定义 BGM 主题，clip 2+ 段 5 显式写 `same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip`，靠 prompt 文字约束 Seedance 选同一 BGM 主题。v9 vs v10 关键差异：clip 2+ 段 5 从"自由 BGM 主题词"变为"继承前 clip 主题词（same ... from the previous clip continues）"。来源：2026-06-03 Eat 吃绘本 4 clip 实测（人耳听感：同 ukulele pizzicato 主题连续）。
triggers:
  - 分镜时序 v10
  - 跨 Clip 同 BGM 主题
  - 跨 Clip 调性一致
  - same melody from the previous clip
  - 领读型同氛围
---

# 分镜时序-prompt 范式 v10 · 跨 Clip 共享 BGM 主题版

> **v7 / v8 / v9 / v10 四范式并存**（按绘本调性选）：
> - **v7** 静默氛围型（Cactus 沙漠孤独）—— 无 BGM
> - **v8** 调性匹配型（Red/Ok 好的 单 Clip 多情绪）—— 按 shot 切 BGM（**已知有 clip 内部断层问题**）
> - **v9** 整 Clip 一致型（Eat 吃 同主题 BGM 渐变）—— 整 Clip 一段 BGM + 调性渐变
> - **v10** 跨 Clip 同主题型（Eat 吃 领读型多 Clip 同氛围）—— 整 Clip 一段 BGM + clip 2+ 段 5 继承前 clip 主题

---

## 1. v10 出现的根因

**v9 已知局限**（2026-06-03 用户反馈）：

> "在之前的基础上，尝试使用提示词来控制 clip2 和 clip3 的 BGM 衔接，让他们具有同样的调性，因为这是儿童领读视频，不需要很准确匹配场景，只要整体氛围达到一定感觉就可以。"

**v9 写法**（clip 2/3 各自自由 BGM 主题词）：

```
Clip 1: Storyboard Audio Description: playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, ...
Clip 2: Storyboard Audio Description: bouncy happy xylophone and pizzicato strings melody continues throughout the entire clip, ...
Clip 3: Storyboard Audio Description: warm cozy acoustic guitar with soft piano melody continues throughout the entire clip, ...
```

**结果**：clip 1/2/3 三个 BGM 主题完全不一样（ukulele / xylophone / acoustic guitar）——**clip 边界 BGM 调性跳变**。

**v10 修正**（clip 2/3 段 5 显式继承 clip 1 主题）：

```
Clip 1: Storyboard Audio Description: playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, ...
Clip 2: Storyboard Audio Description: same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, ...
Clip 3: Storyboard Audio Description: same warm ukulele pizzicato melody and pizzicato strings from the previous clip continues throughout this entire clip, ...
```

**结果**：clip 1/2/3 三个 BGM 主题都是 ukulele pizzicato 系——**跨 clip 调性一致**。

---

## 2. v10 完整 prompt 范式

v10 在 v9 8 段结构基础上，**只改 1 个地方**：段 5 音频描述（clip 2+ 必含 `same ... from the previous clip continues`）。

### 2.1 clip 1（主题源）写法

和 v9 完全一样，**自由定义 BGM 主题**：

```
Storyboard Audio Description: playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the apple; [0.0s] soft excited bubble; [3.5s] soft plop; [7.0s] quiet warm chime;
```

### 2.2 clip 2+（继承源）写法

**必含** `same [clip1 BGM 主题词] from the previous clip continues throughout this entire clip`：

```
Storyboard Audio Description: same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, gently evolving with soft pizzicato strings and xylophone accents, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the banana and carrot; [0.0s] soft excited bubble; [4.0s] soft crunch sound; [8.0s] quiet warm chime;
```

**关键 4 处必含**：
1. `same [主题词] from the previous clip` —— 显式说"前 clip 用了这主题"
2. `continues throughout this entire clip` —— 持续标记（v9 关键）
3. `gently evolving with [其他乐器]` —— 同主题下可微调乐器，但主题词不变
4. `with a mood shift toward X during the second half` —— 软调性变化（v9 关键）

---

## 3. v10 数据结构（`clips-prompt.json`）

引入 `v10_bgm` 字段（继承上一 clip 主题词）：

```json
{
  "clips": [
    {
      "id": 1,
      "bgm_theme": "playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, ...",
      // clip1 不写 v10_bgm（是主题源）
      "prompt": "..."
    },
    {
      "id": 2,
      "bgm_theme": "bouncy happy xylophone ...",  // 保留 v9 bgm_theme（v9 跑时用）
      "v10_bgm": "same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, ...",  // v10 跑时用
      "prompt": "..."  // v10 build 时段 5 替换为 v10_bgm
    }
  ]
}
```

`build_v10_prompt(clip)` 函数：
- 如果 clip 有 `v10_bgm` 字段 → 用 v10_bgm 作段 5
- 否则（clip 1）→ 用 `bgm_theme` 作段 5

```python
def build_v10_prompt(clip):
    # clip1 没有 v10_bgm 字段（主题源），用 bgm_theme；其他 clip 用 v10_bgm
    bgm_theme = clip.get("v10_bgm") or clip["bgm_theme"]
    # ... 用 bgm_theme 渲染段 5，其他段同 build_v9_prompt
```

**build_v10_prompt 实现要点**（2026-06-03 Eat 吃实测）：
- 用 `clip.get("v10_bgm") or clip["bgm_theme"]` 兼容 clip1 缺字段
- 自检脚本需检查 clip 2+ 是否含 `same warm ukulele pizzicato melody` + `from the previous clip` 双关键词
- 自检脚本要兼容两种 BGM 持续标记：`continues throughout the entire clip`（v9 标准）**或** `continues throughout this entire clip`（v10 clip 2+ 变体）

---

## 4. v10 关键限制（必读）

1. **Seedance 不会真去查 clip 1 实际生成的 BGM** —— 只能靠 prompt 文字约束让它"假设"前一个 clip 用了某主题
2. **同一绘本只能选一个 BGM 主题词**（ukulele / xylophone / acoustic guitar 等）—— clip 2+ 都用同一个
3. **如果 v10 跑出来两个 clip BGM 还是不同** —— 说明 Seedance 没遵循 prompt 的"same ... from the previous clip"约束：
   - 方案 A：改 prompt 措辞 `continuing the same warm ukulele pizzicato theme from the start to the end of this clip` 更明确
   - 方案 B：退到 v9（接受跨 clip 主题变化）
   - 方案 C：加大主题词重复（段 5 多次出现 "ukulele pizzicato" 关键词）
4. **音量 dB 不能量化调性一致性**（dB 是响度不是音色）—— 调性是否一致**只能人耳听**

---

## 5. v9 vs v10 量化指标

| 指标 | v9（各自自由） | v10（共享主题词） |
|---|---|---|
| clip 2 4.0s 边界 dB | -27.4 | -29.3 |
| clip 3 4.0s 边界 dB | -23.1 | -34.2 |
| 边界 dB 差 | 4.3 dB | 4.9 dB |
| 音量 dB 是否衡量调性 | ❌（dB 是响度，不是音高/音色）| ❌（同上）|
| **人耳调性听感** | clip 2/3 BGM 风格不同 | **同 ukulele pizzicato 主题** ✅ |

**核心结论**：音量 dB 不能量化调性一致性。**调性是否一致只能人耳听**——v10 跑完后必须连续听两个 clip 的 BGM 风格判断。

---

## 6. seedance.py 调用（v10 完整命令）

`--ref-images` 多图传 `nargs="+"` 空格分隔（**不是逗号**）：

```bash
python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py create \
  --ref-images /path/to/3.jpg /path/to/4.jpg \
  --prompt "<v10 clip2 prompt 文本>" \
  --model doubao-seedance-2-0-fast-260128 \
  --watermark false \
  --ratio 16:9 \
  --duration 9 \
  --generate-audio true \
  --wait \
  --download /path/to/output/clip2-v10.mp4
```

**注意**（v10 Eat 吃绘本 2026-06-03 实测踩坑 2 个）：

- **`--ref-images` 多图必须空格分隔**（seedance.py `nargs="+"`）—— 逗号分隔会报 `File not found: a.jpg,b.jpg` 错误
  - 错版：`--ref-images a.jpg,b.jpg`
  - 对版：`--ref-images a.jpg b.jpg`
- `--duration` 单位秒，范围 4-15
- `--generate-audio true` 必加（v10 跨 clip BGM 靠 Seedance 自带音频生成）
- **`--download` 是文件路径不是目录**（v10 实测踩坑）：多 clip 并行时**每个必须用独立文件名**，否则后一个覆盖前一个
  - 模式 A（推荐）：传文件路径（命令里直接 `clip2-v10.mp4` / `clip3-v10.mp4`）
  - 模式 B：传目录路径 + 立即 `mv` 重命名（`mv output.mp4 output/clip2-v10.mp4`）
  - 错版：`--download ./output/`（多 clip 全写到 `output.mp4` 互相覆盖）

**v10 Eat 吃实测调用记录**：
- clip 2: task `cgt-20260603175454-h6w6z`（175.4s, 9s, seed 81566）
- clip 3: task `cgt-20260603175848-t8qq5`（171.4s, 9s, seed 93085）
- clip 4: task `cgt-20260603181203-s9hwb`（214.8s, 10s, seed 76084）

---

## 7. Eat 吃绘本 v10 实际跑通示例

### 7.1 clip 2 prompt 完整示例

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 4.0s @Image1 is the opening shot, the small bear holds a bright yellow banana in both paws with an excited happy face, sitting in the warm kitchen, in this shot the small bear brings the banana close to its mouth for a bite, then the small bear holds the banana-eating pose for the rest of this shot;
from 4.0s to 8.0s @Image2 is the second shot, the small bear holds a fresh orange carrot in both paws with a curious delighted expression, kitchen background stays warm, in this shot the small bear brings the carrot close to its mouth, then the small bear holds the carrot pose for the rest of this shot;
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, gently evolving with soft pizzicato strings and xylophone accents, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the banana and carrot; [0.0s] soft excited bubble, gentle peel rustle as the banana is unpeeled; [4.0s] soft crunch sound as the carrot is bitten, gentle tap as a piece lands; [8.0s] quiet warm chime settles;
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
Children's picture book illustration style, Eric Carle paper-cut collage with watercolor wash, round Q-version teddy bear character, warm color palette of cream, brown, orange, red, paper texture with visible torn edges, handcrafted feel, the word 'EAT' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays.
```

### 7.2 clip 3 prompt 完整示例

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 4.0s @Image1 is the opening shot, the small bear holds a fresh orange fish in both paws with a happy eating expression, warm kitchen background, in this shot the small bear brings the fish close to its mouth, then the small bear holds the fish-eating pose for the rest of this shot;
from 4.0s to 8.0s @Image2 is the second shot, the small bear holds a freshly baked brown bread in both paws with a warm delighted expression, kitchen background stays cozy, in this shot the small bear brings the bread close to its mouth, then the small bear holds the bread pose for the rest of this shot;
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: same warm ukulele pizzicato melody and pizzicato strings from the previous clip continues throughout this entire clip, gently evolving with soft acoustic guitar warmth, with a gentle mood shift toward a tender warm tone during the second half as the small bear discovers the fish and bread; [0.0s] soft excited bubble, gentle sizzle as the fish is presented; [4.0s] soft crust crunch, gentle warm whoosh as the aroma rises; [8.0s] quiet warm chime settles;
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
Children's picture book illustration style, Eric Carle paper-cut collage with watercolor wash, round Q-version teddy bear character, warm color palette of cream, brown, orange, red, paper texture with visible torn edges, handcrafted feel, the word 'EAT' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays.
```

**clip 2 vs clip 3 段 5 对比**：
- 都含 `same warm ukulele pizzicato melody from the previous clip`（继承源）
- clip 2 加 `xylophone accents`（微调乐器但主题词不变）
- clip 3 加 `acoustic guitar warmth`（微调乐器但主题词不变）
- 都用 `mood shift` 软描述调性变化

### 7.3 clip 4 prompt 完整示例（v10 范式 4 clip 完整跑通）

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 4.5s @Image1 is the opening shot, the small bear holds a pink frosted cake slice in both paws with mouth wide open in joyful anticipation, warm kitchen background, in this shot the small bear brings the cake close to its mouth, then the small bear holds the cake-eating pose for the rest of this shot;
from 4.5s to 9.0s @Image2 is the second shot, the small bear stands with both arms raised high in a triumphant celebration surrounded by a colorful feast of fruits, vegetables, bread, fish, and cake, the bear's smile is huge and joyful, in this shot the bear opens its arms wider to embrace all the food, then the small bear holds the celebration pose for the rest of this shot;
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: same warm ukulele pizzicato melody and pizzicato strings from the previous clip continues throughout this entire clip, gently evolving with soft celebratory bells and warm pizzicato orchestra, with a hopeful uplifting mood shift during the second half as the small bear celebrates eating everything; [0.0s] soft excited bubble, gentle frosting tap as the cake is lifted; [4.5s] soft sparkle as the feast is revealed, gentle warm chime as the celebration begins; [9.0s] single quiet warm chime as the final note;
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
Children's picture book illustration style, Eric Carle paper-cut collage with watercolor wash, round Q-version teddy bear character, warm color palette of cream, brown, orange, red, paper texture with visible torn edges, handcrafted feel, the word 'EAT' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays.
```

**clip 4 是整本绘本最后 1 段**——是唯一**应该**有完整 BGM 收势（"single quiet warm chime as the final note"）的 clip。

---

## 8. v10 必避反模式

- ❌ clip 2+ 段 5 写自由 BGM 主题词（v9 写法） → AI 自由发挥破坏同调性
- ❌ 同一绘本用多个 BGM 主题词（ukulele + xylophone 混用） → 跨 clip 不一致
- ❌ 缺 `continues throughout this entire clip` → BGM 不持续铺底
- ❌ 缺 `mood shift` 软描述 → 整 Clip 同调性无聊
- ❌ 用音量 dB 量化调性一致性（dB 是响度不是音色） → 误判 v10 失败
- ❌ 用 MiniMax 生成 BGM 后期铺（用户禁止）
- ❌ `build_v10_prompt` 对所有 clip 强制要求 `v10_bgm` 字段（clip 1 没有这个字段，会 KeyError）→ 用 `clip.get("v10_bgm") or clip["bgm_theme"]` 兼容
- ❌ **中间 clip 段 5 末尾写"quiet warm chime settles"收势词** → 收势只能用在最后 1 clip（v11 修复）

---

## 9. v7+v8+v9+v10 四范式并存说明

| 范式 | 适用 | 段 5 BGM 写法 | 段 6 写法 | 决策信号 |
|---|---|---|---|---|
| **v7 静默氛围型** | 安静 / 治愈 / 单色系 | 只写拟声 | `No background music, ...` | "安静"/"沙漠" |
| **v8 调性匹配型** | 多情绪 / 暖色 / 复杂调性 | 每 shot 一段 BGM | `No human voice, ...`（删 BGM 禁令）| "复杂"/"多情绪" |
| **v9 整 Clip 一致型** | 同主题多动作 / 一致性优先 | 整 Clip 一段 + mood shift | 同 v8 | "连贯"/"不要切太碎" / **默认** |
| **v10 跨 Clip 同主题型** | 领读型 / 多 clip 同氛围 | 整 Clip 一段 + `same ... from the previous clip continues`（clip 2+） | 同 v8 | "领读型"/"整体氛围一致" |

**默认范式**（2026-06-03 起）：绘本启动默认走 **v9**（v10 作为领读型同氛围需求备选，v8 作为复杂多情绪备选，v7 静默型保留）。

**v10 适用绘本类型**（领读型典型场景）：
- "I eat X" 系列（重复句式、整体氛围一致 > 单图调性精准）
- Pete the cat（重复情节、保持整体风格连贯）
- Dear Zoo（认知启蒙、整体温馨感）
- Brown Bear Brown Bear What Do You See（循环叙事、整体音乐氛围一致）
- 任何"重复句式 + 弱情节变化 + 整体氛围优先"的绘本

---

## 10. 关键产物路径

**v10 范式文档**：`references/分镜时序-prompt范式-v10.md`（本文件）
**v10 真实示例**：`assets/example-prompts/eat-clips-2-3-v10.txt`
**v10 自动化脚本**：在 `build_clips.py` 加 `build_v10_prompt()` 函数 + CLI `--version v9|v10` 切换（**注意**：不是 `scripts/build_v9_clips.py`，是绘本项目目录下的 `build_clips.py`）
**v10 主 SKILL.md 章节**：`§v10 范式 · 跨 Clip 共享同一 BGM 主题`

---

## 11. 关键教训（2026-06-03 v9 → v10 沉淀）

1. **绘本跨 clip 同氛围需求真实存在**（用户原话"领读型视频整体氛围达到一定感觉就可以"）—— v9 解决内部断层不够，**跨 clip 也要一致**
2. **Seedance prompt 文字约束力是有限的** —— `same ... from the previous clip` 写出来 AI 不一定真遵循，需人耳验证
3. **音量 dB 不是调性指标** —— 不能用 dB 差量化"两个 clip BGM 是否同调性"
4. **v10_bgm 字段 + CLI 切换是干净的实现** —— 不污染 v9 build，加新函数即可
5. **同一绘本 1 个 BGM 主题词** —— 多主题词混用 = 跨 clip 必不一致
6. **领读型绘本**（I eat X 系列、Pete the cat、Dear Zoo 等重复句式）特别适合 v10 —— 整体氛围一致 > 调性匹配
7. **`build_v10_prompt` 必须兼容 clip 1 无 `v10_bgm` 字段** —— 用 `clip.get("v10_bgm") or clip["bgm_theme"]`，否则 clip 1 跑 v10 会 KeyError（v10 Eat 吃实测踩坑）
8. **v10 自检脚本要支持两种 BGM 持续标记**：`continues throughout the entire clip`（v9 标准）和 `continues throughout this entire clip`（v10 clip 2+ 变体）—— 用 `or` 连接两个关键词检查
9. **v10 决策树信号**："领读型"/"整体氛围一致"/"重复句式绘本"—— 这些信号触发 v10（v9 是默认）
10. **测试方法**：v10 跨 clip 调性是否一致**只能人耳听**（dB 不能量化），跑完后必须连续听两个 clip 验证 BGM 风格

---

## 12. v10 后续可探索方向

- **v11 思路**：如果 v10 prompt 文字约束力不够（Seedance 不遵循 same ... from the previous clip），可以尝试加 `consistency: use the exact same BGM theme across all clips of this picture book` 之类的元指令，看 Seedance 是否识别为"整本绘本"约束
- **整本绘本合并**：用 ffmpeg 拼接 v10 跑出的所有 clip 测听感（v10 主 SKILL.md §v10 已铺垫"整本绘本同主题"）
- **跨绘本模板化**：把 v10 跑通的 "ukulele pizzicato" 主题词作为领读型绘本默认 BGM 主题，新建绘本时直接复用（避免每次重新选主题）

---

## 13. v10 实测问题（2026-06-03 Eat 吃绘本 4 clip 跑通后 · 用户反馈）

> 来源：2026-06-03 v10 4 clip 跑完（clip1-v9 + clip2-v10 + clip3-v10 + clip4-v10）后用户实测反馈。v10 路线（跨 clip 同主题 BGM）**目标达成**，但**暴露出 3 个新问题**——这些问题是 v11 设计的起点。

### 13.1 问题清单（3 个）

| # | 问题 | 状态 | 根因 |
|---|------|------|------|
| 1 | **BGM 调性统一** | ✅ 通过 | 4 clip 同 ukulele pizzicato 主题（v10 目标达成） |
| 2 | **BGM 收势位置错误** | ❌ 待修复 | 每 clip 都写"quiet warm chime settles"收势，**中间 clip 末尾不该收**——只有最后 1 clip 才用收势 |
| 3 | **画面缺动感** | ❌ 待分析 | 比 v7/v8/v9 缺动感——根因待查（可能是 v10 范式副作用 / prompt 写法问题 / `continues throughout the entire clip` 关键词副作用） |

### 13.2 问题 2 根因 + 修复（BGM 收势）

**根因**（v9 范式继承下来的 bug）：
- v9/v10 模板 `build_v10_prompt()` 给每个 clip 都生成 `[t3] quiet warm chime settles` 收势词
- v9 范式下每 clip 独立视频，末尾收势合理
- **v10 范式下 4 clip 拼成整本绘本时，clip 2/3 末尾的"chime settles"会让 BGM 提前 1s 衰减** → 跨 clip 衔接出现"假结束感"

**v11 修复方向**（两种）：

**A 简单方案**（推荐先试）：
- `clips-prompt.json` 加 `is_final_clip: bool` 字段
- `build_v11_prompt()`：最后一个 clip 用 `final_sfx`（含 chime settles），其他 clip 段 5 末尾改成 `BGM continues softly into the next moment` 不收势

**B 彻底方案**：
- 全部去掉 `shot_3_sfx` 的"settles/chime"收势词
- 改用 `[t3] BGM continues softly into the next moment`（中间 clip 软延续）
- 最后 1 个 clip 才用 `gentle final chord settles`

### 13.3 问题 3 根因 + 修复（画面缺动感）

**可能根因**（按优先级）：
1. **prompt 段 2/3 稳态描述占比过高**——`holds the X pose for the rest of this shot` 这种稳态词**降低了动作变化**
2. **v10 范式副作用**——同主题 BGM 持续铺底 + 稳定画面 + AI 倾向"安全"输出 → 整体平淡
3. **`continues throughout the entire clip` 关键词副作用**——可能让 AI 把整个 clip 拍成"持续 1 个动作"
4. **`final frame ... holds to the last frame` 收势太绝对**——强制画面冻结

**v11 修复方向**（4 种独立可试）：

| 方向 | 改动 | 风险 |
|------|------|------|
| **A. 加微动作** | 段 2/3 在稳态描述前加 1-2 个微动作关键词（`eyes widen with excitement`, `gently sways side to side`） | 低 |
| **B. 软化 final frame** | `holds to the last frame` 改成 `the scene softly continues` | 中（v7/v8 验证过冻结词必要） |
| **C. 改 hold pose 措辞** | `holds the X pose` 改成 `slight natural movement` | 低 |
| **D. 加动态运镜** | 每段加 `the camera slowly drifts, gentle zoom`（v7 范式用过） | 中（v9/v10 没用过运镜） |

**v11 路线图**（建议）：
- **v11-α**：先修 BGM 收势（问题 2），10 分钟出结果
- **v11-β**：再试 A+C 加微动作（问题 3），对比 v10 看是否改善
- **v11-γ**（可选）：camera drift 运镜

**两个问题独立可分开调**——v11-α 和 v11-β 不必同时上。

### 13.4 v10 范式边界（什么时候不用 v10）

经过 Eat 吃 4 clip 实测，v10 适用边界更清晰：

- **适合 v10**：领读型绘本（I eat X / Pete the cat / Dear Zoo / Brown Bear 等重复句式 + 整体氛围优先）
- **不适合 v10**：
  - 单一 clip 内多情绪（用 v8）
  - 静默治愈氛围（用 v7）
  - 8-10s 静态画面要靠 prompt 写出动感（v11 修问题 3 后可解）

### 13.5 用户原话（v10 实测反馈 · 2026-06-03）

> "总结一下本轮 V10 的情况哈：
> 1. BGM 调性：本次 BGM 的调性是符合要求的，每一个 clip 生成的调性是有统一的。
> 2. BGM 收势：BGM 的完结收势，实际上是应该在整个视频最后一段 clip 使用收视，其他的场景中间的 clip 衔接并不需要使用 BGM 收视，这是需要优化的一个点。
> 3. 画面问题：画面缺少了动感，缺少了动态，和 V7、V8V9 相比画面缺少了动感。
> 所以需要你记录这些问题，并思考接下来我们如何进行调试"

—— **3 个问题**已沉淀到本节。**v11 方向**在 §13.2 和 §13.3。
