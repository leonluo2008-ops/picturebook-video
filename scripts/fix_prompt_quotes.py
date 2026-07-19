#!/usr/bin/env python3
"""把中文全角 "…"/'…' 一键改 ASCII 引号。

场景（2026-07-15 Bridge 桥实测沉淀）：
v8.1 prompt 段 3 常用中文表述，LLM 默认输出全角左右引号 "…" / '…'（U+201C/201D/2018/2019）；
而 verify_prompt.py check_full_narration_text 的正则只认 ASCII 引号，
导致 `段 N 念"…"` 整段必 R8 FAIL。

用法：
  python3 scripts/fix_prompt_quotes.py clip1_prompt.txt [clip2_prompt.txt ...]
"""
import sys
from pathlib import Path


def fix(text: str) -> str:
    out = text
    out = out.replace('\u201c', '"').replace('\u201d', '"')
    out = out.replace('\u2018', "'").replace('\u2019', "'")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: fix_prompt_quotes.py <file1.txt> [file2.txt ...]")
        sys.exit(2)
    fixed = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        src = path.read_text(encoding="utf-8")
        new = fix(src)
        if new != src:
            path.write_text(new, encoding="utf-8")
            print(f"[FIXED] {arg}")
            fixed += 1
        else:
            print(f"[OK]    {arg}")
    sys.exit(0 if fixed >= 0 else 1)
