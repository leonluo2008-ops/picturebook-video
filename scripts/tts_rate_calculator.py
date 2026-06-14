#!/usr/bin/env python3
"""
tts_rate_calculator.py · TTS 速率方案校对脚本（绘本视频第 8 个根本性纠错）

用法:
  python3 tts_rate_calculator.py <旁白表.json>

输入: 8 段旁白结构化 JSON + 用户给 TTS 数值
  格式: {
    "user_tts_seconds": 50,
    "segments": [
      {"id": 1, "en_text": "DUCK!", "zh_text": "鸭子 DUCK！", "en_word_count": 1, "gap_count": 0},
      ...
    ]
  }

输出: 多种速率方案 + 8 段 TTS 总和 + 差 vs 用户给 TTS + 判定

退出码:
  0 = 校验通过（差 ≤ 5s）
  1 = 校验失败（差 ≥ 5s · 必查 5 类根因）

来源: 2026-06-13 绘本实战沉淀
参考: references/tts-rate-calibration-workflow.md
"""
import json
import sys
from pathlib import Path


# 5 种速率方案（按 1.0 词/秒自然估为标准）
RATE_SCHEMES = [
    ("1.4/3.5（兜底公式，过快估·已废弃）", 1.4, 3.5, 0.3),
    ("1.2/3.0（中等估）",                   1.2, 3.0, 0.4),
    ("1.0/3.0（自然估·标准·推荐）",        1.0, 3.0, 0.5),
    ("0.9/2.5（慢速自然估）",               0.9, 2.5, 0.5),
    ("0.8/2.5（最慢自然估）",               0.8, 2.5, 0.5),
]

# 5 类常见根因（差 ≥ 5s 时的排查方向）
COMMON_ROOTS = [
    "❌ 漏算家族词组中文（段 7 算 4.29s · 实际 13.67s = 差 3 倍）",
    "❌ 漏算词间停顿（家族词组 4 词 = 6 个 0.5s 停顿 = 3s 漏算）",
    "❌ 漏算中文字数（把'中文'当 0s · 实际 4-12 字 = 1.3-4s）",
    "❌ 用了 1.4 词/秒兜底（过快估 = 漏算中文 + 漏算停顿）",
    "❌ 把 readme 的'非朗读中文'当 0s（readme 写但不读 = 0s · 读 = 必算）",
]


def calc_zh_chars(zh_text: str) -> int:
    """算中文字数（含 duck/UCK 等夹杂的英文部分单独算）"""
    return len([c for c in zh_text if '\u4e00' <= c <= '\u9fff'])


def calc_seg_tts(seg: dict, en_rate: float, zh_rate: float, gap_rate: float) -> float:
    """算单段 TTS: 词数/速率 + 字数/速率 + 词间停顿 × 间隔时长"""
    en_words = seg.get("en_word_count", 0)
    zh_chars = calc_zh_chars(seg.get("zh_text", ""))
    gaps = seg.get("gap_count", 0)
    return en_words / en_rate + zh_chars / zh_rate + gaps * gap_rate


def calc_total_tts(segments: list, en_rate: float, zh_rate: float, gap_rate: float) -> float:
    """算 8 段总 TTS"""
    return sum(calc_seg_tts(s, en_rate, zh_rate, gap_rate) for s in segments)


def judge_diff(diff: float) -> tuple:
    """差值判定"""
    abs_diff = abs(diff)
    if abs_diff <= 3:
        return "✅", "高度正确", 0
    elif abs_diff <= 5:
        return "✅", "可接受（3-5s 容忍范围）", 0
    elif abs_diff < 10:
        return "⚠️", "警告（差过大 · 必跑 Step 3 多种速率对比）", 1
    else:
        return "❌", "严重错误（必查 5 类根因 · 必重算）", 1


def main():
    if len(sys.argv) != 2:
        print("用法: python3 tts_rate_calculator.py <旁白表.json>")
        print("示例: python3 tts_rate_calculator.py 旁白表.json")
        sys.exit(2)

    input_path = Path(sys.argv[1]).expanduser()
    if not input_path.is_file():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(2)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    user_tts = data.get("user_tts_seconds")
    segments = data.get("segments", [])

    if not user_tts or not segments:
        print("❌ 旁白表 JSON 必含 'user_tts_seconds' + 'segments' 字段")
        sys.exit(2)

    print(f"📂 校对文件: {input_path}")
    print(f"📊 旁白段数: {len(segments)} · 用户给 TTS: {user_tts}s")
    print()

    # 显示每段 TTS（用标准速率）
    print("=" * 80)
    print("每段 TTS（标准速率 1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）")
    print("=" * 80)
    print(f"{'段':<4}{'英':<35}{'中':<30}{'词':<4}{'字':<4}{'停顿':<6}{'TTS':<8}")
    print("-" * 80)
    for seg in segments:
        sid = seg.get("id", "?")
        en_text = seg.get("en_text", "")[:33]
        zh_text = seg.get("zh_text", "")[:28]
        en_words = seg.get("en_word_count", 0)
        zh_chars = calc_zh_chars(seg.get("zh_text", ""))
        gaps = seg.get("gap_count", 0)
        tts = calc_seg_tts(seg, 1.0, 3.0, 0.5)
        print(f"{sid:<4}{en_text:<35}{zh_text:<30}{en_words:<4}{zh_chars:<4}{gaps:<6}{tts:<8.2f}")

    # 多种速率方案对比
    print()
    print("=" * 80)
    print("多种速率方案对比")
    print("=" * 80)
    print(f"{'速率方案':<40}{'总 TTS':<12}{'差 vs 用户':<14}{'判定'}")
    print("-" * 80)

    failed = False
    best_match = None
    for label, en_rate, zh_rate, gap_rate in RATE_SCHEMES:
        total = calc_total_tts(segments, en_rate, zh_rate, gap_rate)
        diff = total - user_tts
        status, reason, exit_code = judge_diff(diff)
        print(f"{label:<40}{total:<12.2f}{diff:<+14.2f}{status} {reason}")
        if exit_code == 1 and not failed:
            failed = True
        if best_match is None or abs(diff) < abs(best_match[1] - user_tts):
            best_match = (label, total, diff)

    # 5 类根因提示（失败时）
    if failed:
        print()
        print("=" * 80)
        print("5 类常见根因（差 ≥ 5s 时的排查方向）")
        print("=" * 80)
        for root in COMMON_ROOTS:
            print(f"  {root}")

    # 推荐速率
    print()
    print("=" * 80)
    print(f"推荐: 1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿（标准速率 · 用户原话'自然阅读'）")
    if best_match and best_match[2] != 0:
        print(f"最佳匹配速率: {best_match[0]}（差 {best_match[2]:+.2f}s）")
    print(f"视频总时长: 用户给 TTS {user_tts}s + 5s 冗余 = {user_tts + 5}s")
    print(f"退出码: {1 if failed else 0}")
    print()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
