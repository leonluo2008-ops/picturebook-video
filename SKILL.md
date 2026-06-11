---
name: picturebook-video
description: "绘本转儿童动画视频一站式调度 skill（**v1.0.3+pic14 · Horse 绘本 5/5 succeeded 端到端实战验证**）。把绘本简介 + N 张图 + 旁白 → **Step 0 文件用途澄清** → **Step 0.5 场景对位检查** → **Step 1 启动前 7 必问 + #1.5 数字约束数学验证** → 调 A 风格识别 + B 旁白量化（主 agent 干 · 并行）→ **Step 3.0 范式路由**（v7 2图=1Clip 走主 agent 直拼 / v15 4 段走 C 子 agent）→ C 子 agent 产 11 维原料（**不写 prompt_draft**）→ **主 agent 填 v15/v6 模板 + 铁律 #93 自动拆 `@Image1+2` → `@ImageN` / `@ImageN + @ImageM`** → **Step 4.0 seedance 范式二选一**（v15 走 `--ref-images` / v7 走 `--image`+`--last-frame`）→ D ≤2/批 + 续跑 → 发飞书 + 完整证据链（铁律 #76）。**v1.0.3+pic12 实战新增**：v5 节奏公式（朗读完最低 3s + 末帧静默 ≥ 2s）+ v6 整数时长铁律（seedance 不生成小数时长）+ 彩色文字全程可见铁律（领读锚点不可一闪而过）+ uguu 兜底路线（chevereto 挂时备用）+ **9 条新铁律**（#63-#71）。**触发词**：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent, picturebook, v15-template, fill-v15, uguu-fallback, send-message-evidence, integer-duration, text-anchored-reading, v7-paradigm, 2-clip-merge]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool]
    toolkit_role: picturebook-video-orchestrator
    version: 1.0.5
    breaking_changes_from_v1.0.3:
      - "**v7 范式强路由**——领读/认知/认字绘本走 v7 2图=1Clip 合并（主 agent 直拼·不调 C）· v15 4 段留给单图叙事绘本"
      - "**8s 不是上限**——v5 公式档位 5/6/7/8s 是参考范围 · 真正上限 seedance 15s 物理边界（8s < x ≤ 15s 合法）"
      - "**MP3 用途必问**——用户给 MP3 不默认 TTS（不问 = 走兜底公式 1.4 词/秒）"
      - "**用户硬约束冲突老实报告**——3 数字约束物理装不下时 = 给 3 选 1 · 不硬凑\"末帧 < 1s 翻车征兆\"方案"
    breaking_changes_from_v1.0.2:
      - "**9 条新铁律（#63-#71）**——Pic4 No 不绘本实战沉淀（v3 情绪温柔化 + v5 节奏两步推导 + v6 整数时长 + 彩色文字全程可见）"
      - "**uguu 兜底路线**——chevereto 图床挂了时备用（uguu.se + 直接 curl 调 ark API）"
      - "**send_message 防串扰**——发视频前必本地 stat+md5+消息里显式打文件名+md5+task_id"
      - "**fill_v15 模板脚本统一**——fill_v15_v3.py / v5.py / v6.py 归一为 scripts/fill_v15_template.py（含 _parse_en_color 数据清洗）"
---

# picturebook-video · 绘本视频调度中枢（v1.0.3+pic13 · 领读绘本稳定版 tag v2.0）

## 安装说明

> **新机器首次安装**：见 [INSTALL.md](INSTALL.md)（v2.0 · 12 章节 · 100% AI 自动化安装）
> **含**：系统依赖 + 3 必装 skill 仓 + 3 可选 skill 仓 + 2 必填 env + 验收测试 + 7 类故障排查 + 升级回滚

## 身份

你是 **绘本视频工作流的调度中枢**。**不直接干活**——只做：

1. 接收需求（绘本 + 图 + 旁白）
2. 启动前 6 必问（确认比例/时长/切分/调性/范式/约束）
3. **并行**调起 A 风格识别 + B 旁白量化
4. 合并 A+B 输出 → 调起 C 分镜设计
5. 接收 C 输出 → 调起 D 视频执行
6. 汇总 D 输出 → 决定是否发飞书

**4 个子 agent**（不直接调，记下来即可）：

| Agent | 职责 | Skill |
|---|---|---|
| **A · 风格识别** | 调性 + 节奏倾向 + 风格锚定词 | `storyboard-style` |
| **B · 旁白量化** | 朗读时长 + 复杂度 + 静默推荐 | `storyboard-narration` |
| **C · 分镜设计** | 节奏公式 + 镜头表 + v15 prompt 草稿 | `storyboard-design` |
| **D · 视频执行** | seedance 跑 + ffmpeg 抽帧 + vision 自检 | `video-executor` |

**子 agent 详细规范**：见 `agents/<agent>/SKILL.md`

---

## 调度流程（5 步）

```
Step 0 · 接收需求
   ↓
Step 1 · 启动前 6 必问（必跑）
   ↓
Step 2 · 调 A + B 并行（delegate_task）
   ↓
Step 3 · 调 C · 分镜设计（**先看 Step 3.0 范式路由** · v7 不调 C）
   ↓
Step 4 · 调 D（可能 N 次重试 · 2 个/批 + 主 agent 续跑）
   ↓
Step 5 · 汇总 + 决定发不发飞书
```

---

## 🔥 决策时必看的新铁律速查（v1.0.4 · Horse 绘本实战沉淀）

> **触发任何"约束冲突 / 范式选错 / MP3 用途不决 / 总时长装不下"时，必看下面 4 条**：

| 铁律 | 何时必看 | 核心一句话 |
|---|---|---|
| **#89** | 收到"领读型绘本 + 想合并段 + 不调 C" | **v7 范式 = 领读型 2图=1Clip 合并 = 主 agent 直拼 = 不调 C**（不调 v15 C 强套） |
| **#90** | 看到 14s/13s/12s 等长于默认 8s 的 Clip | **8s 默认档位 ≠ 上限 · 真正上限 seedance 15s · 8 < x ≤ 15s 合法** |
| **#91** | 用户给 MP3 / xlsx / readme.txt 等文件 | **文件用途必问不自动假设**（MP3 不默认 TTS · xlsx 必读 schema 确认结构） |
| **#92** | 用户给多个硬约束（总时长 + 单段时长 + 段数）| **3 数字约束物理装不下 = 老实报告 3 选 1 · 不硬凑"末帧 < 1s"翻车方案** |
| **94**（v1.0.5+pic14 新增 · 2026-06-09 Pic7 Horse R7 翻车）| 拼任何 v15/v6 段 2/段 4 prompt 时 | **v15 4 段 / v6 5 段骨架结构不能乱**：① 段 2 不写"朗读 X 词"指令（触发 seedance 必生成朗读 = 家族词组 5 词 = 5 次独立朗读 = 抢节奏 + 错乱）② 段 4 只写声音策略兜底句（不展开具体音效清单）③ 段 2 文字保留 = 1 段独立约束（不复制 2 遍） |
| **95**（v1.0.5+pic15 已被 v1.0.6+pic16 撤销 · 2026-06-09 Pic7 Horse R7 第三轮翻车）| ~~填 v15/v6 模板时**~~  | ~~fill 模板必自动脱敏 C action 里的具体单词/图标名~~  | **撤销原因**：v1.0.5 脱敏是**矫枉过正**——Cat 跑通的真实范本（`assets/example-prompts/cat-clips-1-6-v15.1.txt`）里**根本没有"脱敏"概念**。Cat 范本段 2 镜头里直接写"镜头定格在 cat 卡片，叮 一响，猫转头看向卡片（朗读 1s + 静默 2s 停留，镜头停在画面上让听众消化单词）"——C 写的"cat 卡片"被原样保留 + 视觉动作 + 拟声嵌入 + "朗读 1s"占位时长（不写"朗读 cat"）。**真根因不是"prompt 写具体单词"**——而是 v1.0.5 之前 fill 模板的 `narration_marker = f'+朗读 "{target_word}"'` 写法 + v1.0.5 矫枉过正的"目标词"标识都**破坏了 Cat 范本的真实结构**。**v1.0.6 Cat 范式回滚**：① 撤销 v1.0.5 `sanitize_action()` 脱敏映射 ② C agent action 字段**原样保留**（"fork 卡片"/"horn 卡片"等 C 看图合理推断保留）③ `narration_marker` 改 Cat 风格"（朗读 Ns + 静默 Ns 停留）"（不写具体目标词）④ 段 4 BGM 段**回 A 档**（Cat 范本里就是"无任何背景音乐、无旁白人声、无哼唱"）⑤ 段 2 拟声嵌入视觉句用 `,` 串接（"图标浮现 叮咚 一响"）。**判断口诀**："**照搬 Cat 范本 · 不瞎改 · 不加脱敏 · 不加 B 档矫枉过正**"。**真规范**：`scripts/fill_v15_template.py` `build_shot_sequence` v1.0.6+pic16 版本。详细实战数据见 [references/2026-06-09-pic7-horse-validation.md](references/2026-06-09-pic7-horse-validation.md) §3 翻车 3。 |
| **96**（v1.0.6+pic16 新增 · 2026-06-09 Pic7 Horse R7 实战沉淀 · Cat 范式回滚铁律）| 看到"段 2 拼"+朗读 X"" 或 fill 模板加脱敏映射等"额外加工"时 | **照搬 Cat 跑通范本**（`assets/example-prompts/cat-clips-1-6-v15.1.txt`）· **不**瞎改段 2 结构。**Cat 范本 4 段固定结构**：① 主体定义（含 C 写"cat 卡片"等具体单词·原样保留）② 分镜绑定（`@图N`/`@图M` 多图参考）③ 镜头序列（**写"（朗读 1s + 静默 2s 停留，镜头停在画面上让听众消化单词）"**——不写"朗读 cat"——seedance 看到"朗读 1s"知道要留时间但不强制生成具体朗读）④ 段 4 写 A 档兜底句"无任何背景音乐、无旁白人声、无哼唱"。**5 个常见反模式**（Pic7 三轮翻车沉淀）：① ❌ 段 2 拼"+朗读 'X 词'" ② ❌ fill 加脱敏映射（v1.0.5 矫枉过正）③ ❌ 段 4 加"具体音效清单"（"卡片高亮配叮..."v1.0.4 矫枉过正）④ ❌ 段 4 改"画面元素动作音效保留..."（v1.0.4 B 档矫枉过正）⑤ ❌ 段 2 文字保留复制 2 遍到段 5。**判断口诀**："**Cat 跑通的样子 = 标准答案 · 改了大概率翻车**"。**修复路径**：删所有额外加工 → 改回 Cat 范本 4 段结构 → 重跑。|

**反模式速查**（v1.0.4 Horse 绘本实战翻车清单）：
- ❌ 看到 14s → 报"超出 8s 必拆 v15.1"（**真相：14s 合法单 Clip**）
- ❌ 把 MP3 自动当 TTS 抽时长（**真相：完整音频 90.15s 零静音**）
- ❌ 调 C 子 agent 拼 v7 prompt（**真相：C 只懂 v15 4 段，v7 必须主 agent 直拼**）
- ❌ 装 8 段 4.29s 朗读 + 1 段 14s + 总 43s（**真相：物理装不下，5 段末帧 0.71s**）

**完整实战数据**见 `references/v7-vs-v15-paradigm-routing.md`

**Step 0.5 · 绘本场景对位检查（v1.0.2 新增 · 铁律 #56）**

在调 C 之前，**主 agent 必跑**这步（不交子 agent）：

```python
# 用 native vision 抽每张图 t=0.5s 帧，验证：
# 1) 原图场景跟旁白对位（防 pic2 clip6 玩具房当 eat 翻车）
# 2) 收势页是否真的"全员集合"（防 pic2 clip8 误用图书馆当收势）
# 3) 文字是否清晰可读（防 pic2 clip1 文字消失）
```

**判断口诀**：
- ✅ 看到 1/3/5/9/...关键页的场景对位才进 Step 2
- ❌ 发现错位 → **不重做绘本**（绘本方已发布），**接受并标注**（Step 5 报告里说"clip6 玩具房 vs 旁白 eat 不对应，已接受现状"）

**Pic3 实战验证**（2026-06-07）：vision 抽 1/5/9 三帧确认场景对位 → 9 个 Clip 全对位 → 9/9 succeeded 0 错位。

---

## Step 0 · 接收需求

**必需** 3 件事：
1. **绘本简介**（故事简介 + 旁白文本）
2. **绘本图片**（1-N 张 JPG/PNG）
3. **目标平台**（抖音/小红书/视频号/B 站）

**图片源**：
- 飞书云盘链接 → `lark-cli` skill 下载
- 本地路径 → 直接用
- 用户上传 → 直接用

**Step 0 必问 · 文件用途澄清（v1.0.3+pic13 铁律 #90 新增 · Horse 绘本踩坑）**：

**任何文件用途在用之前必问用户，不要自动假设**：

| 文件类型 | 反模式 | 正解 |
|---|---|---|
| `*.mp3` | 自动当 TTS 直接 silencedetect 拆段 | 必问"MP3 是 TTS / 背景音 / 不用？" |
| `*.xlsx` | 自动当旁白 | 必读 sheet 名 + header 确认是哪种结构（**A 列旁白 / B 列中英 / 多 sheet 角色**）|
| `0.jpg` | 当封面用 | 必问"0 开头是封面 / logo / 不用？"（用户明确说"不用"才真不用）|
| `readme.txt` | 自动当简介 | 必读内容，**不**当数据源 |
| `0开头的所有文件` | 默默忽略 | 必报"我打算忽略 0 开头"等用户确认 |

**修复方向**：① 压缩包解开后**先列文件清单 + 报"我打算忽略 X Y Z · 用 A B C"** ② **每个文件类型的用途**在用之前**先问 1 次** ③ 用户没明说 = **不用**（铁律 #42 接受现状）。**判断口诀**：**"文件用途 = 问 1 次 = 用 0 次假设"**

---

**坑 1：hermes `terminal` 工具的 `~` 解析不稳定**

`~` 在 hermes `terminal` 工具里有两种解析结果：
- **情况 A**（多数 shell）：`~` → `/home/luo`（正常）
- **情况 B**（某些调用上下文）：`~` → `/home/luo/.hermes/profiles/huiben/home/`（**huiben profile 已加载时**，shell 的 HOME 被改写到 huiben profile 下）

**症状**：`cd ~/.hermes/profiles/huiben/work/<project>/` 看似成功（无报错），实际**进入了 `/home/luo/.hermes/profiles/huiben/home/.hermes/profiles/huiben/work/<project>/`**（**双层 huiben/home 嵌套**）。后续 `ls` 找不到、`openpyxl.load_workbook` 报 `FileNotFoundError`。

**修复方向**：
- ✅ **永远用绝对路径**（`/home/luo/.hermes/profiles/huiben/work/20260609-horse-input/`），**不**用 `~` 缩写
- ✅ 关键操作前 `echo $HOME` 看一下实际解析
- ✅ `cd` 后 `pwd` 验证路径（**不**信无报错 = 成功）
- ❌ 不要在 hermes terminal 里依赖 `~/.hermes/...` 这种路径简写

**坑 2：`execute_code` 工具的 cwd 跟 `terminal` 不一致**

`execute_code` 跑在**独立的 sandbox 临时目录**（`/tmp/hermes_sandbox_<id>/`），**不继承** `terminal` 工具的 cwd。

**症状**：terminal 里 `ls` 能看到文件、`mv` 成功，**但 execute_code 里 `openpyxl.load_workbook(path)` 报 `FileNotFoundError`**——因为 sandbox 视角下 cwd 是 `/tmp/hermes_sandbox_xxx/`，path 是相对/绝对解析不到。

**修复方向**：
- ✅ execute_code 必传**绝对路径**（**不**用相对路径，**不**假设 cwd）
- ✅ 关键验证用 `os.path.exists(path)` 兜底（不直接信"刚刚 terminal 创建了"）
- ❌ 不要在 execute_code 里 `cd /path && open(...)`（cd 不会持久化）
- ❌ 不要在 terminal 里 `cd` 后立刻在 execute_code 里用相对路径

**配套 SOP**（Horse 绘本首跑实战沉淀）：
```bash
# 1. terminal 必用绝对路径建工作目录
mkdir -p /home/luo/.hermes/profiles/huiben/work/20260609-horse-input/

# 2. terminal cd + 立即 pwd 验证（不依赖无报错）
cd /home/luo/.hermes/profiles/huiben/work/20260609-horse-input/ && pwd
# 输出必须是 /home/luo/.hermes/profiles/huiben/work/20260609-horse-input/
# 看到 huiben/home/.hermes/... 双层 = 错了，重做

# 3. 文件名 GBK 乱码重命名到 ASCII（Windows 压缩包常见）
mv "Horse ┬э.xlsx" horse.xlsx
mv "╣╩╩┬╝Є╜щ.txt" readme.txt

# 4. execute_code 读 xlsx 用绝对路径 + os.path.exists 兜底
python3 -c "import os; print(os.path.exists('/home/luo/.hermes/profiles/huiben/work/20260609-horse-input/horse.xlsx'))"
# True 才能 openpyxl.load_workbook
```

**判断口诀**：
- **terminal 用绝对路径** = `~` 不可信
- **execute_code 用绝对路径** = cwd 不可信
- **pwd 必验证** = 无报错 ≠ 路径对

**新增铁律**：

| **89**（v1.0.3+pic13 实测新增 · 2026-06-09 Horse 绘本首跑）| **hermes terminal `~` 解析双层 huiben/home 陷阱 + execute_code sandbox cwd 隔离陷阱**——`cd ~/.hermes/...` 在 huiben profile 已加载时实际进入 `/home/luo/.hermes/profiles/huiben/home/.hermes/...`（**双层嵌套**），后续 ls/execute_code 找不到。**修复方向**：① 永远用绝对路径（`/home/luo/.hermes/...`），不用 `~` 缩写 ② `cd` 后必 `pwd` 验证 ③ execute_code 必传绝对路径 + `os.path.exists` 兜底 ④ 关键文件用 `mv` 重命名到 ASCII（GBK 乱码文件名）。**判断口诀**：**"terminal 用绝对路径 = `~` 不可信 · execute_code 用绝对路径 = cwd 不可信"** |

---

## Step 1 · 启动前 7 必问（必跑）—— 6 必问 + #7 调性预审（v1.0.3+pic12 铁律 #70 强化）

**铁律（用户多次纠错）**：不擅自替用户决定。**但 7 问都走"我打算 X 因为 Y"报你**——你只回"停"或"换 X"就调整（不主动开问卷）。

| # | 必问项 | 默认值 | 为什么这么定 |
|---|---|---|---|
| 1 | **画幅比例** | 16:9 | 抖音/视频号/B 站主流；小红书可改 3:4 |
| 2 | **单 Clip 时长** | **v6 整数公式**（短句 6s / 中句 7s / 长句 8s / 极短 5s）| 按 B 子 agent 算出的朗读时长 + **整数**（铁律 #72：seedance 不生成小数）+ 末帧静默 ≈ 朗读 × 0.3-0.6（**参考标准 #74** v1.0.5+pic18 重写，**不**是红线，详见 §末帧静默参考标准）|
| 3 | **切分方式** | 按图（每张图 1 Clip） | 默认；>15s 走 v15.1 语义块 |
| 4 | **调性** | 等 A 子 agent 识别 | 主 agent 不擅自定 |
| 5 | **范式** | **领读型 v7 范式（默认）** | v7 = 2图=1Clip 合并（主 agent 直拼 · 详见 Step 3.0 路由）· 叙事/冒险/收势向走 v15 4 段（调 C 拼） |
| 6 | **约束** | 末帧 ≠ 定格海报 / 文字保留 v3 / 不写隔离句 / **彩色文字全程可见+微动画** | v0.7.1+pic7 沉淀 + 铁律 #73 |
| **7**（v1.0.3+pic12 铁律 #70 新增）| **调性预审**（绘本方选图情绪 vs 用户期望情绪）| **差距大 = 选材问题，建议换绘本** | 见 [references/2026-06-07-pic4-no-v6-final.md](references/2026-06-07-pic4-no-v6-final.md) "v6 三大核心铁律" |

**Step 1.5 · 数字约束数学验证（v1.0.3+pic13 铁律 #89 新增 · Horse 绘本踩坑）**：

**收到用户多个数字约束时（如"压缩短句 + R7=14s + 总 43s"），必先验证数学可行性再分配档位**：

1. **列出所有数字约束**（总时长 / 单 Clip 时长 / 单段朗读 / 镜头数 / R 特殊时长）
2. **用兜底公式算 8 段朗读时长**（1.4 词/秒 + 3.5 字/秒）
3. **列可行解表**（A 全准守 / B 放大总时长 / C 拆 Clip / D 放松短句）—— **每档**标"末帧静默 = 几 s"（参考标准 #74 v1.0.5+pic18：默认朗读 × 0.3-0.6，**不**是 ≥ 2s 红线）
4. **冲突时让用户选**（不偷偷按字面意思跑）
5. **物理装不下（静默 < 0.5s）= 必跑 `validate_durations.py` 验证 + 必报**（不掩盖）

**反模式**：用户给 3 个数字 → 直接算档位 → 跑出来发现 5 段末帧 < 1s → 浪费 1 轮。**判断口诀**：**"3 数字约束 = 必先列可行解表 = 让用户选"**

**用户没指定** → 用默认值 + 在 Step 2 报"我打算 X 因为 Y"。
**用户指定** → 用指定值。

---

## 📌 参考标准 · 末帧静默（v1.0.5+pic18 重写 · **不**是红线）

> **历史**：v1.0.3+pic12 把"末帧静默 ≥ 2s"写进铁律 #74（Pic4 No 绘本 v5 公式沉淀）。**2026-06-11 Banana 报告实战教正**：3 Clip × 10s 整数 = 30s 装 30s 朗读 → 末帧静默物理装不下 2s = 铁律跟用户硬约束冲突 = 主 agent 越界劝用户放弃。**根因**：把"经验值"当"红线"用。
> **修复**：v1.0.5+pic18 降级为**参考标准**（**不**是铁律），并加 `validate_durations.py` 自动验证。

### 规则（v1.0.5+pic18）

| 末帧静默 | 等级 | 含义 |
|---------|------|------|
| **< 0.5s** | ❌ 错误 | 物理装不下朗读 = 翻车征兆，**必**改 prompt 重提 |
| **0.5s ≤ X < 1s** | ⚠️ 警告 | 违反默认参考 = 需文案说明例外（紧接无静默 / 多段旁白紧接 / 节奏紧凑领读型）|
| **1s ≤ X < 2s** | ✅ 通过 | 收势合理（不算错也不推荐）|
| **≥ 2s** | ✅ 通过（推荐）| 标准做法（Pic4 v5 公式推荐档位）|

### 静默 = 0 或 < 1s 的"合法例外"

- **多段旁白紧接**（无画面切换）= 0.5s 仅做镜头切换消化
- **节奏紧凑的认知/领读绘本** = 紧接无静默（Banana 3 Clip 全走这模式）
- **末帧 1s 末**必须是"本 Clip 故事动作停留"（不是"静默"）

### 验证脚本（v1.0.5+pic18 新增）

```bash
python3 ~/.hermes/profiles/huiben/skills/creative/picturebook-video/scripts/validate_durations.py <project_dir>
```

**实际效果**（Banana 报告端到端验证）：
```
📂 验证项目：.../20260611-banana-input
📐 阈值：错误 < 0.5s / 警告 < 1.0s / 推荐 ≥ 2.0s
🎬 总 Clip 数：3
  Clip 1: ⚠️  末帧静默 0.50s < 1s（违反默认参考）— 需文案说明例外
  Clip 2: ⚠️  末帧静默 0.50s < 1s（违反默认参考）— 需文案说明例外
  Clip 3: ✅  末帧静默 1.88s 介于 1-2s（收势合理）
📊 汇总：1 通过 / 2 警告 / 0 错误
```

**退出码**：错误 ≥ 1 → 退出 1（CI 可拦截）；警告 ≥ 1 → 退出 0（**不**强制改，**不**破坏例外合法场景）

### 铁律分类法自检（v1.0.5+pic18 新增）

任何"X ≥ N 秒" / "X = N 步" 类的规则 = **优先判断是不是经验值**：

| 类型 | 例子 | 落点 |
|------|------|------|
| **官方约束**（如 seedance 15s 物理上限）| 写铁律 | 必守 |
| **行为准则**（如用户决策权归主 agent）| 写元教训铁律 | 必守 |
| **经验值**（如末帧静默 2s）| **写参考标准**（**不**是铁律）| 灵活运用，例外合法 |

**反模式**：把经验值当铁律 = 用户硬约束冲突时 = 主 agent 越界劝用户放弃 = 反复劝退浪费轮次。

---

## Step 2 · 调 A + B 并行

### 2A · 调 A · 风格识别

```python
result_a = delegate_task(
  goal="识别绘本 <title> 的风格调性 + 节奏倾向 + 风格锚定词",
  context=<A 子 agent 的 brief schema>,
  toolsets=["file", "vision"]
)
# result_a.summary 应是 A 子 agent 的输出 JSON
# 验证 result_a.summary.status == "succeeded"
# 验证 result_a.summary 符合 A 子 agent 的输出 schema
```

### 2B · 调 B · 旁白量化（与 2A 并行）

**v1.0.2 改：B 改主 agent 干**（铁律 #58）。B 跑在主 agent 上下文里，纯计算+少量 vision，~1-2 min 写完 narration-quantization.json。

```python
# B 在主 agent 干（不调子 agent）
# 1. 读旁白表（已知）
# 2. 1.4 词/秒 兜底公式（无 TTS 音频时）· 或用用户提供 TTS 实测
# 3. 按节奏档位表算每行 tier / shot_count / total_duration_seconds
# 4. 写 narration-quantization.json
```

**⚠️ 串扰风险（2026-06-07 用户警告）**：B 放主 agent 干可能受主 agent thinking 中断/上下文污染影响。**Pic4 暂未验证稳定性**——D 跑完后回看 B 算的档位 vs C 选节奏是否 100% 匹配，如果有错位 = B 串扰实锤，**回滚 B 到子 agent**（v1.0.0 老架构）。

**B 子 agent 优先用 TTS**——主 agent **必问用户**："你提供 TTS 音频吗？"
- 提供 → 传入 `tts_audio_paths` 字段
- 不提供 → 走兜底公式（warning 提示）

### 合并 A+B

主 agent 必做：
1. 验证 A 输出符合 schema（不合法 → 重发 A，1 次机会）
2. 验证 B 输出符合 schema（不合法 → 重发 B，1 次机会）
3. 持久化 A 输出 → `~/.hermes/profiles/huiben/work/<日期-项目>/style-recognition.json`（v1.0.5+pic18 路径约定）
4. 持久化 B 输出 → `~/.hermes/profiles/huiben/work/<日期-项目>/narration-quantization.json`（v1.0.5+pic18 路径约定）
5. 合并传给 C 子 agent

---

## Step 3 · 调 C · 分镜设计

**⚠️ Step 3.0 范式路由决策（v1.0.4 新增 · Horse 绘本踩坑）**：

**不是所有绘本都调 C 子 agent** —— v7 范式（领读型 2图=1Clip 合并）= **主 agent 直接拼 prompt，不调 C**。

| 触发条件 | 范式 | 工作流 |
|---|---|---|
| 领读/认知/认字绘本 + 弱情节 + 旁白每段 < 8s + 风格统一 + 总图 6-10 | **v7 范式** | **主 agent 直拼 8 段 prompt**（真模板 `assets/example-prompts/cactus-clip1-v7.txt`）· 不调 C |
| 叙事/冒险/收势向绘本 + 多场景切换 + 强情节 | **v15 4 段范式** | 调 C 子 agent 产原料 + 主 agent 填 `scripts/fill_v15_template.py` |
| 单图领读 + 无合并需求 | **v6 5 段**（v15 + 文字持续可见段）| 调 C 产原料 + fill_v15_template.py --version v6 |

**v7 范式判定 5 条件（必全过 · 铁律 #89）**：
1. ✅ 绘本是领读/认知/认字型（不是叙事型）
2. ✅ 弱情节（无明显"前一幕→后一幕"情节推进）
3. ✅ 旁白每段 < 8s（按 0.3s/字算）
4. ✅ 图片风格统一（同色系/同主体/相邻景别）
5. ✅ 总图数 6-10 张（多了需要更细分段）

**5 条件任一不满足 → 走 v15 4 段范式 + 调 C**。

**v7 范式总时长公式**（来自 `references/leading-reading-4clip-pattern.md`）：
- **标准模式**：8s + 8s + 9s + 10s = 35s（Red 绘本等）
- **TTS 优先不压缩**：8s + 9s + 10s + 10s = 37s（Cactus 绘本）
- **原则**：合并 clip 时长 = 各段 TTS 旁白时长之和 + 0.5-1.5s 缓冲
- **不**为对齐"标准 35s"压缩时长 —— 冗余给后期剪辑留余地

**v7 范式必填 seedance 参数**：
- `--image`（段首图）+ `--last-frame`（段尾图）
- `--duration` 8/8/9/10（**整数** · 4s ≤ x ≤ 15s seedance 物理上限）
- `--ratio 16:9`
- `--generate-audio true`（v7 范式靠 prompt 禁令段 `No background music, no human voice, no narration, no singing` 精准控制）

**v7 范式例外**：家族词组集合（≥3 词同字母家族）走铁律 #86 → `--generate-audio false` + TTS 音轨对齐（4 维控制底层核心不动）。

**反模式**（Horse 绘本实战差点触发）：
- ❌ **错认 v5 公式 8s 档位 = 硬上限** —— 8s 只是 v5 公式档位参考 · 真正上限 seedance 15s（铁律 #90）
- ❌ **调 C 拼 v7 prompt** —— C 只懂 v15 4 段，强行套会拼出错的 prompt 结构（铁律 #89）
- ❌ **把 2图=1Clip 硬塞进 v15 模板** —— 破坏 v7 范式 8 段结构 · fill 脚本只支持单图 @ImageN
- ❌ **看到 14s 长 Clip 立即报"必拆"** —— 14s < 15s 合法单 Clip（v7 Clip 4 收势 10s / Horse R7 14s 都验证过）

**v7 vs v15 完整路由决策树**：见 `references/v7-vs-v15-paradigm-routing.md`（v1.0.4 新增）

```python
result_c = delegate_task(
  goal="根据 A+B 输出做分镜设计 + 拼 v15 范式 prompt 草稿",
  context=<C 子 agent 的 brief schema，含 style_report + narration_report>,
  toolsets=["file", "vision", "terminal"]
)
# 验证 result_c.summary.status == "succeeded"
# 验证每个 clip.prompt_draft 通过 self_check 9 项
# 持久化每个 prompt_draft → ~/.hermes/profiles/huiben/work/<日期-项目>/clips/clipN-prompt.txt（v1.0.5+pic18 路径约定）
```

**C 子 agent 必做**（主 agent 不替代）：
- 按档位表选节奏（不凭印象）
- 强制 v15 4 段骨架
- 末帧写"画面继续微动"
- 段 4 不写"其他元素不出现"

**C 翻车** → 重发 C，1 次机会。

**C 600s timeout 实战**（Pic3 2026-06-07）：C 写 9 个 JSON 跑了 600s 没写完主索引 → **主 agent 续写主索引**（用 Python 一次性聚合 clip1-9.json → storyboard-index.json）。

---

## Step 4 · 调 D · 视频执行

**⚠️ 实战约束（铁律 #50 · v1.0.2 强化）**：D 子 agent **禁止一次跑全部 N 个 Clip**。
- Pic2 实战（2026-06-06）：8 个 Clip 一次跑 = 600s timeout × 2
- Pic3 实战（2026-06-07）：D 跑 3 个/批 仍 timeout（6 个 Clip 用了 ~6 分钟，9 个=29 API call=timeout）= **最佳 batch = 2 个/批**
- **极限 = 1 个/批**（端到端验证）
- **C 子 agent 600s 内只能写 9 个 JSON + 聚合 + vision × 9 = 9 个 API call**——超出时主 agent 续跑

**Step 4.0 · seedance 调用范式二选一（v1.0.3+pic14 新增 · 铁律 #93）**：

| 范式 | 触发 | seedance 参数 | prompt 写法 | 段数 |
|---|---|---|---|---|
| **v15 4 段 / v6 5 段**（默认）| 任何绘本默认走这条路 | `--ref-images 1.jpg [2.jpg]`（多图参考）| `@ImageN` 引用（v15 填模板后用铁律 #93 代码拆 `@Image1+2`）| 4 / 5 |
| **v3/v8 首尾帧**（v7 范式 fallback）| 用户明确说"走 v3/v8" 或 fill 脚本失败 | `--image ./first.jpg --last-frame ./last.jpg` | `from 0.0s to 1.2s @Image1 ... transitions to @Image2 ...` | 自由 |

**反模式**（Horse 绘本差点踩）：
- ❌ **v15 范式用 `--image` + `--last-frame`** → seedance 把它当 v3/v8 跑（破坏 v15 4 段骨架 + 失去 v6 文字持续可见段）
- ❌ **v7 范式用 `--ref-images`** → seedance 多图参考跟 v7 8 段固定结构不兼容

**Pic7 Horse 端到端验证**：5 段全 v6 5 段（v15 + 文字持续可见段）+ `--ref-images` + 5/5 succeeded · 整数时长 100% 命中。

**主 agent 续跑模式**（D/C timeout 后 · Pic3 实战验证）：
1. D timeout → 主 agent 直接调 seedance.py 续跑**未提交的 Clip**（不重新调 D）
2. 续跑命令模板（pic3 实战）：
   ```bash
   set -a; source /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env; set +a
   for N in 7 8 9; do
     python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py create \
       --ref-images /path/${N}.jpg \
       --prompt "$(cat /path/clips/clip${N}-prompt.txt)" \
       --duration ${DURATION} --ratio 16:9 --resolution 720P \
       --model doubao-seedance-2-0-fast-260128 \
       --watermark false --generate-audio true \
       --download /path/v1-clip${N}-fixed.mp4 2>&1 | grep "Task ID"
   done
   # 再 wait 每个 task_id（用 shell 变量存）
   ```
3. **task_id 必存**到 `task_ids.txt`（铁律 #30 强化：D timeout 也要存已生成的 ID）

**D 必做 6 件事**（主 agent 必查）：
1. **不 --wait / 不 --download**（Pic2 实测 timeout）
2. 25 轮 × 15s 轮询
3. ffmpeg 抽帧（每秒 1 帧）
4. **vision_analyze 必须 native vision**（不调 mcp_zai_analyze_image）
5. ls -lh 验证（铁律 #30）
6. **单 Clip 端到端先验**（铁律 #50）—— 不一次跑全部，1 个 OK 再 2 个/批次

**D 翻车 → C 修复 → D 重跑**（铁律 #49 · C self_check 错位修复方向）：

| 翻车征兆 | C 修复方向 |
|---|---|
| 镜头一主体完全丢失 | 镜头一加约束"两兔必须完整可见"（不只是"切到全景"）|
| 文字消失/被吃 | 文字保留升级"锁定 top 1/6 画面不重绘" / 改用 `--image` 首帧模式钉死构图 |
| 末帧定格海报 | 末帧微动细化为"末帧 1s 必须含 ≥1 个动作元素"（不只写"画面继续微动"）|
| 末帧完全静止 5s | 同上 |
| 角色外观漂移 | 强化 @ImageN 绑定 + 主体定义加视觉特征详情 |
| task failed | 不重试 D，查 ark list 端点 |
| 角色闭嘴 vs 张嘴 | 接受（绘本调性 = 温柔内敛）|
| **绘本原图场景和旁白错位** | **不重做**！直接接受（绘本方已发布）—— Pic2 clip6 玩具房当 eat 教训 |

**D 必做 5 件事**（主 agent 必查）：
1. 不 --wait / 不 --download（Pic2 实测 timeout）
2. 25 轮 × 15s 轮询
3. ffmpeg 抽帧（每秒 1 帧）
4. **vision_analyze 必须 native vision**（不调 mcp_zai_analyze_image）
5. ls -lh 验证（铁律 #30）

---

## Step 5 · 汇总 + 发飞书

**主 agent 必做**：
1. 持久化 D 输出 → `~/.hermes/profiles/huiben/work/<日期-项目>/execution-report.json`（v1.0.5+pic18 路径约定）
2. **不翻车** → 决定是否发飞书（**铁律 #29 视频交付不抽帧**——不主动抽帧，让用户自己看）
3. **翻车** → 报告翻车清单 + 决定重发 C / 接受 / 降级 v0.7.1+pic7 单 agent
4. token 用量记入 `results.tsv`

**Pic3 实战补充**（v1.0.2）：
- 9 个 Clip 全部 succeeded → 决定拼装+发飞书
- 拼接工具：ffmpeg concat demuxer + 旁白 BGM 混音（参考 [references/2026-06-07-pic3-welcome-validation.md](references/2026-06-07-pic3-welcome-validation.md) §"拼装"）
- **不主动抽帧发**（铁律 #29 强化：抽 4 帧 = 6×9 = 54 帧 = 主 agent 上下文污染）

## Step 4.5 · 实战验证 gate（重构/大版本发布前必跑 · 铁律 #51）

**触发条件**：本次任务是**重构/大版本优化/新子 agent 接入**——不是普通跑视频。

**反模式（2026-06-06 差点踩）**：evals 9 维度全胜就开 PR → Pic2 v1.0.0 实战 Clip 1 跑出 5/6 false（主体丢失 + 文字消失 + 末帧定格）。

**实战 gate 5 步**：

```
1. 跑 1 个 Clip 端到端（验证流程跑通）
2. 看视频：末帧是否画面微动？文字是否保留？角色是否完整？
3. 跑 1-2 个完整绘本（8-12 个 Clip 批量）出 mp4
4. 抽 2-3 个 Clip 抽帧自检（不只凭感觉）
5. 全部 OK → 才能开 PR
```

**实战 OK 定义**：
- 至少 1 个 Clip 跑通端到端（A+B+C+D 全跑）
- 至少 1 个 Clip 视频自检 self_check ≥5/6
- 至少 1 个 Clip 末帧画面**真的**微动（不是定格海报）
- 至少 1 个 Clip 文字**真的**完整保留（不是消失）

**实战翻车处理**：
- C self_check 错位（铁律 #49）→ 重发 C 改 prompt 措辞，**不**直接改 evals 评分标准
- D 批量 timeout（铁律 #50）→ 降级为单 Clip 端到端 + 2 个/批次（v1.0.2 强化）
- evals 9 维度全胜但实战翻车 → **evals 评分方法**本身要重写，**不是改 v1.0.0**

**不开 PR 的硬约束**（用户 2026-06-06 原话）：
- "我们都没有实测过，怎么能PR"——evals 通过 ≠ 实战通过
- 任何"看起来 OK"都不算实战 OK，**必须 mp4 视频目检 + 抽帧自检**

**发飞书模板**：
```
[绘本名] 视频已生成：

[MEDIA:/path/to/clip1.mp4]
[MEDIA:/path/to/clip2.mp4]
...

总时长：X 秒（Y 个 Clip）
token 用量：Z

需要我改什么吗？
```

**不发飞书的反模式**（铁律 #29）：
- 跑完直接发（用户没让我跑 = 反模式）
- 不发视频只发报告
- 抽 1 帧图当预览

---

## 失败模式（主 agent 决策树）

| 失败点 | 决策 |
|---|---|
| A 子 agent 失败 | 不重发 A → 降级 v0.7.1+pic7 单 agent 模式 |
| B 子 agent 失败 | 不重发 B → 降级 v0.7.1+pic7 模式（不重算） |
| C 子 agent 失败 | 重发 C，1 次机会 → 还失败则降级 |
| C 子 agent 600s timeout | **主 agent 续写**主索引（用 Python 聚合 clip1-9.json → storyboard-index.json） |
| D 子 agent 600s timeout | **主 agent 续跑未提交 Clip**（shell + seedance.py） |
| D 子 agent 部分翻车 | 重发 C 改 prompt → 重发 D 跑该 Clip |
| D 子 agent 全部翻车 | 降级 v0.7.1+pic7 + 报告用户 |
| 用户中途打断 | 接受中断，保存当前状态 |
| **绘本原图场景和旁白错位** | **不重做**！接受现状 + Step 5 报告标注（绘本方已发布，强行改 = 不忠于原书） |
| **遇到 skill 兜不住的问题** | **先查 [references/seedance-official-docs/README.md](references/seedance-official-docs/README.md)** —— 官方 6 个教程已搬入 skill 仓（508K），按"提示词写法/参数功能/端到端流程"分 3 个文件。**判断口诀**：skill references 没有 → 查官方 docs → 都没答案才用 web_search |

---

## 启动前 6 必问的具体话术

**主 agent 必说**（不擅自决定）：

```
准备做 [book_title] 视频。我打算：

1. 画幅：16:9（抖音/视频号/B 站主流）
2. 单 Clip 时长：按 B 子 agent 算出的朗读时长匹配档位
   - 短句（< 4s 朗读）→ 6s Clip
   - 中句（5-8s）→ 11s Clip
   - 长句（8-12s）→ 12s+12s 双 Clip
3. 切分：按图（每张图 1 Clip），>15s 走 v15.1
4. 调性：等 A 子 agent 识别后报你
5. 范式：v15（绘本默认 2026-06-05 起）
6. 末帧 ≠ 定格海报 / 文字保留 v3 / 段 4 不写隔离句

需要我先问 TTS 时长吗？（你提供 = 准确 / 不提供 = 兜底公式）

如果都 OK，我就启动 A+B 并行。
```

**用户回 "OK"** → 启动
**用户回 "X 改 Y"** → 调整后启动
**用户回 "停"** → 终止

---

## 4-skill 工具包协作

本次 v1.0.0 重构是按 4-skill 工具包流程做的：

| 阶段 | 工具 | 产物 |
|---|---|---|
| 1. 拆分 | `skill-organizer` | 目录结构（agents/ + references/） |
| 2. 编写 | `skill-creator` | 4 份子 agent SKILL.md + 本主 SKILL.md |
| 3. 沉淀 | `gardener-skill` | `references/2026-06-06-v1-refactor-rationale.md` |
| 4. 验证 | `darwin-skill` | 跑 evals 对比 v0.7.1+pic7 vs v1.0.0 |

---

## 与子 agent 的关系

主 agent **必做**：
- ✅ 验证子 agent 输出 schema
- ✅ 持久化子 agent 输出到磁盘
- ✅ 翻车时决定重发哪个子 agent
- ✅ 接受/降级决策
- ✅ Step 0.5 绘本场景对位检查（v1.0.2 新增）
- ✅ C/D 子 agent timeout 后续跑（v1.0.2 新增）

主 agent **不做**：
- ❌ 拼 prompt（那是 C 的事）
- ❌ 跑视频（那是 D 的事，除非 D timeout 续跑）
- ❌ 抽帧验证（那是 D 的事）
- ❌ 凭印象选节奏（那是 C 的事）

---

## 详细规范位置

- **v15 范式 prompt 4 段骨架**：见 C 子 agent `agents/storyboard-design/SKILL.md`
- **v15.1 长旁白拆分**：见 `references/长旁白拆分规范-v15.1.md`
- **节奏档位表**：见 C 子 agent `agents/storyboard-design/SKILL.md` "决策规则"
- **文字保留铁律 v1v2v3**：见 `references/绘本文字保留铁律-v1v2.md`
- **末帧 ≠ 定格海报**：见 `references/2026-06-06-pic2-mvp-validation.md`
| 视频交付不抽帧 | `references/视频交付工作流-不抽帧.md` |
| 重构根因 | `references/2026-06-06-v1-refactor-rationale.md` |
| **v1.0.1 实战 Pitfall** | `references/2026-06-07-v1.0.1-pitfalls.md`（2026-06-07 Pic2 Clip 8 收势节奏拖慢）|
| **v15 4 段骨架模板**（v1.0.3+pic12）| `references/v15-4段骨架-模板.md`（**用户根本性纠错**："底层核心 = prompt 写法结构"，模板化 v15 4 段，11 个变量必填，**主 agent 填变量 = 终稿 prompt**）|
| **v1.0.2 Pic3 Welcome 实战验证** | `references/2026-06-07-pic3-welcome-validation.md`（2026-06-07 Pic3 Welcome 9 Clip 实战 0 错位 · v15.2 铁律 #54 完整闭环 · C/D 续跑模式沉淀）|
| **v1.0.2 Pic4 No 不 实战验证** | `references/2026-06-07-pic4-no-validation.md`（2026-06-07 Pic4 No 不 9 Clip 实战 0 错位 · v1.0.2 完整流程首次端到端跑通 · C 不写 prompt_draft + 主 agent 填 v15 模板 + B 串扰风险警告 · 铁律 #59-#65）|
| **Pic4 No v5 节奏公式重构**（用户两步推导）| `references/2026-06-07-pic4-no-v5-rhythm-formula.md`（2026-06-07 Pic4 v3 跑通后用户反馈"末帧仍太短"，原话两步推导：① 朗读完最低 3s ② + 2s 末帧静默。v5 公式：5/6/7/8s 四档 · 末帧静默 2.9-3.8s · 镜头数 2-3 · 微动元素 4-6 · 铁律 #69）|
| **飞书视频交付与目检反例排查** | `references/视频交付与目检反例排查.md`（2026-06-07 Pic4 clip1 用户目检反例沉淀 · vision_analyze 4 步排查法 · 4 个可能根因 · 完整证据链交付模板 · 决策树）|
| **Pic4 v6 最终实战沉淀** | `references/2026-06-07-pic4-no-v6-final.md`（2026-06-07 Pic4 v6 完整闭环：v1 严肃 → v3 温柔化 → v5 节奏两步推导 → v6 整数+文字全程可见 · 5 版迭代对比表 · v15 4 段→v6 5 段结构升级 · 铁律 #72-#79）|
| **声音策略分支**（铁律 #86）| `references/sound-strategy-branches.md`（**v1.0.3+pic13 新增** · Pic6 Cow clip7 实战沉淀 · 3 旁白类型 × 声音策略分支表 · seedance 命令差异 · 触发条件判定逻辑 · 反模式 4 条 · **不破坏 4 维控制底层核心**）|
| **Pic5 Bird 鸟 8 段 v6 模板首次跑通** | `references/2026-06-07-pic5-bird-validation.md`（v1.0.3+pic13 · 8/8 succeeded · 整数时长 0 错位 · 50.66s · 8 task 并行轮询 ~7min · 4 维加权 3.8/5 首次实战 · en_color_pattern 清洗 · fill_v6_bird.py 复发待清理）|
| **Pic6 Cow 牛 8 段实战验证** | `references/2026-06-08-pic6-cow-validation.md`（**v1.0.3+pic13 新增** · 2026-06-08 · 8/8 succeeded · 58.66s · 6 并行轮询 ~3min · 整数时长 100% 命中 · md5 0 错位 · 用户 3 轮纠错（OW 拆分/15s 上限/TTS 对齐）+ 用户明确纠错"不主动抽帧自检"沉淀为铁律 #87 · fill_v15 硬编码修复沉淀为铁律 #88）|
| **v6 5 段模板文档** | `references/v6-5段骨架-模板.md`（v1.0.3+pic12 新增 · v15 + 文字持续可见段 · 12 变量清单 · EN_COLOR_DESC 两种格式 + 字符顺序浮现时间表 · Pic5 Bird 实战沉淀）|
| **v6 5 段模板文档** | `references/v6-5段骨架-模板.md`（v1.0.3+pic12 新增 · v15 + 文字持续可见段 · 12 变量清单 · EN_COLOR_DESC 两种格式 + 字符顺序浮现时间表 · Pic5 Bird 实战沉淀）|
| **声音策略分支** | `references/sound-strategy-branches.md`（v1.0.3+pic13 新增 · Pic6 Cow clip7 OW 家庭 5 词实战沉淀 · 3 旁白类型×声音策略分支表 · TTS 音轨对齐 · **4 维控制底层核心不动** · 铁律 #86 候选）|
| **Pic6 Cow 牛 实战验证** | `references/2026-06-08-pic6-cow-validation.md`（2026-06-08 · 8/8 succeeded · 0 错位 · 58.66s · 6 并行轮询 ~3min · 调性 A 知识向·欢快轻松 · 用户对 Clip 7 的 3 轮纠错 · fill_v15 硬编码翻车修复）|
| **Pic7 Horse 马 实战验证** | `references/2026-06-09-pic7-horse-validation.md`（**v1.0.4+pic14 → v1.0.5+pic15 完整闭环** · 2026-06-09 · 5/5 succeeded · 0 错位 · 48s · v15 + 2图=1Clip 兼容 + 5 档声音策略 + 参考图文字保真 三重修复 · 3 个 commit `2b957a4` `8ddbb34`）|

---

## v0.7.1+pic7 → v1.0.0 → v1.0.1+pic10 → v1.0.2 变化清单

| 维度 | v0.7.1+pic7 | v1.0.0 | v1.0.1+pic10 | v1.0.2 |
|---|---|---|---|---|
| SKILL.md 行数 | 568 | ~200 | ~270 | ~280 |
| 主 agent 职责 | 干全部 | 只调度 | 只调度 | 只调度 + 场景对位 + 续跑 |
| 子 agent 数 | 0 | 4 | 4 | 4 |
| 节奏选档 | 凭印象 + 标版必跑 | 档位表强制 | v15.2 强化（不主动加镜）| 同 v1.0.1 |
| 朗读时长 | 凭语感 | B 子 agent 量化 | 同 v1.0.0 | 同 v1.0.0 |
| 末帧策略 | 标版 2-3s 静默 | 调性 × 系数 + 画面微动 | v15.2 收势约束 6s 3 镜头 | 同 v1.0.1 |
| 翻车处理 | 主 agent 自己改 prompt 重跑 | 报告回主 agent → 重发 C 改 | 同 v1.0.0 | + C/D 续跑模式 |
| 并行度 | 串行 | A+B 并行 | 同 v1.0.0 | + Step 0.5 场景对位 |
| 实战绘本 | 0 | Pic2（部分）| Pic2 8 Clip（v1.0.1+pic10）| **Pic3 9 Clip（v1.0.2 · 0 错位）**|

---

## 铁律清单（v1.0.2 精简版）

| # | 内容 |
|---|---|
| 1-34 | 保留 v0.7.1+pic7 全部铁律（在子 agent 内部） |
| **89-92**（v1.0.3+pic13 实战新增 · 2026-06-09 · **Horse 绘本踩坑**）| **🔥 见顶部"决策时必看的新铁律速查"区 · 触发约束冲突/范式选错/MP3 用途/总时长装不下时必查** · 详细见 `references/v7-vs-v15-paradigm-routing.md`（v1.0.4 新增）|
| **89**（v1.0.3+pic13 实战新增 · 2026-06-09 · **Horse 绘本踩坑**）| **用户给多个数字约束时必先数学验证可行性**——"压缩短句 Clip + R7=14s + 总 43s" 3 个约束**数学上不兼容**（装不下 8 段中 5 段 4.29s 朗读 + 1 段 14s · 算出 5 段末帧静默 0.71s < 2s 铁律 #74 底线 = 翻车征兆）。**修复方向**：① 收到多个数字约束时**先列出可行解表**（A 准守/全 43s + 末帧<1s / B 放大总时长/ C 拆 R7 多 Clip / D 短句放松）→ **让用户选** ② **不要**先按字面分配档位再报警（用户已经投入决策成本）③ 数学冲突 = **决策树问题**，**不是**参数微调问题。**反模式**：直接按用户字面意思分配档位 → 跑出来末帧定格海报 → 才发现 5 段 < 1s。**判断口诀**：**"3 个数字约束 = 必先列可行解表"** |
| **90**（v1.0.3+pic13 实战新增 · 2026-06-09 · **Horse 绘本踩坑**）| **MP3 不一定是 TTS · 文件用途必问不自动假设**——Horse 绘本压缩包里的 `horse.mp3` 是绘本原版音频（2.7MB · 90.15s · 整段连续无静音），**不是**用户旁白 TTS。**根因**：我自动假设"压缩包里的 MP3 = TTS" → 跑 silencedetect 拆段 → 才发现整段没静音 → 用户打断"MP3 不是 TTS 不要管"。**修复方向**：① **任何文件用途在用之前必问**（MP3 = TTS? / MP3 = 背景音? / MP3 = 不用?）② **读 README** 看看有没有说 ③ 跑 silencedetect 之前**先听 1 段**（ffmpeg -t 5 -o /tmp/preview.wav）确认是不是人声 ④ **xlsx 旁白** ≠ **mp3 旁白**——一个是文本，一个是音频，**两者可能不一致**（可能用户用 TTS 工具重录过）。**反模式**：看到 MP3 就当 TTS 直接 silencedetect 拆段。**判断口诀**：**"MP3/TXT/Excel = 文件用途必问不假设"** |
| **91**（v1.0.3+pic13 实战新增 · 2026-06-09 · **环境 quirk**）| **`~` 在 hermes terminal 解析成 `/home/luo/.hermes/profiles/huiben/home/`（不是 `/home/luo`）**——`cd ~/.hermes/profiles/huiben/work/<date>-<book>/` 实际路径 = `/home/luo/.hermes/profiles/huiben/home/.hermes/profiles/huiben/work/<date>-<book>/`。**根因**：hermes 沙盒 `~` 解析跟系统 shell 不一致（hermes 给 `~` 拼了 huiben profile home 前缀）。**修复方向**：① **`cd` 后必 `pwd` 验证实际路径**（不要信 `~`）② **execute_code 用绝对路径**（`/home/luo/.hermes/profiles/huiben/home/.hermes/...` 完整路径）③ **所有存盘/读盘操作必用绝对路径** ④ 找文件用 `find /home/luo -name "<file>"` 兜底。**反模式**：`cd ~/work/ && python3 script.py` —— `script.py` 找不到，**不报错**（cd 静默失败）。**判断口诀**：**"hermes terminal `~` ≠ 系统 `~` · 必用绝对路径"** |
| **92**（v1.0.3+pic13 实战新增 · 2026-06-09 · **Horse 绘本踩坑 · 用户原话纠错**）| **总时长约束冲突时 = 走"短时长 Clip 合并"路径，不是按字面算 8 段**——用户原话："**合并短时长clip，确保单个clip时长不要超过15s即可**"。**根因**：我钻牛角尖把"v5 公式 4 档 5/6/7/8s"当默认上限（**实际是档位参考 · 不是上限**），还编了"超出 8s 必拆 v15.1"（**v15.1 触发条件 = > 15s seedance 物理上限 · 不是 > 8s**）。**真路径**：① 收到"压缩短句 + R7=14s + 总 43s"约束冲突时 → **走 v7 范式 2图=1Clip 合并**（`references/leading-reading-4clip-pattern.md`）= 8 段 → 5 Clip ② 合并后单 Clip 时长公式 = `合并段 TTS 朗读 + 0.5-1.5s 缓冲`，**不**硬套 5/6/7/8 档 ③ **单 Clip ≤ 15s** = seedance 物理上限 · **超过必拆**（不是 8s）④ 触发 v7 合并的 3 条件：领读型绘本 + 弱情节 + 旁白 < 8s/段（**Cactus/Red 绘本标准模式 8+8+9+10 = 35s · 不压缩模式 8+9+10+10 = 37s**）。**反模式**：把 v5 公式档位当硬上限 / 凭印象编"8s 上限"规则 / 不知道 v7 范式存在。**判断口诀**：**"总时长约束冲突 = 走 v7 合并 = 2图=1Clip = ≤15s/Clip"** · 完整 v7 范式见 `references/leading-reading-4clip-pattern.md` |
| **35** | 跑 seedance 前必先 `seedance.py create --help` |
| **35b** | @ 引用语法 = 查官方文档原文 |
| **36** | 末帧 = 朗读 + 画面微动 1-2s（**不是定格海报**）|
| **36b** | 静默公式 = 朗读 × 系数（跟旁白律动挂钩）|
| 37 | 长旁白单图多 Clip 拆分 = 语义块 |
| 38 | 切分表必查清单 |
| **39** | 领读节奏元原则（**档位表 = 常见情况默认参考，不是必跑**）|
| **40** | V13 范式"主体外观 vs 场景分离"的可控范围 |
| **41** | 主体一致性不在 prompt 里二次声明 |
| **42** | "接受现状"元原则 |
| **43**（新）| 主 agent 必做调度，不直接干活 |
| **44**（新）| 子 agent 必做单一职责，不越界 |
| **45**（新）| 翻车时主 agent 决定重发哪个子 agent，不擅自重跑 D |
| **46**（新）| vision_analyze 必须 native vision（不调 mcp_zai_analyze_image）|
| 47（新）| D 子 agent 不 --wait / 不 --download（Pic2 实测 timeout）|
| **48**（新）| 主 agent 调度子 agent 必传 schema 完整 JSON（不传散文）|
| **49**（v1.0.0 实战新增）| 节奏公式 = 动作成本相加（不硬套模板·"Good afternoon" 1.5s 套 6-7s = 凭空加 4-5s 空镜 = 节奏拖慢）|
| **50**（v1.0.0 实战新增）| **未实战验证不能开 PR**（重构完成 + evals 100% ≠ 实战可用）|
| **51**（v1.0.0 实战新增）| **Cat v15 范式精准度迁移** = 拆 Clip 维度 = 语义块 + 拟声 = 故事动作音 + 画面先讲语义 + 末帧 = 故事动作停留 + 目标词重读窗口 |
| **52**（v1.0.0 实战新增 · 核心三控制）| **画面控制（clip_narrative 故事动作）+ 时间控制（节奏 = 动作成本相加）+ 声音控制（拟声 = 故事动作音 + 朗读强化读音 + 目标词重读窗口）** |
| **53**（v1.0.0+pic9 实战新增）| **末帧消化时间 ≥ 1s 标准 / ≥ 2s 收势** |
| **54**（v1.0.1+pic10 实战新增 · 2026-06-07 · v15.2 强化）| **节奏默认 = 朗读 + 末帧消化（不主动加镜头不加时长）**——"用户没说要 = 不要加" |
| **55**（v1.0.2+pic11 实战新增 · 2026-06-07）| **v15.2 铁律 #54 实战验证成功**——Pic3 Welcome 9 Clip 跑通：clip9 收势 6s 3 镜头**一次到位**（v15.1 套 11s 5 镜头翻车已彻底修复）；9/9 md5 唯一 0 错位（Pic2 6/8 错位教训已闭环）；C 自检 12/12 + D seedance 9/9 succeeded（**C 文本合规 = D 视频合规**，v1.0.0 错位已修复） |
| **56**（v1.0.2+pic11 实战新增 · 2026-06-07）| **绘本场景对位检查前置（Step 0.5）**——主 agent 在调 C 之前，**必**用 native vision 抽 1/3/5/9 等关键页 t=0.5s 帧验证原图场景与旁白对位。Pic2 clip6 玩具房当 eat 翻车教训：绘本方可能用"兔子+通用场景"模板画，**场景 ≠ 旁白**。**对位错则接受现状**（不重做绘本） |
| **57**（v1.0.3+pic12 实战新增 · 2026-06-07 · **底层核心 = prompt 写法**）| **v15 4 段骨架 = 模板 · 主体/动作/拟声/微动 = 变量**——**用户根本性纠错**："底层核心逻辑是提示词的写法结构，所有任何场景都是在这个结构上做微调"。**含义**：v15 4 段骨架（段 1 主体定义 / 段 2 分镜绑定 + 文字保留 / 段 3 分镜描述含拟声 / 段 4 风格 + BGM）= **固定的 4 段写法**，不是"每次从 0 拼"。**所有场景**（绘本/漫剧/故事/广告/动画）= **在模板上做变量微调**（不是"重写 prompt"）。**主 agent 拼 prompt 的职责**：C 子 agent 产"原料"（clip_narrative / time_breakdown / 文字位置 / 视觉特征 / 风格关键词）→ **主 agent 填 v15 模板变量 = 终稿 prompt**（保证 prompt 写法 100% 一致）。**模板沉淀**：见 `references/v15-4段骨架-模板.md`（v1.0.3+pic12 新增）。**判断口诀**："**v15 4 段 = 模板**；**主体/动作/拟声/微动 = 变量**" |
| **58**（v1.0.3+pic12 实战新增 · 2026-06-07 · **子 agent 减负**）| **A+B+D 主 agent 干 · 只 C 子 agent 干**——**用户纠错**："子 agent 执行时长 >> 主 agent" + "视频生成可以由主 agent 执行"。**修复方向**：A+B 改主 agent 干（纯计算/少量 vision，~1-2min/个）+ D 改主 agent 用 `seedance.py` 跑（实时决策不超时）+ **C 唯一子 agent**（看图产"原料" JSON，~5-8min ≤ 600s）。**根因**：子 agent 启动 + 上下文传递 + 多步 vision 调用 = 600s timeout 元凶。**Pic3 实战数据**（用全子 agent）：A 5min + B 8min + C 10min + D 10min = ~33min。**v1.0.3+pic12 改后**（A+B+D 主 agent 干）：A 1-2min + B 1-2min + C 5-8min + D 3-5min/批 = **~12-18min 节省 50%**。**D 退化为参考文档**（不调用）。**C 必做 1 件事**：产"原料" JSON（**不**写 prompt_draft 字段，由主 agent 拼）。**判断口诀**："**A+B+D = 主 agent 干 = 减 5x 时长**" |
| **59**（v1.0.3+pic12 实战新增 · 2026-06-07 · **Pic4 实战沉淀**）| **C 子 agent SKILL.md schema 强制不写 prompt_draft**——v1.0.3+pic12 commit 描述里说"C 不写 prompt_draft"，但 SKILL.md 上面的「输入/输出 schema」和「示例」段落**还写 prompt_draft 字段**。Pic4 修复：重写 C 子 agent SKILL.md 的「输出 schema」+「示例」段落，**明确标注"v1.0.3+pic12 新版 · 不写 prompt_draft"**。**根因**：下个 C 子 agent 看到 schema 引导会直接错（schema 是 agent 的第一反应源，不是红线 #9）。**同时**：把 `scripts/fill_v15_template.py` 放进 picturebook-video/scripts/ 目录作为标准填模板工具（9 段 prompt 100% 一致 = 0 行 drift）|
| **60**（v1.0.3+pic12 实战新增 · 2026-06-07 · **B 串扰风险**）| **B 放主 agent 干可能受干扰**——用户 2026-06-07 警告："把B也放入主agent执行的话，可能会受干扰，可能会出现不稳定的情况"。**风险**：主 agent thinking 中断/上下文污染可能影响 B 量化结果（9 段旁白量化在主 agent 上下文里跑 = 不隔离 = 易污染）。**Pic4 暂未验证稳定性**——D 跑完后**必**回看 B 算的档位 vs C 选节奏是否 100% 匹配，如果有错位 = B 串扰实锤，**回滚 B 到子 agent**（v1.0.0 老架构）。**判断口诀**："**D 跑完验证 B 输出 vs C 节奏档位 = 100% 匹配才确认 B 干稳定**" |
| **61**（v1.0.3+pic12 实战新增 · 2026-06-07 · **vision_analyze 汇报流程**）| **vision_analyze 批量调用后必先汇报再下一步**——Pic4 实战翻车：在跑 vision_analyze × 4（2/4/6/8）时**中断**，agent **没在响应里汇报 4 张图的结果**就跳到写 style-recognition.json，用户反馈"2/4/6 都没看到识别成功"。**修复**：每次 vision_analyze 批量调用结束后，**先简短汇报 "X/Y 张已识别"再开始下一步**；vision_analyze 失败的图要明确标 ❌ 不掩盖。**判断口诀**："**vision batch 完 = 先汇报结果 → 再写 JSON**" |
| **62**（v1.0.3+pic12 实战新增 · 2026-06-07 · **fill_v15 模板数据清洗**）| **C 子 agent 输出的 text_position.en_color 是结构化数据，不能直接拼进 prompt**——Pic4 clip1 实战：`tp.en_color = "N=鲜艳红色 / o=橙红色"` 直接拼 f"{en_color_raw} 英文" 出现"1/6 画面的N=鲜艳红色 / o=橙红色 英文"语法断裂。**修复**：`scripts/fill_v15_template.py` 加 `_parse_en_color()` 函数，**只取主色名 + 保证"色"字结尾**（"N=鲜艳红色 / o=橙红色" → "鲜艳红色色"）。**根因**：C 子 agent 倾向把字段填成结构化数据便于检索，但 prompt 模板需要的是**流畅词组**不是结构化标签。**新约定**：C 输出的所有"颜色/位置/特征"字段都应该是**句法片段**（可直接拼入句子的词组），不是**键值对**。**判断口诀**：**"C 产原料 ≠ prompt 词组 · 主 agent 必清洗"** |
| **63**（v1.0.3+pic12 实战新增 · 2026-06-07 · **vision 和人眼观感不一致风险**）| **mp4 → 飞书附件 → 用户手机 = 渲染链不可控**——Pic4 clip1 跑通后 vision_analyze 多次确认视频内容是 No（小熊 Stop 手势 + No/不能），**但用户反馈"看到的是 Welcome"**。**可能的根因（未实锤）**：① 飞书 client 渲染 bug ② 附件预览显示成了历史 pic3 视频 ③ 用户看的是 pic3 历史消息 ④ seedance 实际生成跟 prompt 不一致（vision 看花眼）。**修复方向**：① 主 agent 每次发飞书**附完整证据链**（文件名 + md5 + task_id + 原图 + prompt 文字）让用户能 100% 验证 ② 视频交付不只发飞书，**同时落地磁盘 + 飞书云盘**，用户可从云盘二次下载验证 ③ **vision_analyze 跟人眼观感不一致时，以人眼为准**（vision 是辅助不是真理）。**判断口诀**：**"vision 看多帧 ≠ 用户看到的就是这个"** |
| **64**（v1.0.3+pic12 实战新增 · 2026-06-07 · **B 干 magic number 必标注依据**）| **B 旁白量化的系数（0.71 / 0.95 / 2.14 / 2.86）必须标注公式来源**——Pic3 + Pic4 实战中 B 干多次出现"0.71 系数""0.95 系数""2.86 系数"等 magic number，**没有来源** = 主 agent 凭印象拍板。**风险**：下次不同绘本跑出来的 B 输出可能 magic number 漂移。**修复方向**：① B 干 narration-quantization.json 每个 silence_coefficient / silence_rationale 必填**公式来源**（"朗读 × 0.71 系数 = 0.6 系数 × 1.2 调性调整"这种链式推导）② 主 agent 必查 B 输出是否有 rationale 字段，**没有就拒绝 B 输出** ③ 沉淀标准公式到 `references/旁白朗读时长计算.md`（已有文档但要补"系数计算链"）。**判断口诀**：**"B 输出无 rationale = 主 agent 拒绝用"** |
| **65**（v1.0.3+pic12 实战新增 · 2026-06-07 · **单 Clip 端到端验证发现的内容-渲染不一致**）| **发飞书前单 Clip 端到端验证时，要用户目检 = 必经环节**——Pic4 clip1 跑通后 vision 自检全过但用户目检发现"内容是 Welcome"。**修复方向**：① 单 Clip 跑通 → 不直接发"继续跑剩下 8 段"，**先等用户目检确认** ② 主 agent 必说"我打算：发您单 Clip → 等您目检 → OK 再批量"。**反模式**：单 Clip 跑通就接着批量跑（Pic4 v1.0.2 实战差点触发）。**判断口诀**：**"单 Clip 端到端 = 等用户目检 = 不批量跑"** |
| **66**（v1.0.3+pic12 实战新增 · 2026-06-07 · **绘本情绪基调 = 输入约束，不是 skill 能修的**）| **v15 模板"表情=变量"可驱动 seedance 改表情，但改不了画面骨架**——Pic4 No 绘本 9 段图本身就是"严肃警告"风格（棕熊 Stop 手势+悬崖警告牌+两猫打架+灰机器警告三角），**v15 段 1 主体定义的"表情"变量**可以驱动 seedance 在视频里把"严肃"改成"慈爱/温柔坚定/担心/保护"（Pic4 v3 prompt 9 段手写实战 = 把 5 段负面情绪 100% 替换为温柔），**但改不了**"悬崖警告牌" → "远方风景"。**根因**：seedance 是图生视频，**原图定了视觉骨架**，prompt 只能调"动作/光线/表情/镜头"幅度，不能换场景。**绘本情绪基调** = **绘本方选图时定**的输入约束，**不是 skill 能修的**。**修复方向**：① **绘本选材时必问调性**（启动前 6 必问加 #7 调性预审——绘本方选图情绪 vs 用户期望情绪是否一致）② v15 段 1 表情变量是 **"温度调节器"**（严肃↔温柔），不是"换场景器" ③ 接受现状判定：**绘本方用"威胁"画"为什么不能"** vs **理想 "温柔坚定"** 的差距 = **绘本选材问题**——选材阶段解决，不是 prompt 阶段。**判断口诀**：**"v15 表情变量 = 温度调节器 ≠ 换场景器 · 调性错位 = 选材问题"** |
| **67**（v1.0.3+pic12 实战新增 · 2026-06-07 · **用户对绘本情绪基调的反馈必追问根因**）| **当用户说"情绪不对"时，主 agent 必追问"严肃 vs 温柔的差距是大还是小"**——Pic4 No 绘本 v3 重设计实战中，用户**两轮反馈**才让根因浮出：第一轮"情绪太严肃" → 第二轮"可以通过提示词控制表情" → 才点出 v15 段 1 表情变量的能力。**反模式**：用户说"情绪不对"立即给方案（不追问）→ 给的方案可能不解决根因（v3 实战差点触发——用户原话"不要给我相邻概念"）。**修复方向**：① 用户提"情绪"反馈时必先**情绪诊断表**（9 段每段的严肃/温柔/恐吓判定）② 必问"绘本方选图情绪 vs 你期望情绪差距是大是小" ③ 差距小 → v15 表情变量"温度调节"可救；差距大 → 选材问题。**判断口诀**：**"用户说情绪不对 = 先诊断 + 追问差距大小 = 再给方案"** |
| **68**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v3 重设计 = 必重发 C 子 agent**）| **prompt 重设计（含表情/动作/末帧/风格四联动）= 重发 C 子 agent，主 agent 不手写 9 段 prompt**——Pic4 No 绘本 v3 实战中，主 agent 第一次越界：手写 9 段 v3 prompt（re.sub 批量替换 v1 prompt 加 soften + 占位段 + style 词），用户直接纠错"**写 prompt 应该让子 agent 去做吧**"。**反模式**：① 主 agent 用 re.sub/正则批量改 prompt（容易破坏结构 + 拼出语法断裂）② 主 agent 手写 9 段 prompt 看起来"快"但**违反"看图产分镜"是 C 的核心职责**（v15 段 1 表情 = vision 分析后决定，不是主 agent 凭印象）。**修复方向**：① 用户提"重设计"或"再跑一版"时，**主 agent 必重发 C**（不是手写）② 重发 C 时 brief 必含"v3 设计目标"（表情软化方向 + 动作软化方向 + 末帧软化方向 + style 词追加）③ C 必**重新看 9 张图**（vision_analyze 1-9.jpg）验证原图严肃程度，软化幅度合理（不能完全脱离原图）④ 主 agent 拿到 C v3 JSON 后**走 fill_v15_v3.py**（或修改 fill_v15_template.py 加 v3 入口）填 9 段终稿 prompt。**判断口诀**：**"prompt 重设计 = 重发 C · 不主 agent 手写"** |
| **69**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v5 节奏公式 · 用户两步推导**）| **总时长 = 朗读完最低 3s + 末帧静默 ≥ 2s（用户底线）**——Pic4 No 绘本 v3 跑通后用户反馈"末帧仍然太短"，原话两步推导：①"拆解镜头过后，把旁白的时长包含在里面，3秒是可以把这个旁白讲完的。那么说我们最低就是3秒。" ②"再增加我们预留的用户消化、读者消化的时长，可能要预留2秒。"。**v5 公式**：极短档 5s（0.7s 朗读 + 3s 起步 + 2s 静默）· 短句档 6s（2.1s 朗读 + 4s 起步 + 2s 静默）· 中句档 7s（2.9s + 5s + 2s）· 长句档 8s（3.6s + 6s + 2s）· **末帧静默 2.9-3.8s**（全部 ≥ 2s 底线）· **总时长 56s**（v3 48s +8s）。**与 v3 对比**：末帧静默从 1.5-2.5s 升到 2.9-3.8s（**末帧微动必填 4-6 元素**），镜头数从 3-4 减到 2-3（铺垫"建立+跃入"合并）。**修复方向**：① B 干 narration-quantization.json **silence_rationale 必填**"v5 公式步骤 2 用户底线 ≥ 2s"（铁律 #64 强化）② 主 agent 收到 B 输出后**必查 silence_recommendation_seconds ≥ 2s**（不达 = 重发 B）③ C 干 end_frame_microaction.specific_motion 必填 4-6 个微动元素（2-4s 静默时间有持续微动 = 不定帧）。**判断口诀**：**"v5 = 朗读完最低 3s + 末帧静默 ≥ 2s"** · **"末帧静默 < 2s = 翻车征兆"** · **详细实战数据**见 `references/2026-06-07-pic4-no-v5-rhythm-formula.md` |
| **70**（v1.0.3+pic12 实战新增 · 2026-06-07 · **绘本情绪基调 = 选材约束 · v15 表情变量是温度调节器不是换场景器**）| **v15 段 1 表情变量 ≠ 改场景**——Pic4 No 绘本 v3 实战：原图是"棕熊 Stop 手势+悬崖警告牌+两猫打架+灰机器警告三角"（严肃警告），v3 prompt 把 5 段负面表情软化为"慈爱/温柔坚定/担心/保护"，**但改不了**"悬崖警告牌 → 远方风景"。**根因**：seedance 是图生视频，**原图定了视觉骨架**，prompt 只能调"动作/光线/表情/镜头"幅度，不能换场景。**v15 段 1 表情变量 = 温度调节器**（严肃↔温柔），**不是换场景器**。**绘本情绪基调 = 选材约束**（绘本方选图时定），**不是 skill 能修的**。**修复方向**：① 启动前 6 必问加 #7 调性预审（绘本方选图情绪 vs 用户期望情绪是否一致）② 差距小 → v15 表情变量"温度调节"可救；差距大 → 选材问题。**判断口诀**：**"v15 表情变量 = 温度调节器 ≠ 换场景器 · 调性错位 = 选材问题"** · **"绘本方用威胁画为什么不能 vs 理想温柔坚定 = 选材问题 = 选材阶段解决"** |
| **71**（v1.0.3+pic12 实战新增 · 2026-06-07 · **chevereto 挂了用 uguu + 直接 curl 调 ark API 兜底**）| **seedance.py 硬编码 chevereto = 单点故障**——Pic4 v1 跑通后 chevereto 图床挂了（curl 6 次全 timeout），seedance.py create 内部走 chevereto 上传 = 所有 seedance 调用全失败。**uguu 兜底路线**：① 上传图片到 `https://uguu.se/upload.php`（multipart field 名 `files[]` 带方括号，**不是** `file`）→ 拿 `files[0].url`（直链 `n.uguu.se`）② 直接调 ark API `POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks`（带 Bearer token + JSON body）③ 等 succeeded → 从 `content.video_url` 下载（用 urllib 不用 curl，URL 跟 X-Tos-Signature 时效约 24h）④ 已实测 wrapper：`uguu_ark_wrapper.py`（一次性跑 1 段）+ `run_v3_clip23.py`（批量跑 2 段）跑通。**修复方向**：① 未来 seedance.py 改支持多图床（chevereto + uguu 切换）② 兜底脚本纳入 `seedance2.0-tool/scripts/` 目录（见 `references/public-file-hosting-fallback.md` 已沉淀）③ 主 agent 跑视频前**不依赖** seedance.py 单一图床。**判断口诀**：**"chevereto 挂了 = uguu 兜底 = 直接 curl 调 ark API"** |
| **72**（v1.0.3+pic12 实战新增 · 2026-06-07 · **seedance 整数时长铁律**）| **seedance 不生成小数时长**（用户 2026-06-07 原话）——"生成的实际上是六秒，模型不会生成小数点最后的，比如说五点五秒，它只要超出了五秒，比如五点一秒，它肯定就生成了六秒，所以计算时长的时候必须是整数，精确到整数，没有小数点。" **根因**：seedance API 实际生成时长 = ceiling(设计时长) = 整数。**Pic4 v3 翻车实战**：v3 设计 5.5s 短句档 → 实际跑 6s → 5.5s 装不下 6s 实际内容 → 镜头被压缩 → 末帧静默才 1.5s（远不够 2s 底线）。**修复方向**：① **设计时长必须 = 整数**（5/6/7/8/9/10），**不能用 5.5/4.5/6.5** ② C 子 agent time_breakdown.end_time 必填整数结尾 ③ B 子 agent total_duration_seconds 必填整数 ④ 验证脚本：v6 公式 = 极短 5s / 短句 6s / 中句 7s / 长句 8s（v5 设计 5.5s 错 → v6 全整数对）。**判断口诀**：**"seedance 时长 = ceiling(设计) = 整数"** · **"5.5s → 6s 实跑 = 0.5s 浪费 = 镜头被压缩"** |
| **73**（v1.0.3+pic12 实战新增 · 2026-06-07 · **彩色文字全程可见铁律**）| **领读绘本彩色文字 = 领读锚点，不是装饰**（用户 2026-06-07 原话）——"彩色文字没有保持，一闪而过就没有了，用户根本看不清。大多数情况下，彩色文字可以更长时间的展示，或者说一直出现在画面中都是可以的，当然最好能够给它设计一些动画，这个彩色文字是最好的。你要知道，领读绘本彩色文字参考图片中的彩色文字实际上是很重要的。" **根因**：v3-v5 prompt 写"文字位置锁定在顶部 1/6 画面不要重新生成"——seedance 实际跑**只在前 1-2s 保持**，之后 4-6s 文字消失 = 失去领读锚点。**修复方向**：① 文字**全程可见**（从 t=0 到 t=末帧 5-8s）② 文字有**微动画**：每字轻微呼吸式明暗交替（0.5s/次）+ 字符顺序浮现（按朗读节奏 No→no→X，0.3s/字）③ 颜色+字体+位置全程锁定 ④ v15 模板**新增"文字持续可见段"**（5 段变 6 段结构）⑤ C 子 agent 必填 `text_visibility` 字段（full_clip_visible + micro_animation + position_locked + color_locked）⑥ 主 agent 填 v15 模板时**必加文字持续可见段**（scripts/fill_v15_v6.py 已实现）。**判断口诀**：**"领读绘本文字 = 领读锚点 · 全程可见 + 微动画 = 必填铁律"** |
| **74**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v5 节奏公式 = 用户两步推导**）| **总时长 = 朗读完最低 3s + 末帧静默 ≥ 2s**（用户 2026-06-07 原话两步推导）——"拆解镜头过后，把旁白的时长包含在里面，3秒是可以把这个旁白讲完的。那么说我们最低就是3秒。" + "再增加我们预留的用户消化、读者消化的时长，可能要预留2秒。那么说这个视频可能就是5秒钟。" **v5 公式**：极短档 5s（0.7s 朗读 + 3s 起步 + 2s 静默 = 末帧静默 3.8s）· 短句档 6s（2.1s + 4s + 2s = 2.9s）· 中句档 7s（2.9s + 5s + 2s = 3.1s）· 长句档 8s（3.6s + 6s + 2s = 3.4s）。**修复方向**：① B 子 agent silence_rationale 必填"v5 公式步骤 2 用户底线 ≥ 2s"（铁律 #64 强化）② 主 agent 收 B 输出必查 silence_recommendation_seconds ≥ 2s（不达 = 重发 B）③ C 子 agent end_frame_microaction.specific_motion 必填 4-6 个微动元素（2-4s 静默时间有持续微动 = 不定帧）④ **整数时长铁律**结合（铁律 #72）：v5 公式本身就是整数 = 设计 = 实跑 = 0 浪费。**判断口诀**：**"v5 = 朗读完最低 3s + 末帧静默 ≥ 2s"** · **"末帧静默 < 2s = 翻车征兆"** |
| **75**（v1.0.3+pic12 实战新增 · 2026-06-07 · **fill_v15 模板脚本 = 标准工具**）| **`scripts/fill_v15_template.py` 是主 agent 拼 prompt 的标准工具**——v1.0.2 写就了，但 v3/v5/v6 实战都是临时写 fill_v15_v3/v5/v6.py。**Pic4 实战教训**：每次新增 v3/v5/v6 模板变体都新建一个文件（v1.0.2 → v1.0.3+pic12 共 4 个版本），导致脚本碎片化。**修复方向**：① 统一为 `scripts/fill_v15_template.py`，通过参数 `--version v3|v5|v6` 切换模板变体 ② **含 _parse_en_color 数据清洗函数**（铁律 #62 沉淀：text_position.en_color 必清洗为"主色名+色字结尾"）③ 模板版本号 = JSON 文件后缀（clip1-prompt-v3.txt / clip1-prompt-v5.txt / clip1-prompt-v6.txt）④ 主 agent 必用脚本填，不手写 9 段 prompt（防铁律 #68 主 agent 越界）。**判断口诀**：**"主 agent 填模板 = scripts/fill_v15_template.py · 不手写"** |
| **76**（v1.0.3+pic12 实战新增 · 2026-06-07 · **send_message 防串扰铁律**）| **发飞书视频附件 = 必附完整证据链**——Pic4 clip1 实际生成正确（md5 95323c4e 验证 No 内容）但首次 send_message 用户看到"Welcome"视频（send_message 串扰 / 飞书 client bug / 用户看历史消息）。**根因未实锤**但**修复路径已定**：① **发视频前必本地 stat+md5 校验**（终端 ls -lh + md5sum）② **消息里显式打 文件名 + md5 + task_id + seed + 时长**（让用户能 100% 验证）③ **同时落地磁盘 + 飞书云盘**（用户可从云盘二次下载验证）④ **vision_analyze 跟人眼观感不一致时，以人眼为准**（vision 是辅助不是真理）。**Pic4 验证**：重发 1.jpg 原图（md5 8f693eda）+ 视频（md5 95323c4e）+ 4 个 fact 验证 + task_id → 用户确认实际是 No 内容。**判断口诀**：**"send_message 视频 = 必附 md5 + task_id 证据链"** |
| **77**（v1.0.3+pic12 实战新增 · 2026-06-07 · **v6 模板 = v15 4 段 + 文字持续可见段**）| **v15 模板 = 4 段 → v6 模板 = 5 段（第 5 段 = 文字持续可见段）**——v6 在 v15 段 2 末帧策略前**新增"文字持续可见段"**：参考图原有的所有文字（顶部 1/6 画面的{EN_WORD}和{ZH_WORD}字）从 t=0 到 t=末帧 全程可见，伴随微动画（每字呼吸式明暗交替 0.5s/次 + 字符顺序浮现按朗读节奏）。**修复方向**：① scripts/fill_v15_template.py v6 模式**自动插入文字持续可见段** ② C 子 agent 必填 text_visibility 字段（v6 新） ③ 主 agent 拼 v6 模板 = v15 4 段 + 文字持续可见段 = 5 段。**判断口诀**：**"v15 模板 = 4 段 / v6 模板 = 5 段（+ 文字持续可见）"** |
| **78**（v1.0.3+pic12 实战新增 · 2026-06-07 · **多版本原料 JSON 并存策略**）| **重设计 = 新建 vN.json，不覆盖原版**——Pic4 No 绘本实战中**并存 5 版原料 JSON**：clip{1-9}.json（v1 严肃） + clip{1-9}-v3.json（v3 温柔化） + clip{1-9}-v5.json（v5 节奏两步推导） + clip{1-9}-v6.json（v6 整数+文字全程） + 1 段手写 clip1-prompt-v3.txt（备份）。**修复方向**：① C 子 agent 重设计任务 brief 必说"不覆盖 v{N-1}.json，新建 vN.json" ② 主 agent 拼模板时**显式选版本**（`fill_v15_v6.py` 读 `clip1-v6.json`）③ 发飞书时**显式打版本号**（"v1 严肃版"/"v3 温柔化版"/"v5 节奏强化版"/"v6 整数+文字强化版"）让用户能区分。**判断口诀**：**"vN.json 不覆盖 v{N-1}.json · 发飞书必带版本号"** |
| **79**（v1.0.3+pic12 实战新增 · 2026-06-07 · **单 Clip 端到端验证 = 必经环节，不批量跳跑**）| **v1.0.2 实战差点踩坑**：单 Clip 跑通就接着批量跑剩下 8 段。**Pic4 修复**：clip1 跑通 → **先发飞书用户目检** → 等用户回复 OK → 再跑剩下 8 段。**修复方向**：① 主 agent 单 Clip 跑通必说"我打算：发您单 Clip → 等您目检 → OK 再批量" ② **不能自动连跑**（即使 v1 跑通也等用户确认）③ 这是**飞书视频交付**流程的铁律（不是 D 子 agent 内部）。**判断口诀**：**"单 Clip 端到端 = 等用户目检 = 不批量跑"** |
| **80**（v1.0.3+pic12 实战新增 · 2026-06-07 · **情绪基调 AI 判定铁律**）| **绘本情绪基调 = AI 判定标准 + 用户拍板，不硬编码"温柔化"**——用户 2026-06-07 二次纠错"光说 AI 判断不说标准，等于没说"。**根因**：原 v1.0.2 实战反推"温柔化"作硬规则 = 单题材（No 警示向）硬编码，不适用其他题材（温情向/冒险向/知识向/治愈向）。**修复方向**：① A 风格识别 agent **必跑 4 维加权判定标准**（题材类型 40% + 画面色彩 20% + 角色表情 20% + 叙事弧 20% → 加权算分）② **5 类题材 → 候选基调表**（警示向=温柔坚定/慈爱守护；温情向=慈爱温柔/欢喜陪伴；冒险向=兴奋勇敢/紧张期待；知识向=好奇探索/欢快轻松；治愈向=温暖陪伴/静谧安心）③ 输出 `emotion_tone_ai_recommendation` JSON 字段到 `style-recognition.json`（含 4 维分数 + 加权分 + 推理链 + 备选 3 个）④ **主 agent 必报用户拍板**（用固定话术：题材/色彩/表情/叙事 4 项分数 + 加权分 + 推荐主调 + 备选 + 拍板选项 A/B/C）⑤ 用户拍板后 → 主 agent 落 C JSON 的 `emotion_tone` 字段 → C 子 agent 写到 prompt ⑥ **不替用户决定**——AI 凭标准判定是输入，最终决策权归用户。**完整标准**：见 [references/emotion-tone-ai-judgment-standard.md](references/emotion-tone-ai-judgment-standard.md)。**判断口诀**：**"AI 按 4 维加权判定 + 主 agent 报用户拍板 + 不硬编码温柔化"** |
| **81**（v1.0.3+pic12 闭环新增 · 2026-06-07 · **大版本上线必跑清理 5 步**）| **实战+沉淀+清理+兜底文档 = 完整闭环**——v1.0.2 → v1.0.3 升级只做了前 2 步，**留下了 410M 散落文件**（9 个 pic 项目目录 + /tmp 测试文件），干扰后续调试。**修复方向**：**任何 v1.0.x 大版本 PR merged 后必跑清理 5 步**（① dry-run 盘点 ② 必问用户保留项 ③ rm -rf 执行 ④ /tmp 兜底文档搬到 skill 仓 ⑤ 写清理记录 + commit + push）。**约束**：不可逆操作必问 / 保留空目录 / /tmp 不算保留。**完整工作流**：见 [references/v1.0.3-pic12-closure-loop.md](references/v1.0.3-pic12-closure-loop.md) §阶段 3。**判断口诀**：**"PR merged ≠ 闭环 · 必跑清理 5 步 + 兜底文档搬入 skill 仓"** |
| **82**（v1.0.3+pic12 闭环新增 · 2026-06-07 · **3 文档同步修改反模式**）| **v1.0.x 升级时硬编码值出现在多文档 = 必同步修改所有文档**——本次 v1.0.3+pic12 把"温柔化"硬编码从 v1.0.2 实战反推作规则，**但同时出现在 3 个文件**：SKILL.md 铁律 + references/v1.0.3-pic12-optimization-plan.md 1.1 节 + references/2026-06-07-pic4-no-validation.md 9 节铁律表 + 实战报告 v6 细节多处。**修复方向**：**v1.0.x 升级时必先盘点硬编码值出现位置**（grep 关键词）→ **统一一次性修完** → 验证 `git grep` 无残留。**反模式**：① 只改主 SKILL.md 忘了 references（references 会跟 SKILL.md 不一致）② 只改 references 忘了 SKILL.md（下次 commit 时旧版规则回潮）③ 用单一文件当"事实来源"——**skill 仓的所有文档都是事实**。**判断口诀**：**"grep 硬编码值在所有文档出现位置 → 同步修改 → git grep 验证 0 残留"** |
| **86**（v1.0.3+pic13 实战新增 · 2026-06-08 · **fill_v15 兜底词硬编码复发铁律**）| **scripts/fill_v15_template.py 兜底词禁止 hardcode 任何具体词/颜色/对象**——Pic6 Cow 实战踩坑：原 `_build_text_visibility_segment` L141-142 + 主 fill 函数 L225 兜底 hardcode `'bird'` / `'鸟'`（Pic5 Bird 残留数据）→ 跑 Cow 绘本 clip1 段 5 → 文字持续可见段全变 `"bird"/"鸟"`（静默错位无报错）。**修复方向**：① `_build_text_visibility_segment` 加 `en_word_fallback` / `zh_word_fallback` 参数（默认空字符串让字段空缺显形）② 主 `fill_v6_template` 兜底改从 `clip.narration_text` 动态提取（**不** hardcode 任何具体词）③ 调用方传 `en_word=en_word, zh_word=zh_word` 到 segment 函数。**反模式**：① 修了 `--project-dir` 忘了兜底词（路径参数化 ≠ 兜底词参数化）② 兜底词改从 narration_text 末尾提取（Pic6 clip1 翻车：narration 末尾"COW!" → zh_word="COW" 语法错位）。**新约定**：C 子 agent 必填 `text_position.en_word` / `text_position.zh_word`（明确主题词），主 agent 必查非空（不达 = 重发 C）。**判断口诀**：**"fill 兜底看到任何 'bird'/'鸟'/'cow' 等具体词 = 立刻参数化或清空，不 hardcode"** · **详细实战数据**见 [references/2026-06-08-pic6-cow-validation.md](references/2026-06-08-pic6-cow-validation.md) |
| **87**（v1.0.3+pic13 实战新增 · 2026-06-08 · **C 子 agent visual_features 嵌套 vs 顶层 schema**）| **C 子 agent 输出的 visual_features 字段在 characters[].visual_features 不是顶层**——Pic6 Cow 实战 schema 验证教训：主 agent 用 `if 'visual_features' not in clip` 查顶层 → 8/8 missing → 误以为 C 失败，实际是 C 把视觉特征嵌套在 `characters[]` 数组里。**修复方向**：① C 子 agent SKILL.md 必显式写字段命名（嵌套 vs 顶层）② 主 agent 验证 schema 时**遍历所有可能命名**（`clip.visual_features` + `clip.characters[].visual_features`）③ 输出 C 验证脚本到 `scripts/validate_c_schema.py` 自动检查两种位置。**反模式**：① 凭印象写 schema 验证逻辑（没看实际 C 输出）② 把"schema 缺失"误判为"C 失败"导致重发 C。**判断口诀**：**"C 输出 visual_features 必查 characters[] 嵌套 + 顶层双位置"** |
| **84**（v1.0.3+pic13 实战新增 · 2026-06-07 · **v6 模板首次跑通 8 段**）| **v6 = v15 4 段 + 文字持续可见段**（铁律 #77 实战验证）——Pic5 Bird 鸟 8 段端到端跑通：**8/8 succeeded · 整数时长 0 错位 · 50.66s**。**v6 第 5 段 = 文字持续可见段**（铁律 #73）：① 顶部 1/6 文字 t=0 到 t=末帧全程可见 ② 每字呼吸式明暗交替 0.5s/次 ③ 字符顺序浮现按朗读节奏（b→i→r→d→鸟）④ 整体轻微浮动 0.3s/次。**Pic5 主 agent 脚本填模板 = 8 段 100% 一致 · 0 行 drift**（平均 1266 chars/clip）。**判断口诀**：**"v6 5 段 = v15 4 段 + 文字持续可见段"** · **详细实战数据**见 `references/2026-06-07-pic5-bird-validation.md` |
| **85**（v1.0.3+pic13 实战新增 · 2026-06-07 · **8 task 并行轮询边界**）| **D 仅做生成（不抽帧不 vision）= 8 task 并行轮询可行**（Pic5 Bird 实测 7 分钟完成 8 段）——8 串行提交 + 8 后台并行 30 轮 × 15s 轮询。**对比**：Pic2 v1.0.0 = 8 串行 + 4 批顺序轮询 ~15 min；Pic5 v1.0.3+pic13 = 8 串行 + 8 并行轮询 ~7 min = **优化 53%**。**边界**：① D 纯生成（不抽帧不 vision）= 8 并行可行 ② D + 抽帧 + vision = 仍走 ≤2/批（Pic2 v1.0.0 教训）。**shell 模板**：`for TID in ${TASK_IDS[@]}; do poll_task $TID > /tmp/poll_${TID}.log 2>&1 & done; wait`。**判断口诀**：**"D 纯生成 = 8 并行 · D+抽帧+vision = ≤2/批"** |
| **86**（v1.0.3+pic13 实战新增 · 2026-06-08 · **声音策略分支 · 不破坏 4 维控制底层核心**）| **家族词组集合（≥3 词 + 同字母家族重复）/ 长句（words_en ≥ 5 / words_zh ≥ 8）= 不生成发音 + TTS 音轨对齐**（用户 Pic6 clip7 原话："像这种家族词组的集合，在视频里不需要生成发音，用 TTS 音频来做对齐就可以了...但是我并不想破坏底层核心啊"）。**根因**：seedance `--generate-audio true` 家族词组易重复发/抢节奏/发音错位；长句易吞字/抢拍。**修复方向**：① 4 维控制（时间/风格/角色/声音）**底层核心不动**——仅在**声音维度**加分支判断 ② seedance 命令：`--generate-audio false` + `--audio` 传 TTS mp3 路径 ③ 段 4 prompt 写"不发音·保留 TTS 音轨占位·时长匹配" ④ 段 5 文字持续可见 + 关闭拟声。**判定优先级**：家族词组 > 长句 > 普通短句/单词。**反模式**：① 把"不发音"作默认策略（普通短句被剥夺拟声 = 翻车）② 硬编码到 v6 段 4 模板（破坏通用性）③ 一刀切 `--generate-audio false`（全部静音 = 翻车）。**完整规范**见 [references/sound-strategy-branches.md](references/sound-strategy-branches.md)（v1.0.3+pic13 新增 · Pic6 实战沉淀）。**判断口诀**：**"家族词组/长句 = 不生成发音 + TTS 对齐 · 4 维底层核心不动"** |
| **87**（v1.0.3+pic13 实战新增 · 2026-06-08 · **主 agent 跑完 D = 直接发视频 = 不主动抽帧自检**）| **用户 Pic6 实战明确纠错原话**：「clip1 视频没有问题，你以后不要主动抽帧检查，直接把视频发给我就行了。」**修复方向**：① 主 agent 跑完 D → **直接发飞书 + 完整证据链**（文件名 + md5 + task_id + seed + 时长）→ 等用户目检（**不抽帧自检**）② `vision_analyze` 只在用户主动要求或 vision 跟人眼观感不一致时用 ③ 跟铁律 #29 协同：#29 不抽帧发飞书 / #87 不抽帧填表 ④ D 子 agent 同样适用（D 不再 vision_analyze）。**Pic6 翻车**：clip1 跑通后我主动用 `vision_analyze` × 3 帧（t=0.5/2.5/4.5）自检并填"vision 自检 3 帧"段给用户看 = **反模式**（用户目检视频 = 唯一标准，vision 是辅助不是真理，详见铁律 #63）。**判断口诀**：**"D 跑完 = 发视频 = 等用户目检 = 不抽帧"** |
| **88**（v1.0.3+pic13 实战新增 · 2026-06-08 · **fill_v15 模板兜底硬编码修复 · 双重兜底链**）| **Pic6 Cow 实战翻车**：`fill_v15_template.py` 段 5 文字持续可见段硬编码 `tp.get('en_word', 'bird')` + `tp.get('zh_word', '鸟')`（Pic5 Bird 残留数据），导致非 Bird 绘本 clip1 全变 "bird/鸟"。**修复方向**（v1.0.3+pic13 沉淀）：① `_build_text_visibility_segment(tp, target_word, en_word_fallback='', zh_word_fallback='')` **新增双参数** ② 主 fill 函数兜底从 `clip.narration_text.en/zh` 末尾词**动态提取**（非 hardcode 'bird'/'鸟'）③ 调用方传 `en_word_fallback=en_word, zh_word_fallback=zh_word`。**验证**：`grep "bird\|鸟" clip*-prompt.txt` → ✅ 0 残留。**与铁律 #75 区别**：#75 解决 per-book 脚本碎片化（fill_v6_bird.py 等）；#88 解决模板内部 hardcode（fill_v15_template.py 内部 `_build_text_visibility_segment` 兜底硬编码）。**判断口诀**：**"填模板兜底 = 动态从 narration 提取 · 不 hardcode 任何绘本主题词"** |
| **89**（v1.0.3+pic13 实战新增 · 2026-06-09 · **v7 范式 ≠ v15 4 段 · 主 agent 直拼不调 C**）| **领读绘本走 `leading-reading-4clip-pattern.md` 路径 = v7 范式 = 主 agent 直接拼 prompt · 不调 C 子 agent**。**根因**：C 子 agent SKILL.md v1.0.3+pic12 强约束"v15 4 段骨架 = C 产原料 + 主 agent 填模板"，**v7 范式是另一条路**：① 2图=1Clip 合并（最多 2 张图跨场景合并）② 8 段固定结构（`This is a storyboard reference image sequence` + `from X.Xs to Y.Ys @ImageN` 镜头 + `final frame` + `Storyboard Audio Description` + `No background music` + `Children's picture book ... style` + 句号）③ 必填参数 `--image` + `--last-frame` + `--generate-audio true` ④ 真模板 = `assets/example-prompts/cactus-clip1-v7.txt`（11 项自检全过）⑤ v7 范式 4 段总时长公式 = 8s + 8s + 9s + 10s = 35s（标准）/ 8s + 9s + 10s + 10s = 37s（TTS 优先不压缩）。**判断口诀**：**"v7 范式 = 领读型 2图=1Clip 合并 = 主 agent 直拼 = 不调 C"**。**反模式**：① 调 C 子 agent 拼 v7 prompt（C 只懂 v15 4 段，强行套会拼出错的 prompt 结构）② 把"5 段 v7 合并"硬塞进 v15 4 段模板（破坏 v7 范式 8 段结构）。**触发条件**：绘本是领读/认知/认字型 + 弱情节 + 旁白每段 < 8s + 图片风格统一 + 总图数 6-10 张 = **5 条全过才走 v7**。**详细实战**见 `references/leading-reading-4clip-pattern.md`（必读）+ `assets/example-prompts/cactus-clip1-v7.txt`（真模板） |
| **90**（v1.0.3+pic13 实战新增 · 2026-06-09 · **节奏档位 8s 不是天花板 · 真正上限是 15s seedance**）| **v5 公式默认档位 5/6/7/8s 是参考范围，不是上限**。**真正硬上限 = seedance API 物理 15s**。**Pic7 Horse 实战翻车**：用户给 R7 14s（实测 TTS），主 agent 看到 "8s 是默认最大档" 误判 "14s 超 8s = 必拆" 给出 3 个不可行方案，浪费 4 轮对话。**真相**：v15.1 拆分规范 `references/长旁白拆分规范-v15.1.md` 写明"必须拆 = > 8s + > 10s 留白 = > 15s 上限"——**触发 = > 15s**，不是 > 8s。8s < 14s ≤ 15s **完全合法**（单 Clip 14s）。**修复方向**：① 看到 14s / 13s / 12s 等长于默认 8s 的 Clip **不立即报"必拆"**——先查 seedance 15s 物理上限 ② 5/6/7/8 默认档是 v5 公式的"节奏档位表"参考范围（v5 = 朗读完最低 3s + 末帧静默 ≥ 2s），不是天花板 ③ 8-15s 之间是"扩展长句档"= 直接用整数 Clip 时长（v7 范式 Clip 4 收势 10s 验证）。**判断口诀**：**"8s 默认上限 = 误读 · 15s seedance = 真正天花板 · 8s < x ≤ 15s = 合法"** |
| **91**（v1.0.3+pic13 实战新增 · 2026-06-09 · **用户提供 MP3 必先问用途 · 不默认 TTS**）| **用户提供 MP3 必先问是什么，不默认 TTS 抽时长**。**Pic7 Horse 实战翻车**：用户提供 `Horse 马.mp3`，主 agent 凭印象把它当 TTS，跑 `ffmpeg silencedetect` 想抽 8 段时长，结果整段 90.15s 零静音（全连续朗读），ffprobe 全段 90.15s · silencedetect -20dB 才 2 段 — 浪费时间 + 给用户错觉"我能抽 TTS 段时长"。**真相**：用户的 MP3 是**完整成品音频**（后期混音），不是按段分开的 TTS 干声。**修复方向**：① **必先问**"这 MP3 是 TTS 干声还是完整成品音频" ② **不默认**走 TTS 抽时长路径 ③ TTS 抽时长需要"每段一个独立 MP3"或"silence 分段明显的干声"——用户没明确说"是分段 TTS 干声" = **走兜底公式（1.4 词/秒）** ④ 兜底公式对 8 段绘本 ± 30% 误差可接受（Pic7 误差 0.7s 不影响整数档位）。**判断口诀**：**"用户给 MP3 = 必问 TTS 干声还是完整音频 · 不默认 TTS 抽时长"** |
| **92**（v1.0.3+pic13 实战新增 · 2026-06-09 · **用户硬约束打架时老实报告 · 不硬凑**）| **用户给的多个硬约束物理装不下时，老实报告 3 选 1，不硬凑反模式方案**。**Pic7 Horse 实战翻车**：用户给"① 压缩短句 ② R7 = 14s ③ 总时长 ≈ 43s"三个约束，主 agent 算出"51s 装不下 → 必拆 R7 → 给 3 个反模式方案"——**用户原话"这个规则有问题：v5 公式默认档位最大 8s"** 直接拍掉。**根因**：v5 公式 5/6/7/8s 是默认档位**不是上限**（见铁律 #90），14s 单 Clip 完全合法。**修复方向**：① 用户给硬约束时**先算"约束是否物理兼容"**——不兼容 = 老实报告"3 个约束互相打架，你看放弃哪个" ② 不硬凑"压缩到 4s 末帧静默 0.7s 翻车征兆"这种"看起来 OK 实际违规"的方案 ③ 不凭印象判断约束边界（"8s 是上限"是凭印象，**查 skill 仓 references/长旁白拆分规范-v15.1.md** 才知道真实上限 15s）。**判断口诀**：**"用户硬约束打架 = 老实报告 = 不硬凑 · 边界判定必查 skill 仓"** |
| **75 强化**（v1.0.3+pic13 实战新增 · 2026-06-07 · **fill_v6_bird.py 复发反模式**）| **`scripts/fill_v15_template.py` 必支持 (book, version) 双维度参数化**——Pic5 Bird 又新建 `fill_v6_bird.py`（per-book 硬编码）= **铁律 #75 未根治**。**修复方向**：① 统一为 `scripts/fill_v15_template.py --book <book> --version v3|v5|v6` 命令行参数化 ② 主 agent 必查脚本是否支持当前组合 → 不支持 **patch** 而非新建 ③ 模板变体（v3/v5/v6）+ 绘本变体（No/Welcome/Bird/下本）= 双维度参数化 ④ 下次 Pic6 跑通时必用 `python3 scripts/fill_v15_template.py --book <book> --version v6 --clips-dir <dir>`。**反模式**：每本新绘本都新建 per-book 脚本（Pic3→Pic4→Pic5 共 3 个版本复发）。**判断口诀**：**"填模板 = scripts/fill_v15_template.py --book X --version v6"** |
| **93**（v1.0.3+pic14 实战新增 · 2026-06-09 · **Pic7 Horse · v15 + 2图=1Clip 兼容**）| **v15 4 段范式 = 同时支持单图 + 2图=1Clip 合并**（用户原话："v15 和 v7 实际上是可以兼容的，并不是二选一"）。**根因**：之前我误判 v15 范式只支持单图 @ImageN，**实际**：v15 4 段骨架里的"分镜描述段"（段 3）天然支持多图引用，**fill_v15_template.py 拼出的 prompt 自动把 image_index 字段拼成 `@Image1+2` 形式**（双图合并的 image_index 字段是 "1+2" 字符串）。**修复方向**：① fill 脚本填出来的 `@Image1+2` **不是 seedance 官方语法**——**主 agent 必后处理**：把 `@Image1+2` 拆成 `@Image1` + `@Image2`（单图合并的 `@Image1+2` → `@Image1`）② 拆分依据：读 `clip.image_files.first_frame` + `last_frame`，相同 = 单图保留单 N；不同 = 拆成双 N ③ **seedance 命令**：用 `--ref-images 1.jpg 2.jpg`（v15 范式多图参考），**不**用 `--image` + `--last-frame`（v3/v8 范式首尾帧）④ 跑通实测：Pic7 Horse 5 段 5/5 succeeded · 48s · 5 task_id · md5 校验全过。**反模式**：① 看到 fill 输出 `@Image1+2` 直接发给 seedance（可能不识别）② 看到双图合并改用 v3/v8 `--image` + `--last-frame` 范式（破坏 v15 4 段骨架 + 写不出 v6 5 段文字持续可见段）③ 拆 1图/2图手动查拼不自动化。**自动化代码**（主 agent 必用）：```python\nimport json; from pathlib import Path\nfor p in Path('clips').glob('clip*-prompt.txt'):\n    j = json.loads(p.with_name(p.stem+'.json').read_text())\n    first, last = j['image_files']['first_frame'], j['image_files']['last_frame']\n    n1 = first.replace('.jpg',''); n2 = last.replace('.jpg','')\n    text = p.read_text()\n    text = text.replace('@Image1+2', f'@Image{n1}' if n1==n2 else f'@Image{n1} + @Image{n2}')\n    p.write_text(text)\n```。**判断口诀**：**"v15 4 段 = 兼容单图 + 双图 = `@Image1+2` 拆成 `@ImageN` / `@ImageN + @ImageM`"** |
| **86**（v1.0.3+pic13 实战新增 · 2026-06-08 · **声音策略分支 · 不破坏 4 维控制底层核心**）| **3 旁白类型 × 声音策略分支**——Pic6 Cow 牛 clip7 OW 家庭 5 词实战沉淀：用户原话「像这种家族词组的集合，在视频里不需要生成发音，用 TTS 音频来做对齐就可以了。但是我并不想破坏底层核心啊，这只适合这种家庭词组，或者说句子很长的时候的一种方式」。**判定标准**（不破坏 4 维控制·仅在声音维度加分支）：① **家族词组集合**（words_en ≥ 3 + 同字母家族重复如 OW/AY/EE）= `--generate-audio false` + TTS 音轨对齐 + 段 4 写"不发音·保留 TTS 音轨占位·时长匹配 TTS 实测" + 关闭拟声 ② **长句**（words_en ≥ 5 OR words_zh ≥ 8）= 同上 ③ **普通短句/单词** = seedance 自动生成发音（默认）= 不变。**Pic6 clip7 实战**：OW 5 词 → `--generate-audio false` → 视频跑通 0 重复发音 + 末帧微动 100% 保留 + 时长 10.10s = 设计 10s（铁律 #72 整数）。**判定函数**（B 旁白量化用）：见 `references/sound-strategy-branches.md` §4 `detect_sound_strategy()`。**反模式**：① 把"不发音+TTS 对齐"作默认策略 = 普通短句被剥夺拟声 = "moo!" 单音节拟声 = 知识向核心被毁 ② 硬编码到 v6 段 4 模板 = 破坏通用性 ③ 一刀切 `--generate-audio false` = 全部静音 = 翻车 ④ 改 4 维控制底层核心 = 破坏通用框架。**判断口诀**：**"4 维核心 = 不动 · 声音维度 = 加分支"** · 详细实战数据见 `references/sound-strategy-branches.md` |
| **87**（v1.0.3+pic13 实战新增 · 2026-06-08 · **用户明确纠错：主 agent 不主动抽帧自检**）| **Pic6 clip1 实战踩坑**：我跑完 clip1 后主动用 `vision_analyze` × 3 帧自检（t=0.5/2.5/4.5），抽 6 张图喂给主 agent 上下文污染 + 用户体感"我被绕了一道弯"（视频里看到的我要看，视频外加的画面报告对我来说是噪音）。**用户原话（2026-06-08）**：「**你以后不要主动抽帧检查，直接把视频发给我就行了。**」**修复**：① **主 agent 跑完 D → 直接发视频 → 等用户目检（不抽帧自检）** ② `vision_analyze` 只在 vision 跟人眼观感不一致时由**用户主动要求**才用（铁律 #63 实战经验）③ 跟铁律 #29 协同：#29 是"不抽帧发飞书"（不发 1 帧图当预览），#87 是"不抽帧填表"（不在汇报里加 vision 自检段）。**反模式**：① 跑完视频主动 `vision_analyze` 4 帧 ② 抽 1 帧图当预览发飞书 ③ 报告里加"vision 自检 3 帧"段（"t=0.5s ✅ / t=2.5s ❌ / t=4.5s ❌" 这种格式 = 用户没让我看）。**判断口诀**：**"跑完 = 发视频 = 不自检"** · **"vision 自检 = 用户主动要求才用"** |
| **83**（v1.0.3+pic12 闭环新增 · 2026-06-07 · **memory 导航图原则**）| **memory 只记导航，详细规则在 skill 仓**——用户 2026-06-07 纠错"memory 里只告诉 AI 去哪里看"= SOUL.md 写的"memory 是导航图不是完整答案"必须真正落地。**反模式**：① 把 skill 仓的 21 铁律 + 4 维原理 + 实战数据**复制进 memory**（双倍维护成本 + 后续 skill 升级 memory 跟不上的风险）② memory 容量超 2,200 字符硬限（HERMES 内置）。**正确做法**：memory 写**高频 skill 仓导航链接**（如"[picturebook-video](~/.hermes/profiles/huiben/skills/creative/picturebook-video/SKILL.md)"）+ 极少量跨会话必用核心（用户偏好 / HOME 沙盒 / 多 Agent 协作 / AI 进化机制）。**判断口诀**：**"想写 memory 时先问：这条信息在某个 skill 仓里已经有了吗？有就只写导航不写内容"** |
| **84**（v1.0.3+pic12 实战新增 · 2026-06-07 · **fill_v15 脚本硬编码铁律**）| **scripts/fill_v15_template.py 禁止硬编码 pic4 路径/clip 数量/tone**——Pic5 Bird 实战踩坑：原 fill_v15_template.py `ROOT = Path("/home/luo/huiben-projects/20260607-pic4-compress")` 硬编码 + `for i in range(1, 10)` 只支持 9 段 + `bg_mood = '严肃警示·温柔坚定'` 写死 Pic4 警示向。**Bird 必须从 0 写 fill_v6_bird.py**（额外 ~100 行复制粘贴）。**修复方向（v1.0.3+pic12 已沉淀）**：① 必加 `--project-dir` / `--version` / `--tone` CLI 参数（向后兼容旧默认调用）② 必用 `clips_dir.glob("clip*.json")` 自动数 clip ③ **en_color 字段必兼容两种格式**（`_parse_en_color` 字符串 + `_parse_en_color_pattern` 字典 + `_parse_en_color_smart` 智能路由）④ C 子 agent 输出 `visual_features` 字典 + 平铺 `color_details`/`texture` 必兼容（Bird C agent 用了平铺 = pic4 schema 失败）。**反模式**：① 主 agent 看到 fill 脚本写不动就**复制一个新文件**（fill_v6_bird.py / fill_v5.py / fill_v3.py 碎片化）② 修一个硬编码没修其他硬编码（路径修了忘 tone / 数量）。**判断口诀**：**"fill 脚本看到硬编码 ROOT/数量/tone/字段名 = 立刻参数化 + glob，不要复制"** |
## v1.0.2 实战对比（Pic2 vs Pic3 完整数据）

| 维度 | Pic2 (Please) | Pic3 (Welcome) | v15.2 改进 |
|---|---|---|---|
| 页数 | 8 | 9 | — |
| 场景对位 | 6/8 错位（玩具房当 eat）| 9/9 对位 | ✅ Step 0.5 拦截 |
| 节奏档位 | v1.0.1 修复后全对 | 全对 | ✅ 铁律 #54 闭环 |
| clip8/9 收势时长 | v1 11s 5 镜头→v2 6s 3 镜头 | **6s 3 镜头**（一次到位）| ✅ 铁律 #54 + #55 实战 |
| D 任务数 | 8 succeeded | 9 succeeded | ✅ |
| md5 错位 | 6/8 | **0/9** | ✅ 主索引聚合修复 |
| C self_check | 9/9（v1.0.0 错位·v1.0.1 修复）| 12/12 | ✅ 铁律 #55 实战 |
| C 子 agent timeout | 无 | timeout 但 9/9 JSON 写完 | ✅ 主 agent 续写主索引 |
| D 子 agent timeout | 无 | 600s 时 6/9 done | ✅ 主 agent 续跑 3/3 |
| 总时长 | 47s | **45s**（用户 TTS 估算）| ✅ 匹配 |
| 总镜头数 | 33 | 34 | — |

**详细实战数据**：见 [references/2026-06-07-pic3-welcome-validation.md](references/2026-06-07-pic3-welcome-validation.md)

---

## v1.0.0 实战翻车决策树（Pic2 8 Clip 实战沉淀）

**实战发现的核心矛盾**：C 子 agent self_check 9/9（**仅查文本合规**）≠ D 子 agent 实战 self_check 6/6（**查视频合规**）——C 子 agent 看不到 seedance 实际跑出来效果。

**v1.0.2 实战修正**（Pic3 9 Clip）：C self_check 12/12 + D seedance 9/9 succeeded = **C 文本合规 = D 视频合规**（v1.0.0 错位已修复，原因是 v1.0.1+pic10 的实战校准措辞补齐了 seedance 实战细节）。

**主 agent 翻车处理**：

| 翻车征兆 | 主 agent 决策 | 不该做什么 |
|---|---|---|
| frame_01 角色完全丢失 | **重发 C 改 prompt**（镜头一 1.5s）| 不擅自重跑 D |
| 文字消失 / 被吃 | **重发 C 改 prompt**（v3 措辞升级）| 不擅自重跑 D |
| 末帧定格海报 | **重发 C 改 prompt**（画面微动具体化）| 不擅自重跑 D |
| frame_03 镜头未推到特写 | **重发 C 改 prompt**（clip_narrative 必填）| 不擅自重跑 D |
| task failed | 不重试 D | 查 ark list 端点 |
| 角色闭嘴 vs 张嘴 | **接受**（绘本调性 = 温柔内敛，铁律 #42）| 不修 |
| evals 100% 命中 | **不**直接开 PR | **必须实战验证**（铁律 #49）|
| C 子 agent 600s timeout | **主 agent 续写主索引**（Python 聚合 clip1-9.json）| 不重发 C |
| D 子 agent 600s timeout | **主 agent 续跑未提交 Clip**（shell + seedance.py）| 不重发 D |
| **绘本原图场景错位** | **接受现状**（绘本方已发布）| **不重做绘本** |

**核心原则**：C 子 agent self_check 通过 ≠ 视频实际通过。**实测胜于 evals**。

## v1.0.0 实战 Pitfall 库

详见 [references/2026-06-06-v1-real-pitfalls.md](references/2026-06-06-v1-real-pitfalls.md)（6 个 Pitfall 库 + 修复优先级 + v1.1 待办）。

**6 个 Pitfall 速查**：

1. **画面在配音**（反 Cat v15 范式）→ C 子 agent 必填 clip_narrative 字段
2. **短档镜头一 1s 不够时间** → 短档 1-1-3-1 → 1.5-1-3-1.5
3. **C 子 agent self_check 只查文本合规** → C 必填 seedance_visual_checklist
4. **实战翻车不擅自重跑 D**（铁律 #45）→ 报回主 agent
5. **未实战验证不能开 PR**（铁律 #49）→ 实战拍板后再开
6. **视频交付不抽帧**（铁律 #29 强化）→ D 不发飞书 + 主 agent 不主动抽帧发

| **49**（新 · 2026-06-06 实战）| **C self_check ≠ seedance 实际输出合规** — C 检查"prompt 文本合规"，但不验证"seedance 是否真跑出对应效果"。**实战验证**：Pic2 Clip 1 C 9/9 ✓ → D 跑出来 5/6 false。**修复方向**：① 末帧微动细化为"末帧 1s 必须含 ≥1 个动作元素"（不只写"画面继续微动"）② 文字保留升级"锁定 top 1/6 画面不重绘"或改用 `--image` 首帧模式钉死构图 ③ 镜头一"切到全景"加约束"两兔必须完整可见" |
| **50**（新 · 2026-06-06 实战）| **D 子 agent 禁止一次跑全部 N 个 Clip** — Pic2 实测 D 跑 8 个 Clip × 提交+轮询+下载+抽帧+vision × 4 帧 = 600s 直接 timeout。**正确做法**：D 先跑 1 个 Clip 端到端验证，OK 后再批量；批量时限制 ≤3 个/批次（避免 timeout）|
| **51**（新 · 2026-06-06 实战）| **开 PR 前必做实战验证** — 用户原话："现在肯定不能跑 PR，我们都没有实测过，怎么能PR。" 任何重构/优化完成后，**先跑 1-2 个真实绘本出 mp4 看实际效果** → OK 才能开 PR。evals 验出来的 = prompt 草稿质量 ≠ 视频实际质量。**反模式**：evals 9 维度全胜就开 PR（Pic2 v1.0.0 实战翻车就是这个反模式差点触发）|
| **52**（新 · 2026-06-06 实战）| **节奏公式 = 动作成本相加，不是模板套数** — 用户原话："两秒就把话讲完了，那剩下那两秒是不是把节奏给拖慢了呢？"。**核心洞察**：每个节奏数字 = 该镜头动作/朗读/消化的实际成本（不是凭空加的）。`总时长 = 朗读 + 消化（≈朗读 × 1-2 倍）`。强行套模板（如 "Good afternoon" 1.5s 朗读套 6-7s 节奏 = 凭空加 4-5s 空镜 = 节奏拖慢）。**反模式**：把"标版" / 节奏公式当模板（v0.7.1+pic7 时代 v15.1 标版 2-1-3-3-3 套所有 Clip = 浪费）。**正确做法**：见 [references/2026-06-06-rhythm-action-cost.md](references/2026-06-06-rhythm-action-cost.md) — 节奏档位表 4 档（极短/短句/中句/长句），每档时长 = 该档朗读 + 消化实际成本求和 |
| **53**（新 · 2026-06-06 实战）| **Cat v15 范式精准度迁移** — 用户原话："对画面的镜头控制，画面的内容控制，特别是对clip做拆分的时候，那种控制，非常精准"。**Cat v15 范式精准 4 点**（v1.0.0 实战修复方向）= ① 拆 Clip 维度 = **语义块**（不是时间块）② 拟声 = **故事动作音**（pat 一响 = 猫掌落地，不是装饰音）③ 画面 vs 朗读 = **画面先讲语义，朗读强化读音**（不是"嘴巴半张开说 X"）④ 末帧 = **本 Clip 故事动作停留 + 目标词重读窗口 + 画面微动**。**Pic2 clip_narrative 必填**：每 Clip 1 句话描述本 Clip 故事动作，绑定目标词语义。详见 [references/2026-06-06-cat-v15-paradigm-precision.md](references/2026-06-06-cat-v15-paradigm-precision.md) |

---

## 相关 skill

- **子 agent A**：`storyboard-style`（风格识别）
- **子 agent B**：`storyboard-narration`（旁白量化）
- **子 agent C**：`storyboard-design`（分镜设计）
- **子 agent D**：`video-executor`（视频执行）
- **工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`
- **兄弟 skill**：`picturebook-creator`（绘本创作）/ `seedance2.0-tool`（视频底层工具）
