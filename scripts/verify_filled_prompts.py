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
    """检查 3 · 段 4 B 档音效版（非 A 档全静音）"""
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
        # 找段 4 区域（粗略：最后 1/4）
        quarter = max(1, len(text) // 4)
        segment_4 = text[-quarter:]
        is_a_grade = any(p.search(segment_4) for p in a_grade_patterns)
        is_b_grade = any(p.search(segment_4) for p in b_grade_indicators)
        if is_a_grade:
            errors.append(f'  ❌ {f.name}: 段 4 仍是 A 档（无 BGM/无人声/无哼唱 = 全静音翻车）')
        elif not is_b_grade:
            errors.append(f'  ⚠️ {f.name}: 段 4 不含 B 档音效版标识（无 BGM + 音效）')
    return errors


def check_4_dynamic_char_floats(prompt_files):
    """检查 4 · char_floats 动态按 en_word 字母数生成（非硬编码"参/考/图/原/考"）"""
    errors = []
    dynamic_pattern = re.compile(
        r'→\s*[A-Za-z一-鿿]\s*[\(（]\s*0\.\d+s\s*[\)）]'
    )
    for f in prompt_files:
        text = f.read_text(encoding='utf-8', errors='ignore')
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
