---
name: v7-prompt-template
description: 绘本 v7 范式 prompt 模板（分镜时序+精准动画+Storyboard Audio Description+音频禁令）。从 SKILL.md Phase 8 必读 + references/分镜时序-prompt范式-v7.md 提取。来源：2026-06-02 Cactus 仙人掌绘本 8 图分 4 Clip 实测沉淀。
triggers:
  - v7 模板
  - 绘本 v7 prompt
  - 8 段固定结构
  - 分镜时序 prompt
  - Storyboard Audio Description
---

# v7 范式 Prompt 模板 · 8 段固定结构

> **使用场景**：领读型绘本（弱情节、靠画面+旁白推）+ TTS 后期卡点。
> **2-N 图=1 Clip 合并**：本范式原生支持，配合 `--image <前图> --last-frame <后图>` 使用。
> **必跑自检**：见 [§5](#5-自检清单)。

---

## 1. 模板

```python
from dataclasses import dataclass


@dataclass
class ShotV7:
    """单 shot 数据（v7 范式）"""
    image_num: int              # @ImageN 编号（1/2/3...）
    t_start: float              # 时间窗起点（秒）
    t_end: float                # 时间窗终点（秒）
    shot_name: str              # shot 定位词（opening/second/third/fourth...）
    action_verb: str            # 动作描述（in this shot [动作]）
    state_hold: str             # 动作完成后稳态（then [状态] hold steady for the rest of this shot）


@dataclass
class AudioSegmentV7:
    """音频时段数据"""
    t_start: float              # 时段起点（秒）
    t_end: float                # 时段终点（秒）
    description: str            # 音效描述（如 "a single paper-landing tap-tap as the letters settle"）


@dataclass
class ClipV7:
    """完整 Clip 数据（v7 范式）"""
    shots: list                # ShotV7 列表（按时间顺序）
    audio_segments: list        # AudioSegmentV7 列表
    audio_end_chime: str        # 末尾单次 chime 描述（如 "a single brief warm chime"）
    style_sentence: str         # 风格锁定句

    def render_prompt(self) -> str:
        # 段 1：分镜引导
        intro = "This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video"
        # 段 2-N：shot 视觉分镜
        shot_lines = []
        for shot in self.shots:
            shot_lines.append(
                f"from {shot.t_start:.1f}s to {shot.t_end:.1f}s @Image{shot.image_num} is the {shot.shot_name} shot, "
                f"in this shot {shot.action_verb}, {shot.state_hold}"
            )
        # 段 N+1：收势词
        final = "final frame: the camera locks completely, paper textures crisp and vivid, the scene holds its final pose"
        # 段 N+2：音频描述（分时段）
        audio_parts = []
        for seg in self.audio_segments:
            audio_parts.append(f"{seg.t_start:.1f}s to {seg.t_end:.1f}s {seg.description}")
        audio = "Storyboard Audio Description: " + ", ".join(audio_parts) + f", {self.audio_end_chime} at the very end"
        # 段 N+3：音频禁令
        ban = "No background music, no human voice, no narration, no singing"
        # 段 N+4：风格锁定 + 句号
        style = f"{self.style_sentence}."

        segments = [intro] + shot_lines + [final, audio, ban, style]
        return ";\n".join(segments) + "\n"
```

**8 段固定结构**（分号 7 个 + 句号 1 个在风格段尾）：
1. 分镜引导（`This is a storyboard reference image sequence; render ...`）
2-N. shot 视觉分镜（`from X.Xs to Y.Ys @ImageN is the ... shot, in this shot [动作], [稳态]`）
N+1. 收势词（`final frame: the camera locks completely, ...`）
N+2. 音频描述（`Storyboard Audio Description: X.Xs to Y.Ys [音效1]...`）
N+3. 音频禁令（`No background music, no human voice, no narration, no singing`）
N+4. 风格锁定（`Children's picture book collage illustration style, ...`）

---

## 2. 字段填充示例（Cactus Clip 1 v7 · 真实跑通）

```python
clip1 = ClipV7(
    shots=[
        ShotV7(
            image_num=1,
            t_start=0.0, t_end=1.2,
            shot_name="opening",
            action_verb="the colorful paper-collaged letters 'CACTUS' bounce into the frame from the edges and land in the center, settling into place one by one to spell CACTUS",
            state_hold="then they hold steady for the rest of this shot"
        ),
        ShotV7(
            image_num=2,
            t_start=1.2, t_end=8.0,
            shot_name="second",
            action_verb="a green saguaro cactus slowly grows up from the yellow desert sand with paper layers unfolding",
            state_hold="then it stands tall and sways gently in a warm breeze for the rest of this shot"
        ),
    ],
    audio_segments=[
        AudioSegmentV7(
            t_start=0.0, t_end=1.2,
            description="a single paper-landing tap-tap as the CACTUS letters settle then ambient silence"
        ),
        AudioSegmentV7(
            t_start=1.2, t_end=1.2,
            description="a quick soft whoosh as the cactus grows up"
        ),
        AudioSegmentV7(
            t_start=1.2, t_end=8.0,
            description="minimal desert ambient silence"
        ),
    ],
    audio_end_chime="a single brief warm chime",
    style_sentence="Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel"
)

print(clip1.render_prompt())
# 输出见 references/分镜时序-prompt范式-v7.md §"完整 v7 真实示例（Cactus Clip 1）"
```

---

## 3. seedance.py 调用

```bash
python3 seedance.py create \
  --image <前图> \
  --last-frame <后图> \
  --prompt "$(clip1.render_prompt())" \
  --duration 8 \
  --ratio 16:9 \
  --generate-audio true \
  --wait \
  --download ./clip1.mp4
```

**关键参数**：
- `--image` / `--last-frame` 锁首尾帧（v7 范式用前图 + 后图）
- `--generate-audio true`（v7 范式靠 prompt 里的音频禁令段精准控制，不用 false）
- `--duration` 整数（4-15s）

---

## 4. 批量生成 SOP

```python
clips = [clip1, clip2, clip3, clip4]
for i, clip in enumerate(clips, 1):
    # 1) 拼 prompt
    prompt = clip.render_prompt()
    # 2) 跑自检（见 §5）
    assert check_v7_self_test(prompt), f"clip{i} 自检失败"
    # 3) 调 seedance.py（建议后台并行跑）
    # 4) 等用户单测门确认后再批量
```

**单测门 SOP**（强制）：
- 先跑 clip1 → vision 自评 + 发飞书让人听音效
- 等用户"OK 可以继续" → 跑 clip2-4
- 跳过单测门 = 4 个 clip 全跑完才发现 prompt 写错

---

## 5. 自检清单

跑 `clip.render_prompt()` 后必跑 11 项自检：

```python
def check_v7_self_test(prompt: str) -> bool:
    sentences = [s.strip() for s in prompt.split(';') if s.strip()]

    # 1. 段数 = 8（4 段基础 + N shot 段，2 图 = 8 段）
    assert len(sentences) == 8, f"段数={len(sentences)} != 8"

    # 2. 分号数 = 7
    assert prompt.count(';') == 7, f"分号数={prompt.count(';')} != 7"

    # 3. 句号数 ≤ 9（数字缩写如 1.2s/8.0s 不计入）
    import re
    period_count = len(re.findall(r'(?<!\d)\.(?!\d)', prompt))
    assert period_count <= 9, f"句号数={period_count} > 9"

    # 4. 段 4 含 final frame（倒数第 4 段，对应音频段之前）
    final_idx = next(i for i, s in enumerate(sentences) if 'final frame' in s)
    assert final_idx == 4, f"final frame 在段{final_idx+1} != 段5（应在第5段）"

    # 5. 段 5 以 Storyboard Audio Description 开头
    audio_idx = next(i for i, s in enumerate(sentences) if 'Storyboard Audio Description' in s)
    assert audio_idx == 5, f"音频段在段{audio_idx+1} != 段6（应在第6段）"

    # 6. 段 6 以 No background music 开头
    ban_idx = next(i for i, s in enumerate(sentences) if 'No background music' in s)
    assert ban_idx == 6, f"禁令段在段{ban_idx+1} != 段7（应在第7段）"

    # 7. 段 7 以 Children's picture book 开头
    style_idx = next(i for i, s in enumerate(sentences) if "Children's picture book" in s)
    assert style_idx == 7, f"风格段在段{style_idx+1} != 段8（应在第8段）"

    # 8. 段 7 末尾有 1 个句号收尾
    assert sentences[-1].endswith('.'), "风格段末尾缺句号"

    # 9. 视觉段（段 1-4）无否定句
    visual_segments = sentences[:4]
    for s in visual_segments:
        assert ' no ' not in s.lower(), f"视觉段含否定句：{s[:50]}"

    # 10. 无独立 [Sound effect: ...] 块
    assert '[Sound effect:' not in prompt, "含独立 [Sound effect: ...] 块"

    # 11. 收势词在最后一句画面描述（不是音频/禁令/风格段）
    assert 'final frame' in sentences[3], "收势词不在最后一句画面描述"

    return True
```

---

## 6. 关联文档

- `picturebook-video/SKILL.md` Phase 8 必读 · 绘本 prompt 三铁律 + 范式选择决策树
- `picturebook-video/references/分镜时序-prompt范式-v7.md` · 完整 v7 范式文档
- `picturebook-video/references/绘本音效-prompt写法.md` §7 · Storyboard Audio Description 模式
- `picturebook-video/references/leading-reading-4clip-pattern.md` · 4-Clip 切分 + 时长公式
