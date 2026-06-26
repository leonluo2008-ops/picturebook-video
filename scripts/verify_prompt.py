#!/usr/bin/env python3
"""
verify_prompt.py · v8.1 prompt 硬规则检查脚本 (v5.0.13 路由增强)

目的:把 picturebook-video SKILL.md 里的"铁律"从文档约束变成可执行门禁。
背景:v5.0.9 修复 7 个不稳定问题, v5.0.10 新增 SRT 驱动 + 动作模板,
     配套 3 条新硬规则解决"画面静止"翻车。
     v5.0.11 新增 4 条 Potato 蓝本结构规则(R6-R9), 区分优/劣 prompt。
     v5.0.12 新增 R10 音频描述规则(generate_audio=True 时必写段 5 音频描述)。
     v5.0.13 路由调整: 音效必写,人声旁白仅路径 A(SRT)必写 (路径 B 无 SRT 可选)
                      + 末尾约束硬约束 #1 = 永远无 BGM。
本脚本 = 把规则自动化。

用法:
  python3 verify_prompt.py <prompt_file> [--ref-images N] [--tts-seconds S] [--clip-target-duration 4-15]
                            [--generate-audio] [--has-srt/--no-srt]

输入: v8.1 prompt 文本文件 + 参数
输出: JSON { ok: bool, failures: [...], warnings: [...] }
退出码: 0=全过 / 1=有失败 / 2=有警告

v5.0.9 检查项(8 项, 保留兼容):
  1. 必含 @ImageN        (#29 @ImageN 必含)
  2. 不缺参考图          (#29 ref_images 长度匹配)
  3. v8 4 段骨架         (#28 v8 简洁收尾)
  4. 末帧段落 0 冗余     (#28 反模式)
  5. 单镜头时长 2-4s     (#37 单镜头时长倾向)
  6. 总时长 ∈ [4, 15]    (#33 合并决策核心约束)
  7. TTS 拟时长差 ≤ 5s   (#21+#27+#33 旁白时长优先)
  8. 不脱离参考图视觉    (#26 参考图是起点不是限制)

v5.0.10 新增(3 项, 解决"画面静止"翻车):
  9. WARN R1/R4 时间锚点 (建议含 MM:SS.mmm 格式时间戳 — 跟旁白时间点对齐)
  10. FAIL R3 凝固语    (禁用 v5.0.9 旧收尾语"持续循环"等 — 让画面凝固)
  11. WARN R1 主体动作   (段 2 提到运镜时必须有主体动作 — 否则画面静止)

v5.0.10.1 BUG 修复 (Potato 实测驱动):
  - 检查项 9 (R1/R4 时间锚点) 从 FAIL 降级为 WARN
  - 跟 Seedance 官方"不强制限制每段时长"对齐 (提示词指南 §2)
  - 4 个按事件分镜 prompt 不再误判 fail (符合官方正面案例)

v5.0.11 新增(4 项, Potato 蓝本结构规则 · 优/劣区分):
  12. FAIL R6 段 1 逐图描述 (每张 @ImageN 必须分别描述视觉基底 + "接着"衔接)
  13. FAIL R7 镜头-旁白绑定 (段 2 镜头必含 @ImageN + "段 N 旁白" 绑定)
  14. FAIL R8 完整旁白文本 (段 3 必含 "段 N 念"完整旁白文本"" 格式)
  15. FAIL R9 具体收尾   (段 4 必含 "镜头 N 末尾" 位置 + 具体微动描述)

v5.0.12 新增(1 项, 音频描述规则):
  16. FAIL R10 音频描述 (generate_audio=True 时, 段 5 必含 "人声旁白：" + "音效：" 描述;
     generate_audio=False / 领读型绘本时跳过此项)
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


# 铁律 #28 反模式:末帧段落 4 句堆砌
END_FRAME_REDUNDANT_PATTERNS = [
    r"末帧定格",
    r"末帧微动",
    r"不得成为定格海报",
    r"1s 内至少 1 个动作元素",
    r"定格在.*?瞬间",
    r"持续跑步动作循环",
    r"保持跑步姿态",
    r"持续交替",
    r"持续摆动",
]

# 铁律 #26 反模式:把参考图当枷锁(严格匹配原构图)
ANTI_REFERENCE_PATTERNS = [
    r"必须保持参考图的整体构图",
    r"严格匹配参考图",
    r"固定原景别不做推拉",
    r"不得脱离参考图",
]

# v5.0.10 反模式 R3:凝固语 — 让画面趋向静止
FROZEN_LANGUAGE_PATTERNS = [
    r"持续循环不切断",
    r"持续.*?循环",
    r"保持.*?稳定",
    r"保持.*?静止",
    r"自然流动有运动感",
    r"画面自然流动",
    r"循环不切断不冻结",  # v5.0.9 旧收尾典型语
]

# v5.0.10 反模式 R1 主体动作缺失:段 2 不能只写运镜而无主体动作
CAMERA_ONLY_KEYWORDS = [
    "镜头推近", "镜头拉远", "镜头推进", "镜头拉近", "镜头缓推", "镜头慢推",
    "镜头微摇", "镜头缓摇", "镜头摇移", "镜头摇", "镜头推", "镜头拉",
    "镜头跟拍", "镜头固定", "镜头切换",
]
SUBJECT_ACTION_KEYWORDS = [
    "摆动", "摇晃", "伸展", "收缩", "跳动", "移动", "走动", "跑动", "飞行",
    "旋转", "翻转", "伸展", "展开", "合拢", "掉落", "飘落", "上升", "下沉",
    "伸入", "伸进", "伸出", "伸手", "触摸", "抓取", "捏住", "握住", "捧起",
    "光斑", "光影", "闪烁", "闪动", "流动", "翻滚", "涌动", "波动", "涟漪",
    "水珠", "露珠", "雨滴", "飘动", "飘荡", "摇曳", "微动", "轻摆", "飘摇",
    "呼吸", "心跳", "眨眼", "张嘴", "说话", "吞咽", "吞吃", "咀嚼", "品尝",
    "揉搓", "揉捏", "撕开", "掰开", "切开", "剥开",
]


def check_at_image_n(text: str, expected_count: int | None = None) -> list[str]:
    """检查 #29 @ImageN 必含。"""
    failures = []
    matches = re.findall(r"@Image(\d+)", text)
    if not matches:
        failures.append("FAIL #29: 必含 @ImageN(0 处找到 = 模型不知道参考图是谁)")
    elif expected_count and len(set(matches)) < expected_count:
        failures.append(
            f"FAIL #29: 多图 Clip @ImageN 数量不足 "
            f"(期望 ≥ {expected_count}, 实际唯一数 = {len(set(matches))})"
        )
    return failures


def check_end_frame_redundant(text: str) -> list[str]:
    """检查 #28 末帧段落冗余。"""
    failures = []
    for pattern in END_FRAME_REDUNDANT_PATTERNS:
        if re.search(pattern, text):
            failures.append(f"FAIL #28: 末帧段落冗余命中 '{pattern}'(v8 简洁收尾 = 末段只写 1 句)")
    return failures


def check_anti_reference(text: str) -> list[str]:
    """检查 #26 反模式:把参考图当枷锁。"""
    failures = []
    for pattern in ANTI_REFERENCE_PATTERNS:
        if re.search(pattern, text):
            failures.append(f"FAIL #26: 参考图枷锁反模式 '{pattern}'(参考图是起点不是限制)")
    return failures


def check_v8_skeleton(text: str) -> list[str]:
    """检查 #28 v8 4 段骨架(粗略:4 个段落分隔符)。"""
    # v8 4 段骨架用 "镜头 1:" "镜头 2:" ... 分段
    shot_markers = re.findall(r"镜头\s*\d+[::]?", text)
    if len(shot_markers) < 2:
        return [
            f"WARN #28: v8 多镜头叙事未检测到足够镜头数 "
            f"(找到 {len(shot_markers)} 个 '镜头 N:' 标记,期望 ≥ 2 — 总时长 ≥ 4s 时优先多镜头)"
        ]
    return []


def check_single_shot_duration(text: str) -> list[str]:
    """检查 #37 单镜头时长倾向 2-4s(粗略:时长数字检查)。"""
    # 抓所有 "X-Ys" 或 "X秒" 数字
    durations = re.findall(r"(\d+(?:\.\d+)?)\s*(?:s|秒)", text)
    failures = []
    long_shots = []
    for d in durations:
        d_val = float(d)
        if d_val > 5:
            long_shots.append(d_val)
    if long_shots:
        failures.append(
            f"WARN #37: 单镜头时长倾向 ≤ 5s, 发现 {long_shots}(过长 = 画面机械/循环/丢失运镜)"
        )
    return failures


def check_total_duration(text: str, target_min: int = 4, target_max: int = 15) -> list[str]:
    """检查 #33 拟时长 ∈ [4, 15]。"""
    failures = []
    # 抓 "总时长 Xs" 或 "total Xs"
    m = re.search(r"(?:总时长|total|时长)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*s", text)
    if m:
        total = float(m.group(1))
        if total < target_min:
            failures.append(f"FAIL #33: 总时长 {total}s < {target_min}s 下限(拆太碎 = 必合并)")
        elif total > target_max:
            failures.append(f"FAIL #33: 总时长 {total}s > {target_max}s 上限(旁白装不下 = 必拆 Clip)")
    return failures


def check_tts_diff(text: str, tts_seconds: float) -> list[str]:
    """检查 #21+#27+#33 TTS 拟时长差 ≤ 5s。"""
    failures = []
    m = re.search(r"(?:总时长|total|时长)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*s", text)
    if m and tts_seconds:
        total = float(m.group(1))
        diff = abs(total - tts_seconds)
        if diff > 5:
            failures.append(
                f"FAIL #21+#27+#33: 拟时长 {total}s vs 用户给 TTS {tts_seconds}s 差 {diff:.1f}s > 5s 容差"
            )
    return failures


def check_time_anchor(text: str) -> list[str]:
    """v5.0.10 R1/R4 反模式: prompt 缺 SRT 时间锚点 (降级为 WARN)。

    检测: 必须至少 1 处 "MM:SS.mmm" 或 "MM:SS,mmm" 或 "MM:SS" 时间戳格式。
    没有 → 视为 prompt 没跟旁白时间点对齐 (画面错位风险)。

    v5.0.10.1 BUG 修复: 跟 Seedance 官方"不强制限制每段时长"对齐,
    时间戳从 FAIL 降级为 WARN — 提示但不阻断 (用户 Potato BUG 反馈:
    强制 100ms 精度 = 官方明确反模式, 4 个 prompt 全 fail 在这个检查上)。
    仍建议写时间锚点 (用近似值如 "约 2 秒处"), 但不强制。
    """
    warnings = []
    patterns = [
        r"\b\d{1,2}:\d{2}[.,]\d{1,3}\b",  # 00:00.000 / 00:00,000
        r"\b\d{1,2}:\d{2}\s*[-–~]\s*\d{1,2}:\d{2}",  # 00:00 - 00:05
    ]
    matches = []
    for p in patterns:
        matches.extend(re.findall(p, text))
    if not matches:
        warnings.append(
            "WARN R1/R4: prompt 无 SRT 时间锚点 (无 MM:SS.mmm 格式时间戳) — "
            "建议写近似锚点 (如 '约 2 秒处' 或 '念到 X 词时 Y 动作'), "
            "但官方明确不强制, 改为 WARN 不阻断 (Potato BUG 修复)"
        )
    return warnings


def check_subject_action(text: str) -> list[str]:
    """v5.0.10 R1 反模式: 段 2 只写运镜而无主体动作。

    检测思路: 如果 prompt 提到"镜头推近/拉远/推进"等运镜词, 但没提任何主体动作
    (摆动/摇晃/光斑/水珠/伸手等) → 警告画面可能静止。
    """
    warnings = []
    has_camera_only = any(kw in text for kw in CAMERA_ONLY_KEYWORDS)
    if has_camera_only:
        has_subject_action = any(kw in text for kw in SUBJECT_ACTION_KEYWORDS)
        if not has_subject_action:
            warnings.append(
                "WARN R1: 段 2 提到运镜但无主体动作描述 — "
                "画面可能静止 (主体本身需要动, 不只镜头动, 见 v8.1 模板)"
            )
    return warnings


def check_frozen_language(text: str) -> list[str]:
    """v5.0.10 R3 反模式: 凝固语 — 让画面趋向静止。"""
    failures = []
    for pattern in FROZEN_LANGUAGE_PATTERNS:
        if re.search(pattern, text):
            failures.append(
                f"FAIL R3: 凝固语命中 '{pattern}' "
                f"(v5.0.9 旧收尾语 → 画面凝固, v8.1 改为末段时间点+保持运动状态)"
            )
    return failures


def check_per_image_description(text: str, ref_images: int | None = None) -> list[str]:
    """v5.0.11 R6: 段 1 必须逐张图分别描述视觉基底 + "接着"衔接。

    检测逻辑:
    - 多图 Clip(≥2 张 @ImageN)必须至少有一处"接着"衔接词，表示逐图描述
    - 如果只有 1 张图，跳过此项(单图无需"接着"衔接)
    - 目的: seedance 需要知道每张图的视觉差异才能做镜头切换
    """
    failures = []
    if ref_images is None or ref_images <= 1:
        return failures  # 单图不需要"接着"衔接

    # 检查"接着"衔接词
    connectors = ["接着", "然后", "之后"]
    has_connector = any(c in text for c in connectors)

    if not has_connector:
        failures.append(
            "FAIL R6: 段 1 缺逐图描述衔接词(缺 '接着'/'然后'/'之后') — "
            "多图 Clip 必须逐张图分别描述视觉基底并用衔接词连接，"
            "否则 seedance 无法区分不同参考图的视觉差异"
        )
    return failures


def check_shot_narration_binding(text: str) -> list[str]:
    """v5.0.11 R7: 段 2 每个镜头必须绑定 @ImageN + "段 N 旁白"。

    检测逻辑:
    - 找所有"镜头 N"标记
    - 至少一个镜头标记行附近(同句)必须同时含 @ImageN 和 "段" 字
    - 如果完全没有镜头-旁白绑定，FAIL
    - 目的: seedance 需要知道每个镜头对应哪张参考图和哪段旁白
    """
    failures = []
    shot_markers = re.findall(r"镜头\s*\d+[：:]?", text)
    if not shot_markers:
        return failures  # 没有镜头标记，其他规则会管

    # 找含"镜头"且同时含"段"的行
    lines = text.split("\n")
    bound_shots = 0
    for line in lines:
        if re.search(r"镜头", line) and re.search(r"段\s*\d+", line):
            bound_shots += 1

    # 宽松: 至少 1 个镜头有绑定就算过(Prompt 可能只有 2 个镜头但只有 1 个绑定了)
    # 严格: 有镜头标记但没有任何一个绑定的才是 FAIL
    if bound_shots == 0 and len(shot_markers) >= 2:
        failures.append(
            "FAIL R7: 段 2 镜头未绑定旁白段 — "
            "至少 1 个镜头必须含 '镜头 N（@ImageN + 段 N 旁白）：' 格式绑定，"
            "否则 seedance 不知道画面动作对应哪段旁白"
        )
    return failures


def check_full_narration_text(text: str) -> list[str]:
    """v5.0.11 R8: 段 3 必须列出段 N 的完整旁白文本。

    检测逻辑:
    - 必须至少有 1 处 `段 N 念"` 格式（"念"后面跟引号包裹的旁白文本）
    - 目的: seedance 需要旁白原文才能直接对照时间点
    """
    failures = []
    # 匹配 "段 N 念"xxx"" 格式
    narration_matches = re.findall(r'段\s*\d+\s*念[""\'"\'".]', text)
    if not narration_matches:
        failures.append(
            "FAIL R8: 段 3 缺完整旁白文本 — "
            "必须用 '段 N 念\"完整旁白文本\"：动作描述' 格式列出每段旁白原文，"
            "只写 '念到 X 词时' 不够(seedance 需要原文直接对照)"
        )
    return failures


def check_specific_closing(text: str) -> list[str]:
    """v5.0.11 R9: 段 4 必须指明镜头位置 + 具体微动。

    检测逻辑:
    - 必须含 "镜头 N 末尾" 或 "镜头 N（收尾）" 格式指明位置
    - 且收尾行必须含具体动作词(不只有"回到开场状态"等抽象语)
    """
    failures = []
    # 检查位置标记
    has_position = bool(
        re.search(r"镜头\s*\d+\s*末尾", text)
        or re.search(r"镜头\s*\d+\s*[（(]\s*收尾\s*[）)]", text)
    )

    # 检查抽象收尾语(即使有位置标记，内容太抽象也算)
    abstract_closing_patterns = [
        r"回到开场状态[，,]",
        r"回到初始状态[，,]",
    ]
    has_abstract = any(re.search(p, text) for p in abstract_closing_patterns)

    if has_abstract:
        failures.append(
            "FAIL R9: 段 4 收尾过于抽象 — "
            "不可用 '回到开场状态'/'回到初始状态' 等抽象语, "
            "必须用 '镜头 N 末尾：具体微动描述' 格式列出明确动作"
        )
    elif not has_position:
        failures.append(
            "FAIL R9: 段 4 缺收尾位置标记 — "
            "必须含 '镜头 N 末尾' 或 '镜头 N（收尾）' 指明在哪个镜头后收尾"
        )
    return failures


def check_audio_description(text: str, generate_audio: bool = False, has_srt: bool = True) -> list[str]:
    """v5.0.12 R10 + v5.0.13 路由调整: generate_audio=True 时段 5 必须包含音频描述。

    v5.0.13 路由规则(2026-06-26 Beet Pepper 实测沉淀):
    - generate_audio=False 时跳过(spike/强制静默, 不需要 seedance 生成音频)
    - generate_audio=True 时:
      - **音效必写** (任何情况下 seedance 都要有音效)
      - **人声旁白仅路径 A(SRT)必写**, 路径 B(无 SRT) 可省略
        - 有 SRT (has_srt=True): 必须含 "人声旁白：" + "音效："
        - 无 SRT (has_srt=False): 只需含 "音效：" (人声旁白可选)
    - 目的: seedance generate_audio=True 会自动生成音频,
      不写音频描述段 → seedance 自己猜内容和节奏 → 不可控
    """
    failures = []
    if not generate_audio:
        return failures  # spike/强制静默 不需要音频描述

    has_sound_effect = bool(re.search(r"音效[：:]", text))

    if not has_sound_effect:
        failures.append(
            "FAIL R10: generate_audio=True 但 prompt 缺 '音效：' — "
            "v5.0.13 硬约束:任何 generate_audio=True 的 prompt 都必须写 '音效：{具体音效描述}',"
            "否则 seedance 生成的音效不可控"
        )

    # 人声旁白: 仅路径 A(SRT)必写, 路径 B(无 SRT)可选
    if has_srt:
        has_voiceover = bool(re.search(r"人声旁白[：:]", text))
        if not has_voiceover:
            failures.append(
                "FAIL R10: 路径 A(有 SRT) 但 prompt 缺 '人声旁白：' — "
                "v5.0.13 规则: 有 SRT 时必须写 '人声旁白：\"{SRT原文}\"' 指定旁白内容,"
                "否则 seedance 会自己猜测旁白内容(2026-06-26 Beet Pepper v1 翻车沉淀)"
            )

    return failures


def verify_prompt(
    text: str,
    ref_images: int | None = None,
    tts_seconds: float | None = None,
    target_min: int = 4,
    target_max: int = 15,
    generate_audio: bool = False,
    has_srt: bool = True,
) -> dict:
    """主入口:返回 { ok, failures, warnings, summary }。"""
    failures: list[str] = []
    warnings: list[str] = []

    # 必检(失败就红)
    failures.extend(check_at_image_n(text, ref_images))
    failures.extend(check_end_frame_redundant(text))
    failures.extend(check_anti_reference(text))
    failures.extend(check_total_duration(text, target_min, target_max))
    failures.extend(check_frozen_language(text))       # v5.0.10 R3
    failures.extend(check_per_image_description(text, ref_images))  # v5.0.11 R6
    failures.extend(check_shot_narration_binding(text))                # v5.0.11 R7
    failures.extend(check_full_narration_text(text))                  # v5.0.11 R8
    failures.extend(check_specific_closing(text))                      # v5.0.11 R9
    failures.extend(check_audio_description(text, generate_audio, has_srt))  # v5.0.12 R10 + v5.0.13 路由
    if tts_seconds is not None:
        failures.extend(check_tts_diff(text, tts_seconds))

    # 警告(可能可接受) — v5.0.10.1 R1/R4 时间锚点从 FAIL 降级
    warnings.extend(check_v8_skeleton(text))
    warnings.extend(check_single_shot_duration(text))
    warnings.extend(check_time_anchor(text))           # v5.0.10.1 降级
    warnings.extend(check_subject_action(text))        # v5.0.10 R1

    return {
        "ok": len(failures) == 0,
        "failures": failures,
        "warnings": warnings,
        "summary": {
            "failures_count": len(failures),
            "warnings_count": len(warnings),
            "text_chars": len(text),
            "@ImageN_count": len(set(re.findall(r"@Image(\d+)", text))),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="picturebook-video v8 prompt 硬规则检查")
    parser.add_argument("prompt_file", help="v8 prompt 文本文件")
    parser.add_argument("--ref-images", type=int, help="该 Clip 对应参考图数量(用于 #29 多图检查)")
    parser.add_argument("--tts-seconds", type=float, help="用户给 TTS 秒数(用于 #21+#27+#33 时长差检查)")
    parser.add_argument("--target-min", type=int, default=4, help="总时长下限(默认 4s)")
    parser.add_argument("--target-max", type=int, default=15, help="总时长上限(默认 15s)")
    parser.add_argument("--quiet", action="store_true", help="只输出 JSON,不打印细节")
    parser.add_argument("--generate-audio", action="store_true",
                        help="v5.0.13 路由:该 Clip 使用 generate_audio=True (触发 R10 音频描述检查)")
    parser.add_argument("--has-srt", action="store_true", default=True,
                        help="v5.0.13 路由: 路径 A 有 SRT → 人声旁白必写 (默认 True)")
    parser.add_argument("--no-srt", dest="has_srt", action="store_false",
                        help="v5.0.13 路由: 路径 B 无 SRT → 人声旁白可选, 只需音效")
    args = parser.parse_args()

    text = Path(args.prompt_file).read_text()
    result = verify_prompt(
        text,
        ref_images=args.ref_images,
        tts_seconds=args.tts_seconds,
        target_min=args.target_min,
        target_max=args.target_max,
        generate_audio=args.generate_audio,
        has_srt=args.has_srt,
    )

    if not args.quiet:
        if result["failures"]:
            print(f"❌ {result['summary']['failures_count']} failures:")
            for f in result["failures"]:
                print(f"  {f}")
        if result["warnings"]:
            print(f"⚠️  {result['summary']['warnings_count']} warnings:")
            for w in result["warnings"]:
                print(f"  {w}")
        if not result["failures"] and not result["warnings"]:
            print("✅ all checks passed")
    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(1 if result["failures"] else 0)


if __name__ == "__main__":
    main()