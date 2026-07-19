# R8 中文引号坑 · 中文全角 `"…"` 必败 ASCII 引号

> **来源**：2026-07-15 Bridge 桥绘本实测 · 3 个 Clip 提示词文件全部失败，根因为段 3 `段 N 念"…"` 用了中文全角左右引号。

## 1. 根因

`scripts/verify_prompt.py` 里 `check_full_narration_text()` 的正则：

```python
narration_matches = re.findall(r'段\s*\d+\s*念["""\'"\'"\'".]', text)
```

字符类里只有 **ASCII 双引号 `"`** 和 **ASCII 单引号 `'`**，但中国大陆 LLM 默认输出是 **中文全角左右引号 `"…"`**（U+201C / U+201D）。

正则字符类 `["""\'"\'"\'".]` 实际只命中：
- `"` (ASCII 0x22)
- `'` (ASCII 0x27)
- 一些预设字符，但 **U+201C/U+201D 不在内**

因此 `段 1 念"桥 Bridge！"`（中文引号）= 100% FAIL，**即使旁白文本完全正确**。

## 2. 反例（Bridge 桥 · 2026-07-15）

```text
【段 3 · 旁白-动作对应】
段 1 念"桥 Bridge！"：木桥完整出现在画面中央。
段 2 念"木头做的桥，bridge"：镜头沿木板横移。
```

中文 `"…"` 包裹 → verify_prompt.py R8 FAIL → ok=False。

修复：

```text
段 1 念"桥 Bridge！"：...
段 2 念"木头做的桥，bridge"：...
```

ASCII `"…"` 包裹 → R8 PASS → ok=True。

## 3. 一键修复 · `scripts/fix_prompt_quotes.py`

```python
#!/usr/bin/env python3
"""把中文全角 "…"/'…' 一键改 ASCII 引号。仅用于段 3 '段 N 念"…"：' 行。"""
import sys
from pathlib import Path

def fix(text: str) -> str:
    out = text
    out = out.replace('\u201c', '"').replace('\u201d', '"')
    out = out.replace('\u2018', "'").replace('\u2019', "'")
    return out

if __name__ == "__main__":
    for p in sys.argv[1:]:
        path = Path(p)
        src = path.read_text(encoding="utf-8")
        new = fix(src)
        if new != src:
            path.write_text(new, encoding="utf-8")
            print(f"[FIXED] {p}")
        else:
            print(f"[OK]    {p}")
```

用法：

```bash
python3 scripts/fix_prompt_quotes.py clip1_prompt.txt clip2_prompt.txt clip3_prompt.txt
python3 scripts/verify_prompt.py clip1_prompt.txt --ref-images 2 --tts-seconds 5.067 --generate-audio --has-srt
```

## 4. 预防 · 写 prompt 时口诀

> **"中文叙述，英文断引"** — 中文文章里只需要 ASCII 双引号包裹 SRT 原文，前面 `段 N 念` 前缀 + 后面 `：` + 动作描述。

写完 1 段建议立刻跑：

```bash
python3 -c "import re,sys; t=open(sys.argv[1]).read(); print('OK' if re.search(r'段\\s*\\d+\\s*念[\"\\']', t) else 'FAIL 中文引号')" clip1_prompt.txt
```

FAIL → 跑 `fix_prompt_quotes.py` → 再 verify_prompt.py 确认 R8 PASS。

## 5. 版本

v1.0 (2026-07-15 Bridge 桥实测沉淀)
