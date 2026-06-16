---
name: v8-tts-rate
description: v8 写法 TTS 速率方案 — 5 档语速对比 + 兜底公式 + 严格匹配范式 + 合并配方。整合 5-tier-rate-anti-pattern + tts-duration-merge-recipe + tts-rate-calibration-workflow + tts-strict-match-paradigm 4 个老 references 的核心方法论。
license: Apache-2-2
metadata:
  hermes:
    tags: [v8, tts, rate, calibration, 2026-06-16]
  related_skills: [picturebook-video, seedance2.0-tool]
---

# v8 写法 TTS 速率方案

> **整合**：5 档语速 + 合并配方 + 校对 + 严格匹配
> **核心口诀**：绘本短句领读型 = 1.4/4.0 档为默认起点
> **反推拟合 ≠ 真实速率** = 必跑但必不选

---

## 5 档语速对比

| 档 | 英文（词/秒）| 中文（字/秒）| 物理意义 | 适用 |
|---|---|---|---|---|
| 1 | 0.67 | 2.0 | 反推档（数学拟合）| **必跑但必不选** |
| 2 | 1.0 | 3.0 | 标准慢速 | 慢估看上限 |
| 3 | **1.4** | **4.0** | **领读短句** | **绘本短句双语领读型默认** |
| 4 | 1.5 | 4.0 | 极短单词 | 单词型绘本 |
| 5 | 2.0 | 5.0 | 快速读 | 演讲/广告 |

**反推档（0.67/2.0）** = 用缩放系数同时缩放中英速率 = **数学拟合 ≠ 真实速率** = 总和看起来匹配但单项速率毫无物理意义（英文 0.67 词/秒 = 每词 1.5s = 异常慢）。

---

## 5 步必走（Step 3）

```bash
# Step 3.1: 慢估看上限（1.0/3.0）
python3 scripts/tts_rate_calculator.py --rate 1.0 3.0 --input narration.txt
# 期望：偏长（如绘本 28s 旁白 → 41.67s，差 +13.67s 远超 5s 容忍）

# Step 3.2: 领读短句档看下限（1.4/4.0）
python3 scripts/tts_rate_calculator.py --rate 1.4 4.0 --input narration.txt
# 期望：命中（绘本 28s 旁白 → 30.46s，差 +2.46s ✅）

# Step 3.3: 极短单词档（1.5/4.0）
python3 scripts/tts_rate_calculator.py --rate 1.5 4.0 --input narration.txt
# 期望：更短，备选

# Step 3.4: 反推档仅参考不选（0.67/2.0）
python3 scripts/tts_rate_calculator.py --rate 0.67 2.0 --input narration.txt
# 期望：匹配但速率无物理意义

# Step 3.5: 选物理意义最强 + 跟用户 TTS 差 ≤ 5s
# 判定：1.4/4.0 是绘本短句 + 双语领读型 = 物理意义最强的档
```

---

## 兜底公式（用户不给 TTS 时）

```python
def tts_estimate(narration):
    # 拆分中英
    en_words = count_english_words(narration)
    zh_chars = count_chinese_chars(narration)
    en_segments = en_words  # 英文按词数
    zh_segments = zh_chars  # 中文按字数
    
    # 标准慢速（兜底）
    en_rate = 1.0  # 词/秒
    zh_rate = 3.0  # 字/秒
    gap = 0.5  # 词间停顿
    
    total = en_segments / en_rate + zh_segments / zh_rate + gap * (en_segments + zh_segments - 1)
    return total
```

---

## 用户给 TTS = 视频总时长基准

```
用户给 TTS = 30s
  ↓
5 档对比选 1.4/4.0 = 30.46s（差 +0.46s ✅）
  ↓
视频总时长 = 用户给 TTS + 5s 冗余（默认）= 35s
  或 视频总时长 = 用户给 TTS（严格匹配，用户说"TTS 有冗余/严格匹配"）= 30s
```

### 用户说"严格匹配"或"TTS 有冗余" = 不加 5s

**判定口诀**：
- 用户说"TTS = 30s" → 默认 30 + 5 = 35s
- 用户说"严格匹配 TTS" / "TTS 有冗余" → 视频总时长 = 30s（不加 5s）

---

## 整数化（API 拒绝 7.5s）

```
旁白 4.2s → 向上取整 = 5s
旁白 6.7s → 向上取整 = 7s
旁白 7.5s → API 拒绝 → 8s
旁白 8.1s → 8s（已整数）
```

**约束**：duration ∈ [4, 15] 且必须为整数。

---

## 合并配方（多段旁白 = 1 Clip）

```python
def merge_segments_to_clip(segments, tts_rate=1.4):
    """
    输入：segments = [{text, language}, ...]
    输出：1 Clip 总时长
    """
    total = 0
    for seg in segments:
        if seg['language'] == 'en':
            total += len(seg['text'].split()) / tts_rate
        else:
            total += len(seg['text']) / 4.0  # 中文 4.0 字/秒
        total += 0.5  # 词间停顿
    return int(total + 0.5)  # 向上取整
```

---

## 实战案例（Run 跑 2026-06-16）

```
用户给 TTS = 28s
  ↓
5 档对比：
  - 1.0/3.0 = 41.67s（差 +13.67s ❌）
  - 1.4/4.0 = 30.46s（差 +2.46s ✅ 选这档）
  - 1.5/4.0 = 28.21s（差 +0.21s ✅ 但物理意义弱于 1.4/4.0）
  - 0.67/2.0 = 28.00s（数学拟合 ✅ 但速率无物理意义 ❌）
  ↓
选 1.4/4.0 档
  ↓
整数化：
  - Clip 1 段 1+2+3 = 9.10s → 9s
  - Clip 2 段 4 = 5.05s → 5s
  - Clip 3 段 5 = 5.20s → 5s
  - Clip 4 段 6 = 4.05s → 4s
  - Clip 5 段 7 = 4.10s → 4s
  - Clip 6 段 8 = 5.50s → 5s
  ↓
总时长 = 9+5+5+4+4+5 = 32s
  跟用户给 28s + 5s 冗余 = 33s 接近 ✅
```

---

## 反模式（必避）

| 反模式 | 后果 |
|---|---|
| 用 0.67/2.0 反推档 | 单项速率无物理意义（英文 1.5s/词异常慢）|
| 5 档对比不跑完 | 错过最优档 |
| 兜底公式不验证 | 跟用户 TTS 差 > 5s |
| 视频总时长 = 用户 TTS + 5s（用户说"严格匹配"）| 时长超过用户期望 |
| 视频总时长硬塞整数（不为整数化 + 0.5s 微动）| 整数化失败 |

---

## 跟铁律的对应

| 铁律 | 对应 |
|---|---|
| #5 画面时长匹配旁白时长 | Step 3.1-3.5 |
| #6 静默 = 编排工具不是义务 | 5s 冗余不是铁律，用户说"严格匹配" = 不加 |
| #7 1 故事 = 1 Clip | 合并配方（多段旁白 = 1 Clip）|
| #21 TTS 速率铁律（1.4/4.0 档）| 5 档对比 + 反推拟合反模式 |

---

## 自检命令

```bash
# 5 档必跑
for rate in "1.0 3.0" "1.4 4.0" "1.5 4.0" "0.67 2.0" "2.0 5.0"; do
  python3 scripts/tts_rate_calculator.py --rate $rate --input narration.txt
done

# 选档判定（差 ≤ 5s + 物理意义最强）
python3 scripts/select_best_rate.py --user_tts 28 --narrations_file narration.txt

# 整数化
python3 scripts/integerize_duration.py --durations 9.10 5.05 5.20 4.05 4.10 5.50
```
