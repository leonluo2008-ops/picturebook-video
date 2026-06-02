#!/usr/bin/env python3
"""
build_clip_prompts.py · 绘本 v7 范式 prompt 自动拼接工具

输入：clip 清单（每段：首帧/尾帧/时长/分镜时序/视觉动作/Storyboard Audio Description/音频禁令）
输出：可以直接喂给 seedance.py create 的 prompt 文本
       + 自动跑 v7 必跑自检 11 项（不通过打 ERROR 拒绝输出）

用法：
    # 1) 编辑本文件末尾的 CLIP_LIST 变量（你的绘本数据）
    # 2) python3 scripts/build_clip_prompts.py
    # 3) 把输出的 prompt 喂给 seedance.py

来源：2026-06-02 Cactus 绘本 v7 范式沉淀（picturebook-video/references/分镜时序-prompt范式-v7.md）
"""

import sys
from dataclasses import dataclass


# === v7 范式 prompt 模板（picturebook-video skill 当前推荐范式）===

PROMPT_TEMPLATE_V7 = """This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from {t1_start:.1f}s to {t1_end:.1f}s @Image{img1} is the {shot1_name} shot, in this shot {action1_verb}, then {state1_hold};
from {t2_start:.1f}s to {t2_end:.1f}s @Image{img2} is the {shot2_name} shot, in this shot {action2_verb}, then {state2_hold};
final frame: the camera locks completely, paper textures crisp and vivid, the scene holds its final pose;
Storyboard Audio Description: {audio_segment_1};
No background music, no human voice, no narration, no singing;
{style}."""


# 风格锁定句（绘本通用，可改）
DEFAULT_STYLE = "Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel"


@dataclass
class ClipV7:
    """v7 范式一个 clip 的输入数据

    8 段固定结构对应 8 个必填字段（动作 + 稳态） + 1 段音频描述
    """
    name: str                          # 例如 "clip1"
    img1: int                          # 第 1 段画面绑定图（@ImageN）
    t1_start: float                    # 第 1 段时间窗起点
    t1_end: float                      # 第 1 段时间窗终点
    shot1_name: str                    # 第 1 段画面定位词（opening / first / ...）
    action1_verb: str                  # 第 1 段动作描述
    state1_hold: str                   # 第 1 段动作完成后稳态（例：then they hold steady for the rest of this shot）
    img2: int                          # 第 2 段画面绑定图
    t2_start: float                    # 第 2 段时间窗起点（= t1_end）
    t2_end: float                      # 第 2 段时间窗终点
    shot2_name: str                    # 第 2 段画面定位词
    action2_verb: str                  # 第 2 段动作描述
    state2_hold: str                   # 第 2 段动作完成后稳态
    audio_segment_1: str               # 整段 Storyboard Audio Description（按时间窗分时描述）
    duration: int                      # 4-15s
    style: str = DEFAULT_STYLE


def build_prompt_v7(clip: ClipV7) -> str:
    """v7 范式：分镜时序 + 精准动作 + 精准音频控制"""
    return PROMPT_TEMPLATE_V7.format(
        t1_start=clip.t1_start,
        t1_end=clip.t1_end,
        img1=clip.img1,
        shot1_name=clip.shot1_name,
        action1_verb=clip.action1_verb,
        state1_hold=clip.state1_hold,
        t2_start=clip.t2_start,
        t2_end=clip.t2_end,
        img2=clip.img2,
        shot2_name=clip.shot2_name,
        action2_verb=clip.action2_verb,
        state2_hold=clip.state2_hold,
        audio_segment_1=clip.audio_segment_1,
        style=clip.style,
    )


def self_check_v7(prompt: str) -> list[str]:
    """
    v7 必跑自检 11 项（picturebook-video/references/分镜时序-prompt范式-v7.md）

    返回 ERROR 列表，空列表 = 通过
    """
    errors = []
    sentences = [s.strip() for s in prompt.split(';') if s.strip()]

    # 1. 段数 = 8
    if len(sentences) != 8:
        errors.append(f"[自检1] 段数={len(sentences)} ≠ 8（v7 范式固定 8 段）")

    # 2. 分号数 = 7
    if prompt.count(';') != 7:
        errors.append(f"[自检2] 分号数={prompt.count(';')} ≠ 7（v7 范式固定 7 个分号）")

    # 3. 句号数 ≤ 9（数字缩写 1.2s/8.0s 不计入）
    import re
    visual_sentences = sentences[0:4]  # 段 1-4 是视觉段
    period_in_visual = sum(s.count('.') for s in visual_sentences)
    if period_in_visual > 4:  # 数字缩写会贡献 ≤ 4 个句号
        errors.append(f"[自检3] 视觉段句号数={period_in_visual} 超出 4（含数字缩写）")

    # 4. 段 4 含 final frame
    if len(sentences) >= 4 and "final frame" not in sentences[3]:
        errors.append(f"[自检4] 段 4 缺少 'final frame' 收势词")

    # 5. 段 5 以 Storyboard Audio Description 开头
    if len(sentences) >= 5 and not sentences[4].startswith("Storyboard Audio Description"):
        errors.append(f"[自检5] 段 5 必须以 'Storyboard Audio Description:' 开头")

    # 6. 段 6 以 No background music 开头
    if len(sentences) >= 6 and not sentences[5].startswith("No background music"):
        errors.append(f"[自检6] 段 6 必须以 'No background music' 开头")

    # 7. 段 7 以 Children's picture book 开头
    if len(sentences) >= 7 and not sentences[6].startswith("Children's picture book"):
        errors.append(f"[自检7] 段 7 必须以 'Children's picture book' 风格锁定句开头")

    # 8. 段 7 末尾有 1 个句号收尾
    if len(sentences) >= 8 and not sentences[7].rstrip().endswith('.'):
        errors.append(f"[自检8] 段 8 末尾缺少句号收尾（应为 '。' 句号）")

    # 9. 视觉段（段 2-4）无否定句
    visual_block = ';'.join(sentences[1:4])
    for forbid in [" no ", "No BGM", "no speech", "no narration"]:
        if forbid.lower() in visual_block.lower():
            errors.append(f"[自检9] 视觉段（段 2-4）含否定句 '{forbid}'（违反三铁律 3）")

    # 10. 整段无独立 [Sound effect: ...] 块
    if "[Sound effect:" in prompt or "[Sound:" in prompt:
        errors.append("[自检10] 包含 [Sound effect: ...] 独立块（应嵌入视觉句中或用 Storyboard Audio Description 段）")

    # 11. 收势词在最后一句画面描述里（不是音频/禁令/风格段）
    if len(sentences) >= 4:
        final_frame_sentence = sentences[3]
        audio_sentence = sentences[4] if len(sentences) >= 5 else ""
        if "final frame" in audio_sentence or "final frame" in (sentences[5] if len(sentences) >= 6 else ""):
            errors.append("[自检11] 'final frame' 出现在音频段或禁令段（应在视觉段末尾）")

    return errors


def render_command_v7(clip: ClipV7, first_frame: str, last_frame: str, output_path: str) -> str:
    """
    渲染完整的 seedance.py create 命令（v7 范式）
    """
    prompt = build_prompt_v7(clip)
    return f"""python3 seedance.py create \\
  --image {first_frame} \\
  --last-frame {last_frame} \\
  --prompt "{prompt}" \\
  --duration {clip.duration} \\
  --ratio 16:9 \\
  --generate-audio true \\
  --wait \\
  --download {output_path}"""


# === 用户编辑区：替换成你的绘本数据 ===

# 范例：Cactus 绘本 Clip 1（按 0.3s/字算 TTS，1.2s 是旁白 1 结束点）
CLIP_LIST = [
    ClipV7(
        name="clip1",
        img1=1,
        t1_start=0.0,
        t1_end=1.2,
        shot1_name="opening",
        action1_verb="the colorful paper-collaged letters 'CACTUS' bounce into the frame from the edges and land in the center, settling into place one by one to spell CACTUS",
        state1_hold="then they hold steady for the rest of this shot",
        img2=2,
        t2_start=1.2,
        t2_end=8.0,
        shot2_name="second",
        action2_verb="a green saguaro cactus slowly grows up from the yellow desert sand with paper layers unfolding",
        state2_hold="then it stands tall and sways gently in a warm breeze for the rest of this shot",
        audio_segment_1="0.0s to 1.2s a single paper-landing tap-tap as the CACTUS letters settle then ambient silence, 1.2s a quick soft whoosh as the cactus grows up, 1.2s to 8.0s minimal desert ambient silence, a single brief warm chime at the very end",
        duration=8,
    ),
    # === 下面继续加 clip2 / clip3 / clip4 ... ===
]


# === 主程序 ===

def main():
    if not CLIP_LIST:
        print("ERROR: CLIP_LIST 为空，请编辑本文件填入你的绘本数据", file=sys.stderr)
        sys.exit(1)

    print(f"=== build_clip_prompts.py · v7 范式 · 共 {len(CLIP_LIST)} 段 ===\n")
    all_pass = True
    for i, clip in enumerate(CLIP_LIST, 1):
        prompt = build_prompt_v7(clip)
        errors = self_check_v7(prompt)
        status = "✅" if not errors else "❌"
        print(f"{status} {clip.name} ({clip.duration}s)")
        if errors:
            all_pass = False
            for e in errors:
                print(f"   {e}")
        print()
        # 打印 prompt（用户复制）
        print(f"--- {clip.name} prompt ---")
        print(prompt)
        print()

    if not all_pass:
        print("\n❌ v7 自检未通过，请修正后再跑", file=sys.stderr)
        sys.exit(1)

    # 打印 seedance.py create 命令
    print("\n=== seedance.py create 命令（直接复制）===")
    for i, clip in enumerate(CLIP_LIST, 1):
        first = f"./{i*2-1}.jpg"  # 默认 1.jpg 2.jpg 3.jpg ... 按图号顺序
        last = f"./{i*2}.jpg"
        output = f"./{clip.name}.mp4"
        print(render_command_v7(clip, first, last, output))
        print()


if __name__ == "__main__":
    main()
