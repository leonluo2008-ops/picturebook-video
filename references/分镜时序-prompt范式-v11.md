---
name: 分镜时序-prompt范式-v11
description: v10 跑通后实测出 3 个问题（BGM 收势位置 / 画面缺动感 / v10 范式边界），其中 BGM 收势问题已被连跑多 clip 隐式解决。v11-α 解决剩下 1 个：画面缺动感。**最小改动方案**：段 2/3 在"holds the X pose"前注入微动作关键词 `with a warm smile and subtle gentle breathing`，让 Seedance 知道主体应该"活"起来。v10 vs v11 关键差异：v11 段 2/3 prompt 多一个微动作短语，v10 同调性 BGM 完整保留。来源：2026-06-03 Eat 吃绘本 clip 2 v11-α 单测。
triggers:
  - 分镜时序 v11
  - 画面缺动感
  - 微动作
  - with a warm smile
  - subtle gentle breathing
  - v10 范式副作用
  - v11-α
---

# 分镜时序-prompt 范式 v11-α · 段 2/3 加微动作版

> **v7 / v8 / v9 / v10 / v11-α 五范式并存**（按绘本调性选）：
> - **v7** 静默氛围型（Cactus）—— 无 BGM
> - **v8** 调性匹配型（Red/Ok 好的）—— 按 shot 切 BGM（**已知有 clip 内部断层**）
> - **v9** 整 Clip 一致型（Eat 吃默认）—— 整 Clip 一段 BGM + 调性渐变
> - **v10** 跨 Clip 同主题型（Eat 吃领读型）—— clip 2+ 段 5 继承前 clip 主题
> - **v11-α** 画面动感增强型（Eat 吃领读型 + 画面缺动感修复）—— v10 + 段 2/3 加微动作

---

## 1. v11-α 出现的根因

**v10 实测 3 个问题**（2026-06-03 Eat 吃 4 clip 跑完用户反馈）：

1. **BGM 调性** ✅：4 clip 同 ukulele pizzicato 主题（v10 目标达成）
2. **BGM 收势** ✅：已被"连跑多 clip = 自动不收势"隐式解决（v10 BGM 收势机制实测沉淀）
3. **画面缺动感** ❌：**唯一待修复**——比 v7/v8/v9 缺动感

**用户原话**：
> "画面缺少了动感，缺少了动态，和 V7、V8、V9 相比画面缺少了动感。"

---

## 2. v11-α 最小改动方案

**改动点**：段 2/3 在"holds the X pose"前注入 1-2 个微动作关键词。

```diff
- in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose for the rest of this shot
+ in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose with a warm smile and subtle gentle breathing for the rest of this shot
```

**保持不动**：
- ✅ 段 1 引导句（v7+ 关键）
- ✅ 段 5 BGM 描述（v10 同调性主题词 `same ... from the previous clip continues`）
- ✅ 段 6 禁令（禁人声）
- ✅ 段 7 风格锚点
- ✅ `final frame ... holds to the last frame`（v7/v8/v9 验证过必要）

**注入常量**：
```python
V11_MICRO_MOTION = " with a warm smile and subtle gentle breathing"
```

**regex 注入规则**（`build_v11_prompt` 调用）：
```python
import re
pattern = r'(holds the [\w\s-]+ pose)( with warm kitchen light glowing)?( for the rest of this shot)?'
def repl(m):
    base = m.group(1)
    light = m.group(2) or ''
    rest = m.group(3) or ''
    return f"{base}{light}{V11_MICRO_MOTION}{rest}"
content_with_motion = re.sub(pattern, repl, content)
```

**关键 regex 细节**：
- `[\w\s-]+` 必须含 `-`（如 `banana-eating pose` 的 `banana-eating`）
- 第二组 `( with warm kitchen light glowing)?` 是 v9 模板里 shot 1/clip 1 特有的中间短语
- 第三组 `( for the rest of this shot)?` 是稳态标记
- 注入位置在 `pose` 后 + 中间短语后 + 稳态前

**v11-α 不动收势词**（`shot_3_sfx` 保留 `quiet warm chime settles`）—— 因为 v11-α 走 v10 同调性 BGM 路线，**连跑多 clip 时 Seedance 自动不收势**（v10 实测沉淀的隐式规则）。

---

## 3. v11-α 完整 prompt 范式

v11-α 在 v10 8 段结构基础上，**只改 1 个地方**：段 2/3 段末尾注入微动作短语。

### 3.1 段 1（引导句）

v10 不变：
```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
```

### 3.2 段 2/3（视觉段，v11 关键改动）

**v10 写法**（v9 模板原版）：
```
from 0.0s to 4.0s @Image1 is the opening shot, ..., in this shot the small bear brings the banana close to its mouth for a bite, then the small bear holds the banana-eating pose for the rest of this shot;
```

**v11-α 写法**（注入微动作）：
```
from 0.0s to 4.0s @Image1 is the opening shot, ..., in this shot the small bear brings the banana close to its mouth for a bite, then the small bear holds the banana-eating pose with a warm smile and subtle gentle breathing for the rest of this shot;
```

**段 2/3 注入位置**（4 段都必须）：

| 段 | 原句尾 | 注入后句尾 |
|----|--------|-----------|
| shot 1 段 | `holds the banana-eating pose for the rest of this shot` | `holds the banana-eating pose with a warm smile and subtle gentle breathing for the rest of this shot` |
| shot 2 段 | `holds the carrot pose for the rest of this shot` | `holds the carrot pose with a warm smile and subtle gentle breathing for the rest of this shot` |
| shot 1 段（含 light） | `holds the welcoming arms-up pose with warm kitchen light glowing, then the bear holds the pose for the rest of this shot` | `holds the welcoming arms-up pose with warm kitchen light glowing with a warm smile and subtle gentle breathing, then the bear holds the pose for the rest of this shot` |
| shot 2 段（节庆） | `holds the celebration pose for the rest of this shot` | `holds the celebration pose with a warm smile and subtle gentle breathing for the rest of this shot` |

### 3.3 段 4（收势）

v10 不变：
```
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
```

### 3.4 段 5（BGM · v10 同调性）

v10 不变（clip 2+ 段 5 用 v10_bgm）：
```
Storyboard Audio Description: same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, gently evolving with soft pizzicato strings and xylophone accents, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the banana and carrot; [0.0s] soft excited bubble, gentle peel rustle as the banana is unpeeled; [4.0s] soft crunch sound as the carrot is bitten, gentle tap as a piece lands; [8.0s] quiet warm chime settles;
```

### 3.5 段 6（禁令）+ 段 7（风格）+ 段 8（句号）

v10 完全不变。

---

## 4. v11-α 自动化实现（`build_v11_prompt`）

在 `build_clips.py`（绘本项目目录）加 v11 范式函数 + CLI 切换：

```python
# v11-α 微动作注入规则（最小改动）
V11_MICRO_MOTION = " with a warm smile and subtle gentle breathing"


def inject_micro_motion(content):
    """在 'holds the X pose' 前注入微动作关键词"""
    import re
    # X 可含 - 字符如 banana-eating
    pattern = r'(holds the [\w\s-]+ pose)( with warm kitchen light glowing)?( for the rest of this shot)?'
    def repl(m):
        base = m.group(1)
        light = m.group(2) or ''
        rest = m.group(3) or ''
        return f"{base}{light}{V11_MICRO_MOTION}{rest}"
    return re.sub(pattern, repl, content)


def build_v11_prompt(clip):
    """v11-α 范式：v10 BGM 同调性 + 段 2/3 加微动作（最小改动解决画面缺动感）"""
    s1, s2 = clip["shot_1"], clip["shot_2"]
    t1 = s1["time"].split(" to ")[0]
    t2 = s2["time"].split(" to ")[0]
    t3 = clip["shot_3_time"].split(" to ")[0]
    # v11 用 v10 同调性 BGM
    bgm_theme = clip.get("v10_bgm") or clip["bgm_theme"]
    # v11 关键：段 2/3 注入微动作
    s1_content = inject_micro_motion(s1['content'])
    s2_content = inject_micro_motion(s2['content'])
    prompt = f"""{GUIDE};
from {s1['time']} {s1_content};
from {s2['time']} {s2_content};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: {bgm_theme}; [{t1}] {s1['sfx']}; [{t2}] {s2['sfx']}; [{t3}] {clip['shot_3_sfx']};
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
{STYLE_ANCHOR}."""
    return prompt
```

**CLI 入口**（`__main__`）：
```python
if version == "v11":
    build_fn = build_v11_prompt
```

**自检脚本**加 v11 专属检查：
```python
if "with a warm smile" not in prompt and "subtle gentle breathing" not in prompt:
    issues.append("❌ v11 模式：段 2/3 缺微动作关键词（'with a warm smile' / 'subtle gentle breathing'）")
```

**v11 Eat 吃实测调用记录**：
- clip 2: task `cgt-20260603185736-v7jbb`（217.7s, 9s, seed 76124）
- 输出：`/home/luo/huiben-projects/20260603-eat-picbook/output/clip2-v11.mp4` (2.8M, 9s)

---

## 5. v11-α 关键限制（必读）

1. **v11-α 不动 BGM 段**——v10 同调性路线完全保留（v11 是 v10 的"画面动感增强版"，**不是替代版**）
2. **v11-α 不动收势词**——`shot_3_sfx` 保留 `quiet warm chime settles`（v10 实测连跑自动不收势的隐式规则照常生效）
3. **v11-α 不动 `final frame ... holds to the last frame`**——画面冻结是 v7/v8/v9/v10 验证过必要的收势，**不能改**
4. **注入位置必须在 `holds the X pose` 后的稳态短语前**——regex 已经处理，**不要手动改 content 字段**
5. **注入常量可替换**——`with a warm smile and subtle gentle breathing` 是 Eat 吃绘本测试值，**其他绘本可换**（如 "with a curious tilt of the head and bright eyes"、"with gentle whisker twitches"——视主体特征定）

---

## 6. v11-α 必避反模式

- ❌ 把"with a warm smile"放在 "holds the X pose" **前**（v11 regex 注入在 pose 后）→ AI 看不到"主体表情变化"指向
- ❌ 改 `holds to the last frame` 收势（v11-α 不动 final frame 段）→ 画面收势失败
- ❌ v11-α 走 v9 自由 BGM 范式（v11 必须配 v10 同调性 BGM）→ 跨 clip 不一致
- ❌ 注入"complex action"复杂动作（v11-α 微动作要轻量，1-2 个词）→ 反而让 AI 困惑
- ❌ 注入"drastic motion"剧烈动作（v11-α 微动作要"subtle"）→ 与"holds the X pose"稳态矛盾
- ❌ 用 MiniMax 生成 BGM 后期铺（用户禁止）

---

## 7. v11-α 关键产物路径

**v11-α 范式文档**：`references/分镜时序-prompt范式-v11.md`（本文件）
**v11-α 真实示例**：`assets/example-prompts/eat-clips-2-3-v11.txt`
**v11-α 自动化脚本**：在 `build_clips.py`（Eat 吃项目目录）加 `build_v11_prompt()` + `inject_micro_motion()` + CLI `--version v9|v10|v11` 切换
**v11-α 主 SKILL.md 章节**：`§v11-α 范式 · 段 2/3 加微动作版`（v10 章节之后追加）

---

## 8. v11 后续可探索方向（v11-β/γ/δ）

v11-α 解决"画面缺动感"最小改动方案。**如果 v11-α 验证不够，可试 v11-β/γ/δ**（4 种方向 A/B/C/D 的部分子集）：

| 范式 | 方向 | 改动 | 风险 |
|------|------|------|------|
| **v11-α** | 加微动作 | 段 2/3 注入"with a warm smile and subtle gentle breathing" | **低**（已实测 1 clip）|
| **v11-β** | 改 hold pose 措辞 | `holds the X pose` 改成 `slight natural movement` | 低 |
| **v11-γ** | 软化 final frame | `holds to the last frame` 改成 `the scene softly continues` | 中（v7/v8 验证过冻结词必要）|
| **v11-δ** | 加动态运镜 | 每段加 `the camera slowly drifts, gentle zoom`（v7 范式用过）| 中（v9/v10/v11-α 没用过运镜）|

**推荐叠加顺序**（如果 v11-α 不够）：
- v11-α + v11-β 叠加（最稳，2 个低风险方向）
- v11-α + v11-β + v11-δ（叠加运镜，v7 验证过能加）
- v11-γ 不建议叠加（动 final frame 风险高）

---

## 9. v11 关键教训（2026-06-03 v10 → v11 沉淀）

1. **"听用户原话要听场景"是 v11 设计的根本起点**——v10 4 clip 跑完用户说"画面缺动感"，直接给最小改动（v11-α），不脑补到"换 BGM 主题"或"加 camera drift"等相邻概念
2. **v11-α 是 v10 的"画面增强版"不是"替代版"**——v10 同调性 BGM 路线完整保留，仅在段 2/3 加 1 个微动作短语
3. **v10 跑通 ≠ 完美**——v10 4 clip 跑完后用户给的 3 个反馈是 v11 设计的起点（**v11 来自用户实测反馈，不是我脑补**）
4. **regex 注入是干净的实现**——不改 CLIPS 数据（content 字段保持原版），加一个 `inject_micro_motion()` 函数即可切换 v10 → v11
5. **v11-α 注入词可替换**——`with a warm smile and subtle gentle breathing` 是 Eat 吃小熊的微动作，**其他主体特征要换**（如鱼/鸟/车的微动作）
6. **v11-α 实测有效**——clip 2 v11 单测跑通（task `cgt-20260603185736-v7jbb`，9s, seed 76124），**等用户人耳听判断画面动感**——如有效再跑完整 4 clip
7. **v11 跟 v10 一样**——**测试方法只能人耳听**（dB 不能量化画面动感），跑完后必须让用户看效果

## 10. v11-α 实测最终结果（2026-06-03 用户反馈 · 失败）

> **状态**：❌ v11-α **失败**（不是"待验证"——已实测 clip 2 并收到用户反馈）

**用户原话反馈**（2026-06-03 v11-α clip 2 单测后）：
> "几乎没有什么变化。"
> "这个可能是因为本的画面、原始图片和剧情导致的，没有更多的发挥空间。"

**v11-α 失败根因**（用户原话推断 + skill 架构层面根因）：

### 用户层根因（用户原话）

> "**绘本原始图片和剧情的限制**——**没有给 AI 更多动作发挥空间**"

- Eat 吃是 **Eric Carle 静态拼贴风**绘本（手撕纸 + 水彩），原图本身就是"静止"的
- 拼贴风没有"动作轨迹"线索 → Seedance 想"动"也无从"动"起
- 用户的判断：**不是 prompt 写得不好，是原图本身限制**

### skill 架构层根因（园丁 Phase 1.5 分析）

> 园丁视角：**v11-α 改 prompt 是错方向**——根因不在 prompt，在**输入端**（图片本身）

- 绘本视频工作流 = `静态图 → 提示词 → Seedance` 3 步
- **缺 1 个工作流节点**：`静态图 → **多帧增强** → 提示词 → Seedance` 4 步
- 多帧增强 = 用即梦 AI 生图**生成中间动作帧**（如小熊从手臂抬起 → 中间帧 → 手臂完全举起），让 Seedance 在多帧间做插值
- **v11-α 错在只改 prompt**——真正的解法是**改输入**（多帧图）

### v11-α 必避反模式（实测确认）

- ❌ **静态拼贴风绘本**（Eric Carle 类）改 prompt 加微动作无效——根因不在 prompt
- ❌ 改动太小看不出差异（v11-α 注入"with a warm smile"对 AI 影响极轻）
- ❌ 误以为"v10 同调性 BGM 路线"+"加微动作"= 画面动感改善——**这是把 2 个独立问题混在一起**
- ❌ 把 v11-α 标为"待验证"——**v11-α 已实测失败**，下次不要重复跑

### v11 真正方向（不再走 v11-α）

按"v11-α 失败根因"重新排方向：

| 范式 | 方向 | 改动 | 实测状态 |
|------|------|------|---------|
| **v11-α** | 加微动作 | 段 2/3 注入"with a warm smile..." | ❌ 已实测失败（用户反馈） |
| **v11-β** | 改 hold pose 措辞 | `holds the X pose` → `slight natural movement` | 🔜 未测（v11-α 失败后**优先级降**，因为同样是改 prompt）|
| **v11-γ** | 软化 final frame | `holds to the last frame` → `the scene softly continues` | 🔜 未测（**不建议**——v7/v8 验证过冻结词必要）|
| **v11-δ** | **加多帧输入** | 跑前用即梦生成 4 帧中间动作图，作为 `--ref-images` 输入 | 🔜 **P0 必做**——v11-α 失败根因的正确解法 |
| **v11-ε** | 换写实风绘本 | Dear Zoo / Brown Bear 类有真实动物动作空间 | 🔜 可作为 v11-δ 的验证绘本 |

**v11-δ 工作流（推荐 v11 真正路线）**：
```
1. 拿原绘本 8 张图（eat 1-8.jpg）
2. 对每张图用即梦生成"动作中间帧"（如 eat 1-mid1.jpg, 1-mid2.jpg, 1-mid3.jpg）
3. 把"原图 + 中间帧"作为 `--ref-images` 传给 Seedance
4. prompt 引导 AI"在这些帧之间做平滑插值"
```

**v11-α 结论（写进 SKILL.md §v11-α 章节末尾）**：
- v11-α 是 v10 的"画面增强 v1"探索，**实测失败**（用户反馈 + 根因分析）
- 真正的 v11 路线 = **v11-δ（多帧输入）**，不是 v11-α 后续优化
- 未来不要重复跑 v11-α——它已死

### 报告归档

v10 + v11-α 完整测试报告：`/home/luo/huiben-projects/20260603-eat-picbook/TEST-REPORT-v10-v11.md`（4.6KB，含产物清单）
