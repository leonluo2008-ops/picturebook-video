# 声音策略分支（Sound Strategy Branches · v6 第 4 段声音维度微调）

> **铁律 #86 候选 · v1.0.3+pic13 新增**（Pic6 Cow 牛 clip7 实战沉淀 · 2026-06-08）
> 声音维度的"分支判断"·**不破坏 4 维控制底层核心**。
> **触发条件**：旁白 = 家族词组集合（≥3 词 + 同字母家族重复）OR 长句（英文 ≥ 5 词 / 中文 ≥ 8 字）

---

## 0. 为什么需要这个分支

**用户 2026-06-08 实战反馈原话**：
> "像这种家族词组的集合，在视频里不需要生成发音，用 TTS 音频来做对齐就可以了。...但是我并不想破坏底层核心啊，这只适合这种家庭词组，或者说句子很长的时候的一种方式。"

**根因**：
- seedance `--generate-audio true` 时会**自动生成拟声/朗读**作为参考音频层的补充
- 家族词组（cow, bow, now, how, wow）= 5 个独立音节 → seedance 容易**重复发/抢节奏/发音错位**（Pic6 clip7 v1 实测）
- 长句（>5 词）= 音节密度高 → seedance 容易**吞字/抢拍/语气错**
- 用户提供 TTS 音频时 = 已有准确音轨 → seedance 自动生成 = **冗余且翻车风险高**

**本分支目的**：
- 4 维控制底层核心**不动**（时间/风格/角色/声音 4 维照走）
- 仅在**声音维度**加一条"分支判断"——根据旁白类型选 seedance 音频生成策略
- 避免**重复发/抢节奏/发音错位**翻车
- TTS 音轨对齐 = 唯一声音源

---

## 1. 底层 4 维控制（不动）

| 维度 | 内容 | 是否修改 |
|---|---|---|
| **时间** | 节奏公式 v5/v6（朗读完最低 3s + 末帧静默 ≥ 2s）| **不动** |
| **风格** | 段 3 风格锁（v15 4 段 / v6 5 段结构）| **不动** |
| **角色** | 段 1 主体定义（视觉特征字典 + @ImageN）| **不动** |
| **声音** | 段 4 BGM 段 + 拟声 + 朗读策略 | **加分支** ← 本文件 |

---

## 2. 3 旁白类型 × 声音策略分支表

| 旁白类型 | 判定标准 | 声音策略 | 段 4 BGM 段写法 | 段 5 文字持续可见 | 拟声 |
|---|---|---|---|---|---|
| **普通短句/单词** | words_en ≤ 2 且 words_zh ≤ 4 | seedance **自动生成**发音（prompt 引导）| "无任何背景音乐、无旁白人声、无哼唱" | 全程可见 + 微动画 | 自由发挥 |
| **家族词组集合** | words_en ≥ 3 且 含同字母家族重复（OW/AY/EE 等） | **不生成发音** + TTS 音轨对齐 | 加"不发音·保留 TTS 音轨占位·时长匹配" | 全程可见 + 微动画 | **关闭** |
| **长句** | words_en ≥ 5 OR words_zh ≥ 8 | **不生成发音** + TTS 音轨对齐 | 加"不发音·保留 TTS 音轨占位·时长匹配" | 全程可见 + 微动画 | **关闭** |

**判定优先级**（从高到低）：
1. 家族词组集合（即使 < 5 词也算，如 AY 三词）
2. 长句
3. 普通短句/单词

---

## 3. seedance 命令差异

| 旁白类型 | `--generate-audio` | `--audio` 参数 | 段 4 prompt 写法 |
|---|---|---|---|
| 普通短句/单词 | `true` | 不传 | 引导拟声 + 单音节朗读 |
| 家族词组集合 | `false` | 传 TTS mp3 路径 | "不发音·保留 TTS 音轨占位·5 词顺序朗读·时长匹配 TTS 实测" |
| 长句 | `false` | 传 TTS mp3 路径 | "不发音·保留 TTS 音轨占位·完整朗读·时长匹配 TTS 实测" |

**Pic6 clip7 实战**：家族词组（cow, bow, now, how, wow 5 词）= `--generate-audio false` + 段 4 prompt 写"无任何背景音乐" → 视频跑通无重复发音 ✅

---

## 4. 触发条件判定（v6 fill 模板 B 旁白量化必填）

`narration-quantization.json` 每条记录加 `sound_strategy` 字段：

```json
{
  "id": 7,
  "en": "cow, bow, now, how, wow",
  "zh": "奶牛 cow 的 OW 家族...",
  "words_en": 5,
  "words_zh": 5,
  "sound_strategy": "family_word_set",  // ← 新字段
  "sound_strategy_rationale": "5 词同字母家族重复（OW）· 走分支·不生成发音+TTS 对齐"
}
```

**枚举值**：
- `single_word`：普通单词（COW! / moo! / bow!）
- `short_phrase`：普通短句（"A black and white cow."）
- `family_word_set`：家族词组集合（cow, bow, now, how, wow）
- `long_sentence`：长句（>5 词 / >8 字）

**判定逻辑**（B 子 agent / 主 agent 干 B 时必跑）：
```python
def detect_sound_strategy(words_en, words_zh, en_text):
    # 1. 家族词组集合判定
    if words_en >= 3:
        # 检测同字母家族重复（OW/AY/EE/AR 等）
        import re
        # 简单规则：3+ 词共用相同 2 字母结尾（如 -ow, -ay, -ee）
        words = [w.rstrip('!.,?') for w in en_text.lower().split(',')]
        suffixes = [w[-2:] for w in words if len(w) >= 2]
        if len(suffixes) >= 3 and len(set(suffixes)) == 1:
            return 'family_word_set'
    # 2. 长句判定
    if words_en >= 5 or words_zh >= 8:
        return 'long_sentence'
    # 3. 普通短句/单词
    if words_en <= 2 and words_zh <= 4:
        return 'single_word'
    return 'short_phrase'
```

---

## 5. 与 v6 fill 模板的衔接（暂未联动）

**v1.0.3+pic13 决策**（Pic6 实战）：

✅ **写 reference 文档**（本文件）— 沉淀判断逻辑
❌ **不**直接改 v6 fill 模板 — 等 Pic7/Pic8 实战验证"家族词组判定"准不准
⏳ **下本（Pic7/Pic8）实战后再考虑升格**为 B 字段联动 + fill 模板自动读字段

**理由**：
- OW 家族（5 词 + -ow 重复）= 典型家族
- AY/EE/AR 家族 = 实战未验证
- 判定规则可能反复调（OW 用"后 2 字母重复"，AY 也用，AR 结尾不同可能要改"含相同字母家族"广义规则）

---

## 6. Pic6 clip7 实战验证

| 维度 | 修复前（v1 默认）| 修复后（本分支）| 结果 |
|---|---|---|---|
| `--generate-audio` | true | false | ✅ 关闭拟声自动生成 |
| TTS 音轨 | 无 | 预留 | ✅ TTS 插入位明确 |
| seedance 5 词发音 | 易重复/抢节奏 | 不生成 | ✅ 干净 |
| 末帧微动（呼吸+OW 高亮+卡片上浮）| 受音频生成干扰 | 不受干扰 | ✅ 5 个微动元素 100% 保留 |
| 时长 10.10s | 设计 10s + ceiling 0.10s | 同 | ✅ 铁律 #72 整数 |

**用户反馈**：「clip7，本轮的 clip7，实际上非常好，就是符合我提供的时长，并且声音也符合需求。」

---

## 7. 反模式（不要做）

| 反模式 | 后果 |
|---|---|
| 把"不发音+TTS 对齐"作为默认策略 | 普通短句被剥夺拟声 = 翻车（"moo!" 单音节拟声是领读绘本灵魂）|
| 把"不发音+TTS 对齐"硬编码到 v6 段 4 模板 | 破坏模板通用性 · Pic5 Bird 等非家族词组也走静音 |
| 不分旁白类型一刀切 `--generate-audio false` | 全部静音 = 翻车（"moo!" 拟声 = 知识向核心）|
| 改 4 维控制底层核心 | 破坏通用框架 · 用户原话「不想破坏底层核心」|

---

## 8. 关联铁律 / 文件

- **picturebook-video/SKILL.md**：铁律清单 + 4 维控制原理
- **references/v6-5段骨架-模板.md**：v6 5 段结构定义
- **references/v15-4段骨架-模板.md**：v15 4 段结构定义
- **references/旁白朗读时长计算.md**：B 旁白量化公式
- **Pic6 Cow 牛 实战报告**（待写）：clip7 5 词设计 + 声音策略分支验证

---

## 9. 检索词

`声音策略分支` / `sound_strategy` / `家族词组集合` / `family_word_set` / `TTS 音轨对齐` / `不发音+TTS 对齐` / `4 维控制底层核心` / `铁律 #86` / `v1.0.3+pic13` / `Pic6 Cow clip7`
