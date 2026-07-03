#!/usr/bin/env python3
"""
srt_parser.py — v5.0.10 SRT 解析器

功能: 把剪映/通用工具导出的 SRT 文件解析成结构化时间轴 JSON,
      供 Step 3 (srt 优先路径) 和 Step 5 (prompt 时间锚点) 使用。

输入: SRT 文件路径
输出: JSON 写到 stdout + 可选 --out 指定文件

JSON 结构:
{
  "source_file": "...",
  "total_duration_s": 30.266,
  "total_segments": 8,
  "rate_calibration": {
    "chinese_chars": 40,
    "english_words": 8,
    "speech_seconds": 22.5,
    "chinese_rate": 1.78,   # 字/秒 (剔停顿后)
    "english_rate": 0.36,   # 词/秒
    "pause_seconds": 7.766
  },
  "pause_distribution": {
    "lt_0.3s": 0,    # 紧接
    "0.3_to_0.8s": 0, # 呼吸
    "gte_0.8s": 7    # 段间停顿
  },
  "segments": [
    {
      "idx": 1,
      "start": 0.066, "end": 1.800, "duration": 1.734,
      "pause_after": 1.133,
      "text": "生菜Lettuce",
      "pause_type": "段间停顿"  # <0.3 紧接 / 0.3-0.8 呼吸 / >=0.8 段间停顿
    },
    ...
  ]
}

用法:
  python3 scripts/srt_parser.py /path/to/file.srt
  python3 scripts/srt_parser.py /path/to/file.srt --out timeline.json
  python3 scripts/srt_parser.py /path/to/file.srt --pause-threshold 0.8
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SRT_PATTERN = re.compile(
    r"(\d+)\n"
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*"
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\n"
    r"(.+?)(?=\n\n|\Z)",
    re.DOTALL,
)

NON_ALPHA = re.compile(r"[a-zA-Z\s]+")
ALPHA_WORD = re.compile(r"[a-zA-Z]+")


def hmsms_to_s(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def classify_pause(pause_s: float, threshold: float) -> str:
    """段间停顿分类 — 不再假设 >=0.8 是画面切换点 (v5.0.10 修正)"""
    if pause_s < 0.3:
        return "紧接"
    if pause_s < threshold:
        return "呼吸"
    return "段间停顿"


def parse_srt(path: Path, pause_threshold: float = 0.8) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    segments: list[dict[str, Any]] = []
    for m in SRT_PATTERN.finditer(content):
        idx = int(m.group(1))
        start = hmsms_to_s(m.group(2), m.group(3), m.group(4), m.group(5))
        end = hmsms_to_s(m.group(6), m.group(7), m.group(8), m.group(9))
        text = m.group(10).strip().replace("\n", " ")
        segments.append({
            "idx": idx,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "text": text,
        })

    # 段间停顿 (最后一段没有 pause_after)
    pauses: list[float] = []
    pause_dist = {"lt_0.3s": 0, "0.3_to_0.8s": 0, "gte_0.8s": 0}
    for i in range(len(segments) - 1):
        gap = round(segments[i + 1]["start"] - segments[i]["end"], 3)
        segments[i]["pause_after"] = gap
        segments[i]["pause_type"] = classify_pause(gap, pause_threshold)
        pauses.append(gap)
        if gap < 0.3:
            pause_dist["lt_0.3s"] += 1
        elif gap < pause_threshold:
            pause_dist["0.3_to_0.8s"] += 1
        else:
            pause_dist["gte_0.8s"] += 1
    # 末段标记
    if segments:
        segments[-1]["pause_after"] = 0.0
        segments[-1]["pause_type"] = "末段"

    # 速率反推 (剔停顿)
    all_text = " ".join(s["text"] for s in segments)
    chinese_chars = len(NON_ALPHA.sub("", all_text))
    english_words = len(ALPHA_WORD.findall(all_text))
    speech_seconds = sum(s["duration"] for s in segments)
    pause_seconds = sum(pauses)

    return {
        "source_file": str(path),
        "total_duration_s": round(segments[-1]["end"] - segments[0]["start"], 3) if segments else 0.0,
        "total_segments": len(segments),
        "rate_calibration": {
            "chinese_chars": chinese_chars,
            "english_words": english_words,
            "speech_seconds": round(speech_seconds, 3),
            "pause_seconds": round(pause_seconds, 3),
            "chinese_rate": round(chinese_chars / speech_seconds, 2) if speech_seconds > 0 else 0.0,
            "english_rate": round(english_words / speech_seconds, 2) if speech_seconds > 0 else 0.0,
        },
        "pause_distribution": pause_dist,
        "segments": segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse SRT into structured timeline JSON")
    parser.add_argument("srt_file", type=Path, help="Path to SRT file")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path (default: stdout)")
    parser.add_argument(
        "--pause-threshold",
        type=float,
        default=0.8,
        help="Pause classification threshold in seconds (default: 0.8)",
    )
    args = parser.parse_args()

    if not args.srt_file.exists():
        print(f"ERROR: SRT file not found: {args.srt_file}", file=sys.stderr)
        return 1

    result = parse_srt(args.srt_file, args.pause_threshold)
    out_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.out:
        args.out.write_text(out_json, encoding="utf-8")
        print(f"Wrote timeline to {args.out}", file=sys.stderr)
    else:
        print(out_json)

    # 简洁摘要到 stderr (供 agent 快速读取)
    rc = result["rate_calibration"]
    print(
        f"\n[SUMMARY] {result['total_segments']} 段 / "
        f"总时长 {result['total_duration_s']}s / "
        f"朗读 {rc['speech_seconds']}s + 停顿 {rc['pause_seconds']}s / "
        f"速率 中文 {rc['chinese_rate']}字/秒 + 英文 {rc['english_rate']}词/秒",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())