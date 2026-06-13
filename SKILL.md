---
name: picturebook-video
description: "绘本转儿童动画视频的标准制作流程。接收绘本简介 + 图片 + 旁白 → 通读旁白标叙事弧合并到 3-5 Clip（导演分镜·不按图分段）→ fill v15/v6 5 段模板（B 档音效默认）→ seedance 提交 `--generate-audio true` + `--ref-images` 多图 → 端到端验证。默认 16:9 · 整数时长 · 3-5 Clip · 紧凑对齐 TTS（总时长 ≥ TTS）。触发词：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, storyboard, fill-v15, seedance, director-cut, ref-images]
  related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool, picturebook-creator]
  toolkit_role: picturebook-video-orchestrator
---

# picturebook-video · 绘本视频标准制作流程

> **当前唯一标准做法**——任何绘本按此跑。绘本做完 skill 不变（不在 SKILL.md 加铁律"XX 绘本踩坑"、不开新分支、不绑版本号、不绑绘本名）。

---

## 核心方法论（一句话）

**通读旁白 → 标叙事弧 → 合并到 3-5 Clip（导演分镜）→ fill v15/v6 模板 → seedance 跑出视频**

**4 个反直觉点**：
1. **不按图分段**（8 张图 ≠ 8 Clip）· 通读旁白后按叙事弧合并（导演分镜）
2. **默认 v15 4 段 / v6 5 段 + `--ref-images` 多图** · 不用首尾帧范式（除非用户明确指定）
3. **整数时长 + 紧凑对齐 TTS**（视频总时长 ≥ TTS 总时长）· 单 Clip 不超过 seedance 15s 物理上限
4. **绘本做完 skill 不动** · 全部产物在工作目录（`~/.hermes/profiles/huiben/work/<日期-绘本名>/`）

---

## 7 步标准流程

```
Step 1 · 接收需求（绘本简介 + 图片 + 旁白 + 目标平台）
   ↓
Step 2 · vision 自检关键页（1/N/中间/末页）+ 通读旁白
   ↓
Step 3 · 标叙事弧 → 合并到 3-5 Clip（导演分镜）
   ↓
Step 4 · 写 11 维 JSON（≤ 4 Clip 主 agent 直干 / > 4 Clip 调 C 子 agent）
   ↓
Step 5 · fill v15/v6 模板（段 4 B 档默认 + @Image 空格语法 + char_floats 动态）
   ↓
Step 6 · seedance 提交（--generate-audio true + --ref-images 多图 + 整数时长）
   ↓
Step 7 · 端到端验证 → 发飞书 + 完整证据链
```

---

## Step 1 · 接收需求

**必收 3 件事**：
1. **绘本简介**（故事简介 + 旁白文本）
2. **绘本图片**（本地路径 / 飞书云盘链接 / 附件 · PNG/JPG 都行）
3. **目标平台**（抖音 / 小红书 / 视频号 / B 站）

**文件用途澄清**（不解就问，不假设）：
- `*.mp3` → 问"TTS 干声 / 完整音频 / 不用？"
- `*.xlsx` → 读 schema 确认结构
- `0.jpg` → 问"封面 / logo / 不用？"
- `readme.txt` → 读内容，不当数据源

---

## Step 2 · vision 自检 + 通读旁白

**2.1 vision 必跑**（native vision）：

| vision 状态 | 动作 |
|---|---|
| 全成功 | 继续 |
| 部分失败 | 立即重试 1 张验证（临时过载 vs 真挂） |
| 全部失败 | **立即降级**——不依赖 vision，凭简介+兜底描述走主 agent 直干 |

**必看的 4 维**（缺 = prompt 拼错）：
1. 风格类型（彩纸拼贴 / 水彩 / 平面矢量 / 3D 毛毡 / 2D 卡通）—— 决定 prompt 风格词
2. 主体数量（1 颗 / 2 颗 / 1+鸟 / 1 小孩）—— 决定主体描述
3. 背景色调（米黄 / 青绿 / 草绿 / 混合）—— 决定 prompt 背景描述
4. 文字是否在画面（顶部 1/6 居中 / 散落 / 无文字）—— 决定是否让字母动画

**2.2 通读旁白 1 遍**：

把整本旁白读一遍，**标出叙事弧**（故事起伏）· 不要看图分段（**通读优先于按图**）。

**叙事弧模板**（3 弧）：
- 唤醒+观察 → 感知+行动 → 反馈+情感
- 引入 → 冲突 → 解决
- 看到 → 想到 → 做到

---

## Step 3 · 标叙事弧 → 合并到 3-5 Clip（**导演分镜**·核心步骤）

**核心原则**：
- **8 张图 ≠ 8 Clip**（通读旁白后**优先按叙事弧合并**，不按图机械分段）
- **3-5 Clip 是甜区**（太少 = 节奏快叙事空，太多 = 拖慢且每段没信息量）
- **导演分镜** = 镜头按故事推进组织，不是按"图 1 紧接着图 2"机械拼

**合并决策树**：

```
通读旁白 → 标叙事弧
   ↓
弧的数量 = N（N 通常 2-4）
   ↓
每个弧 = 1 个 Clip（每 Clip 装 1-3 张图）
   ↓
N=3 → 3 Clip（最常见·甜区）
N=4 → 4 Clip
N=2 → 2 Clip（极简绘本）
N>5 → 合并叙事弧到 5 Clip 以内
   ↓
每 Clip 时长 = 弧内 TTS 总朗读 + 1-2s 末帧静默
   ↓
总时长 = Σ 各 Clip 时长 = ≥ TTS 总时长
```

**实拍案例**（8 张图 4 段旁白 → 3 Clip 合并）：

| Clip | 涉及图 | 叙事弧 | 时长 |
|---|---|---|---|
| 1 | 1+2+3 | 唤醒+观察 | 10s |
| 2 | 4+5+6 | 感知+行动（软弹+闻香+吃）| 12s |
| 3 | 7+8 | 反馈+情感（美味+喜欢）| 10s |
| **总计** | 8 张全用 | — | **32s** |

**完整导演分镜 SOP + 通用叙事弧模板 + 旁白 TTS → 单 Clip 时长公式 + 何时不合并例外**：见 `references/director-cut-merge-recipe.md`。

**反模式**（必避）：
- ❌ 8 张图 = 8 Clip（按图机械分段 · 节奏碎）
- ❌ 16 张图 = 16 Clip（叙事弧被切碎）
- ❌ 8 张图 = 2 Clip（4 图 1 Clip = 镜头信息量爆炸）

---

## Step 4 · 写 11 维 JSON

**Clip ≤ 4**：主 agent 直干（不调子 agent）
**Clip > 4**：调 C 子 agent 产原料 JSON

**11 维 JSON 必填字段**（每 Clip 一个）：

```json
{
  "clip_id": 1,
  "image_files": {
    "first_frame": "1.jpg",
    "last_frame": "3.jpg"
  },
  "narration_text": {"en": "Mango! Look!", "zh": "芒果！看！"},
  "image_index": "1+2+3",
  "subject_definition": "single yellow mango character with smiling face",
  "background_description": "warm cream background with soft yellow gradient",
  "style_keywords": "2D cartoon, webtoon style, high saturation, warm colors",
  "shot_sequence": [
    {"start": 0.0, "end": 4.0, "shot": "camera holds on the smiling mango, gentle breathing pulse"},
    {"start": 4.0, "end": 8.0, "shot": "camera slowly pushes in, the mango waves a tiny hand"},
    {"start": 8.0, "end": 10.0, "shot": "final frame: the mango smiles brightly, soft warm light glows"}
  ],
  "end_frame_microaction": "the mango keeps gently breathing with a soft smile for 2s",
  "text_visibility": {
    "en_word": "Mango",
    "zh_word": "芒果",
    "color_en": "bright red",
    "color_zh": "鲜艳红色",
    "full_clip_visible": true,
    "micro_animation": "breathing pulse 0.5s/cycle + character-order float (M→a→n→g→o)"
  },
  "sound_strategy": "B"
}
```

**sound_strategy 档位**（声音维度分支·不破坏 4 维核心）：

| 档位 | 触发 | seedance 参数 | 段 4 写法 |
|---|---|---|---|
| **A** | 不使用（**不推荐·全静音翻车**）| `--generate-audio false` | — |
| **B 默认** | 普通短句/单词 | `--generate-audio true` | 无 BGM + 允许并保留画面元素动作音效 |
| **C** | 家族词组（≥3 同字母家族）/ 长句（words_en≥5）| `--generate-audio false` + `--audio tts.mp3` | 不发音·保留 TTS 音轨占位·时长匹配 |

---

## Step 5 · fill v15/v6 模板

**v15 4 段骨架**（默认·无文字持续可见需求）：

```
段 1 · 主体定义（含 @ImageN 引用 + 风格锚定词）
段 2 · 分镜绑定（@Image1 + @Image2 + @Image3 多图参考）
段 3 · 分镜描述（含拟声 + 镜头运动 + 末帧微动）
段 4 · 风格 + BGM（B 档默认 = 无 BGM + 允许音效 + 无朗读人声）
```

**v6 5 段骨架**（有顶部文字·领读型）：

```
段 1 · 主体定义
段 2 · 分镜绑定
段 3 · 分镜描述
段 4 · 风格 + BGM
段 5 · 文字持续可见段（全程可见 + 呼吸动画 + 字符顺序浮现）
```

**标准工具**：`scripts/fill_v15_template.py`（主 agent 必用·不手写 prompt）

**fill 完必查 4 项**（防止 fill 脚本 bug）：

| 检查 | 期望 |
|---|---|
| 0 双重前缀 | `grep -c "@Image@Image" clip*-prompt.txt` = 0 |
| @Image 空格语法 | `grep "@Image1 + @Image2 + @Image3" clip*-prompt.txt` ✅ |
| 段 4 B 档音效版 | 找 "无 BGM" + "音效" 字样（不是 A 档"无任何背景音乐、无旁白人声、无哼唱"）|
| char_floats 动态 | `grep "M(0.3s) → a(0.6s)" clip*-prompt.txt` ✅ 按 en_word 字母数生成 |

**一键验证脚本**（**主 agent 必用·不手敲 4 个 grep**）：

```bash
python3 ~/.hermes/profiles/huiben/skills/creative/picturebook-video/scripts/verify_filled_prompts.py <clips_dir>
```

退出码 0 = 4/4 全过 · 1 = 任 1 项失败。详细检查项 + 修复路径见 `references/verify-filled-prompts.md`。

---

## Step 6 · seedance 提交

**每 Clip 必传参数**：

```python
mcp_seedance_generate_video(
  prompt=<fill 出的 prompt 文本>,
  ref_images=["/abs/path/1.jpg", "/abs/path/2.jpg", "/abs/path/3.jpg"],
  duration=<整数 · 5-15>,
  ratio="16:9",
  watermark="none",
  generate_audio=True,  # B 档·B 档默认必传 true
  resolution="720p",
  model="doubao-seedance-2-0-fast-260128"
)
```

**关键约束**：

| 约束 | 规则 |
|---|---|
| 整数时长 | 设计时长 = 整数（5/6/7/8/9/10/11/12）· seedance 不生成小数 |
| 单 Clip 上限 | ≤ 15s（seedance 物理上限） |
| 视频总时长 | ≥ TTS 总时长（铁律·硬底线） |
| @Image 语法 | `@ImageN + @ImageM` 带空格（不带空格 = 错） |
| 多图参考 | `--ref-images`（不用首尾帧范式·除非用户明确） |

**单 Clip 端到端验证**（必走·铁律）：
1. 提交 1 个 Clip
2. 等 succeeded
3. 下载 + 本地 `md5sum` 验证
4. 发飞书用户目检
5. **等用户确认 OK** → 再批量跑剩下

**反模式**：
- ❌ 跑完 1 个 Clip 自动连跑剩下（没用户目检 = 翻车无拦截）
- ❌ 8 个 Clip 一次跑（D timeout 风险）
- ❌ 视频 < TTS（音频多出没画面 = 黑场翻车）

---

## Step 7 · 端到端验证 + 发飞书

**发飞书前必查**：

```bash
# 1. 本地 stat + md5
ls -lh clips/clip*.mp4
md5sum clips/clip*.mp4

# 2. 验证整数时长（ffprobe）
for f in clips/clip*.mp4; do
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f"
done
```

**发飞书模板**：

```
[绘本名] 视频已生成：

[MEDIA:/abs/path/clips/clip1.mp4]
[MEDIA:/abs/path/clips/clip2.mp4]
[MEDIA:/abs/path/clips/clip3.mp4]

📊 元数据：
• 总时长：32s（3 个 Clip · TTS 30s + 2s 末帧）
• md5 唯一 0 错位
• 整数时长 100% 命中
• 涉及图：8 张全用

需要我改什么吗？
```

**核心原则**：
- ✅ 一次发完整组视频（不拆开发）
- ✅ 必附完整证据链（md5 + task_id + 涉及图）
- ✅ 不主动抽帧自检（vision 是辅助不是真理·等用户目检）
- ❌ 不发飞书云盘兜底链接（用户没要求）

---

## 7 类必走（不可省）

| # | 步骤 | 不可省原因 |
|---|---|---|
| 1 | 通读旁白 1 遍 + 标叙事弧 | 防止按图分段=8 Clip 翻车 |
| 2 | vision 抽 1/N 关键页 | 防止主体数量/背景色/文字位置 凭印象拼错 |
| 3 | 主 agent fill 完必查 @Image 语法 4 项 | 防止双重前缀 + char_floats 硬编码 + 段 4 误用 A 档 |
| 4 | 提交 seedance 必传 `--generate-audio true` | 防止 v1 全静音翻车（B 档默认）|
| 5 | 单 Clip 端到端验证 + 用户目检 | 防止跑完 4 个 Clip 才发现在 v1 错 |
| 6 | 视频总时长 ≥ TTS 总时长 | 防止黑场翻车（铁律·硬底线） |
| 7 | fill_v15_template.py 主 agent 必用·不手写 prompt | 防止 prompt 写法 drift |

---

## 7 类反模式（必避）

| 反模式 | 触发 | 修复 |
|---|---|---|
| ❌ 8 张图 = 8 Clip | 收到绘本直接按图分 | 通读旁白 → 标叙事弧 → 合并到 3-5 Clip |
| ❌ 视频 < TTS | 按范式默认档位算总时长 | 视频总时长 = max(范式总时长, TTS)·取大不取小 |
| ❌ 全静音翻车 | fill 脚本段 4 写"无 BGM/无人声/无哼唱" | 改 B 档默认："无 BGM + 有音效" |
| ❌ `@Image@Image1+2` 双重前缀 | fill 脚本拼错 | 查 4 项 · 空格语法 · 必删双重前缀 |
| ❌ `@Image1+@Image2` 无空格 | 拼 ref 时漏空格 | 带空格：`@Image1 + @Image2 + @Image3` |
| ❌ 5.5s/4.3s 小数时长 | 按朗读时长反推 Clip 时长 | 整数（5/6/7/8/9/10/11/12）· seedance 不生成小数 |
| ❌ 跑完 1 个 Clip 自动连跑 | 没等用户目检 | 单 Clip → 发飞书 → 等目检 → OK 再批量 |

---

## 调性 / 范式 / 约束（默认 vs 备选）

| 项 | 默认 | 备选 | 触发备选 |
|---|---|---|---|
| 画幅 | 16:9 | 3:4（小红书） | 用户说小红书 |
| 范式 | v15 4 段（叙事型）| v6 5 段（领读型·有文字持续可见）| 顶部 1/6 有彩色文字 |
| 范式 | v15 4 段 | v7 首尾帧（`--image`+`--last-frame`）| 用户明确说"走首尾帧" |
| 声音档位 | B（普通短句） | C（家族词组/长句）| ≥3 同字母家族词 或 words_en≥5 |
| 段 4 BGM | 无 BGM + 有音效 | 有 BGM（用户指定）| 用户说"要 BGM" |
| 整数时长档位 | 6/7/8/10/12 | 5/9/11 | 短句 5s / 长句 14s |
| 总时长 | 紧凑对齐 TTS（TTS+5-7s）| 严格匹配 TTS | 用户说"视频=TTS 严格匹配" |
| Clip 数 | 3-5（甜区） | 2-6 | 极简绘本 2 / 大绘本 6 |

---

## 绘本做完 = 不动 skill（最重要·元教训）

> 用户原话（2026-06-13）："**绘本做完不要在 skill 里加版本号**" + "**绘本做法规范到 skill 里作为标准的制作流程**" + "**不要有太多分支/版本**" + "**不要再开新分支**"

**绘本完成 = 全部产物在工作目录（`~/.hermes/profiles/huiben/work/<日期-绘本名>/`）· skill 不变**：

- ❌ **不**在 SKILL.md 加铁律"v1.0.5+picXX · XX 绘本踩坑"
- ❌ **不**在 references/ 加 `2026-06-XX-绘本名-validation.md`
- ❌ **不**修改 fill 脚本（除非发现通用 bug）
- ❌ **不**开新 git 分支
- ❌ **不**在 SKILL.md / fill 脚本注释 / 铁律名出现特定绘本名
- ✅ **可以**在 work/<日期-绘本名>/ 加本绘本专属笔记（业务文档·不入 skill）
- ✅ **可以**清理 work 旧绘本残留（每绘本完成一周后）

**反问自检**："这个铁律是因为某本绘本踩坑，还是因为通用方法论？"
- **通用方法论** → 加铁律（不绑绘本名）
- **某本绘本踩坑** → work/<日期-绘本名>/ 写笔记，不加 skill

---

## 与子 agent 的关系

主 agent **必做**：
- ✅ 验证子 agent 输出 schema
- ✅ 持久化子 agent 输出到磁盘
- ✅ 翻车时决定重发哪个子 agent
- ✅ 接受/降级决策
- ✅ 端到端验证 + 用户目检

主 agent **不做**：
- ❌ 拼 prompt（用 `scripts/fill_v15_template.py` 填模板）
- ❌ 跑视频（用 `seedance.py` 或 `mcp_seedance_generate_video`）
- ❌ 抽帧验证（vision 是辅助不是真理·等用户目检）
- ❌ 凭印象选节奏（按叙事弧合并 + 整数时长档位表）

**4 个子 agent**（不直接调，记下来即可）：

| Agent | 职责 | Skill |
|---|---|---|
| **A · 风格识别** | 调性 + 节奏倾向 + 风格锚定词 | `storyboard-style` |
| **B · 旁白量化** | 朗读时长 + 复杂度 + 静默推荐 | `storyboard-narration` |
| **C · 分镜设计** | 节奏公式 + 镜头表 + 11 维 JSON | `storyboard-design` |
| **D · 视频执行** | seedance 跑 + 抽帧 + vision 自检 | `video-executor` |

**默认调用规则**：
- Clip ≤ 4：主 agent 直干（不调 C）
- Clip > 4：调 C 子 agent
- A + B 始终主 agent 干（纯计算/少量 vision）

---

## 工具位置

- **fill 模板脚本**：`scripts/fill_v15_template.py`（v15 4 段 / v6 5 段自动切换）
- **fill 后必跑验证**：`scripts/verify_filled_prompts.py`（4 项关键检查·一键验证）
- **时长校验**：`scripts/validate_durations.py`（整数时长 + 末帧静默阈值）
- **敏感词检查**：`scripts/check_sensitive_words.py`（`OutputVideoSensitiveContentDetected` 防护）
- **seedance 调用**：MCP `mcp_seedance_generate_video` / 兜底 `seedance2.0-tool/seedance.py`
- **图床**：uguu.se 优先（chevereto 兜底·已挂）

---

## 维护陷阱（绘本完成后必看）

| 陷阱 | 反模式（**必去绘本名/版本号占位**）| 修复 |
|---|---|---|
| 1. skill 装绘本"版本号" | 在铁律名里嵌入"`v\d+\.\d+\+pic\d+`"或"XX 绘本踩坑"等字样 | 铁律以**通用方法论**命名·反问自检："这条铁律是某本绘本踩坑还是通用方法论？" → 仅后者入 skill |
| 2. 开新 git 分支做"实验" | 每本绘本 = 新分支（`{绘本名}-Nclip-{vX.X+picN}` 模式）| 沿用现有 fix/feature 分支累加 commit |
| 3. 1 个 commit = 1 个完整变更单元 | N 个半成品 commit | 本轮工作 = 1 个 commit·message 列出"通用方法论 + fill 脚本 bug 修复" |
| 4. 子 agent 累积未提交修改 | `git status` 满屏 `M` / `??` | 开工前必先 `git status`·要么 commit 要么 stash |

**自检命令**（绘本完成后必跑 0 残留验证）：

```bash
# 1. SKILL.md 内 0 绘本名残留
grep -E "特定绘本名" SKILL.md scripts/*.py references/*.md templates/*.md assets/example-prompts/*.txt
# 期望：无任何输出

# 2. SKILL.md 内 0 v\d+\.\d+\+pic\d+ 标签
grep -E "v[0-9]+\.[0-9]+\+pic[0-9]+" SKILL.md scripts/*.py references/*.md templates/*.md
# 期望：无任何输出（反例占位也用 `v\d+\.\d+\+pic\d+` 通用占位符）
```

**反例教学的正确写法**（示范）：

```markdown
# ❌ 错：绑了具体绘本名和版本号
**#110**（v1.0.5+pic32 实战新增 · 某绘本踩坑 ...）
每本绘本 = 新分支（`某绘本-4clip-v1.0.5+pic37` 等）

# ✅ 对：用通用占位符
**#110**（绘本踩坑实战新增）
每本绘本 = 新分支（`{绘本名}-Nclip-{vX.X+picN}` 模式）
```

---

## 相关 skill

- **绘本创作**：`picturebook-creator`（静态绘本）
- **分镜子 agent**：`storyboard-style` / `storyboard-narration` / `storyboard-design` / `video-executor`
- **视频工具**：`seedance2.0-tool`（底层 seedance 兜底脚本）
- **4-skill 工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`
