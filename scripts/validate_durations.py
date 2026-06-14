#!/usr/bin/env python3
"""
v1.0.5+pic18 铁律 #74 验证脚本（Banana 报告沉淀 · 2026-06-11）

背景：v1.0.3+pic12 把"末帧静默 ≥ 2s"写进铁律 #74（红线），Banana 实战发现：
- 3 Clip × 10s 整数 = 30s 装 30s 朗读 → 末帧静默必须 = 0（物理装不下）
- 末帧静默 = 0 是合法"例外"（节奏紧凑的认知/领读绘本紧接无静默）
- 铁律分类误用：把"经验值"当"红线"用

规则（v1.0.5+pic18 重写）：
- 默认参考：朗读 × 0.3-0.6 倍（标准词组 1-2s，收势 2-3s）
- 例外（静默 = 0 或 < 1s 也合法）：
  - 多段旁白紧接（无画面切换）= 0.5s 仅做镜头切换消化
  - 节奏紧凑的认知/领读绘本 = 紧接无静默
- 静默 < 0.5s = 错误（物理装不下朗读 → 翻车征兆）
- 静默 < 1s = 警告（违反默认参考，需文案说明例外原因）
- 静默 ≥ 1s 且属"例外" = 通过
- 静默 ≥ 2s = 通过（标准做法）

用法：
  python3 validate_durations.py <project_dir>

输出：
  ✅ / ⚠️ / ❌ 标记 + 详细末帧静默秒数

关联文件：
- 主 SKILL.md 铁律 #74 段（v1.0.5+pic18 重写为"参考标准"）
- Banana 报告：/home/luo/.hermes/profiles/huiben/work/20260611-banana-input/REPORT-dev-issues-2026-06-11.md
"""
import json
import sys
from pathlib import Path

# 阈值常量（v1.0.5+pic18 新增）
ERROR_THRESHOLD = 0.5  # < 0.5s 必错
WARN_THRESHOLD = 1.0    # < 1.0s 警告
RECOMMEND_THRESHOLD = 2.0  # ≥ 2s 推荐


def load_storyboard(project_dir: Path) -> dict:
    """读 <project_dir>/clips/storyboard-*.json（只取第一个匹配的）"""
    clips_dir = project_dir / "clips"
    if not clips_dir.exists():
        sys.exit(f"❌ {clips_dir} 不存在")

    storyboards = sorted(clips_dir.glob("storyboard*.json"))
    if not storyboards:
        sys.exit(f"❌ {clips_dir} 找不到 storyboard*.json（先跑 storyboard-design 子 agent）")

    with open(storyboards[0], encoding="utf-8") as f:
        return json.load(f)


def _extract_silence_from_action(action: str, fallback_silence: float) -> float:
    """从 action 字段抽"末帧 X 秒"指令（Banana clip1/clip2 实战：末段 duration=0 但 action 写"末帧 0.5s"）"""
    import re
    m = re.search(r"末帧\s*([\d.]+)\s*s", action)
    if m:
        return float(m.group(1))
    return fallback_silence


def validate_clip(clip: dict) -> dict:
    """验证单个 clip 的末帧静默，返回 {status, silence_seconds, message}"""
    clip_index = clip.get("clip_index", "?")
    tb = clip.get("time_breakdown", [])
    if not tb:
        return {
            "clip_index": clip_index,
            "status": "❌",
            "silence_seconds": None,
            "message": "time_breakdown 为空",
        }

    # 末段 = 最后一段（end == clip 总时长 或 tb[-1]）
    last_segment = tb[-1]
    last_duration = last_segment.get("duration", 0.0)
    last_narration = last_segment.get("narration_seconds", 0.0)
    fallback_silence = last_duration - last_narration
    # ⚠️ Banana clip1/clip2 末段 duration=0 但 action 写"末帧 0.5s"——
    # 从 action 字段抽真静默值（fallback 到 duration-narration）
    silence_seconds = _extract_silence_from_action(
        last_segment.get("action", ""), fallback_silence
    )

    # 判定
    if silence_seconds < ERROR_THRESHOLD:
        return {
            "clip_index": clip_index,
            "status": "❌",
            "silence_seconds": round(silence_seconds, 2),
            "message": f"末帧静默 {silence_seconds:.2f}s < 0.5s 物理装不下朗读 = 翻车征兆",
        }
    elif silence_seconds < WARN_THRESHOLD:
        return {
            "clip_index": clip_index,
            "status": "⚠️",
            "silence_seconds": round(silence_seconds, 2),
            "message": f"末帧静默 {silence_seconds:.2f}s < 1s（违反默认参考）— 需文案说明例外（紧接无静默 / 多段旁白紧接 / 节奏紧凑领读型）",
        }
    elif silence_seconds >= RECOMMEND_THRESHOLD:
        return {
            "clip_index": clip_index,
            "status": "✅",
            "silence_seconds": round(silence_seconds, 2),
            "message": f"末帧静默 {silence_seconds:.2f}s ≥ 2s 标准做法",
        }
    else:
        # 1.0 ≤ silence < 2.0
        return {
            "clip_index": clip_index,
            "status": "✅",
            "silence_seconds": round(silence_seconds, 2),
            "message": f"末帧静默 {silence_seconds:.2f}s 介于 1-2s（收势合理）",
        }


def main():
    if len(sys.argv) != 2:
        print("用法：python3 validate_durations.py <project_dir>")
        print("例：  python3 validate_durations.py ~/.hermes/profiles/huiben/work/20260611-banana-input")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).expanduser()
    if not project_dir.exists():
        sys.exit(f"❌ {project_dir} 不存在")

    print(f"📂 验证项目：{project_dir}")
    print(f"📐 阈值：错误 < {ERROR_THRESHOLD}s / 警告 < {WARN_THRESHOLD}s / 推荐 ≥ {RECOMMEND_THRESHOLD}s\n")

    storyboard = load_storyboard(project_dir)
    clips = storyboard.get("clips", [])
    if not clips:
        sys.exit(f"❌ storyboard.json 找不到 clips 数组")

    print(f"🎬 总 Clip 数：{len(clips)}\n")

    total_errors = 0
    total_warnings = 0
    total_passes = 0

    for clip in clips:
        result = validate_clip(clip)
        print(f"  Clip {result['clip_index']}: {result['status']}  {result['message']}")
        if result["status"] == "❌":
            total_errors += 1
        elif result["status"] == "⚠️":
            total_warnings += 1
        else:
            total_passes += 1

    print(f"\n📊 汇总：{total_passes} 通过 / {total_warnings} 警告 / {total_errors} 错误")

    if total_errors > 0:
        print(f"\n❌ 有 {total_errors} 个 clip 末帧静默 < 0.5s（物理装不下 = 必翻车）— 必改 prompt 重提")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n⚠️ 有 {total_warnings} 个 clip 末帧静默 < 1s（违反默认参考）— 需文案说明例外原因")
        # ⚠️ 警告不退出 0，**不**强制改（用户硬约束物理装不下时 = 例外合法）
        sys.exit(0)
    else:
        print(f"\n✅ 全部通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
