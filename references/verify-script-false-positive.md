# verify_filled_prompts.py 误报 + 手动 grep 4 项范式

> **目的**：沉淀 `verify_filled_prompts.py` 在"中文手写 prompt" + "v15 4 段范式"两类场景下的误报问题，以及**手动 grep 4 项验证**作为兜底范式。
>
> **来源**：2026-06-16 Run 跑绘本（4 个 Clip · 全手写 · 全 v15 4 段）· verify 报 9 个错，手动 grep 验证全部 5/5 通过
>
> **方法**：verify 脚本默认按 v15 模板（fill 脚本产出）的英文标识 + v6 5 段范式判别 · **对中文手写 + v15 4 段 = 必误报**

---

## 误报 1 · 检查 3「段 4 B 档音效版」对中文手写 prompt 必报

**触发场景**：手写 prompt 段 4 用中文写"无任何背景音乐，保留画面元素的动作音效" → verify 报 `段 4 不含 B 档音效版标识`

**根因**：

`verify_filled_prompts.py` 的 `b_grade_indicators` 列表里只接受**英文标识**：

```python
b_grade_indicators = [
    re.compile(r'no\s+background\s+music', re.I),
    re.compile(r'(ambient|environmental|gentle|soft)\s+(sound|effect)', re.I),
]
```

**中文"无任何背景音乐" / "音效" / "拟声" → 不匹配英文正则 → 报"不含 B 档音效版标识"**

**反模式**：
- ❌ 看到 verify 报"段 4 不含 B 档音效版" → 立即改英文 BGM 标识 → 跟 fill 模板默认的英文写法对齐 → 牺牲中文 prompt 的可读性
- ❌ 看到报 → 改 fill 脚本默认范式 → 破坏手写灵活性

**正确修复**：
- ✅ 手动 grep 中文"无任何背景音乐" + "音效"/"拟声" 同时出现 = **B 档语义 OK**
- ✅ 这是脚本对中文手写的局限，**不盲跟脚本**

---

## 误报 2 · 检查 4「char_floats 段 5」对 v15 4 段范式必报

**触发场景**：v15 4 段范式（段 1 主体 + 段 2 分镜 + 段 3 风格 + 段 4 BGM）→ verify 报 `段 5 找不到动态 char_floats 模式（可能不是 v6 模板？）`

**根因**：

`verify_filled_prompts.py` 的 `check_4_dynamic_char_floats`：

```python
# v7 模板跳过 char_floats 检查
is_v7 = "storyboard reference image sequence" in text.lower()
if is_v7:
    continue
```

**只跳过 v7，没跳过 v15 4 段**。v15 4 段 = 没段 5（char_floats 段）= **必报"段 5 找不到"= 误报**。

**反模式**：
- ❌ 看到报"段 5 找不到" → 改写 v6 5 段范式 → 给短绘本硬加段 5（文字持续可见段）= 没必要
- ❌ 看到报 → 加伪段 5 = prompt 凑字数

**正确修复**：
- ✅ v15 4 段范式 = 没段 5 是**合法**的，char_floats 是 v6 5 段才需要
- ✅ 判断范式：看 `段 1 · / 段 2 · / 段 3 · / 段 4 ·` 4 个标记是否齐全 = v15 4 段 = 跳过检查 4

---

## 误报 3 · 检查 2「@Image 空格语法」对单图 Clip 误报

**触发场景**：单图 Clip（如 Clip 3 只有 `@Image6`）→ verify 报 `检查 2 失败: 单图参考（不需要空格合并）`

**实际逻辑**：脚本 `check_2_space_syntax` 只在**多图合并**时查"@Image1+@Image2"无空格问题。单图本来就只有 1 个 `@Image`，**不需要空格语法**。

**根因**：脚本的判定逻辑误把"单图"也算成"需要空格" = 缺例外分支。

**正确修复**：
- ✅ 单图 Clip = 检查 2 跳过
- ✅ 多图 Clip = `@Image1 + @Image2 + @Image3` 带空格（不带空格 = 错）

---

## 手动 grep 4 项范式（替代 verify 误报时）

```python
import re, os
clips_dir = "<你的 clips 目录>"
files = sorted([f for f in os.listdir(clips_dir) if f.endswith('.txt')])

for fname in files:
    text = open(os.path.join(clips_dir, fname)).read()
    print(f"📄 {fname}")
    
    # 1. 双重前缀
    print("  ✅ 1" if "@Image@Image" not in text else "  ❌ 1: 含双重前缀")
    
    # 2. 空格语法（仅多图检查）
    bad = re.findall(r'@Image\d+(@Image\d+)+', text)
    if bad:
        print(f"  ❌ 2: 不带空格的合并 {bad}")
    elif re.search(r'@Image\d+ \+ @Image\d+', text):
        print("  ✅ 2: @Image 带空格语法正确")
    else:
        print("  ℹ️ 2: 单图参考（不需要空格合并）")
    
    # 3. B 档（中文语义判断）
    has_no_bgm = "无任何背景音乐" in text
    has_sfx = "音效" in text or "拟声" in text
    if has_no_bgm and has_sfx:
        print("  ✅ 3: B 档语义 OK（无 BGM + 音效/拟声）")
    elif has_no_bgm and not has_sfx:
        print("  ❌ 3: 写'无任何背景音乐'但缺音效 → A 档翻车")
    else:
        print("  ⚠️ 3: 缺'无任何背景音乐'或'音效'标识")
    
    # 4. v15 4 段 vs v6 5 段
    is_v15 = ("段 1 ·" in text or "主体定义" in text) and "段 4 ·" in text
    print("  ✅ 4: v15 4 段范式" if is_v15 else "  ⚠️ 4: 非 v15 4 段")
    
    # 末尾约束 4 行
    has_4lines = all([
        "保持无字幕" in text,
        "不要生成水印" in text,
        "不要生成 Logo" in text,
        "无人声" in text and "无歌唱" in text and "无配音" in text and "无朗读" in text,
    ])
    print("  ✅ 末尾约束 4 行齐全" if has_4lines else "  ❌ 末尾约束 4 行缺失")
```

---

## 反模式（verify 误报时必避）

- ❌ 看到 verify 报 → 立即改 prompt 适配脚本（破坏中文可读性 / 牺牲手写灵活性）
- ❌ 看到 verify 报 → 改 fill 脚本默认范式（破坏 fill 模板标准化）
- ❌ 看到 verify 报 → 加伪段 5 / 改 v15 → v6 = 凑字数
- ❌ 看到 verify 报 → 改英文 BGM 标识 = 跟中文手写冲突

---

## 何时信任 verify / 何时手动 grep

| 场景 | 信任 verify | 手动 grep |
|---|---|---|
| 用 fill 脚本填的 v15 模板 | ✅ 信任 | 兜底 |
| 手写 v15 4 段范式 | ❌ 误报 | ✅ 必走 |
| v6 5 段范式 | ✅ 信任（含 char_floats 检查） | 兜底 |
| v7 首尾帧范式 | ⚠️ 部分跳过（v7 跳过 char_floats） | 补检查 |
| 单图 Clip | ⚠️ 检查 2 误报 | ✅ 手动 |
| 多图 Clip | ✅ 信任 | 兜底 |

---

## 修复优先级（待 verify 脚本本身修）

| 修复点 | 优先级 | 状态 |
|---|---|---|
| 检查 3 接受中文"无任何背景音乐"+ 音效/拟声 | P1 | ⚠️ 未修（脚本读中文应等价） |
| 检查 4 跳过 v15 4 段范式（不只跳过 v7） | P1 | ⚠️ 未修 |
| 检查 2 单图 Clip 加例外分支 | P2 | ⚠️ 未修 |
| verify 文档说明误报场景 | P0 | ✅ 本 references 沉淀 |

---

## 关联沉淀

- **picturebook-video SKILL.md** §"Step 5 节点应变" 加 verify 误报判定（"v15 → 跳过 char_floats 检查 = 脚本里'可能不是 v6 模板？'提示就是误报"）
- **picturebook-video SKILL.md** §"填完必查 4 项" 加"中文手写 v15 范式 = 必走手动 grep 兜底"

---

## 实战案例（2026-06-16 Run 跑）

- 4 个 Clip 全手写 v15 4 段 + 中文段 4 "无任何背景音乐，保留画面元素的动作音效"
- verify 报 9 个错（4 个检查 3 + 4 个检查 4 + 1 个检查 2 误报单图）
- 手动 grep 4 项 + 末尾约束检查 = **5/5 全过**
- Clip 3 试跑成功（5.085s · 720p · B 档音效）→ 用户目检中