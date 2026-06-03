"""
Eat 吃绘本视频 - v9 范式 4 个 Clip 提示词生成（v9 模板 + 11 项自检）
=============================================================
来源：2026-06-03 Eat 吃绘本 8 图分 4 Clip 实测沉淀
v9 vs v8 核心差异:
- v8: 每 shot 一段 BGM 调性词（shot 边界硬切 BGM）
- v9: 整 Clip 一段 BGM 主题贯穿 + `mood shift` 软描述

使用方法:
  1. 改本文件的 CLIPS 数据（旁白 / image_start / image_end / bgm_theme / shot_*）
  2. python3 build_v9_clips.py
  3. 输出 clips-prompt.json + 11 项自检结果
  4. 提交 seedance.py create 命令

依赖：Python 3.8+（无第三方库）
"""

import json

# ===== 风格锚点（统一所有 Clip） =====
STYLE_ANCHOR = "Children's picture book illustration style, Eric Carle paper-cut collage with watercolor wash, round Q-version teddy bear character, warm color palette of cream, brown, orange, red, paper texture with visible torn edges, handcrafted feel, the word 'EAT' as a large colorful collaged graphic element integrated into the scene, text-as-graphic, 16:9, no subtitles, no text overlays"

# ===== 引导句（Cactus/v7/v8/v9 共用） =====
GUIDE = "This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video"


def build_v9_prompt(clip):
    """v9 范式 prompt 生成器"""
    s1, s2 = clip["shot_1"], clip["shot_2"]
    t1 = s1["time"].split(" to ")[0]
    t2 = s2["time"].split(" to ")[0]
    t3 = clip["shot_3_time"].split(" to ")[0]
    bgm_theme = clip["bgm_theme"]

    # v9 8 段：1 引导 + 2 shot1 + 3 shot2 + 4 收势 + 5 音频(整 Clip BGM + 拟声) + 6 禁令 + 7 风格
    prompt = f"""{GUIDE};
from {s1['time']} {s1['content']};
from {s2['time']} {s2['content']};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame;
Storyboard Audio Description: {bgm_theme}; [{t1}] {s1['sfx']}; [{t2}] {s2['sfx']}; [{t3}] {clip['shot_3_sfx']};
No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;
{STYLE_ANCHOR}."""
    return prompt


def real_check(prompt, duration):
    """v9 11 项自检（含 v9 专属检查项）"""
    issues = []
    # 1. 段 1 引导句
    if "storyboard reference image sequence" not in prompt:
        issues.append("缺段 1 引导句")
    # 2. 分号数 ≥ 6（8 段需要 6 个分号）
    if prompt.count(";") < 6:
        issues.append(f"分号数应≥6（实为 {prompt.count(';')}）")
    # 3. 收势词
    if "holds to the last frame" not in prompt:
        issues.append("缺收势词")
    # 4. no fade no dissolve
    if "no fade, no dissolve" not in prompt:
        issues.append("缺 no fade, no dissolve")
    # 5. No human voice
    if "No human voice" not in prompt:
        issues.append("缺 No human voice")
    # 6. 段 6 不含 No background music
    if "No background music" in prompt:
        issues.append("❌ 残留 No background music（v9 去掉让 BGM 自由生成）")
    # 7. 段 6 不含独立 "no music" 否定词
    if " no music" in prompt.lower() or ", no music" in prompt.lower() or "; no music" in prompt.lower():
        issues.append("❌ 残留音乐否定词（no music 独立词）")
    # 8. 时序窗
    if "0.0s to" not in prompt:
        issues.append("缺时序窗")
    # 9. @Image1 is the opening shot
    if "@Image1 is the opening shot" not in prompt:
        issues.append("shot1 缺少 'is the opening shot'")
    # 10. 风格锚点
    if "Children's picture book" not in prompt:
        issues.append("缺风格锚点")
    # 11. v9 关键：continues throughout the entire clip
    if "continues throughout the entire clip" not in prompt:
        issues.append("❌ 缺 v9 关键：'continues throughout the entire clip'")
    # 12. v9 关键：mood shift 软描述
    if "mood shift" not in prompt.lower():
        issues.append("⚠️ 缺 v9 软调性变化描述：'mood shift'")
    # 13. duration 4-15s
    if not 4 <= duration <= 15:
        issues.append(f"duration {duration}s 超出 4-15s 范围")
    return issues


# ===== 默认 4 个 Clip 数据（Eat 吃绘本） =====
CLIPS = [
    {
        "id": 1,
        "duration": 8,
        "image_start": 1,
        "image_end": 2,
        "narration_1": "I eat. 我吃eat.",
        "narration_2": "I eat apple. 我吃苹果eat.",
        "bgm_theme": "playful cheerful warm ukulele pizzicato melody continues throughout the entire clip, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the apple",
        "shot_1": {
            "time": "0.0s to 3.5s",
            "content": "@Image1 is the opening shot, a small round teddy bear sits at a wooden dining table in a warm cozy kitchen with arms raised in a happy welcoming gesture, surrounded by a colorful spread of fruits and bread on the table, the bear's mouth is open with a joyful expression, in this shot the bear holds the welcoming arms-up pose with warm kitchen light glowing, then the bear holds the pose for the rest of this shot",
            "sfx": "soft excited bubble as the small bear greets the food, gentle tap as a strawberry lands on the plate",
        },
        "shot_2": {
            "time": "3.5s to 7.0s",
            "content": "@Image2 is the second shot, the small bear holds a red apple in both paws with a delighted expression, the kitchen background stays warm and cozy, the camera slowly pushes in toward the apple, in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose for the rest of this shot",
            "sfx": "soft plop as the apple is lifted, gentle whoosh as the camera pushes in",
        },
        "shot_3_time": "7.0s to 8.0s",
        "shot_3_sfx": "quiet warm chime settles",
    },
    {
        "id": 2,
        "duration": 9,
        "image_start": 3,
        "image_end": 4,
        "narration_1": "I eat banana. 我吃香蕉eat.",
        "narration_2": "I eat carrot. 我吃胡萝卜eat.",
        "bgm_theme": "bouncy happy xylophone and pizzicato strings melody continues throughout the entire clip, with the rhythm gently brightening during the second half as the small bear discovers a fresh orange carrot",
        "shot_1": {
            "time": "0.0s to 4.0s",
            "content": "@Image1 is the opening shot, the small bear holds a bright yellow banana in both paws with an excited happy face, sitting in the warm kitchen, in this shot the small bear brings the banana close to its mouth for a bite, then the small bear holds the banana-eating pose for the rest of this shot",
            "sfx": "soft excited bubble, gentle peel rustle as the banana is unpeeled",
        },
        "shot_2": {
            "time": "4.0s to 8.0s",
            "content": "@Image2 is the second shot, the small bear holds a fresh orange carrot in both paws with a curious delighted expression, kitchen background stays warm, in this shot the small bear brings the carrot close to its mouth, then the small bear holds the carrot pose for the rest of this shot",
            "sfx": "soft crunch sound as the carrot is bitten, gentle tap as a piece lands",
        },
        "shot_3_time": "8.0s to 9.0s",
        "shot_3_sfx": "quiet warm chime settles",
    },
    {
        "id": 3,
        "duration": 9,
        "image_start": 5,
        "image_end": 6,
        "narration_1": "I eat fish. 我吃鱼eat.",
        "narration_2": "I eat bread. 我吃面包eat.",
        "bgm_theme": "warm cozy acoustic guitar with soft piano melody continues throughout the entire clip, with a tender lullaby-like softening during the second half as the scene shifts to fresh warm bread",
        "shot_1": {
            "time": "0.0s to 4.0s",
            "content": "@Image1 is the opening shot, the small bear holds a fresh orange fish in both paws with a happy eating expression, warm kitchen background, in this shot the small bear brings the fish close to its mouth, then the small bear holds the fish-eating pose for the rest of this shot",
            "sfx": "soft excited bubble, gentle sizzle as the fish is presented",
        },
        "shot_2": {
            "time": "4.0s to 8.0s",
            "content": "@Image2 is the second shot, the small bear holds a freshly baked brown bread in both paws with a warm delighted expression, kitchen background stays cozy, in this shot the small bear brings the bread close to its mouth, then the small bear holds the bread pose for the rest of this shot",
            "sfx": "soft crust crunch, gentle warm whoosh as the aroma rises",
        },
        "shot_3_time": "8.0s to 9.0s",
        "shot_3_sfx": "quiet warm chime settles",
    },
    {
        "id": 4,
        "duration": 10,
        "image_start": 7,
        "image_end": 8,
        "narration_1": "I eat cake. 我吃蛋糕eat.",
        "narration_2": "I eat all! 我全都爱吃eat all!",
        "bgm_theme": "joyful celebratory warm bells and pizzicato orchestra melody continues throughout the entire clip, building to a hopeful uplifting tone in the final seconds as the small bear celebrates eating everything",
        "shot_1": {
            "time": "0.0s to 4.5s",
            "content": "@Image1 is the opening shot, the small bear holds a pink frosted cake slice in both paws with mouth wide open in joyful anticipation, warm kitchen background, in this shot the small bear brings the cake close to its mouth, then the small bear holds the cake-eating pose for the rest of this shot",
            "sfx": "soft excited bubble, gentle frosting tap as the cake is lifted",
        },
        "shot_2": {
            "time": "4.5s to 9.0s",
            "content": "@Image2 is the second shot, the small bear stands with both arms raised high in a triumphant celebration surrounded by a colorful feast of fruits, vegetables, bread, fish, and cake, the bear's smile is huge and joyful, in this shot the bear opens its arms wider to embrace all the food, then the small bear holds the celebration pose for the rest of this shot",
            "sfx": "soft sparkle as the feast is revealed, gentle warm chime as the celebration begins",
        },
        "shot_3_time": "9.0s to 10.0s",
        "shot_3_sfx": "single quiet warm chime as the final note",
    },
]


def main():
    print("=" * 70)
    print("v9 范式 4 个 Clip 提示词生成（Eat 吃绘本）")
    print("v9 核心：整 Clip 一段 BGM 主题贯穿 + 调性渐变（不按 shot 切 BGM）")
    print("=" * 70)

    prompts = {}
    for c in CLIPS:
        prompts[c["id"]] = build_v9_prompt(c)
        print(f"\n--- Clip {c['id']}（{c['duration']}s, 图 {c['image_start']}+{c['image_end']}）---")
        print(f"旁白: {c['narration_1']}")
        print(f"      {c['narration_2']}")
        print(prompts[c["id"]])
        print()

    print("\n" + "=" * 70)
    print("v9 自检结果（含 v9 专属检查项）")
    print("=" * 70)
    for clip_id, p in prompts.items():
        duration = next(c["duration"] for c in CLIPS if c["id"] == clip_id)
        issues = real_check(p, duration)
        if issues:
            print(f"Clip {clip_id}: ❌ {issues}")
        else:
            print(f"Clip {clip_id}: ✅ 通过（含 v9 专属'continues throughout the entire clip' + 'mood shift'）")

    # 输出 JSON
    output = {
        "project": "Eat 吃",
        "version": "v9-20260603",
        "total_duration": sum(c["duration"] for c in CLIPS),
        "total_clips": len(CLIPS),
        "style_anchor": STYLE_ANCHOR,
        "guide": GUIDE,
        "v9_key": "整 Clip 一段 BGM 主题贯穿 + 调性渐变（continues throughout the entire clip）",
        "clips": [
            {
                "id": c["id"],
                "duration": c["duration"],
                "image_start": c["image_start"],
                "image_end": c["image_end"],
                "narration_1": c["narration_1"],
                "narration_2": c["narration_2"],
                "bgm_theme": c["bgm_theme"],
                "prompt": prompts[c["id"]],
            }
            for c in CLIPS
        ],
    }

    with open("./clips-prompt.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ prompts 已写入 clips-prompt.json")
    print(f"总时长: {output['total_duration']}s, 总 Clip 数: {output['total_clips']}")


if __name__ == "__main__":
    main()
