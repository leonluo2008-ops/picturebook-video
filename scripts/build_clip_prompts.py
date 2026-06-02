#!/usr/bin/env python3
"""
build_clip_prompts.py · 绘本 v3 范式 prompt 自动拼接工具

输入：clip 清单（每段：首帧/尾帧/时长/起止画面/音效副词）
输出：可以直接喂给 seedance.py create 的 prompt 文本
       + 自动跑三铁律自检清单（不通过打 ERROR 拒绝输出）

用法：
    # 1) 编辑本文件末尾的 CLIP_LIST 变量（你的绘本数据）
    # 2) python3 scripts/build_clip_prompts.py
    # 3) 把输出的 prompt 喂给 seedance.py

来源：2026-06-02 Red 绘本 v3 prompt 范式沉淀（picturebook-video/SKILL.md · Phase 8 必读 · 三铁律）
"""

import sys
from dataclasses import dataclass


# === v3 范式 prompt 模板（picturebook-video skill 强制前置章节）===

# 模板 A：单线连续运镜（无时间锚点）—— 适合不在意 TTS 卡点 / 氛围型
PROMPT_TEMPLATE = """@Image1 as the opening frame, {start_scene}, {start_sound};
{camera_motion}, {mid_sound}, transitions seamlessly to @Image2 as the second half, {end_scene};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame, {end_sound}.
{style}."""


# 模板 B：v3 变体（带时间锚点）—— 适合需要 TTS 后期精准匹配画面切换
# 三段时间用 "as the camera X at 1.3 seconds" 等触发式短句分号串接
# 不破坏视觉单段语义（不切碎成独立小节）
PROMPT_TEMPLATE_ANCHORED = """@Image1 as the opening frame, {start_scene}, {start_sound};
{segment_1}, {camera_motion_begins}, {mid_sound};
{segment_2}, transitions seamlessly to @Image2 as the second half, {end_scene};
{segment_3}, final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame, {end_sound}.
{style}."""


# 风格锁定句（绘本通用，可改）
DEFAULT_STYLE = "Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel"


@dataclass
class Clip:
    """一个 clip 的输入数据（替换成你自己的绘本数据）"""
    name: str              # 例如 "clip1" "clip2"
    start_scene: str       # 起始画面描述（首帧 @Image1）
    start_sound: str       # 起始音效副词（嵌入起始画面句）
    camera_motion: str     # 镜头运镜（贯穿整段）
    mid_sound: str         # 中段音效副词（嵌入运镜句）
    end_scene: str         # 结束画面描述（尾帧 @Image2）
    end_sound: str         # 收尾音效副词（嵌入收势句）
    duration: int          # 4-15s
    style: str = DEFAULT_STYLE


@dataclass
class ClipAnchored:
    """模板 B：v3 变体（带时间锚点）的输入数据

    三段时间锚点（segment_1/2/3）对应 TTS 旁白切换点
    适合需要 TTS 后期精准匹配画面切换的场景
    """
    name: str
    start_scene: str       # 起始画面描述（首帧 @Image1）
    start_sound: str       # 起始音效副词
    segment_1: str         # 第 1 段时间动作（0 → 切换点 1）含"as the camera X at 1.3s starts"
    camera_motion_begins: str  # 镜头运镜（贯穿整段，跟 segment_1 配对）
    mid_sound: str         # 中段音效副词
    segment_2: str         # 第 2 段时间动作（切换点 1 → 切换点 2）
    end_scene: str         # 结束画面描述（尾帧 @Image2）
    segment_3: str         # 第 3 段时间动作（切换点 2 → 收势）
    end_sound: str         # 收尾音效副词
    duration: int          # 4-15s
    style: str = DEFAULT_STYLE


def build_prompt(clip: Clip) -> str:
    """模板 A：单线连续运镜"""
    return PROMPT_TEMPLATE.format(
        start_scene=clip.start_scene,
        start_sound=clip.start_sound,
        camera_motion=clip.camera_motion,
        mid_sound=clip.mid_sound,
        end_scene=clip.end_scene,
        end_sound=clip.end_sound,
        style=clip.style,
    )


def build_prompt_anchored(clip: 'ClipAnchored') -> str:
    """模板 B：v3 变体（带时间锚点）—— TTS 后期精准匹配用"""
    return PROMPT_TEMPLATE_ANCHORED.format(
        start_scene=clip.start_scene,
        start_sound=clip.start_sound,
        segment_1=clip.segment_1,
        camera_motion_begins=clip.camera_motion_begins,
        mid_sound=clip.mid_sound,
        segment_2=clip.segment_2,
        end_scene=clip.end_scene,
        segment_3=clip.segment_3,
        end_sound=clip.end_sound,
        style=clip.style,
    )


def self_check(prompt: str) -> list[str]:
    """
    三铁律自检（picturebook-video/SKILL.md 强制章节）
    返回 ERROR 列表，空列表 = 通过

    v3 范式允许的句号分布：
    - 0 个句号在视觉段中间（"RED" 这种缩写不算——但保险起见我们也允许 ≤ 1 个）
    - 1 个句号在收势句末尾（紧跟 end_sound 后）
    - 1 个句号在风格段末尾（整段结束）
    共 ≤ 2 个
    """
    errors = []

    # 铁律 1: 视觉段中间不出现句号
    # 找 "final frame:" 之前的内容（视觉段），数句号
    if "final frame:" in prompt:
        visual_part = prompt.split("final frame:", 1)[0]
        period_in_visual = visual_part.count(".")
        if period_in_visual > 0:
            errors.append(
                f"[铁律1] 视觉段（final frame: 之前）出现句号 {period_in_visual} 次（应为 0，"
                f"应全部用分号/逗号连接）"
            )

    # 铁律 1 续: 总句号 ≤ 2（收势句末尾 + 风格段末尾）
    total_period = prompt.count(".")
    if total_period > 2:
        errors.append(
            f"[铁律1] 整段句号数={total_period} > 2（应在收势句末尾 + 风格段末尾）"
        )

    # 铁律 2: 收势词在最后一句
    closing_keywords = ["final frame:", "camera locks", "holds to the last frame"]
    last_sentence = prompt.rsplit(".", 1)[0]  # 最后一个句号前的部分
    for kw in closing_keywords:
        if kw not in last_sentence:
            errors.append(f"[铁律2] 收势词「{kw}」不在最后一句画面描述里")

    # 铁律 2 续: 收势词后不追加 [Sound effect: ...] 独立块
    if "final frame:" in prompt:
        after_final = prompt.split("final frame:", 1)[1]
        if "[Sound effect:" in after_final or "[Sound:" in after_final:
            errors.append("[铁律2] 收势词后追加了 [Sound effect: ...] 独立块")

    # 铁律 3: 没有否定性指令
    forbidden = ["No speech", "no narration", "no background music", "no BGM"]
    for f in forbidden:
        if f.lower() in prompt.lower():
            errors.append(f"[铁律3] 包含否定性指令「{f}」（应删除，正向描述已够）")

    # 三铁律通用: 没有 [Sound effect: ...] 独立块
    if "[Sound effect:" in prompt:
        errors.append("[三铁律] 包含 [Sound effect: ...] 独立块（应嵌入视觉句中）")

    return errors


def render_command(clip: Clip, first_frame: str, last_frame: str, output_path: str) -> str:
    """
    渲染完整的 seedance.py create 命令（模板 A：单线连续）
    """
    prompt = build_prompt(clip)
    return _render_seedance(prompt, first_frame, last_frame, clip.duration, output_path)


def render_command_anchored(clip: ClipAnchored, first_frame: str, last_frame: str, output_path: str) -> str:
    """
    渲染完整的 seedance.py create 命令（模板 B：带时间锚点）
    """
    prompt = build_prompt_anchored(clip)
    return _render_seedance(prompt, first_frame, last_frame, clip.duration, output_path)


def _render_seedance(prompt: str, first_frame: str, last_frame: str, duration: int, output_path: str) -> str:
    """实际渲染 seedance.py 命令（共享给两个模板）"""
    return f"""python3 seedance.py create \\
  --image {first_frame} \\
  --last-frame {last_frame} \\
  --prompt "{prompt}" \\
  --duration {duration} \\
  --ratio 16:9 \\
  --generate-audio true \\
  --wait \\
  --download {output_path}"""


# === 用户编辑区：替换成你的绘本数据 ===

CLIP_LIST = [
    # === 模板示例（Red 绘本 Clip 1，可参考后改）===
    Clip(
        name="clip1",
        start_scene="the bold collaged letters 'RED' in red, blue and yellow paper stand on a yellow paper strip, a small white rabbit looks up at them, soft white background",
        start_sound="gentle paper-landing tap-tap-tap as the three letters settle into place",
        camera_motion="the camera slowly pushes in with a warm light bloom sweeping across the scene, paper textures become more vivid",
        mid_sound="soft plop as the apple gently appears",
        end_scene="a red paper-collaged apple with green stem and brown leaf sits in the center, handcrafted paper-cut style throughout",
        end_sound="quiet warm chime settles",
        duration=8,
    ),
    # === 下面继续加 clip2 / clip3 / clip4 ... ===
]


# === 主程序 ===

def main():
    if not CLIP_LIST:
        print("ERROR: CLIP_LIST 为空，请编辑本文件填入你的绘本数据", file=sys.stderr)
        sys.exit(1)

    print(f"=== build_clip_prompts.py · 共 {len(CLIP_LIST)} 段 ===\n")
    all_pass = True
    for i, clip in enumerate(CLIP_LIST, 1):
        prompt = build_prompt(clip)
        errors = self_check(prompt)
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
        print("\n❌ 三铁律自检未通过，请修正后再跑", file=sys.stderr)
        sys.exit(1)

    # 打印 seedance.py create 命令
    print("\n=== seedance.py create 命令（直接复制）===")
    for i, clip in enumerate(CLIP_LIST, 1):
        first = f"./{i*2-1}.jpg"  # 默认 1.jpg 2.jpg 3.jpg ... 按图号顺序
        last = f"./{i*2}.jpg"
        output = f"./{clip.name}.mp4"
        print(render_command(clip, first, last, output))
        print()


if __name__ == "__main__":
    main()
