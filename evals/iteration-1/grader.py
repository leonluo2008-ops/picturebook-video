#!/usr/bin/env python3
"""darwin grader: 给 Pic2 evals 8 个 Clip 打分（结构 + 效果）。"""
import json
from pathlib import Path

ITER = Path("/home/luo/.hermes/profiles/huiben/skills/creative/picturebook-video/evals/iteration-1")
EXPECTED = json.load(open(ITER.parent / "evals-pic2-v1.json"))


def grade_one(clip_path: Path) -> dict:
    """给单个 Clip 输出打分。"""
    d = json.loads(clip_path.read_text(encoding="utf-8"))
    expected = next(e for e in EXPECTED if e["id"] == d["clip_index"])
    sc = d.get("self_check", {})

    # 9 项 self_check 命中率
    self_check_total = 9
    self_check_passed = sum(1 for v in sc.values() if v is True)

    # 节奏档位正确性（数字 vs expected）
    rhythm_match = (d.get("rhythm_formula") == expected["expected_rhythm"])
    duration_match = (d.get("total_duration_seconds") == expected["expected_clip_duration"])
    shots_match = (d.get("镜头数") == expected["expected_clip_count_per_clip"])

    # 末帧策略正确性（关键词命中）
    endframe = d.get("末帧_strategy", "")
    endframe_contains_微动 = ("微动" in endframe) or ("小动" in endframe) or ("闪烁" in endframe)
    endframe_contains_定格 = "最终定格" in endframe

    # 段 4 隔离句检测
    prompt = d.get("prompt_draft", "")
    isolation_contains = "其他元素不出现" in prompt or "没有其他元素" in prompt

    # @Image 语法 vs @图N 中文别名
    uses_image_syntax = "@Image" in prompt
    uses_zh_alias = "@图" in prompt

    return {
        "clip_index": d["clip_index"],
        "rhythm_match": rhythm_match,
        "duration_match": duration_match,
        "shots_match": shots_match,
        "self_check_passed": self_check_passed,
        "self_check_total": self_check_total,
        "endframe_contains_微动": endframe_contains_微动,
        "endframe_contains_定格": endframe_contains_定格,
        "isolation_contains": isolation_contains,
        "uses_image_syntax": uses_image_syntax,
        "uses_zh_alias": uses_zh_alias,
        "rhythm_formula": d.get("rhythm_formula"),
        "expected_rhythm": expected["expected_rhythm"],
        "duration": d.get("total_duration_seconds"),
        "expected_duration": expected["expected_clip_duration"],
    }


def grade_set(set_name: str) -> list[dict]:
    out_dir = ITER / set_name / "outputs"
    return [grade_one(p) for p in sorted(out_dir.glob("clip*.json"))]


def aggregate(grades: list[dict], label: str) -> dict:
    n = len(grades)
    if n == 0:
        return {"label": label, "n": 0}
    sc_total = sum(g["self_check_passed"] for g in grades)
    sc_max = sum(g["self_check_total"] for g in grades)
    return {
        "label": label,
        "n": n,
        "rhythm_match_pct": round(100 * sum(g["rhythm_match"] for g in grades) / n, 1),
        "duration_match_pct": round(100 * sum(g["duration_match"] for g in grades) / n, 1),
        "shots_match_pct": round(100 * sum(g["shots_match"] for g in grades) / n, 1),
        "self_check_pct": round(100 * sc_total / sc_max, 1),
        "endframe_微动_pct": round(100 * sum(g["endframe_contains_微动"] for g in grades) / n, 1),
        "endframe_定格_pct": round(100 * sum(g["endframe_contains_定格"] for g in grades) / n, 1),
        "isolation_句_pct": round(100 * sum(g["isolation_contains"] for g in grades) / n, 1),
        "@Image_syntax_pct": round(100 * sum(g["uses_image_syntax"] for g in grades) / n, 1),
        "@图N_别名_pct": round(100 * sum(g["uses_zh_alias"] for g in grades) / n, 1),
        "rhythm_match_n": sum(g["rhythm_match"] for g in grades),
        "duration_match_n": sum(g["duration_match"] for g in grades),
        "sc_passed": sc_total,
        "sc_max": sc_max,
    }


with_skill = grade_set("with_skill")
old_skill = grade_set("old_skill")
agg_ws = aggregate(with_skill, "v1.0.0 (with_skill)")
agg_os = aggregate(old_skill, "v0.7.1+pic7 (old_skill)")

# 写 grading.json
out = {
    "iteration": 1,
    "test_set": "pic2-v1",
    "n_clips": 8,
    "with_skill_detail": with_skill,
    "old_skill_detail": old_skill,
    "with_skill_aggregate": agg_ws,
    "old_skill_aggregate": agg_os,
}
(ITER / "grading.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))

print("=" * 70)
print("  Pic2 v1.0.0 vs v0.7.1+pic7 · darwin grader 结果")
print("=" * 70)
print()
print(f"{'维度':<30} {'v0.7.1+pic7':<15} {'v1.0.0':<15} {'delta':<10}")
print("-" * 70)
metrics = [
    ("节奏档位正确率", "rhythm_match_pct"),
    ("时长档位正确率", "duration_match_pct"),
    ("镜头数正确率", "shots_match_pct"),
    ("self_check 9 项通过率", "self_check_pct"),
    ("末帧含'微动'（应≥）", "endframe_微动_pct"),
    ("末帧含'定格'（应=0）", "endframe_定格_pct"),
    ("段 4 隔离句（应=0）", "isolation_句_pct"),
    ("@Image 官方语法（应=100）", "@Image_syntax_pct"),
    ("@图N 中文别名（应=0）", "@图N_别名_pct"),
]
for name, key in metrics:
    v_old = agg_os[key]
    v_new = agg_ws[key]
    delta = round(v_new - v_old, 1)
    sign = "+" if delta > 0 else ""
    print(f"{name:<30} {v_old:>6.1f}%         {v_new:>6.1f}%      {sign}{delta:>5.1f}%")
print()
print(f"self_check 实际命中项：v0.7.1+pic7 = {agg_os['sc_passed']}/{agg_os['sc_max']} | v1.0.0 = {agg_ws['sc_passed']}/{agg_ws['sc_max']}")
