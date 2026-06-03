#!/usr/bin/env python3
"""
build_v8_clips.py · 绘本 v8 范式 prompt 自动拼接工具

输入：clip 清单（每段：首帧/尾帧/时长/起止画面/BGM 调性词/音效副词）
输出：可以直接喂给 seedance.py create 的 prompt 文本
       + 自动跑 11 项自检清单（不通过打 ERROR 拒绝输出）
       + clips-prompt.json（自动化跑 seedance.py 用）

v8 vs v3 关键差异：
- 段 5 音频描述：每 shot 加 BGM 调性词前缀 + throughout this shot
- 段 6 禁令：删除 No background music（让 Seedance 自由配纯音乐 BGM）
- 段 6 保留：No human voice / no singing / no vocal / no humming / no whistling（人声禁令）

用法：
    # 1) 编辑本文件末尾的 CLIP_LIST 变量（你的绘本数据）
    # 2) python3 scripts/build_v8_clips.py
    # 3) 把输出的 prompt 喂给 seedance.py
    # 4) 用 clips-prompt.json 自动化跑 seedance.py create（v8 默认 --watermark false）

来源：2026-06-03 Ok 好的绘本 8 图分 4 Clip 实测沉淀
参考：references/分镜时序-prompt范式-v8.md
范式：v8 调性匹配型（每 Clip 配相符 BGM）
"""

import json
import sys


# === v8 范式 prompt 模板（8 段固定结构）===

GUIDE = "This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video"

DEFAULT_STYLE = (
    "Children's picture book illustration style, paper-cut collage with watercolor wash, "
    "round Q-version cartoon animals, warm color palette of orange, yellow, brown, "
    "paper texture with visible torn edges, handcrafted feel, bright primary colors, "
    "16:9, no subtitles, no text overlays"
)


def build_v8_prompt(clip) -> str:
    """v8 8 段：1 引导 + 2 shot1 + 3 shot2 + 4 收势 + 5 音频(BGM+拟声) + 6 禁令 + 7 风格"""
    s1, s2 = clip["shot_1"], clip["shot_2"]
    bgm1, bgm2 = clip["bgm_mood_1"], clip["bgm_mood_2"]
    t1 = s1["time"].split(" to ")[0]
    t2 = s2["time"].split(" to ")[0]
    t3 = clip["shot_3_time"].split(" to ")[0]
    prompt = f"""{GUIDE};
from {s1['time']} {s1['content']};
from {s2['time']} {s2['content']};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: {bgm1} throughout this shot, [{t1}] {s1['sfx']}; {bgm2} throughout this shot, [{t2}] {s2['sfx']}; [{t3}] {clip['shot_3_sfx']};
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
{clip['style']}."""
    return prompt


def v8_self_check(prompt: str, duration: int) -> list[str]:
    """
    v8 11 项自检（references/分镜时序-prompt范式-v8.md §7）
    返回 ERROR 列表，空列表 = 通过

    v8 vs v7 第 7 项是反的（v7 必须有 No background music，v8 必须无）
    """
    errors = []

    # #1: 段 1 引导句
    if "storyboard reference image sequence" not in prompt:
        errors.append("#1 缺段 1 引导句（Cactus 范式核心）")

    # #2: shot 时序
    if "from 0.0s to" not in prompt:
        errors.append("#2 缺显式时序窗（from X.Xs to Y.Ys）")

    # #3: 收势词
    if "holds to the last frame" not in prompt:
        errors.append("#3 缺收势词 'holds to the last frame'")

    if "no fade, no dissolve" not in prompt:
        errors.append("#3 缺 'no fade, no dissolve' 收势指令")

    # #4: 段 5 音频描述
    if "Storyboard Audio Description:" not in prompt:
        errors.append("#4 缺 Storyboard Audio Description 段")

    # #5: v8 专属 — 段 5 每 shot 写 throughout this shot
    if "throughout this shot" not in prompt:
        errors.append("#5 缺 'throughout this shot'（v8 BGM 持续标记，必备）")

    # #6: 段 6 禁令（人声）
    if "No human voice" not in prompt:
        errors.append("#6 缺 'No human voice'（人声禁令）")

    # #7: v8 专属 — 段 6 必避 No background music
    if "No background music" in prompt:
        errors.append("#7 ❌ 含 'No background music'（v8 必删，删了 Seedance 才生 BGM）")

    if "No music" in prompt or "no music" in prompt:
        errors.append("#7 ❌ 含 'no music' 否定词（v8 必删）")

    # #8: 风格锚点
    if "Children's picture book" not in prompt:
        errors.append("#8 缺 'Children's picture book' 风格锚点")

    # #9: 视觉段无否定句
    if "Storyboard Audio" in prompt:
        visual_part = prompt.split("Storyboard Audio", 1)[0]
    else:
        visual_part = prompt
    for neg in ["No speech", "No narration", "No BGM", "no narration", "no speech"]:
        if neg in visual_part:
            errors.append(f"#9 视觉段有否定句 '{neg}'（应放段 6 音频段）")

    # #10: 无独立 [Sound effect: ...] 块
    if "[Sound effect:" in prompt or "[Sound:" in prompt:
        errors.append("#10 有独立 [Sound effect: ...] 块（应嵌入视觉句中或音频段内）")

    # #11: 收势词在最后一句画面描述
    last_meaningful = prompt.rstrip(".").rstrip()
    if "final frame:" in last_meaningful:
        after_final = last_meaningful.split("final frame:")[-1]
        if not after_final.rstrip().endswith("holds to the last frame"):
            errors.append("#11 收势词 'holds to the last frame' 不在最后一句画面描述末尾")

    # 时长硬约束
    if not 4 <= duration <= 15:
        errors.append(f"#时长 duration {duration}s 超出 4-15s 硬约束")

    return errors


def render_seedance_v8(clip, project_dir: str, seedance_path: str = None) -> str:
    """
    渲染 v8 范式完整的 seedance.py create 命令
    - v8 默认参数：--watermark false / --generate-audio true / 16:9
    """
    if seedance_path is None:
        seedance_path = "/home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py"
    prompt = build_v8_prompt(clip)
    first = f"{project_dir}/{clip['image_start']}.jpg"
    last = f"{project_dir}/{clip['image_end']}.jpg"
    output = f"{project_dir}/output/{clip['name']}.mp4"
    return f"""HOME=/home/luo {seedance_path} create \\
  --image {first} \\
  --last-frame {last} \\
  --prompt "{prompt}" \\
  --duration {clip['duration']} \\
  --ratio 16:9 \\
  --watermark false \\
  --generate-audio true \\
  --wait \\
  --download {output}"""


# === 用户编辑区：替换成你的绘本数据 ===

# === 示例（Ok 好的绘本 Clip 1，可参考后改）===
CLIP_LIST = [
    {
        "name": "clip1",
        "duration": 8,
        "image_start": 1,
        "image_end": 2,
        "bgm_mood_1": "playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood",
        "bgm_mood_2": "gentle warm acoustic guitar, tender send-off mood with soft piano",
        "shot_1": {
            "time": "0.0s to 3.5s",
            "content": "@Image1 is the opening shot, a small round bear stands center stage on a circular wooden stage with a warm celebratory atmosphere, surrounded by small forest animal audience clapping, paper-collage crafted theater with warm orange-yellow curtain backdrop, in this shot the small bear raises its right paw to give a thumbs-up with warm light bloom expanding, then the bear holds the thumbs-up pose for the rest of this shot",
            "sfx": "gentle paper-landing tap-tap-tap as the thumbs-up pose settles",
        },
        "shot_2": {
            "time": "3.5s to 7.0s",
            "content": "@Image2 is the second shot, a warm cozy doorway scene at sunrise with a tender send-off mood, golden sunlight pouring in from the open wooden door onto a yellow tiled floor, a mama bear on the right waves goodbye with her left paw, a small bear with a blue-yellow backpack stands on the left stepping through the doorway, in this shot the small bear steps forward through the doorway with the thumbs-up pose, then the small bear holds the pose for the rest of this shot",
            "sfx": "soft morning whoosh as the door swings open, gentle whoosh as golden sunlight pours in",
        },
        "shot_3_time": "7.0s to 8.0s",
        "shot_3_sfx": "quiet warm chime settles",
        "style": DEFAULT_STYLE,
    },
    # === 下面继续加 clip2 / clip3 / clip4 ... ===
]


# === 主程序 ===

def main():
    if not CLIP_LIST:
        print("ERROR: CLIP_LIST 为空，请编辑本文件填入你的绘本数据", file=sys.stderr)
        sys.exit(1)

    print(f"=== build_v8_clips.py · 共 {len(CLIP_LIST)} 段 ===\n")
    all_pass = True
    output_prompts = []

    for clip in CLIP_LIST:
        prompt = build_v8_prompt(clip)
        errors = v8_self_check(prompt, clip["duration"])
        status = "✅" if not errors else "❌"
        print(f"{status} {clip['name']} ({clip['duration']}s, 图 {clip['image_start']}+{clip['image_end']})")
        if errors:
            all_pass = False
            for e in errors:
                print(f"   {e}")
        print()
        print(f"--- {clip['name']} prompt ---")
        print(prompt)
        print()
        output_prompts.append({
            "id": clip["name"],
            "duration": clip["duration"],
            "image_start": clip["image_start"],
            "image_end": clip["image_end"],
            "prompt": prompt,
        })

    if not all_pass:
        print("\n❌ v8 11 项自检未通过，请修正后再跑", file=sys.stderr)
        sys.exit(1)

    # 写 JSON 文件（自动化跑 seedance.py 用）
    project_dir = "/home/luo/huiben-projects/你的绘本项目"
    with open("clips-prompt.json", "w", encoding="utf-8") as f:
        json.dump({
            "version": "v8-20260603",
            "total_clips": len(CLIP_LIST),
            "total_duration": sum(c["duration"] for c in CLIP_LIST),
            "clips": output_prompts,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ prompts 已写入 clips-prompt.json")

    # 打印 seedance.py create 命令
    print("\n=== seedance.py create 命令（直接复制）===")
    for clip in CLIP_LIST:
        print(render_seedance_v8(clip, project_dir))
        print()


if __name__ == "__main__":
    main()
