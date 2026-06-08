# Pic6 Cow 牛 实战验证（v1.0.3+pic13）

> **2026-06-08 · 8/8 succeeded · 0 错位 · 58.66s**
> 调性：A 知识向·欢快轻松
> 范式：v6 5 段（v15 4 段 + 文字持续可见段）
> 铁律闭环：#50 / #72 / #75 / #85 / #86 新增 / #87 新增

---

## 0. 实战背景

**绘本**：Cow 牛 · 8 页双语启蒙绘本（领读型 · 知识向）
**素材包**：8 张原图（/tmp/cow_extract/1.jpg ~ 8.jpg）+ 故事简介.txt
**用户 TTS**：~50s · 用户主动拆分 OW 家庭（Clip 7）· 最终 8 段实测节奏稳定
**目标平台**：抖音/视频号/B 站（16:9）

---

## 1. 端到端流程

```
Step 0    · 接收 cow.tar 素材包（解压 /tmp/cow_extract/）
   ↓
Step 0.5  · 场景对位检查（vision 抽 1/3/5/8 关键页 4/4 100% 命中）
   ↓
Step 1    · 启动前 7 必问（用户拍板调性 = A 知识向·欢快轻松）
   ↓
Step 2    · A 风格识别（4.40/5 加权分）+ B 旁白量化（58s 总时长 / 8 Clip）
   ↓
Step 3    · C 分镜设计（产 8 份"原料" JSON + storyboard-index）
   ↓
Step 4    · 主 agent 填 v6 模板（fill_v15_template.py --version v6 --tone "知识向·欢快轻松"）
   ↓
Step 4.5  · 单 Clip 端到端先验（clip1 + clip7 跑通）→ 用户目检 OK
   ↓
Step 4.6  · 6 段批量并行（≤2/批 + 主 agent 续跑模式）→ 6/6 succeeded ~3min
   ↓
Step 5    · 汇总发飞书（8 视频 + 完整证据链）
```

---

## 2. 8 Clip 时长设计 vs 实跑

| Clip | 旁白 | 档位 | 设计 | 实跑 | md5 简码 |
|---|---|---|---|---|---|
| 1 | COW! | 极短 | 5s | 5.09s | 6effd50b... |
| 2 | A black and white cow | 长句 | 8s | 8.08s | 7f8d52e4... |
| 3 | The cow says moo | 中句 | 7s | 7.08s | 29c7fb22... |
| 4 | The cow eats grass | 中句 | 7s | 7.08s | f47dbab7... |
| 5 | The cow swishes flies | 长句 | 8s | 8.08s | b98b106f... |
| 6 | The cow gives milk | 中句 | 7s | 7.08s | 3313c876... |
| 7 | cow, bow, now, how, wow（5 词拆解）| OW-拆解 | 10s | 10.10s | 1af391c3... |
| 8 | Count the cows | 短句 | 6s | 6.06s | 420216d7... |

**总时长**：58.66s（设计 58s · +0.66s ceiling 容差）
**整数时长铁律 #72**：8/8 实跑 = 设计（0 错位）
**md5 唯一性**：8/8 唯一（Pic2 6/8 错位教训闭环）

---

## 3. 用户对 Clip 7 的 3 轮纠错（v1.0.2+pic11 / v1.0.3+pic13 实战沉淀）

### 3.1 用户纠错 1：OW 家庭需要拆分

**用户原话**：「Clip 7 要做时长调整。Clip 7 是集合的词组，家庭词组拆解。那么说每一个词念完之后，要有足够的消化时长。请你重新设计 Clip 7」

**修复方向**：v6 整数档 + 每词消化时长
- 朗读 0.7s + 消化 ≥ 3s + 末帧 ≥ 2s = 5.7s/词
- v6 整数档：**6s / Clip**（单词）
- 5 词 × 6s = 30s 总视频时长

### 3.2 用户纠错 2：Clip 7 总上限 15s

**用户原话**：「Clip 7 总共时限，上限为 15 秒。你根据时长来分拆几个词组所出镜的时长和动画」

**修复方向**：放弃单词单 Clip 方案，5 词合并 1 Clip
- 朗读 4.5s（5 词 × 0.7s + 0.3s 间隔）+ 末帧 5.5s
- v6 整数档：**10s / Clip**

### 3.3 用户纠错 3：TTS 音频对齐 = 不生成发音

**用户原话**：「像这种家族词组的集合，在视频里不需要生成发音，用 TTS 音频来做对齐就可以了」

**修复方向**：声音策略分支（铁律 #86 候选）
- `--generate-audio false` + TTS 音轨对齐
- 段 4 写"不发音·保留 TTS 音轨占位"
- 关闭拟声
- 4 维控制底层核心不动（仅声音维度加分支）

**Pic6 clip7 实战结果**：
- ✅ 视频跑通 0 重复发音
- ✅ 末帧微动 100% 保留（呼吸式放大缩小 + OW 字母脉动 + 6 卡片上浮回落）
- ✅ 时长 10.10s = 设计 10s（铁律 #72 整数）
- ✅ 用户目检通过：「clip7，本轮的 clip7，实际上非常好，就是符合我提供的时长，并且声音也符合需求」

---

## 4. 关键翻车 & 修复

### 4.1 fill_v15_template.py 硬编码 bird/鸟（铁律 #75 复发）

**翻车**：clip1-prompt 段 5 文字持续可见段硬编码了 "bird" / "鸟"（Pic5 Bird 残留数据）

**根因**：
- `_build_text_visibility_segment()` 兜底 `tp.get('en_word', 'bird')` 写死
- 主 fill 函数兜底 `tp.get('zh_word') or '鸟'`
- C 子 agent 输出 clip JSON 没填 `en_word`/`zh_word` 字段 → 走兜底 → 全变 bird/鸟

**修复（v1.0.3+pic13）**：
```python
# 修复 1: _build_text_visibility_segment 增加 fallback 参数
def _build_text_visibility_segment(tp, target_word, en_word_fallback='', zh_word_fallback=''):
    en_word = tp.get('en_word') or en_word_fallback or ''
    zh_word = tp.get('zh_word') or zh_word_fallback or ''

# 修复 2: 主 fill 函数兜底从 narration 提取
en_word = tp.get('en_word') or clip['narration_text'].get('en', '').split()[-1].rstrip('!.,?')
zh_word = tp.get('zh_word') or clip['narration_text'].get('zh', '').split()[-1].rstrip('!.,?，！？。')

# 修复 3: 调用方传 fallback
variables['text_visibility_segment'] = _build_text_visibility_segment(
    tp, clip.get('target_word_emphasis', {}).get('word', en_word),
    en_word_fallback=en_word, zh_word_fallback=zh_word
)
```

**验证**：`grep "bird\|鸟" clip*-prompt.txt` → ✅ 0 残留

### 4.2 主 agent 主动抽帧自检（铁律 #87 新增 · 用户纠错）

**翻车**：clip1 跑通后我主动用 `vision_analyze` × 3 帧自检（t=0.5/2.5/4.5），输出"vision 自检 3 帧"段给用户看

**用户原话（2026-06-08 明确纠错）**：
> 「clip1 视频没有问题，你以后不要主动抽帧检查，直接把视频发给我就行了。」

**修复方向（铁律 #87）**：
- 主 agent 跑完 D → **直接发视频** → 等用户目检（不抽帧自检）
- `vision_analyze` 只在 vision 跟人眼观感不一致时由用户主动要求才用
- 跟铁律 #29 协同：#29 不抽帧发飞书 / #87 不抽帧填表

### 4.3 zh_word 兜底非真实文字（铁律 #62 沉淀）

**翻车**：clip7-prompt 段 2 zh_word = "大集合"（脚本从 narration.zh 最后词提取）= 实际原图是"OW 家族"

**根因**：B 子 agent 输出的 narration_text.zh 最后词 ≠ 原图真实文字

**未阻塞**：seedance 实际跑出来效果不受 zh_word 兜底影响（兜底值仅用于字符顺序浮现提示）

**修复方向（暂未联动）**：
- v1.0.3+pic13 决策：先在 sound-strategy-branches.md 写判定逻辑
- B 字段联动延后到 Pic7/Pic8 实战后再考虑

---

## 5. 实战数据对比表

| 维度 | Pic2 (Please) | Pic3 (Welcome) | Pic4 (No) | Pic5 (Bird) | **Pic6 (Cow)** |
|---|---|---|---|---|---|
| 页数 | 8 | 9 | 9 | 8 | **8** |
| 调性 | 警示向·温柔坚定 | 警示向·慈爱守护 | 警示向·温柔坚定 | 知识向·好奇探索 | **知识向·欢快轻松** |
| 场景对位 | 6/8 | 9/9 | 9/9 | 8/8 | **8/8** |
| 整数时长 | 错位 | 全对 | 全对 | 全对 | **全对** |
| D 任务数 | 8 | 9 | 9 | 8 | **8** |
| md5 错位 | 6/8 | 0/9 | 0/9 | 0/8 | **0/8** |
| 视频总时长 | 47s | 45s | 56s | 50.66s | **58.66s** |
| 并行轮询 | ≤3/批 | ≤2/批 | ≤2/批 | 8 并行 | **6 并行** |
| 端到端耗时 | ~33min | ~18min | ~25min | ~7min | **~12min** |
| 单 Clip 端到端 | clip1 | clip1 | clip1 | clip1 | **clip1+clip7** |
| v15.2 收势 | 6s 3 镜头 | 6s 3 镜头 | 11s→6s 修复 | 6s 3 镜头 | **6s 3 镜头** |
| 翻车点 | 主体丢失/文字消失 | 0 错位 | v3 温柔化 | bird 硬编码 | **bird 残留/抽帧自检** |
| 新增铁律 | #50-#55 | #56-#58 | #59-#71 | #72-#85 | **#86-#87** |

---

## 6. 6 段批量并行实战（铁律 #85 验证）

**Pic5 Bird 8 段 8 并行 ~7min 完成**（铁律 #85 实战新增）
**Pic6 Cow 6 段 6 并行 ~3min 完成**（进一步优化）

**实测数据**：
- 6 个 task 串行提交耗时：~67s
- 6 个后台轮询并行启动
- 6/6 succeeded 用时：~3min
- 单 Clip 平均：~30s/段
- 比 Pic2 v1.0.0 串行快 ~5x

**边界**：
- D 纯生成（不抽帧不 vision）= 8 并行可行
- D + 抽帧 + vision = 仍走 ≤2/批

---

## 7. 用户纠错沉淀（Pic6 实战）

| # | 纠错 | 沉淀位置 |
|---|---|---|
| 1 | OW 家庭需要拆分 | 实战报告 §3.1（v6 整数档 + 消化时长）|
| 2 | Clip 7 总上限 15s | 实战报告 §3.2（5 词合并 1 Clip）|
| 3 | 不生成发音+TTS 音轨对齐 | 铁律 #86（声音策略分支）+ references/sound-strategy-branches.md |
| 4 | 不主动抽帧自检 | 铁律 #87（主 agent 跑完 = 发视频 = 不自检）|
| 5 | "你给我建议"（A 选项） | SOUL.md 决策权默认归我（沿用 2026-06-03 纠错）|

---

## 8. 关联铁律 / 文件

- **picturebook-video/SKILL.md**：铁律清单 + 4 维控制原理
- **references/v6-5段骨架-模板.md**：v6 5 段结构定义
- **references/sound-strategy-branches.md**：声音策略分支（v1.0.3+pic13 新增）
- **references/emotion-tone-ai-judgment-standard.md**：4 维加权调性判定标准
- **references/2026-06-07-pic3-welcome-validation.md**：Pic3 实战对照
- **references/2026-06-07-pic4-no-validation.md**：Pic4 实战对照
- **references/2026-06-07-pic5-bird-validation.md**：Pic5 实战对照

---

## 9. 检索词

`Pic6 Cow 牛` / `v1.0.3+pic13` / `声音策略分支` / `铁律 #86` / `铁律 #87` / `fill_v15 硬编码 bird/鸟 修复` / `OW 家庭拆解` / `8/8 succeeded 0 错位` / `6 并行轮询 3min` / `58.66s 整数时长`
