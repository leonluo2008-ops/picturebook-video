---
name: picturebook-video
description: "绘本转儿童动画视频一站式调度 skill（**v1.0.8+pic18 · Horse 绘本 5/5 succeeded 端到端实战验证 · Cat 范本对齐终极修复 · 5 词全对 + 零幻觉 + OR Family 完整**）。把绘本简介 + N 张图 + 旁白 → **Step 0 文件用途澄清** → **Step 0.5 场景对位检查** → **Step 1 启动前 7 必问 + #1.5 数字约束数学验证** → 调 A 风格识别 + B 旁白量化（主 agent 干 · 并行）→ **Step 3.0 范式路由**（v7 2图=1Clip 走主 agent 直拼 / v15 4 段走 C 子 agent）→ C 子 agent 产 11 维原料（**不写 prompt_draft**）→ **主 agent 填 v15/v6 模板 + 铁律 #93 自动拆 `@Image1+2` → `@ImageN` / `@ImageN + @ImageM`** → **Step 4.0 seedance 范式二选一**（v15 走 `--ref-images` / v7 走 `--image`+`--last-frame`）→ D ≤2/批 + 续跑 → 发飞书 + 完整证据链（铁律 #76）。**v1.0.3+pic12 实战新增**：v5 节奏公式（朗读完最低 3s + 末帧静默 ≥ 2s）+ v6 整数时长铁律（seedance 不生成小数时长）+ 彩色文字全程可见铁律（领读锚点不可一闪而过）+ uguu 兜底路线（chevereto 挂时备用）+ **9 条新铁律**（#63-#71）。**触发词**：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video、绘本做视频。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent, picturebook, v15-template, fill-v15, uguu-fallback, send-message-evidence, integer-duration, text-anchored-reading, v7-paradigm, 2-clip-merge]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool]
    toolkit_role: picturebook-video-orchestrator
    version: 1.0.8
    breaking_changes_from_v1.0.7:
      - "**Cat 范本对齐终极修复 · 3 个核心修复**（v1.0.8+pic18）—— ① 主体定义写全结构（按从左到右顺序为 horse、fork、horn、corn、pork、橙色星形拼贴）让 seedance 知道有几张卡 ② 镜头序列只说'镜头定格在 X 卡片 / 镜头水平切到 Y 卡片'不写'高亮/边框脉冲/图标动画'让 seedance 自己看图设计动效 ③ 末段写 Cat 范本原文'模型自行设计合理的呈现节奏与动效，不重新生成任何新文字'（不是'参考图原有的所有文字作为画面元素'）"
      - "**5 轮迭代矫枉过正元教训沉淀**（v1.0.8 实战）—— v1.0.4 加'具体音效清单' = 矫枉过正 1 / v1.0.5 加脱敏 = 矫枉过正 2 / v1.0.6 撤脱敏（对） / v1.0.7 加'参考图原有'模糊（对） / v1.0.8 = 照搬 Cat 范本 = 减所有额外加工 = 0 矫枉过正"
      - "**Pic7 R7 第 6 轮翻车修复**（v1.0.6/v1.0.7 修复后仍翻车）—— 主体定义只描述马的外形没提 5 卡片+1星形 → seedance 看到 4 个具体词自己造剩下 1 个（Or 单词塞进来 + horse 单词变马图）→ 5 词变 6 卡"
      - "**不动 fill_v15_template.py 代码**（v1.0.8 vs v1.0.5/v1.0.6/v1.0.7 差异）—— v1.0.8 修复完全在 prompt 写法层（不脱敏 + 不加 B 档 + 不加文字模糊）· 完全照搬 Cat 跑通范本 · 0 矫枉过正"
    breaking_changes_from_v1.0.6:
      - "**Cat 范式回滚 v2 · 5 处文字字段全模糊化**——fill 模板 5 处全部改'参考图原有 · 不在 prompt 重写'（不拼具体 en_word/zh_word/text_position.zh_word）——Pic7 R7 第 5 轮翻车修复（v1.0.6 修复后仍出现'马家族'画面文字 → v1.0.7 真根因 = fill 模板仍拼具体中文翻译 → seedance 自行生成覆盖参考图）"
      - "**撤销 v1.0.5 脱敏 action 字段**（'fork 卡片' → '第2张卡片'）——C agent action 字段原样保留 · fill 模板不拼具体单词到 prompt"
      - "**撤销 v1.0.4 段 4 矫枉过正**（'画面元素动作音效保留...'）——Cat 范本段 4 = A 档兜底句'无任何背景音乐、无旁白人声、无哼唱'"
      - "**字符顺序浮现 4 步走模糊占位**（参/考/图/原 + 考）——不写具体 en_word[0]/[1]/[2]/[3] + zh_word"
    breaking_changes_from_v1.0.5:
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

> ## ⚠️ 元偏好 · 铁律精简原则（2026-06-10 用户红线 · 必读）
>
> **用户原话（升 SKILL 级信号）**：「**铁律的定义是红线、底线，绝对不能逾越的原则。那么说它应该是精简少，而不是数量这么多。**」
>
> **铁律定义**（适用于本 skill + 所有 skill）：
> - ✅ **铁律 = 红线 / 底线 / 不能逾越的原则**——违反 = 必然翻车 / 必然破坏产品 / 必然失败
> - ❌ **不是** = 流程建议 / 方法论 / 范式 / 技巧 / 模板 / 计算公式 / 调试经验 / 历史教训 / 矫枉过正 / 环境 quirk
>
> **精简标准**（每条铁律提交前必问 4 个问题）：
> 1. **违反 = 必然翻车吗？**（红线的本质判据）
> 2. **能合并到其他铁律吗？**（重复定义 = 删）
> 3. **能降级到 references 或 SKILL.md 正文吗？**（不是红线 = 降级）
> 4. **有官方文档原话支持吗？**（官方说"必须/不能" = 红线；官方说"建议/推荐" = 降级）
>
> **本 SKILL.md 当前状态**（2026-06-10 调研发现）：
> - 现有"铁律清单"区 = **65 条**（用户判定 = 太多 = 失控）
> - **真铁律**（红线 / 底线）= **11 条**——见下方「🔥 真铁律速查」（4 范式路由 + 3 官方硬约束 + 4 主 agent 行为）
> - 其余 35 条 = **流程/方法/技巧** = 降级到 `references/经验沉淀-2026-06.md`
> - 其余 18 条 = **反模式/历史/已被覆盖** = 删除
>
**加新铁律必跑流程**（4 问 + 4 必查）：
1. 先自问"违反会怎样"——不能回答 = 不是铁律
2. 必查是否已有同类铁律——重复 = 不加
3. 必查官方文档原话支持（参见 `seedance2.0-tool/references/seedance-official-docs-research-2026-06-10.md`）
4. 主 agent 主动征求用户"算不算铁律"再写入

**新建/更新 references 必跑流程**（4 问 · 2026-06-10 Rabbit 实战沉淀）：
1. **必问"是不是该 patch 现有 references"**——已有 `v7-vs-v15-paradigm-routing.md` / `leading-reading-4clip-pattern.md` / `长旁白拆分规范-v15.1.md` 三大主题文档，新文档是否应作为它们的扩展/合并而非独立文件？
2. **必问"新文档是不是顶层入口"**——是顶层入口（如决策树/路由总览）→ 新建独立文件；是子规则/案例 → 写到对应 references 末尾章节
3. **新建独立文件必含指针区**——每章/每节末尾链回 3 大主题文档（不孤立）
4. **SKILL.md §"详细规范位置"必加一行**——否则下次 agent 找不到

**反模式**（2026-06-10 Rabbit 实战差点踩）：❌ 看到"建合并/拆分决策文档"直接新建 `clip-合并拆分决策-2026-06-10.md` 独立文件，没先问"应该 patch `v7-vs-v15-paradigm-routing.md` 当顶层入口吗"—— 新建后**已用指针区反向链回 3 大主题文档补救**。

**官方文档作为权威依据**（用户元偏好）："**你应该在 seedance 的原始文档中去寻找一些好的设计方法、好的提示词写法**"——任何 prompt 写法/技术规范类铁律必先查官方 doc2/doc3，找到依据才写。

**元教训升铁律通道**（2026-06-10 用户新维度）：**元教训 = "不能逾越的元原则" = 可以是铁律**。两类铁律：① 红线（官方文档/物理约束）② 元教训（修复翻车原则/行为准则）—— 都是铁律。**降级反向也成立**：当用户判定"这条不够格铁律" → 降级到 `references/元教训-YYYY-MM.md`。

**触发场景**：任何 skill 维护时新建"铁律"前 / 整理"铁律清单"时 / 用户反馈"铁律太多"时 / 新建 references 文档时。

## 🔥 真铁律速查（11 条 · A 类红线 · 2026-06-10 精简版）

> **定义**：违反这 11 条 = 必然翻车 / 破坏产品 / 必然失败。
> **每条铁律 = 短句 + 指向 references 详细规则**。规则细节不在 SKILL.md 重复，详见 `references/经验沉淀-2026-06.md`。

### 范式路由铁律（决策入口 · 4 条）

| # | 铁律（短句）| references 详细 |
|---|---|---|
| **⭐路由** | **领读型绘本 = v7 范式（2图=1Clip 合并），叙事型 = v15 4 段范式（单图 1Clip）** | [`v7-vs-v15-paradigm-routing.md`](./references/v7-vs-v15-paradigm-routing.md) |
| **⭐决策树** | **绘本级 → 范式级 → 段级 → 特殊场景，4 层逐级判定** | [`clip-合并拆分决策-2026-06-10.md`](./references/clip-合并拆分决策-2026-06-10.md) |
| **#89** | **v7 范式 5 条件必全过**（领读/弱情节/旁白<8s/风格统一/6-10图） | [`v7-vs-v15-paradigm-routing.md`](./references/v7-vs-v15-paradigm-routing.md) §2 |
| **⭐密度** | **高密度段（家族词组≥3词 / 强文字可见）= 独立 Clip + 14s 起步** | [`clip-合并拆分决策-2026-06-10.md`](./references/clip-合并拆分决策-2026-06-10.md) Step 2A |

### 官方硬约束（红线 · 3 条）

| # | 铁律（短句）| references 详细 |
|---|---|---|
| **⭐官方§4** | **1 个镜头只 1 种运镜方式**（不要同时推拉摇移）| doc2 §4 原话"增加画面不稳定性" |
| **#90** | **seedance 时长 4 ≤ x ≤ 15s** | doc3 line1705 |
| **#72** | **seedance 不生成小数时长**（duration 输入整数，模型 ceiling） | 实战沉淀 |

### 主 agent 行为铁律（元教训 · 4 条）

| # | 铁律（短句）| references 详细 |
|---|---|---|
| **#87** | **主 agent 跑完 = 发视频 = 不主动抽帧自检**（vision 是辅助不是真理） | Pic6 用户原话 |
| **#65+#79** | **单 Clip 端到端 = 等用户目检 = 不批量跳跑** | Pic4 clip1 |
| **#76** | **发飞书视频附件 = 必附完整证据链**（md5 + task_id + seed + 时长） | Pic4 串扰教训 |
| **#99** | **修复翻车 ≠ 加新东西，照搬 Cat 范本 = 减所有额外加工**（减法 > 加法）| Pic7 5 轮迭代 |

### 铁律精简原则

- **铁律 = 红线 / 底线 / 不能逾越**：违反 = 必然翻车
- **每条铁律提交前必过 4 问筛选**（详见上方「⚠️ 元偏好 · 铁律精简原则」段落）：
  1. 违反 = 必然翻车吗？
  2. 能合并到其他铁律吗？
  3. 能降级到 references 或正文吗？
  4. 有官方文档原话支持吗？
- **降级去向**：
  - 流程/方法/技巧 → `references/经验沉淀-2026-06.md`（待建）
  - 反模式/历史/已被覆盖 → 删除
- **本原则不是"铁律数量上限"**——是"每条铁律必须经 4 问筛选"
- 元教训（如 #99、#87）= "不能逾越的元原则" = **符合 4 问 = 可升回铁律**

**Pic4-7 实战必看的另外 N 条**（侧重"翻车征兆 + 决策时必看"，跟精简版互补）：见下方「🔥 决策时必看的新铁律速查」。

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
| **96**（v1.0.6+pic16 新增 · 2026-06-09 Pic7 Horse R7 实战沉淀 · Cat 范式回滚铁律）| 看到"段 2 拼"+朗读 X"" 或 fill 模板加脱敏映射等"额外加工"时 | **照搬 Cat 跑通范本**（`assets/example-prompts/cat-clips-1-6-v15.1.txt`）· **不**瞎改段 2 结构。**Cat 范本 4 段固定结构**：① 主体定义（含 C 写"cat 卡片"等具体单词·原样保留）② 分镜绑定（`@图N`/`@图M` 多图参考）③ 镜头序列（**写"（朗读 1s + 静默 2s 停留，镜头停在画面上让听众消化单词）"**——不写"朗读 cat"——seedance 看到"朗读 1s"知道要留时间但不强制生成具体朗读）④ 段 4 写 A 档兜底句"无任何背景音乐、无旁白人声、无哼唱"。**5 个常见反模式**（Pic7 三轮翻车沉淀）：① ❌ 段 2 拼"+朗读 'X 词'" ② ❌ fill 加脱敏映射（v1.0.5 矫枉过正）③ ❌ 段 4 加"具体音效清单"（"卡片高亮配叮..."v1.0.4 矫枉过正）④ ❌ 段 4 改"画面元素动作音效保留..."（v1.0.4 B 档矫枉过正）⑤ ❌ 段 2 文字保留复制 2 遍到段 5。**判断口诀**：**"Cat 跑通的样子 = 标准答案 · 改了大概率翻车"**。**修复路径**：删所有额外加工 → 改回 Cat 范本 4 段结构 → 重跑。|
| **97**（v1.0.7+pic17 新增 · 2026-06-09 Pic7 Horse R7 第四轮翻车实战沉淀 · Cat 范式回滚 v2 · 5 处文字字段全模糊化）| 看到"画面里出现'马家族'/'马的家族'等与参考图实际文字不一致的画面文字" / "seedance 自作主张生成了不在参考图里的中文翻译"时 | **fill 模板 5 处文字字段全模糊化 · 改"参考图原有 · 不在 prompt 重写"**。**真根因**（v1.0.6 Cat 范式回滚后仍翻车）：v1.0.6 修了"段 2 朗读 X 词"红线 + 段 4 改 A 档兜底句 + 撤销脱敏映射——**但 fill 模板 `_build_text_visibility_segment` 函数 + V15/V6_TEMPLATE 段 2 文字保留句还把 C 输出的具体 `en_word`/`zh_word`/`text_position.zh_word` 拼到 prompt**——seedance 看到具体中文翻译"马 horse 的 OR 家族" → **自己生成**这些字（"马家族"/"马的家族"）→ **覆盖**了 6.jpg 参考图实际的"OR Family"中文翻译。**Pic7 R7 翻车链第 5 轮**（v1.0.7+pic17 终极修复）：v1.0.3 全静音 → v1.0.4 单词不一致 → v1.0.5 脱敏矫枉过正 → v1.0.6 Cat 范式回滚（撤销脱敏）→ **v1.0.7 发现"虽然不脱敏但 prompt 仍拼具体 zh_word → seedance 自作主张生成'马的 OR 家族'"**。**5 处全改模糊描述**：① V15/V6_TEMPLATE 段 2 文字保留句：`"{EN_WORD}" 和中文"{ZH_WORD}"字` → `"（参考图原有 · 不在 prompt 重写）和中文（参考图原有 · 不在 prompt 重写）字"` ② `_build_text_visibility_segment` 段 5 文字持续可见句：同 ① ③ 段 5 微动画句：`"X" 4 字轮流 + "Y" 字` → `"参考图原有英文+中文字轮流"` ④ 段 5 字符顺序浮现 en_word[0-3]：`f"fork[0](0.3s) → horn[1](0.6s) → ..."` → `f"参(0.3s) → 考(0.6s) → 图(0.9s) → 原(1.2s)"` ⑤ 段 5 字符顺序浮现 zh_word：`f"{zh_word}(1.5s)"` → `f"考(1.5s)"`。**Cat 范本精神**（"模型自行设计合理的呈现节奏与动效，不重新生成任何新文字"）——**prompt 不写具体中文翻译**。**修复路径**：`scripts/fill_v15_template.py` v1.0.7+pic17 commit `d7cfaf0` 5 处全改。**实战验证**：Clip 4 重跑 task_id=`cgt-20260609210037-pft2q` · seed 72447 · 14s · audio=true · 调性"俏皮活泼·认知向" → 5 张卡片英文 fork/horn/corn/pork + 标题"OR Family" 100% 跟 6.jpg 一致 + 画面不再有"马 family"/"马家族"字样。**判断口诀**：**"fill 模板看到任何 en_word/zh_word 字段直接拼到 prompt = 立刻改'参考图原有 · 不在 prompt 重写'模糊描述"**。**反模式**（v1.0.5 矫枉过正的另一种）：脱敏 action 字段（"fork 卡片" → "第2张卡片"）= **撤销**（C 看图合理推断该保留·但**不能直接拼到 prompt**让 seedance 看到具体中文）—— **v1.0.7 终极方案 = C 原样保留 + fill 不拼**。|
| **98**（v1.0.8+pic18 新增 · 2026-06-09 Pic7 Horse R7 第五轮翻车实战沉淀 · **Cat 范本对齐终极修复 · 5 词全对**）| 看到 v1.0.6/v1.0.7 修复后**画面文字**仍"5 词变 6 卡（Or 单词塞进来）" / "horse 单词消失变马图" / "pork 单词消失" / "标题 OR Family 缺失"时 | **完全对齐 Cat 跑通范本 `assets/example-prompts/cat-clips-1-6-v15.1.txt` · 3 个核心修复**。**Pic7 R7 翻车链第 6 轮**（v1.0.8+pic18 终极修复）：v1.0.3 全静音 → v1.0.4 单词不一致 → v1.0.5 脱敏矫枉过正 → v1.0.6 Cat 范式回滚 v1（撤脱敏）→ v1.0.7 Cat 范式回滚 v2（5 处文字字段模糊）→ **v1.0.8 主体定义结构修复**。**真根因**（v1.0.7 修复后仍翻车）：v1.0.7 修了"段 2 文字保留 + 段 5 文字持续可见 + 字符顺序浮现 + 目标词标识"——**但没改主体定义里的"5 词卡片结构描述"**——v1.0.7 主体定义只描述马的外形（"horse_in_card_1@Image6（棕红色 · 鬃毛深棕色 · 蹄子黑色 · 卡通Q萌 · 侧身站立 · ..."）——**没提 5 张卡片+1星形**——seedance 看到"5 张卡"需求 + 参考图 6 格 = **自己造**剩下 1 个 = Or + 马图塞了 2 张 = **5 词变 6 卡 + horse 单词消失**。**3 个核心修复**（**完全照搬 Cat 范本 · 不加任何额外加工**）：① **主体定义**写"按从左到右顺序为 horse、fork、horn、corn、pork、橙色星形拼贴"（明确告诉 seedance 有 5 词卡 + 1 星形 = 6 张）② **镜头序列**只说"镜头定格在 horse 卡片" / "镜头水平切到 fork 卡片"——**不写**"卡片高亮/边框脉冲/图标动画/字号"——**让 seedance 自己看图设计动效** ③ **末段**写 Cat 范本原文"参考图原有的所有文字（顶部 OR Family + 5 词卡片顶半部英文 + 卡片下半部中文）作为画面元素自然融入场景，**模型自行设计合理的呈现节奏与动效，不重新生成任何新文字**"（不是"参考图原有的所有文字作为画面元素"——seedance 会自己造中文翻译）。**5 轮迭代矫枉过正元教训**：v1.0.4 加"具体音效清单" = 矫枉过正 1 / v1.0.5 加脱敏 = 矫枉过正 2 / v1.0.6 撤脱敏（对）/ v1.0.7 加"参考图原有"模糊（对）/ **v1.0.8 = 照搬 Cat 范本 = 减所有额外加工 = 0 矫枉过正**。**修复路径**：`scripts/fill_v15_template.py` v1.0.8+pic18 commit（待 tag）= **不改任何代码 · 只重写 prompt 写法**。**实战验证**：Clip 4 重跑 task_id=`cgt-20260609215311-bh95f` · seed 26509 · 14s · 5.75 MB · md5 `26626443529425ee6b752e938656d172` → **5 词全对（horse/fork/horn/corn/pork）+ OR Family 完整 + 零幻觉** + 85% 相似度（v1.0.7 之前是 60%）。**遗留小瑕疵**（不影响核心）：① 第 6 张六角星始终没出现（seedance 把"星形拼贴"理解成装饰）② "horse" 字母 e 边缘裁切（seedance 画框控制）= v1.0.9 候选。**判断口诀**：**"修复翻车 ≠ 加新东西 · 照搬 Cat 范本 = 减所有额外加工"** + **"参考图有 N 个必显式说（主体定义写全结构）"** + **"镜头序列只说动作不写视觉细节"** + **"末段必明写'模型自行设计合理呈现 + 不重新生成任何新文字'"**。**详细实战数据**见 [references/2026-06-09-pic7-horse-v108-success.md](references/2026-06-09-pic7-horse-v108-success.md)。|
| **99**（v1.0.9+pic19 新增 · 2026-06-09 Pic7 Horse **核心 1 条顶 10 条** · 用户原话"以参考图为基准"）| 看到任何"修复画面对齐"的 prompt 写法时 | **🎯 核心原则 = 1 条顶 10 条：以参考图为基准 = 不约束 + 让 seedance 看图 = 任何镜头设计都 OK**。**真根因**（v1.0.4 → v1.0.5 → v1.0.6 → v1.0.7 → v1.0.8 五轮迭代元教训）：我**反复**给 prompt 加约束（"主体定义写全结构"/"fill 模板 5 处模糊化"/"主体定义 2 行 3 列"/"or 红高亮"）= **每加 1 条新约束 = seedance 看到 1 个新触发点 = 自己造的窗口 + 1**。**v1.0.8 跑通 = 减所有额外加工 = 只写"以参考图为基准"+ 让 seedance 看图 = 0 触发点 = 0 错乱**。**Pic7 v1.0.9 实战验证 A+B 混合镜头**（10 镜头 = 5 A 切 + 5 B 持续）= "or 红高亮"完美实现 + horse 卡片柔光脉动 + 5 词全对 + 2 行 3 列布局正确 = **A+B 混合 + Cat 范本对齐 = 1+1 > 2**。**用户原话核心**："**只要理解了以参考图为基准来做设计镜头，不管设计什么镜头实际上都是可以的。哪怕就是一个全景图，让它慢慢的、自然的去镜头流动都是可以的**" + "**用参考图来控制画面的内容，这是非常非常重要的一个东西，属于底层核心逻辑**" + "**这个环节就要去做好这些工作，这是底层核心**"。**修复路径**（**1 句话搞定所有翻车**）：**prompt = 镜头怎么动/呈现 + seedance 自行看图决定细节**——**不写**"卡片有几张/单词有几个/具体视觉元素/约束/不写清单"——**不约束 = seedance 看图 = 对齐**。**反 v1.0.5-v1.0.7 矫枉过正元模式**：❌ 写"主体定义必显式列出 N 个卡" = 约束 = seedance 看到 N 但看图只有 5 = 自己造 1 = 错乱（v1.0.8 反例 = 错写"第 6 张六角星" = 5 张变 6 张）· ❌ 写"fill 模板必模糊化" = 复杂 = 失效（v1.0.7 改 5 处只解决文字不解决结构）· ❌ 写"主体定义必含 2 行 3 列布局" = 约束 = 反而破坏（v1.0.9 反例 = "or 红高亮"虽实现但"第 6 张六角星"在 t=2s 末仍未出现）。**真原则 = 减法不是加法**：修复翻车 = **减额外加工** 不是 **加新约束**。**5 轮迭代减法演进**：v1.0.4（加具体音效清单）→ v1.0.5（加脱敏）→ v1.0.6（撤脱敏）→ v1.0.7（加 5 处模糊化）→ **v1.0.8（照搬 Cat 范本 = 减所有额外加工）= 终极修复**。**判断口诀**：**"任何'修复翻车'的 prompt 改法 = 先问'是不是多了' · 多了就减 · 不加"** + **"参考图为基准 = 1 条顶 10 条"** + **"镜头设计怎么变都 OK = 只要 prompt 不写具体视觉元素"**。**详细实战数据**见 [references/2026-06-09-pic7-horse-v109-success.md](references/2026-06-09-pic7-horse-v109-success.md)（待写）。|

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


## Step 1 · 启动前 7 必问（必跑）—— 6 必问 + #7 调性预审（v1.0.3+pic12 铁律 #70 强化）

**铁律（用户多次纠错）**：不擅自替用户决定。**但 7 问都走"我打算 X 因为 Y"报你**——你只回"停"或"换 X"就调整（不主动开问卷）。

| # | 必问项 | 默认值 | 为什么这么定 |
|---|---|---|---|
| 1 | **画幅比例** | 16:9 | 抖音/视频号/B 站主流；小红书可改 3:4 |
| 2 | **单 Clip 时长** | **v6 整数公式**（短句 6s / 中句 7s / 长句 8s / 极短 5s）| 按 B 子 agent 算出的朗读时长 + **整数**（铁律 #72：seedance 不生成小数）+ 末帧静默 ≥ 2s（铁律 #74 v5 公式）|
| 3 | **切分方式** | 按图（每张图 1 Clip） | 默认；>15s 走 v15.1 语义块 |
| 4 | **调性** | 等 A 子 agent 识别 | 主 agent 不擅自定 |
| 5 | **范式** | **领读型 v7 范式（默认）** | v7 = 2图=1Clip 合并（主 agent 直拼 · 详见 Step 3.0 路由）· 叙事/冒险/收势向走 v15 4 段（调 C 拼） |
| 6 | **约束** | 末帧 ≠ 定格海报 / 文字保留 v3 / 不写隔离句 / **彩色文字全程可见+微动画** | v0.7.1+pic7 沉淀 + 铁律 #73 |
| **7**（v1.0.3+pic12 铁律 #70 新增）| **调性预审**（绘本方选图情绪 vs 用户期望情绪）| **差距大 = 选材问题，建议换绘本** | 见 [references/2026-06-07-pic4-no-v6-final.md](references/2026-06-07-pic4-no-v6-final.md) "v6 三大核心铁律" |

**Step 1.5 · 数字约束数学验证（v1.0.3+pic13 铁律 #89 新增 · Horse 绘本踩坑）**：

**收到用户多个数字约束时（如"压缩短句 + R7=14s + 总 43s"），必先验证数学可行性再分配档位**：

1. **列出所有数字约束**（总时长 / 单 Clip 时长 / 单段朗读 / 镜头数 / R 特殊时长）
2. **用兜底公式算 8 段朗读时长**（1.4 词/秒 + 3.5 字/秒）
3. **列可行解表**（A 全准守 / B 放大总时长 / C 拆 Clip / D 放松短句）—— **每档**标"末帧静默 = 几 s"（必 ≥ 2s 铁律 #74）
4. **冲突时让用户选**（不偷偷按字面意思跑）
5. **翻车征兆（末帧静默 < 2s）= 必报**（不掩盖）

**反模式**：用户给 3 个数字 → 直接算档位 → 跑出来发现 5 段末帧 < 1s → 浪费 1 轮。**判断口诀**：**"3 数字约束 = 必先列可行解表 = 让用户选"**

**用户没指定** → 用默认值 + 在 Step 2 报"我打算 X 因为 Y"。
**用户指定** → 用指定值。


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
3. 持久化 A 输出 → `huiben-projects/<日期-项目>/style-recognition.json`
4. 持久化 B 输出 → `huiben-projects/<日期-项目>/narration-quantization.json`
5. 合并传给 C 子 agent


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
# 持久化每个 prompt_draft → huiben-projects/<日期-项目>/clips/clipN-prompt.txt
```

**C 子 agent 必做**（主 agent 不替代）：
- 按档位表选节奏（不凭印象）
- 强制 v15 4 段骨架
- 末帧写"画面继续微动"
- 段 4 不写"其他元素不出现"

**C 翻车** → 重发 C，1 次机会。

**C 600s timeout 实战**（Pic3 2026-06-07）：C 写 9 个 JSON 跑了 600s 没写完主索引 → **主 agent 续写主索引**（用 Python 一次性聚合 clip1-9.json → storyboard-index.json）。


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


## Step 5 · 汇总 + 发飞书

**主 agent 必做**：
1. 持久化 D 输出 → `huiben-projects/<日期-项目>/execution-report.json`
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


## 4-skill 工具包协作

本次 v1.0.0 重构是按 4-skill 工具包流程做的：

| 阶段 | 工具 | 产物 |
|---|---|---|
| 1. 拆分 | `skill-organizer` | 目录结构（agents/ + references/） |
| 2. 编写 | `skill-creator` | 4 份子 agent SKILL.md + 本主 SKILL.md |
| 3. 沉淀 | `gardener-skill` | `references/2026-06-06-v1-refactor-rationale.md` |
| 4. 验证 | `darwin-skill` | 跑 evals 对比 v0.7.1+pic7 vs v1.0.0 |


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
| **Pic7 Horse 马 实战验证** | `references/2026-06-09-pic7-horse-validation.md`（**v1.0.4+pic14 → v1.0.5+pic15 → v1.0.6+pic16 → v1.0.7+pic17 完整闭环** · 2026-06-09 · 5/5 succeeded · 0 错位 · 48s · v15 + 2图=1Clip 兼容 + 5 档声音策略 + 参考图文字保真 + Cat 范式回滚 v2 · 4 个 commit `2b957a4` `8ddbb34` `f4950b9` `d7cfaf0`）|
| **Pic7 Horse v1.0.8 终极修复** | `references/2026-06-09-pic7-horse-v108-success.md`（**v1.0.8+pic18 · Cat 范本对齐 · 5 词全对 + 零幻觉 + OR Family 完整** · 2026-06-09 · 1 commit · 5 轮迭代元教训沉淀）|
| **Rabbit Clip4 IT 家族首跑** ⭐ 2026-06-10 新增 | `references/2026-06-10-rabbit-clip4-it-family.md`（**v7 范式 14s 单 Clip · 调研笔记 3 条 P0 + Cat 范本对齐 · 5 词 + IT 家族持续可见 + 铁律 #86 家族词组 `--generate-audio false`** · 2026-06-10 · task `cgt-20260610093758-qg6cg` succeeded · 3.77MB · md5 `4b5934ea`） |


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


## 相关 skill

- **子 agent A**：`storyboard-style`（风格识别）
- **子 agent B**：`storyboard-narration`（旁白量化）
- **子 agent C**：`storyboard-design`（分镜设计）
- **子 agent D**：`video-executor`（视频执行）
- **工具包**：`skill-creator` / `skill-organizer` / `gardener-skill` / `darwin-skill`
- **兄弟 skill**：`picturebook-creator`（绘本创作）/ `seedance2.0-tool`（视频底层工具）
