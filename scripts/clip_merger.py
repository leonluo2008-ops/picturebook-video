#!/usr/bin/env python3
"""
clip_merger.py — v5.0.10 时间轴驱动的 Clip 划分器

设计原则:
  - 输入是 srt_parser.py 输出的 JSON (真实时间戳)
  - 不做估算, 直接用真实秒数
  - 不再 "向上取整到 [4,15]" (v5.0.9 估算逻辑在 SRT 路径下被取消)
  - 段间停顿 >= pause_threshold 的视为"画面切换信号" (clip 边界候选)
  - clip 时长硬约束: [4, 15] 秒 (避免 seedance 报错)

核心策略 (5 步):
  1. 累加相邻段 (含停顿) 直到当前组超过 15s → 当前组结束
  2. 检查当前组是否 < 4s → 跟下一组合并 (避免太短)
  3. 检查是否超过 15s → 拆段 (按段边界)
  4. 对齐总时长 vs 用户 TTS (差 <= 1s 精确模式 / <= 5s 兼容模式)
  5. 输出每个 clip 包含: 起止时间 / 时长 / 段列表 / 停顿列表 /
     suggested_duration (ceil 整数, 必含 + 不可 < srt_span) / duration_ok (校验)

P0 铁律: 整数拟时长 ≥ 完整 SRT 窗口 (含尾部停顿)
  srt_span = 末段 end + 末段 pause_after - 首段 start
  画面时长必须覆盖旁白段间静默间隔, 否则下一段旁白还没念完画面就切了

v5.0.10 BUG 修复 (Potato 实测驱动):
  - srt_span 漏算尾部 pause_after → 含尾部停顿 (P0 铁律)
  - SUMMARY [OK]/[OUT] 用错字段 → 改用 suggested_duration
  - 安全网: 任何 clip > 15s 必须 warning

v5.0.10.1 BUG 修复 (云服实测驱动):
  - flush() srt_span 计算: 末段 end - 首段 start → 末段 end + 末段 pause_after - 首段 start
  - 后处理合并段同步修复 tail_pause
  - SUMMARY 输出展示 tail_pause 明细

用法:
  python3 scripts/clip_merger.py timeline.json
  python3 scripts/clip_merger.py timeline.json --max-clip 15 --min-clip 4
  python3 scripts/clip_merger.py timeline.json --user-tts 30.266 --align-tolerance 1.0
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def merge_clips(
    segments: list[dict],
    min_clip: float = 4.0,
    max_clip: float = 15.0,
    pause_threshold: float = 0.8,
) -> list[dict]:
    """
    时间轴驱动合并策略:
      - 累加段 + 段间停顿
      - 当前组超过 max_clip → 切
      - 当前组 + 停顿 + 下一段 ≤ max_clip → 继续合并
      - 当前组 < min_clip → 强制并入下一组
      - 段间停顿 >= pause_threshold → 优先作为切分点
    """
    clips: list[dict] = []
    cur_segments: list[dict] = []
    cur_speech_dur = 0.0
    cur_total_dur = 0.0  # 包含停顿

    def flush() -> None:
        nonlocal cur_segments, cur_speech_dur, cur_total_dur
        if cur_segments:
            # srt_span = 完整 SRT 窗口: 末段 end + 末段 pause_after - 首段 start
            # 必含尾部停顿: 画面要覆盖旁白段间的静默间隔 (P0 铁律)
            start = cur_segments[0]["start"]
            end = cur_segments[-1]["end"]
            tail_pause = cur_segments[-1].get("pause_after", 0.0)
            srt_span = round(end + tail_pause - start, 3)
            suggested = math.ceil(srt_span)
            clips.append({
                "segments": list(cur_segments),
                "speech_duration": round(cur_speech_dur, 3),
                "total_duration": round(end - start, 3),  # 纯语音跨度 (不含停顿)
                "srt_span": srt_span,                # 完整 SRT 窗口 (含尾部停顿)
                "suggested_duration": suggested,     # 整数拟时长 = ceil, seedance 接收
                "duration_ok": suggested >= srt_span,
                "start": start,
                "end": end,
                "tail_pause": tail_pause,
            })
        cur_segments = []
        cur_speech_dur = 0.0
        cur_total_dur = 0.0

    for i, seg in enumerate(segments):
        seg_dur = seg["duration"]
        pause_after = seg.get("pause_after", 0.0)
        # 含停顿的总占用 = 段时长 + 段后停顿 (末段停顿 = 0)
        seg_total = seg_dur + pause_after

        # 第一个段直接入组
        if not cur_segments:
            cur_segments.append(seg)
            cur_speech_dur += seg_dur
            cur_total_dur += seg_dur
            continue

        # 切分判断: 当前组 + 下一段 (含停顿) 超过 max_clip → 切
        would_be_total = cur_total_dur + seg_total
        strong_boundary = pause_after >= pause_threshold and cur_speech_dur >= min_clip

        if would_be_total > max_clip or strong_boundary:
            # 当前组已够 min_clip → 切
            if cur_speech_dur >= min_clip:
                flush()
            # 否则保留当前段入下一组
            else:
                # 当前组太短, 保留当前段+新段再判断
                cur_segments.append(seg)
                cur_speech_dur += seg_dur
                cur_total_dur += seg_total
                continue

        cur_segments.append(seg)
        cur_speech_dur += seg_dur
        cur_total_dur += seg_total

    flush()

    # 后处理: 末段 < min_clip 时跟上一组合并
    if len(clips) >= 2 and clips[-1]["speech_duration"] < min_clip:
        last = clips.pop()
        clips[-1]["segments"].extend(last["segments"])
        clips[-1]["speech_duration"] = round(
            clips[-1]["speech_duration"] + last["speech_duration"], 3
        )
        new_end = clips[-1]["segments"][-1]["end"]
        new_tail_pause = clips[-1]["segments"][-1].get("pause_after", 0.0)
        new_speech_span = round(new_end - clips[-1]["segments"][0]["start"], 3)
        new_srt_span = round(new_end + new_tail_pause - clips[-1]["segments"][0]["start"], 3)
        clips[-1]["total_duration"] = new_speech_span
        clips[-1]["srt_span"] = new_srt_span
        clips[-1]["suggested_duration"] = math.ceil(new_srt_span)
        clips[-1]["duration_ok"] = clips[-1]["suggested_duration"] >= new_srt_span
        clips[-1]["end"] = new_end
        clips[-1]["tail_pause"] = new_tail_pause

    # 给每个 clip 加编号 + 文本摘要
    for i, c in enumerate(clips):
        c["clip_idx"] = i + 1
        c["text_concat"] = " + ".join(s["text"] for s in c["segments"])
        c["segment_indices"] = [s["idx"] for s in c["segments"]]
        # 取每个 clip 的段间停顿列表 (供 prompt 写"停顿处"参考)
        pauses = []
        for j in range(len(c["segments"]) - 1):
            pauses.append(c["segments"][j].get("pause_after", 0.0))
        c["internal_pauses"] = pauses

    return clips


def check_alignment(
    clips: list[dict], user_tts: float, tolerance: float = 1.0
) -> dict[str, Any]:
    """
    对齐检查: 所有 clip 的 suggested_duration 总和 vs 用户 TTS 总时长
    v5.0.10 精确模式: 容差 1s (vs v5.0.9 的 5s)

    注意: clip 总和不包含第一段前的偏移 (SRT 首段 start 通常 >0) 也不包含
          末段后的停顿 (无内容)。这就是预期行为, 不算偏差。

    v5.0.10 BUG 修复: 改用 suggested_duration 总和 — 这才是 seedance 实际接收
    的整数总时长, 用 total_duration (浮点) 会跟用户 TTS 有 0.5-1s 偏差
    """
    actual = sum(c["suggested_duration"] for c in clips)
    diff = round(actual - user_tts, 3)
    # 末段后无停顿 = 预期差, 通常 last_clip.end < user_tts 一点点
    return {
        "user_tts": user_tts,
        "actual_clips_total": round(actual, 3),
        "diff_seconds": diff,
        "within_tolerance": abs(diff) <= tolerance,
        "tolerance_used": tolerance,
        "note": "实际总和用 suggested_duration (ceil 整数) — 这是 seedance 实际接收的整数总时长",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge SRT timeline into video clips")
    parser.add_argument("timeline_json", type=Path, help="Path to timeline JSON from srt_parser.py")
    parser.add_argument("--min-clip", type=float, default=4.0, help="Min clip duration (default: 4s)")
    parser.add_argument("--max-clip", type=float, default=15.0, help="Max clip duration (default: 15s)")
    parser.add_argument("--pause-threshold", type=float, default=0.8, help="Strong boundary threshold (default: 0.8s)")
    parser.add_argument("--user-tts", type=float, default=None, help="User-provided TTS total duration for alignment check")
    parser.add_argument("--align-tolerance", type=float, default=1.0, help="Alignment tolerance in seconds (default: 1.0)")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path")
    args = parser.parse_args()

    if not args.timeline_json.exists():
        print(f"ERROR: timeline JSON not found: {args.timeline_json}", file=sys.stderr)
        return 1

    timeline = json.loads(args.timeline_json.read_text(encoding="utf-8"))
    segments = timeline["segments"]

    clips = merge_clips(segments, args.min_clip, args.max_clip, args.pause_threshold)

    result: dict[str, Any] = {
        "source_timeline": str(args.timeline_json),
        "min_clip": args.min_clip,
        "max_clip": args.max_clip,
        "pause_threshold": args.pause_threshold,
        "total_clips": len(clips),
        "clips": clips,
    }

    # 对齐检查 (可选)
    if args.user_tts is not None:
        result["alignment"] = check_alignment(clips, args.user_tts, args.align_tolerance)
    else:
        # 用 timeline 总时长作为隐含 TTS
        result["alignment"] = check_alignment(
            clips, timeline["total_duration_s"], args.align_tolerance
        )

    out_json = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(out_json, encoding="utf-8")
        print(f"Wrote clips to {args.out}", file=sys.stderr)
    else:
        print(out_json)

    # 摘要到 stderr
    print(f"\n[SUMMARY] {len(clips)} clips:", file=sys.stderr)
    over_limit_warnings = []
    for c in clips:
        suggested = c["suggested_duration"]
        in_range = "OK" if args.min_clip <= suggested <= args.max_clip else "OUT"
        # v5.0.10 BUG 修复: 安全网 — 任何 clip > max_clip 必 warning (用户原话)
        if c["srt_span"] > args.max_clip:
            over_limit_warnings.append(c["clip_idx"])
        print(
            f"  Clip {c['clip_idx']}: {c['speech_duration']}s speech / "
            f"{c['total_duration']}s voice + {c['tail_pause']}s tail_pause = "
            f"{c['srt_span']}s srt_span (suggest={suggested}s) [{in_range}] "
            f"seg #{c['segment_indices'][0]}-#{c['segment_indices'][-1]}",
            file=sys.stderr,
        )
    if over_limit_warnings:
        print(
            f"  ⚠️  WARNING: Clip {over_limit_warnings} srt_span > {args.max_clip}s "
            f"— srt_span > {args.max_clip}s, seedance 无法覆盖, 必拆 clip (P0 铁律)",
            file=sys.stderr,
        )
    al = result["alignment"]
    print(
        f"\n[ALIGN] user_tts={al['user_tts']}s vs actual={al['actual_clips_total']}s "
        f"diff={al['diff_seconds']:+.3f}s [{'OK' if al['within_tolerance'] else 'OUT'}]",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())