#!/usr/bin/env python3
"""
fill_v15 模板填完后必查 4 项 · 验证脚本

跑完 scripts/fill_v15_template.py 后必跑此脚本验证 4 项关键检查（防 fill 脚本 bug 残留）。

用法:
    python3 verify_filled_prompts.py <clips_dir>

退出码:
    0 = 4/4 全过
    1 = 任 1 项失败（CI 拦截）
"""
import sys
import re
from pathlib import Path


CHECKS = {
    1: '0 双重前缀（@Image@Image）',
    2: '@Image 空格语法（不带空格的合并 = 错）',
    3: '段 4 B 档音效版（非 A 档全静音）',
    4: "char_floats 动态按 en_word 字母数生成（非硬编码'参/考/图/原/考'）",
}

# 硬编码 "参/考/图/原/考" = 历史 fill 模板 bug 的具体残留值
HARDCODED_CHAR_FLOATS_RE = re.compile(
    r"参\s*[\(（]\s*0\.\d+s\s*[\)）]\s*→\s*考\s*[\(（]\s*0\.\d+s\s*[\)）]"
)


def check_1_double_prefix(prompt_files):
    """检查 1 · 0 双重前缀"""
    errors = []
    for f in prompt_files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        if '@Image@Image' in text:
            errors.append(f'  ❌ {f.name}: 含 @Image@Image 双重前缀')
    return errors


def check_2_space_syntax(prompt_files):
    """检查 2 · @Image 空格语法（不带空格的合并 = 错）"""
    errors = []
    bad_pattern = re.compile(r'@Image\d+\+@Image')  # 不带空格的 +@
    for f in prompt_files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        if bad_pattern.search(text):
            errors.append(f'  ❌ {f.name}: 含不带空格的 @Image1+@Image2')
    return errors


def check_3_sound_strategy_b(prompt_files):
    """检查 3 · 段 4 B 档音效版（非 A 档全静音）

    支持两种范式：
    - v15/v6 模板：找"段 4 · BGM 段"标记
    - v7 模板：直接搜全文"No background music"（B 档标志）
    """
    errors = []
    a_grade_patterns = [
        re.compile(r'no\s+background\s+music\s*,\s*no\s+human\s+voice\s*,\s*no\s+narration\s*,\s*no\s+singing', re.I),
        re.compile(r'无任何背景音乐\s*[\(（]?\s*无旁白人声\s*[\(（]?\s*无哼唱'),
    ]
    b_grade_indicators = [
        re.compile(r'no\s+background\s+music', re.I),
        re.compile(r'(ambient|environmental|gentle|soft)\s+(sound|effect)', re.I),
    ]
    for f in prompt_files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        # v7 模板识别（包含 "This is a storyboard reference image sequence"）
        is_v7 = "storyboard reference image sequence" in text.lower()
        if is_v7:
            # v7 范式：直接搜全文 B 档标识（v7 末尾都有 "No background music, no human voice, no narration, no singing"）
            segment_4 = text  # 全文本
        else:
            # v15/v6 范式：找"段 4 · BGM 段"标记
            seg4_start = text.find("段 4 · BGM 段")
            if seg4_start < 0:
                # 兜底：v15 模板没有"段 4 · BGM 段"标记，取中间 1/3
                third = max(1, len(text) // 3)
                segment_4 = text[third:2*third]
            else:
                # 找到"段 4 · BGM 段"位置，取到下一个段标记
                seg4_end_candidates = [text.find(marker, seg4_start) for marker in ["段 3 · 风格锁定", "段 5 · 文字持续可见段"]]
                seg4_end_candidates = [e for e in seg4_end_candidates if e > 0]
                seg4_end = min(seg4_end_candidates) if seg4_end_candidates else len(text)
                segment_4 = text[seg4_start:seg4_end]
        is_a_grade = any(p.search(segment_4) for p in a_grade_patterns)
        is_b_grade = any(p.search(segment_4) for p in b_grade_indicators)
        # v7 模板的 "No background music, no human voice, no narration, no singing" 就是绘本 B 档标准写法
        # 不是真 A 档翻车 · 跳过 A 档判定
        if is_v7 and is_a_grade and is_b_grade:
            is_a_grade = False  # v7 模板 + 含 B 档元素 = 不是真 A 档
        if is_a_grade:
            errors.append(f'  ❌ {f.name}: 段 4 仍是 A 档（无 BGM/无人声/无哼唱 = 全静音翻车）')
        elif not is_b_grade:
            errors.append(f'  ⚠️ {f.name}: 段 4 不含 B 档音效版标识（无 BGM + 音效）')
    return errors


def check_4_dynamic_char_floats(prompt_files):
    """检查 4 · char_floats 动态按 en_word 字母数生成（非硬编码"参/考/图/原/考"）

    v6 模板必查，v7 模板跳过（v7 没有文字持续可见段）。
    """
    errors = []
    dynamic_pattern = re.compile(
        r'→\s*[A-Za-z一-鿿]\s*[\(（]\s*0\.\d+s\s*[\)）]'
    )
    for f in prompt_files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        # v7 模板跳过 char_floats 检查
        is_v7 = "storyboard reference image sequence" in text.lower()
        if is_v7:
            continue
        has_hardcoded = bool(HARDCODED_CHAR_FLOATS_RE.search(text))
        has_dynamic = bool(dynamic_pattern.search(text))
        if has_hardcoded:
            errors.append(f'  ❌ {f.name}: char_floats 硬编码"参/考/图/原/考"（fill 脚本 bug 残留）')
        elif not has_dynamic:
            errors.append(f'  ⚠️ {f.name}: 段 5 找不到动态 char_floats 模式（可能不是 v6 模板？）')
    return errors


CHECK_FUNCS = {
    1: check_1_double_prefix,
    2: check_2_space_syntax,
    3: check_3_sound_strategy_b,
    4: check_4_dynamic_char_floats,
}


def main():
    if len(sys.argv) != 2:
        print('用法: python3 verify_filled_prompts.py <clips_dir>')
        print('示例: python3 verify_filled_prompts.py ~/.hermes/profiles/huiben/work/<date>-<book>/clips/')
        sys.exit(2)

    clips_dir = Path(sys.argv[1]).expanduser()
    if not clips_dir.is_dir():
        print(f'❌ 目录不存在: {clips_dir}')
        sys.exit(2)

    prompt_files = sorted(clips_dir.glob('clip*-prompt.txt'))
    if not prompt_files:
        print(f'❌ 目录 {clips_dir} 下找不到 clip*-prompt.txt 文件')
        sys.exit(1)

    print(f'📂 验证目录: {clips_dir}')
    print(f'📄 找到 {len(prompt_files)} 个 prompt 文件')
    print()

    total_errors = 0
    for check_id, check_name in CHECKS.items():
        errors = CHECK_FUNCS[check_id](prompt_files)
        status = '✅' if not errors else '❌'
        print(f'[检查 {check_id}] {check_name} ... {status}')
        for e in errors:
            print(e)
            total_errors += 1
        print()

    print('=' * 60)
    if total_errors == 0:
        print(f'🎉 4/4 全过 · 全部 {len(prompt_files)} 个 prompt 文件验证通过')
        sys.exit(0)
    else:
        print(f'❌ 验证失败 · {total_errors} 个错误')
        print()
        print('修复方向：见 references/verify-filled-prompts.md')
        sys.exit(1)


if __name__ == '__main__':
    main()
