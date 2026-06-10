---
name: picturebook-video
description: "绘本转儿童动画视频一站式调度 skill（**v1.2.0+pic22** · v7 范式彻底删除 + 运镜/音效/镜头名 3 个 Step 决定规则 + 主题编号铁律 13 条）。v15 导演思维版 = **唯一**分镜规范（`references/分镜设计规范-v15director.md`）· v7 + 首尾帧 = **禁用** · 默认'中景拉远+微风+建立场景'模板 = **禁用**（Pic10 6/6 段 100% 套用 = 翻车）· 3 并发 D 视频执行 = picturebook-workflow.md 铁律。绘本 + N 张图 + 旁白 → Step 0 用途澄清 → Step 0.5 场景对位 → Step 1 启动前 7 必问 + #1.5 数字约束 → 调 A 风格 + B 旁白（并行）→ 主 agent 写 6 段 prompt（§1 + §7.6 3 个 Step + `references/分镜设计-模板化反模式-2026-06-10.md`）→ 3 并发 D → 发飞书 + 完整证据链。**v1.2.0 净化**：15 个 v7 专有文件全删。**触发词**：绘本视频、绘本转视频、绘本动画、绘本生成视频、picturebook video。"
license: Apache-2-2
metadata:
  hermes:
    tags: [picturebook-video, orchestration, sub-agent, multi-agent, picturebook, v15-director, v6-deprecated, v7-deprecated, fill-v15, uguu-fallback, send-message-evidence, integer-duration, text-anchored-reading, ref-images-only]
    related_skills: [storyboard-style, storyboard-narration, storyboard-design, video-executor, seedance2.0-tool]
    toolkit_role: picturebook-video-orchestrator
    version: 1.2.0
    breaking_changes_from_v1.1.0:
      - "**v7 范式彻底删除（v1.2.0+pic21 · 2026-06-10 净化）**——用户红线原话：'**草！！！我TM一直在说净化，清理，这就是你清理的结果！！！不要有任何V7的结构，绝不能使用首尾帧！！！**'。v7 范式（领读型 2图=1Clip 合并 · `--image`+`--last-frame` 首尾帧过渡）= **整条路由删除** · SKILL.md 109 处 v7 引用全部清掉 · 5 个 v7 专有 references + 2 个 v7 范式脚本 + 3 个 v7 范式跑通范本 + 1 个 v7.1 混合范式工作流 + Rabbit Clip4 IT 家族 v7 14s 单 Clip 案例 = **15 文件全删**（用户说'删' = 真删 · 不备份到 .deprecated）"
      - "**首尾帧范式 = 禁用**（v1.2.0+pic21）——任何 seedance 调用 = **只用** `--ref-images 1.jpg [2.jpg]`（多图参考）· **不**用 `--image` + `--last-frame`（首尾帧过渡）"
      - "**v15 导演思维版 = 唯一范式**（v1.2.0+pic21 强化）——所有绘本（领读/认知/认字/叙事/冒险/收势）= **统一走 v15 导演思维版 6 段骨架**（`references/分镜设计规范-v15director.md`）· 不再分领读型 vs 叙事型（v7 范式删除后，v15 = 唯一入口）"
---

# picturebook-video · 绘本视频调度中枢（v1.2.0+pic21 · v7 范式已废 · v15 唯一权威）

> ## ⚠️ 2026-06-10 净化 v3 · v7 范式彻底删除 · v15 导演思维版 = **唯一**入口
>
> **用户红线原话**（2026-06-10 14:55）："**草！！！我TM一直在说净化，清理，这就是你清理的结果！！！不要有任何V7的结构，绝不能使用首尾帧！！！**"
>
> **本次净化动作**（15 个文件彻底删除 · `rm -f` 0 备份）：
> - ❌ `templates/v7-prompt-template.md` （v7 范式专用模板）
> - ❌ `assets/example-prompts/cactus-clip1-v7.txt` （v7 范式跑通范本）
> - ❌ `assets/example-prompts/cactus-clips-2-3-4-v7.txt` （v7 范式跑通范本）
> - ❌ `assets/example-prompts/say-p1-v14-v7.txt` （v7 范式跑通范本）
> - ❌ `references/build-v7-clips-script.md` （v7 范式脚本指南）
> - ❌ `references/leading-reading-4clip-pattern.md` （v7 范式 4 clip pattern）
> - ❌ `references/v7-vs-v15-paradigm-routing.md` （v7 vs v15 路由 · v7 死 = 文档无意义）
> - ❌ `references/clip-合并拆分决策-2026-06-10.md` （v7 范式合并决策 · 死）
> - ❌ `references/铁律维护工作流-v7.1混合范式-2026-06-10.md` （v7.1 混合范式 · 死）
> - ❌ `references/v7-12-check.md` （v7 12 项检查 · 死）
> - ❌ `references/2026-06-05-say-pitfalls.md` （Say 绘本 v7 范式踩坑 · 死）
> - ❌ `references/达尔文dry_run实践-v0.7.0.md` （v0.7.0 时代 v7 评估 · 死）
> - ❌ `scripts/build_v8_clips.py` （v7 范式 build 脚本）
> - ❌ `scripts/build_v9_clips.py` （v7 范式 build 脚本）
> - ❌ `references/2026-06-10-rabbit-clip4-it-family.md` （Rabbit Clip4 v7 14s 单 Clip 案例 · **完全删除 · 不作反面教材** · 用户说删 = 真删）
>
|> **唯一分镜规范**（**v15 导演思维版 = 唯一入口 · v1.2.0+pic21**）：
> - ✅ `references/分镜设计规范-v15director.md`（**v1.2.0+pic21 · 2026-06-10 Pic10 Hamster 8 段端到端 + v3 修复"莫名说话声"后验证通过**）
>   - 6 段骨架（素材角色声明 + 主体定义 + **多镜头时间线分镜** + 整段音频约束 + 画面禁令 + Storyboard 引导）
>   - **镜头设计 4 步原则**（**Pic10 Hamster 实战沉淀 · 2026-06-10 用户强纠错**）：① 看参考图 ② 推断情节（旁白+画面双源） ③ 写动作步骤数（1-3 镜/段 · **不固定 3 镜**） ④ 留呼吸感静默（末帧"画面不再动"· 30-40% 整段时长）
>   - ~~镜头数算法（5s=2-3 镜头 / 8s=3-5 镜头 ...）~~ **已废 · 反模式 = 公式套数**（Pic10 v1 翻车案例）
>   - **末尾约束段官方原话 4 词**："**保持无字幕、无水印、无 Logo，无人声、无歌唱、无配音、无朗读**"（v3 修复后）—— **禁止**用元数据术语"TTS 音轨占位 / 音轨占位 / 朗读时长"（Pic10 v2 翻车根因）
>   - 每镜头 4 逻辑齐全（运镜 + 动作 + 位置 + 音频内联）
>   - 完整 Pic10 Hamster v3 验证通过 prompt 模板（5s/6s/7s · 2-3 镜头 · 1695-2012 字符 · 2 分 16 秒到 4 分 4 秒跑完）
>
> **唯一 seedance 调用范式**（**v1.2.0+pic21 铁律**）：
> - ✅ **只用** `--ref-images 1.jpg [2.jpg]`（多图参考）
> - ❌ **禁用** `--image` + `--last-frame`（首尾帧过渡）—— 任何"2图=1Clip 合并" / "首尾帧范式" / "--image + --last-frame" 出现 = 立刻删
>
> **本说明触发场景**：任何新绘本 prompt 编写 / 主 agent 拼 prompt 时 / 子 agent C 调度时 / 老 references 引用解析时

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
> **用户说"删" = 真删 · 0 备份**（v1.2.0+pic21 v7 净化再次确认）：
> - 用户原话"移除其它版本，避免污染"= **彻底删除**（`rm -f` 无备份）
> - ❌ 反模式：擅自 `mv` 到 `废弃-YYYY-MM/` 目录加 `.deprecated` 后缀 = 混合"删"+"保" = 等于没删 = 还在污染
> - ✅ 正解：用户说"删" → 直接 `rm -f` + 不留任何痕迹
> - **触发场景**：任何"清理/净化/移除"用户指令

## 🔥 真铁律速查（v1.2.0+pic22 · 主题编号 = 13 条）

> **定义**：违反 = 必然翻车 / 破坏产品 / 必然失败。
> **每条铁律 = 短句 + 指向 references 详细规则**。规则细节不在 SKILL.md 重复。
> **铁律只升 2 类**（2026-06-10 用户纠错"凡实战经验都打铁律标签"后定义）：
> 1. **红线**（官方文档/物理约束）
> 2. **元教训**（修复翻车的元原则）
> ❌ 流程/方法/技巧/历史清单 = **不**升铁律 → 放 references 章节即可
> ❌ 连续编号（#106/#107/#108...）= **禁用** = 永远在加 = 65 条失控 · 改用**主题编号**（`v15.4步原则` / `seedance.首尾帧禁` / `prompt.末尾约束4词` 等 = 命名空间 + 不连续 + 不会失控）

### v15 范式（2 条）

| 铁律 ID | 铁律（短句）| references 详细 |
|---|---|---|
| **`v15.唯一范式`** ⭐ | **v15 导演思维版 = 唯一分镜规范**（`分镜设计规范-v15director.md`）· 6 段骨架 · **所有绘本统一走** · **v7 范式 = 已删 · 禁用** | [`分镜设计规范-v15director.md`](./references/分镜设计规范-v15director.md) |
| **`v15.4步原则`** ⭐ 2026-06-10 HAMSTER | **prompt 写法 4 步必走**（用户强纠错 · v1.2.0+pic22 验证通过）——① 以参考图作为首帧推断后面 clip 时长 ② 结合旁白内容推断接下来可能发生的事情 ③ 根据旁白故事情节设计镜头**不按固定模式**（1-3 镜/段自由组合 · **不**套"建立/单词/收势"3 镜模板） ④ 留出呼吸感的静默内容（让观众消化）· 末帧写"画面不再动 · 让 XX 在小朋友心中沉淀"（**真正静默不是微动** · 整段 30-40% 时长）· 关键澄清：首帧 ≠ 首尾帧模式（仍用 v15 多图参考 · 必用 `--ref-images`）· 仍然使用导演思维 | [references/分镜设计规范-v15director.md](./references/分镜设计规范-v15director.md) §7 + [references/2026-06-10-hamster-v15-end-to-end-validation.md](./references/2026-06-10-hamster-v15-end-to-end-validation.md) §7 |

### seedance 调用（3 条）

| 铁律 ID | 铁律（短句）| references 详细 |
|---|---|---|
| **`seedance.首尾帧禁`** ⭐ | **seedance 必用 `--ref-images 1.jpg [2.jpg]`（多图参考）· 禁用 `--image` + `--last-frame`（首尾帧过渡）** | 用户 2026-06-10 14:55 红线原话"绝不能使用首尾帧" |
| **`seedance.1镜1运镜`** ⭐ | **1 个镜头只 1 种运镜方式**（不要同时推拉摇移）| doc2 §4 原话"增加画面不稳定性" |
| **`seedance.时长4-15`** | **seedance 时长 4 ≤ x ≤ 15s** | doc3 line1705 |

### prompt 写法（2 条）

| 铁律 ID | 铁律（短句）| references 详细 |
### prompt 写法（2 条 → 升级为 5 条 v1.2.0+pic24）

| 铁律 ID | 铁律（短句）| references 详细 |
|---|---|---|
| **`prompt.末尾约束4词`** ⭐ 2026-06-10 HAMSTER | **末尾约束段必须用官方原话 4 词"无人声/无歌唱/无配音/无朗读"**（v1.2.0+pic21 v3 修复验证通过）——Pic10 v2→v3 修复核心：v2 翻车"莫名说话声" / v3 用户目检修复通过 | [references/分镜设计规范-v15director.md](./references/分镜设计规范-v15director.md) §1[4] + §8 TL;DR + [references/2026-06-10-hamster-v15-end-to-end-validation.md](./references/2026-06-10-hamster-v15-end-to-end-validation.md) §8 |
| **`prompt.减法>加法`** | **修复翻车 ≠ 加新东西，照搬 Cat 范本 = 减所有额外加工**（减法 > 加法）| Pic7 5 轮迭代 |
| **`prompt.段4兜底句-Cat原话`** ⭐ 2026-06-10 DOG | **段 4 兜底句必须用 Cat 范本原话 3 项**："**无任何背景音乐、无旁白人声、无哼唱**"（Cat 6/6 Clip 跑通 = 金标准）—— v1.2.0+pic22 我自己改写 4 项版"无人声/无歌唱/无配音/无朗读" **漏"无BGM"** = **Dog 4/4 段全出 BGM 元凶**（2026-06-10 18:35 用户反馈"大部分视频生成了BGM"）· **正模式**：写新版本前**先翻 Cat 范本原话**（`assets/example-prompts/cat-clips-1-6-v15.1.txt`）= 不要擅自改原话 = 改了就跑通不了 | [references/分镜设计规范-v15director.md](./references/分镜设计规范-v15director.md) §1[4] v1.2.0+pic24 + [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) C2 |
| **`prompt.禁元术语`** ⭐ 2026-06-10 DOG | **prompt 严禁"朗读/旁白朗读/TTS/音轨占位/朗读时长"等元术语**——"朗读"是元术语 = 触发 seedance 激活人声生成路径（**Pic11 Dog clip1 莫名人声元凶** · 用户 2026-06-10 18:35 反馈）· **正模式**：直接写"声音"或"音效"或干脆不写 · 末尾约束段顺序必须严格按官方原话（无字幕/无水印/无Logo/无人声/无歌唱/无配音/无朗读）· **不**打乱顺序 | [references/分镜设计规范-v15director.md](./references/分镜设计规范-v15director.md) §1[4] v1.2.0+pic24 + [references/seedance-prompt-翻车修复方法论-2026-06-10.md](./references/seedance-prompt-翻车修复方法论-2026-06-10.md) + [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) C1 |
| **`prompt.StepA强制化`** ⭐ 2026-06-10 DOG | **主 agent 跑分镜时必走 v22 Step A 看图决定景别 + 运镜**——5 种画面状态对应 5 种运镜（**不**凭印象套）· **触发场景**：任何新绘本 prompt 编写前必走 Step A/B/C 决策表 · 写完 prompt 后**自检 3 问**：① 景别是不是按参考图实际状态定的？② 音效是不是按参考图实际场景定的？③ 镜头名是不是用"动作+状态"命名？· **违反案例**：Dog 4 段运镜单一（clip1 固定中景 / clip2 中景拉远 / clip3 正面平视 / clip7 5 镜都"正面近/中景"）= 用户 2026-06-10 18:35 反馈"运镜设计 6 分" | [references/分镜设计规范-v15director.md](./references/分镜设计规范-v15director.md) §7.6 Step A/B/C + §1.3 反模式区 + §8 TL;DR v1.2.0+pic24 + [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) C3 |

### 主 agent 行为（3 条 + 1 条新铁律 → 升级为 6 条 v1.2.0+pic24）

| 铁律 ID | 铁律（短句）| references 详细 |
|---|---|---|
| **`agent.不主动抽帧`** | **主 agent 跑完 = 发视频 = 不主动抽帧自检**（vision 是辅助不是真理） | Pic6 用户原话 |
| **`agent.查状态用urllib`** ⭐ | **主 agent 查 seedance task 状态走 execute_code + python urllib 直查 REST API**（不走 shell 管道 + seedance.py status） | Pic8 Rabbit qg6cg/r7vxs 误判卡死教训 |
| **`agent.发飞书证据链`** | **发飞书视频附件 = 必附完整证据链**（md5 + task_id + seed + 时长） | Pic4 串扰教训 |
| **`agent.任务完成度自检`** ⭐ 2026-06-10 Dog | **任何汇报"已跑完/已下载/已目检/已通过"前必走 4 步对账**（v1.2.0+pic23 新铁律 · Dog 绘本错位发视频事故后新增）：① **ffprobe 元数据校验**（时长/文件大小/分辨率 — 跟期望档位对比）② **抽帧 + native vision 视觉目检**（看帧内容 = 跟原图期望对比）③ **校验文件名 vs 内容身份一致**（clip7.mp4 必须是 p7 的内容，**不**是 clip1/2/3）④ **抽帧后写"对账报告"**（原图期望 vs 实际帧内容 + 差异分析）· **违反 = 必然错位发视频 / 幻觉成功**（Dog 18:10 事故：发 clip1/2/3 帧目检报告当成 clip7 = 错位发视频）| [references/任务完成度自检流程-2026-06-10.md](./references/任务完成度自检流程-2026-06-10.md) |
| **`agent.发飞书对账报告`** ⭐ 2026-06-10 DOG | **发飞书视频附件前必走 md5 + stat 4 步对账**（v1.2.0+pic24 新铁律 · 4 问审查 = 元教训级）：① stat 元数据（文件大小/修改时间）② md5 校验 ③ 对比文件路径与文件名 ④ 写证据链（md5/task_id/seed/时长）· **违反 = 必然错位发视频** | [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) A1 |
| **`agent.跑完必发视频`** ⭐ 2026-06-10 DOG | **主 agent 跑完每个 Clip = 必发 MEDIA 附件到飞书 = 不可选**——"跑完"语义 = "视频文件已发出"（**不**仅"已下载到本地"）· 4 问审查 = 元教训级（修复翻车的元原则：用户原话"我仍然没有收到视频文件" = 视频文件 ≠ 报告）| [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) A3 |
| **`agent.交付不抽帧`** ⭐ 2026-06-10 DOG | **交付阶段 = 禁止任何 vision_analyze 自动抽帧自检**（v1.2.0+pic24 与 `agent.不主动抽帧` 合并强化）——用户原话"**在我没有明确要求你使用视觉识别的情况下，你不要主动对已生成的视频进行抽帧检查，这个是不必要的，你直接把视频文件发送给我就可以了**"· 4 问审查 = 元教训级 · **诊断阶段 vs 交付阶段边界**（v0.7.1 强化）：v1 翻车修复/MVP 实测标版验证/用户明确要求 = 允许；交付阶段 = 禁止 | [references/视频交付工作流-不抽帧.md](./references/视频交付工作流-不抽帧.md) + [references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md](./references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md) A2 |
| **`agent.发飞书对账报告`** ⭐ 2026-06-10 Dog | **发飞书视频附件前必走 4 步对账 + 必附对账报告**（v1.2.0+pic24 新铁律 · Dog 错位发视频事故后新增）：① **stat 校验**（文件大小 + mtime）② **md5 校验**（与本地源文件 hash 一致）③ **身份校验**（clip1.mp4 必须是 p1 内容，**不**是 p2/3/7）④ **4 步对账报告**（md5 短码 + task_id + seed + 时长 + 档位 + 范式）· 违反 = 必然错位发视频 | [references/send-message-evidence-chain.md](./references/send-message-evidence-chain.md) |
| **`agent.交付不抽帧`** ⭐ 2026-06-10 Dog | **交付阶段（跑通 1 个 Clip 发给用户）= ❌ 禁止抽帧 + vision_analyze**——让人眼看，不是机器看（v1.2.0+pic24 新铁律 · 用户 2026-06-10 红线"不要抽帧，我自己看"）| [references/视频交付工作流-不抽帧.md](./references/视频交付工作流-不抽帧.md) |
| **`agent.跑完必发视频`** ⭐ 2026-06-10 Dog | **主 agent 跑完 1 个 Clip = 必发视频附件到飞书**（v1.2.0+pic24 新铁律 · Dog 18:25 事故"我仍然没有收到视频文件"后新增）——`send_message` + `MEDIA:/path/to/clip.mp4` 是硬闭环，**不**仅发文字报告 | [references/视频交付工作流-不抽帧.md](./references/视频交付工作流-不抽帧.md) §正模式 |

### 净化（3 条）

| 铁律 ID | 铁律（短句）| references 详细 |
|---|---|---|
| **`净化.v15老模板废弃`** ⭐ 2026-06-10 Rabbit | **分镜设计规范 = v15 导演思维版为唯一权威 · 老 v6/v15/v15.1 模板全部废弃**（`v6-5段骨架-模板.md` / `v15-4段骨架-模板.md` / `2026-06-07-pic4-no-v6-final.md` / `2026-06-07-pic4-no-v5-rhythm-formula.md` **已删**）| 2026-06-10 用户原话"移除其它版本，避免污染" |
| **`净化.v7范式彻底删除`** ⭐ 2026-06-10 HAMSTER | **v7 范式（领读型 2图=1Clip 合并 + 首尾帧过渡）= 彻底删除 · 首尾帧范式 = 禁用 · 15 个 v7 专有文件已删** | 2026-06-10 14:55 用户红线"不要有任何V7的结构，绝不能使用首尾帧" |
| **`净化.不擅自建记录`** ⭐ 2026-06-10 HAMSTER | **不要擅自创建"清理决策记录"文档**——违反"用户说删 = 0 备份"铁律（v1.2.0+pic21 净化说明里明文）· 反模式：`_V7-CLEANUP-PLAN-2026-06-10.md` 8626B 想留作"清理计划" = 必删 · 决策记录写在 SKILL.md §"⚠️ 净化说明" / CHANGELOG.md 即可，**不**独立建文件 | [references/2026-06-10-hamster-v15-end-to-end-validation.md](./references/2026-06-10-hamster-v15-end-to-end-validation.md) §6.3 |

### 流程/方法/技巧（**不升铁律** · 放 references 章节）

> ❌ 这些是流程/方法/技巧/历史清单 ≠ 铁律。**降级到 references 章节**，不留在铁律表。
> - 旧 #72（duration 整数）→ 写在 `seedance2.0-tool/SKILL.md` §duration 参数说明里
> - 旧 #65+#79（单 Clip 端到端 = 等用户目检 = 不批量跳跑）→ 写在 `picturebook-video/SKILL.md` Step 1 启动前 7 必问
> - 旧 #103（v15 主 agent 直拼 + 实战数据）→ 实战数据写在 [references/2026-06-10-hamster-v15-end-to-end-validation.md §6.1](./references/2026-06-10-hamster-v15-end-to-end-validation.md)
> - 旧 #104（v7 元数据合法清单）→ v7 已删，清单作废，不留任何位置

## 安装说明

> **新机器首次安装**：见 [INSTALL.md](INSTALL.md)（v2.0 · 12 章节 · 100% AI 自动化安装）

## 身份

你是 **绘本视频工作流的调度中枢**。**不直接干活**——只做：

1. 接收需求（绘本 + 图 + 旁白）
2. 启动前 7 必问（确认比例/时长/切分/调性/范式/约束）
3. **并行**调起 A 风格识别 + B 旁白量化
4. 主 agent 写 6 段 prompt（看分镜设计规范-v15director.md）
5. 调 D 视频执行
6. 汇总 D 输出 → 决定是否发飞书

**4 个子 agent**（不直接调，记下来即可）：

| Agent | 职责 | Skill |
|---|---|---|
| **A · 风格识别** | 调性 + 节奏倾向 + 风格锚定词 | `storyboard-style` |
| **B · 旁白量化** | 朗读时长 + 复杂度 + 静默推荐 | `storyboard-narration` |
| **C · 分镜设计** | 节奏公式 + 镜头表 + v15 prompt 草稿 | `storyboard-design` |
| **D · 视频执行** | seedance 跑 + ffmpeg 抽帧 + vision 自检 | `video-executor` |

**子 agent 详细规范**：见 `agents/<agent>/SKILL.md`

## 调度流程（5 步 · v1.2.0+pic21 · v15 唯一路径）

```
Step 0 · 接收需求
   ↓
Step 1 · 启动前 7 必问（必跑）+ #1.5 数字约束数学验证
   ↓
Step 2 · 调 A 风格识别 + B 旁白量化（并行 · B 主 agent 干）
   ↓
Step 3 · 分镜设计 · **v15 导演思维版 6 段骨架**（**唯一路径**）：
   看 [`分镜设计规范-v15director.md`](./references/分镜设计规范-v15director.md)
   主 agent 按 6 段骨架写 prompt（**不调 C 拼老 v15 4 段/v6 5 段**）
   ↓
Step 4 · 调 D · **seedance 必传 --ref-images**（**禁用 --image + --last-frame**）
   · **状态查询走 execute_code + urllib 直查 REST API**（见 ⭐状态铁律）
   · **3 个/批 + 主 agent 续跑**（picturebook-workflow.md 铁律 · v1.2.0+pic22 升级 · subprocess.Popen 异步提交 3 个/批）
   ↓
Step 5 · 汇总 + 发飞书（必附 md5 + task_id + seed + 时长证据链，见 #76）
```

**v15 导演思维版调度示例**（Rabbit newclip1 v2 · 验证通过）：
1. 看 [`分镜设计规范-v15director.md`](./references/分镜设计规范-v15director.md) §1 6 段骨架
2. 按 §1.3 镜头数算法算镜头数（5s=2-3 镜头 / 8s=3-5 / 12s=4-5 / 14s=5-6）
3. 按 §1.2 写 6 段 prompt（**不调 C 拼老 v15 4 段**）
4. 单测 1 个 Clip → 用户目检 → 批量跑剩下 N-1 个
5. 发飞书 + 完整证据链

**⛔ 禁用范式**（v1.2.0+pic21 · 任何"v7 / 首尾帧 / 2图=1Clip" 出现 = 立刻删）：
- ❌ `--image` + `--last-frame` 首尾帧过渡
- ❌ v7 范式 2图=1Clip 合并
- ❌ v7 范式 8 段 prompt
- ❌ v7 范式 `--generate-audio true` + 禁令段控音

## 🔥 决策时必看的新铁律速查（v1.2.0+pic22 · 主题编号版）

> **所有铁律用主题命名空间**（参考铁律速查表 5 桶）：`时长/约束` · `文件/澄清` · `数字/约束` · `镜头/修复` · `镜头/密度`

| 铁律 ID | 何时必看 | 核心一句话 |
|---|---|---|
| **`时长.15s上限`** | 看到 14s/13s/12s 等长于默认 8s 的 Clip | **8s 默认档位 ≠ 上限 · 真正上限 seedance 15s · 8 < x ≤ 15s 合法** |
| **`文件.用途必问`** | 用户给 MP3 / xlsx / readme.txt 等文件 | **文件用途必问不自动假设**（MP3 不默认 TTS · xlsx 必读 schema 确认结构） |
| **`约束.3数字`** | 用户给多个硬约束（总时长 + 单段时长 + 段数）| **3 数字约束物理装不下 = 老实报告 3 选 1 · 不硬凑"末帧 < 1s"翻车方案** |
| **`镜头.参考图基准`** | 看到任何"修复画面对齐"的 prompt 写法时 | **以参考图为基准 = 不约束 + 让 seedance 看图 = 任何镜头设计都 OK** |
| **`镜头.多镜时间线`** | 看到 v6 "整段不分镜" / 反馈"镜头呆板/单镜头/简单推镜头"时 | **v6 = v15 4 段 + 文字持续可见段 · 多镜头时间线分镜 = 必填 · 镜头数必须匹配时长+旁白密度** |

**反模式速查**（v1.0.4 Horse 绘本实战翻车清单 · 净化 v7 引用版）：
- ❌ 看到 14s → 报"超出 8s 必拆 v15.1"（**真相：14s 合法单 Clip**）
- ❌ 把 MP3 自动当 TTS 抽时长（**真相：完整音频 90.15s 零静音**）
- ❌ 走 v7 范式 2图=1Clip 合并（**真相：v7 已删 · 必走 v15 导演思维版**）
- ❌ 用 `--image` + `--last-frame` 首尾帧（**真相：禁用 · 必用 `--ref-images`**）
- ❌ 装 8 段 4.29s 朗读 + 1 段 14s + 总 43s（**真相：物理装不下，5 段末帧 0.71s**）

**完整实战数据**见 `references/分镜设计规范-v15director.md` §"实战数据"

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


## Step 1 · 启动前 7 必问（必跑）—— 6 必问 + #7 调性预审（v1.2.0+pic21 · v15 唯一版本）

**铁律（用户多次纠错）**：不擅自替用户决定。**但 7 问都走"我打算 X 因为 Y"报你**——你只回"停"或"换 X"就调整（不主动开问卷）。

| # | 必问项 | 默认值 | 为什么这么定 |
|---|---|---|---|
| 1 | **画幅比例** | 16:9 | 抖音/视频号/B 站主流；小红书可改 3:4 |
| 2 | **单 Clip 时长** | **整数公式**（短句 6s / 中句 7s / 长句 8s / 极短 5s）| 按 B 子 agent 算出的朗读时长 + **整数**（铁律 #72：seedance 不生成小数）+ 末帧静默 ≥ 2s |
| 3 | **切分方式** | 按图（每张图 1 Clip） | 默认；>15s 走 v15.1 语义块 |
| 4 | **调性** | 等 A 子 agent 识别 | 主 agent 不擅自定 |
| 5 | **范式** | **v15 导演思维版（唯一）** | **v15 = 唯一入口**（v7 已删 · 禁用）· 看 `分镜设计规范-v15director.md` 6 段骨架 |
| 6 | **约束** | 末帧 ≠ 定格海报 / 文字保留 v3 / 不写隔离句 / **彩色文字全程可见+微动画** | v0.7.1+pic7 沉淀 + 铁律 #73 |
| **7** | **调性预审**（绘本方选图情绪 vs 用户期望情绪）| **差距大 = 选材问题，建议换绘本** | 见 [references/2026-06-07-pic4-no-validation.md](./references/2026-06-07-pic4-no-validation.md) "v6 三大核心铁律" |

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
5. 合并传给主 agent 写 prompt


## Step 3 · v15 导演思维版 6 段骨架（**v1.2.0+pic21 · 唯一路径**）

**⚠️ Step 3.0 范式路由决策（v1.2.0+pic21 强化 · v7 已删）**：

**v1.2.0+pic21 后 = 不再有范式路由决策** · **v15 导演思维版 = 唯一入口** · 任何绘本（领读/认知/认字/叙事/冒险/收势）= **统一走 v15**。

| 触发条件 | 范式 | 工作流 |
|---|---|---|
| **所有绘本** | **v15 导演思维版 6 段骨架**（**唯一**）| 看 [`分镜设计规范-v15director.md`](./references/分镜设计规范-v15director.md) · 主 agent 按 6 段骨架写 prompt（**不调 C 拼老 v15 4 段**）|
| ~~v7 范式~~ | ~~领读/认知/认字 + 弱情节 + 旁白<8s + 风格统一 + 总图 6-10~~ | ~~**v1.2.0+pic21 净化 = 已删 · 禁用**~~ |

**v6 5 段判定**（v1.0.3+pic12 老 v6 范本，**v1.1.0+pic20 起 v6 = v15 + 文字持续可见段**）：
- v6 = v15 4 段 + **段 5 文字持续可见段**（**不是减法版**）
- v6 适用场景：绘本要求彩色文字全程可见 + 字符顺序浮现（如 Cow 8 段 · Bird 8 段）
- v6 写法 = 看 `分镜设计规范-v15director.md` + 补"段 5 文字持续可见段"

**v15 范式必填 seedance 参数**：
- `--ref-images 1.jpg [2.jpg]`（**多图参考** · v1.2.0+pic21 铁律）
- ❌ **禁用** `--image` + `--last-frame`（首尾帧过渡 · v1.2.0+pic21 红线）
- `--duration 5/6/7/8/12/14`（**整数** · 4s ≤ x ≤ 15s seedance 物理上限）
- `--ratio 16:9`
- `--generate-audio true/false`（按段 4 声音策略档位决定）

**v15 范式例外**：家族词组集合（≥3 词同字母家族）走铁律 #86 → `--generate-audio false` + TTS 音轨对齐（4 维控制底层核心不动）。

**反模式**（v1.2.0+pic21 · v7 净化版）：
- ❌ **走 v7 范式 2图=1Clip 合并**（v7 已删 · 禁用）
- ❌ **用 `--image` + `--last-frame` 首尾帧**（禁用）
- ❌ **错认 v5 公式 8s 档位 = 硬上限** —— 8s 只是 v5 公式档位参考 · 真正上限 seedance 15s（铁律 #90）
- ❌ **调 C 子 agent 拼 v7 prompt** —— C 只懂 v15 4 段，强行套会拼出错的 prompt 结构
- ❌ **看到 14s 长 Clip 立即报"必拆"** —— 14s < 15s 合法单 Clip

**v15 范式 6 段骨架**（看 [`分镜设计规范-v15director.md`](./references/分镜设计规范-v15director.md) §1）：
- ① 素材角色声明
- ② 主体定义
- ③ **多镜头时间线分镜**（运镜+动作+位置+音频内联 4 逻辑齐全）
- ④ 整段音频约束
- ⑤ 画面禁令
- ⑥ Storyboard 引导

**v15 调度流程**：
```python
# 主 agent 直拼 v15 6 段骨架（不调 C）
prompt = build_v15_skeleton(
  clip_id="clip1",
  image="1.jpg",
  ref_images=["1.jpg"],
  narration="HAMSTER!",
  duration=5,
  shot_count=2  # 5s = 2-3 镜头
)
```


**Step 4 · 调 D · 视频执行（v1.2.0+pic22 · 3 并发版）**

**⚠️ 实战约束（v1.2.0+pic22 强化 · 2026-06-10 Pic10 Hamster 5-8 段并发实战）**：

- ✅ **推荐 batch = 3 个/批**（picturebook-workflow.md 铁律 · 用户 2026-06-10 原话"seedance 可以并发 3 个"）
  - **3 并发 = 真并发 3 个 subprocess.Popen + 错开 1s 提交 + 各自独立 download 路径**
  - **vs 串行 1 个跑完才跑下 1 个**：5 Clip 串行预估 18 分钟 → 3 并发实际 7 分 18 秒 = **节省 11 分钟**
  - **vs 2 个/批**：5 Clip 2/批 = 3 批 × 4 分钟 = 12 分钟 → 3 并发再省 5 分钟
- ❌ **D 子 agent 禁止一次跑全部 N 个 Clip**（Pic2 实战 8 个 Clip 一次跑 = 600s timeout × 2）
- ⚠️ **极限 1 个/批**（端到端验证，**跑通流程**后立刻切换 3 并发）
- **C 子 agent 600s 内只能写 9 个 JSON + 聚合 + vision × 9 = 9 个 API call**——超出时主 agent 续跑

**3 并发实现模板**（Pic10 Hamster 5-8 段 2026-06-10 实战验证）：

```python
import subprocess, time
# 第 1 批：clip4 + clip5 + clip6 = 3 并发
procs = []
for n, dur in [(4, 6), (5, 6), (6, 7)]:
    with open(f'/path/clips/clip{n}-prompt.txt') as f:
        prompt = f.read().strip()
    output = f'/path/clip{n}.mp4'
    cmd = ['python3', 'seedance.py', 'create',
        '--ref-images', f'/path/{n}.jpg',
        '--prompt', prompt,
        '--model', 'doubao-seedance-2-0-fast-260128',
        '--ratio', '16:9', '--duration', str(dur), '--resolution', '720P',
        '--watermark', 'false', '--generate-audio', 'true',
        '--wait', '--download', output]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, cwd='/path/seedance2.0-tool/')
    procs.append((n, p, time.time()))
    time.sleep(1)  # 错开 1s 避免 API 抖动
# 等待所有任务
for n, p, t0 in procs:
    stdout, _ = p.communicate(timeout=600)
    # 解析 task_id / seed / tokens ...
```

**3 并发红线**（必须遵守）：
- ✅ **每个任务用独立 `--download` 完整路径**（如 `clip4.mp4` / `clip5.mp4` / `clip6.mp4`）—— **不**用目录，**不**复用同一路径（SKILL.md 铁律 · 多任务并发时必须每个任务用不同路径，否则会互相覆盖）
- ✅ **错开 1s 提交**（避免 API 瞬时并发抖动）
- ✅ **每个 task_id / seed / md5 都记**到 `task_ids.txt`（铁律 #76 证据链）
- ❌ **不**用 shell 管道 `&` 或 `wait`（难解析 task_id · 应该走 subprocess.Popen）

**Step 4.7 · 任务完成度自检（铁律 `agent.任务完成度自检` · 必跑 · v1.2.0+pic23 新增）**：

**触发条件**：D 跑完 → 主 agent 准备汇报"已跑完/已下载/已通过" → **必走 4 步对账**：

```python
# Step 4.7.1 · ffprobe 元数据校验
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=width,height \
  -of default=noprint_wrappers=1 clip7.mp4
# 校验：duration ≈ 14s（B 方案）/ size ≈ 5.4MB / 分辨率 1280x720
# 跟期望档位对比 — 不一致 = 任务失败

# Step 4.7.2 · 抽帧 + native vision 视觉目检
ffmpeg -y -i clip7.mp4 -vf "fps=1" clip7-frame-%02d.png
# 然后 native vision 看首帧/中段/末帧 3 张关键帧（**不**用 mcp_zai_analyze_image）

# Step 4.7.3 · 校验文件名 vs 内容身份一致
# clip7.mp4 必须是 p7 的内容（OG 家族 5 词卡片墙）
# 拿 vision 看到的首帧内容跟 p7 原图（7.jpg）对比
# 不匹配 = 错位发视频风险 → 立即停止汇报 + 查任务 ID 是不是 clip7 真实的

# Step 4.7.4 · 写"对账报告"
# 原图期望：p7 = 6 格卡片墙 = 5 词（dog/log/frog/jog/fog）+ 1 装饰格
# 实际首帧：<vision 看到的>
# 差异分析：<符合/扩写/偏离>
```

**反模式**（Dog 18:10 事故 · 用户原话"你发的根本就不是生成的Clip7，发错了"）：
- ❌ 汇报"已跑完"前**不** ffprobe → 不知道视频真实身份
- ❌ 汇报"v22 修复成功"前**不**真测 → 幻觉成功
- ❌ 汇报"已目检"前**不** vision 视觉对比原图 → 把任何帧当成"目检通过"
- ❌ **错位发视频**（把 clip1/2/3 的某帧当成 clip7 目检报告发给用户 = 用户 18:15 拍板"你发的根本就不是生成的Clip7，发错了"）

**根因** = **"用户问 → 我答"模式** = **跳过验证直接汇报** = 4 个必走步骤全跳 = 必然错位发视频

**判断口诀**：
- ✅ **汇报"已跑完"前** = 必 ffprobe
- ✅ **汇报"已通过"前** = 必 vision 视觉对比原图
- ✅ **汇报"已目检"前** = 必校验文件名 vs 内容身份一致
- ✅ **汇报"已发飞书"前** = 必写"对账报告"

**Step 4.0 · seedance 调用范式（v1.2.0+pic21 · 唯一路径）**：

| 范式 | 触发 | seedance 参数 | prompt 写法 | 段数 |
|---|---|---|---|---|
| **v15 导演思维版 6 段骨架**（**唯一**）| 任何绘本默认走这条路 | `--ref-images 1.jpg [2.jpg]`（**多图参考** · 必填）| 看 `分镜设计规范-v15director.md` §1 6 段骨架 | 6 |
| ~~v7 范式~~ | ~~v1.2.0+pic21 净化 = 已删~~ | ~~`--image` + `--last-frame`~~ | ~~**禁用**~~ | ~~**禁用**~~ |

**⛔ 反模式**（v1.2.0+pic21 · v7 净化版）：
- ❌ **v15 范式用 `--image` + `--last-frame`**（v7 范式已删 · 必用 `--ref-images`）
- ❌ **v7 范式 2图=1Clip 合并**（v7 范式已删）
- ❌ **首尾帧过渡**（`--image` + `--last-frame` 组合 = 禁用）

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
5. 范式：v15 导演思维版（**唯一** · v7 已删 · 禁用）
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

**达尔文评估方法**（v1.2.0+pic22 升级 · 2026-06-10 用户拍板方向）：
- ❌ 旧方法 = 8 维静态结构评分（触顶 96.5 4 天无进展 = 失效率高）
- ✅ **新方法 = 核心任务支持率**（5 步调度 D1-D5 触发率 = 81% → 88.5% → 97% → 100% 在 6 小时内撞天花板）
- 详见 `results.tsv` 2026-06-10 4 条记录 + 看 `darwin-skill` §"Phase 1 基线评估" 5 步核心任务场景
- **触发场景**：任何 picturebook-video 重构/优化后跑达尔文验证 = 必用新方法，不要退回到 8 维评分


## 与子 agent 的关系

主 agent **必做**：
- ✅ 验证子 agent 输出 schema
- ✅ 持久化子 agent 输出到磁盘
- ✅ 翻车时决定重发哪个子 agent
- ✅ 接受/降级决策
- ✅ Step 0.5 绘本场景对位检查（v1.0.2 新增）
- ✅ C/D 子 agent timeout 后续跑（v1.0.2 新增）

主 agent **不做**：
- ❌ 拼 prompt（那是 C 的事 · **v1.2.0+pic21 起 = 主 agent 直拼 v15 6 段骨架**）
- ❌ 跑视频（那是 D 的事，除非 D timeout 续跑）
- ❌ 抽帧验证（那是 D 的事）
- ❌ 凭印象选节奏（那是 C 的事）


## 详细规范位置

- **v15 6 段骨架模板（v1.2.0+pic21 唯一权威）**：[references/分镜设计规范-v15director.md](references/分镜设计规范-v15director.md)
- **v15.1 长旁白拆分**：`references/长旁白拆分规范-v15.1.md`
- **节奏档位表**：见 C 子 agent `agents/storyboard-design/SKILL.md` "决策规则"
- **文字保留铁律 v1v2v3**：`references/绘本文字保留铁律-v1v2.md`
- **末帧 ≠ 定格海报**：`references/2026-06-06-pic2-mvp-validation.md`
| 视频交付不抽帧 | `references/视频交付工作流-不抽帧.md` |
| 重构根因 | `references/2026-06-06-v1-refactor-rationale.md` |
| **v1.0.1 实战 Pitfall** | `references/2026-06-07-v1.0.1-pitfalls.md`（2026-06-07 Pic2 Clip 8 收势节奏拖慢）|
| **v15 4 段骨架模板**（v1.0.3+pic12）| `references/v15-4段骨架-模板.md`（**用户根本性纠错**："底层核心 = prompt 写法结构"，模板化 v15 4 段，11 个变量必填，**主 agent 填变量 = 终稿 prompt**）|
| **v1.0.2 Pic3 Welcome 实战验证** | `references/2026-06-07-pic3-welcome-validation.md`（2026-06-07 Pic3 Welcome 9 Clip 实战 0 错位 · v15.2 铁律 #54 完整闭环 · C/D 续跑模式沉淀）|
| **v1.0.2 Pic4 No 不 实战验证** | `references/2026-06-07-pic4-no-validation.md`（2026-06-07 Pic4 No 不 9 Clip 实战 0 错位 · v1.0.2 完整流程首次端到端跑通 · C 不写 prompt_draft + 主 agent 填 v15 模板 + B 串扰风险警告 · 铁律 #59-#65）|
| **Pic4 No v5 节奏公式重构**（用户两步推导）| `references/2026-06-07-pic4-no-v5-rhythm-formula.md`（2026-06-07 Pic4 v3 跑通后用户反馈"末帧仍太短"，原话两步推导：① 朗读完最低 3s ② + 2s 末帧静默。v5 公式：5/6/7/8s 四档 · 末帧静默 2.9-3.8s · 镜头数 2-3 · 微动元素 4-6 · 铁律 #69）|
| **飞书视频交付与目检反例排查** | `references/视频交付与目检反例排查.md`（2026-06-07 Pic4 clip1 用户目检反例沉淀 · vision_analyze 4 步排查法 · 4 个可能根因 · 完整证据链交付模板 · 决策树）|
| **声音策略分支**（铁律 #86）| `references/sound-strategy-branches.md`（**v1.0.3+pic13 新增** · Pic6 Cow clip7 实战沉淀 · 3 旁白类型 × 声音策略分支表 · seedance 命令差异 · 触发条件判定逻辑 · 反模式 4 条 · **不破坏 4 维控制底层核心**）|
| **Pic5 Bird 鸟 8 段 v6 模板首次跑通** | `references/2026-06-07-pic5-bird-validation.md`（v1.0.3+pic13 · 8/8 succeeded · 整数时长 0 错位 · 50.66s · 8 task 并行轮询 ~7min · 4 维加权 3.8/5 首次实战 · en_color_pattern 清洗 · fill_v6_bird.py 复发待清理）|
| **Pic6 Cow 牛 8 段实战验证** | `references/2026-06-08-pic6-cow-validation.md`（**v1.0.3+pic13 新增** · 2026-06-08 · 8/8 succeeded · 58.66s · 6 并行轮询 ~3min · 整数时长 100% 命中 · md5 0 错位 · 用户 3 轮纠错（OW 拆分/15s 上限/TTS 对齐）+ 用户明确纠错"不主动抽帧自检"沉淀为铁律 #87 · fill_v15 硬编码修复沉淀为铁律 #88）|
| **v6 5 段模板文档** | `references/v6-5段骨架-模板.md`（v1.0.3+pic12 新增 · v15 + 文字持续可见段 · 12 变量清单 · EN_COLOR_DESC 两种格式 + 字符顺序浮现时间表 · Pic5 Bird 实战沉淀）|
| **声音策略分支** | `references/sound-strategy-branches.md`（v1.0.3+pic13 新增 · Pic6 Cow clip7 OW 家庭 5 词实战沉淀 · 3 旁白类型×声音策略分支表 · TTS 音轨对齐 · **4 维控制底层核心不动** · 铁律 #86 候选）|
| **Pic7 Horse 马 实战验证** | `references/2026-06-09-pic7-horse-validation.md`（**v1.0.4+pic14 → v1.0.5+pic15 → v1.0.6+pic16 → v1.0.7+pic17 完整闭环** · 2026-06-09 · 5/5 succeeded · 0 错位 · 48s · v15 + 2图=1Clip 兼容 + 5 档声音策略 + 参考图文字保真 + Cat 范式回滚 v2 · 4 个 commit `2b957a4` `8ddbb34` `f4950b9` `d7cfaf0`）|
| **Pic7 Horse v1.0.8 终极修复** | `references/2026-06-09-pic7-horse-v108-success.md`（**v1.0.8+pic18 · Cat 范本对齐 · 5 词全对 + 零幻觉 + OR Family 完整** · 2026-06-09 · 1 commit · 5 轮迭代元教训沉淀）|
| **分镜设计规范 · v15 导演思维版** ⭐ 2026-06-10 Rabbit 验证 v1.0.0 | `references/分镜设计规范-v15director.md`（**任何 seedance 2.0 绘本 prompt 写法的单一权威入口**· 6 段骨架 + 镜头数算法 + 4 逻辑 + 运镜术语库 + 动作量化 + Rabbit newclip1 v2 验证模板· **v6 旧版"整段不分镜"是翻车坑，新规范要求多镜头时间线分镜**）|
| **绘本导演思维 · 4 步原则实战库** ⭐ 2026-06-10 Hamster 强纠错后 | `references/绘本-导演思维-prompt写法-2026-06-10.md`（**用户强纠错**："镜头设计不连续"4 步原则（看图推断 + 不固定 3 镜 + 末帧真正静默）· Hamster 8 段实战 + 7 个反模式库 + Clip 1 v1 vs v2 对比）|
| **seedance prompt 翻车修复方法论** ⭐ 2026-06-10 Pic10 v2→v3 沉淀 | `references/seedance-prompt-翻车修复方法论-2026-06-10.md`（**prompt 写翻车后怎么修**——5 步法（分症状 A 画面/B 音频/C 角色/D 时长 / 走诊断树 / 改对应段 / 单 Clip 端到端先验 / 沉淀到 skill）+ 4 个实战案例：Pic10 v2→v3 修复"莫名说话声" / Pic10 v1→v2 修复镜头死板 / Pic8 v1→v2 修复完全静默 / Rabbit newclip1 v1→v2 修复镜头过密 + 翻车修复优先级表（最高频 = B 类元数据术语触发人声）· 用户原话"这次修复了音频问题"后固化）|
| **任务完成度自检流程** ⭐ 2026-06-10 Dog 错位发视频事故 | `references/任务完成度自检流程-2026-06-10.md`（**v1.2.0+pic23 新铁律详细**· Dog 18:15 错位发视频事故复盘 · 4 步对账流程必走 = ① ffprobe 元数据校验 ② 抽帧 + native vision 视觉目检 ③ 校验文件名 vs 内容身份一致 ④ 写"对账报告" · **元教训级铁律 = 任何汇报"已完成"前必走** · 第二次犯"幻觉成功"教训）|
| **Dog 4 段 11 个元教训汇总** ⭐ 2026-06-10 DOG | `references/2026-06-10-dog-v1.2.0+pic24-元教训汇总.md`（**v1.2.0+pic24 升级依据** · 11 个问题 = A 类 3 个流程型（错位发视频/主动抽帧/跑完不发视频）+ B 类 5 个规划型（v22 规范漏洞）+ C 类 3 个质量型（莫名人声/出BGM/运镜 6 分）· 8/11 = "之前 skill 仓已有约束 · 主 agent 又违反" = 强制化失败 + 6 条新铁律修复方向）|
| **Pic10 Hamster v3 翻车修复方法论** ⭐ 2026-06-10 HAMSTER | `references/seedance-prompt-翻车修复方法论-2026-06-10.md`（**prompt 写翻车后怎么修**——5 步法（分症状 A 画面/B 音频/C 角色/D 时长 / 走诊断树 / 改对应段 / 单 Clip 端到端先验 / 沉淀到 skill）+ 4 个实战案例：Pic10 v2→v3 修复"莫名说话声" / Pic10 v1→v2 修复镜头死板 / Pic8 v1→v2 修复完全静默 / Rabbit newclip1 v1→v2 修复镜头过密 + 翻车修复优先级表（最高频 = B 类元数据术语触发人声）· 用户原话"这次修复了音频问题"后固化）|
| **Rabbit v6→v15 翻车实战链** ⭐ 2026-06-10 Rabbit 8 Clip 验证 | `references/Rabbit-v6-v15-翻车实战链-2026-06-10.md`（**v6 简化版"整段不分镜"= 7 个垃圾视频 = 用户强烈纠错**的完整实战链：Pic4 v2 14s IT 家族特例 OK → 当通用 v6 范本错套 7 Clip → 全部死板推镜头 → 读官方 doc2 §分镜时序+§运镜红线+§特殊字符 → 写分镜设计规范 v1.0.0 → newclip1 v2 通过 → 8/8 Clip 跑通 49.28s）|
| **Hamster 仓鼠 · v15 唯一入口实战** ⭐ 2026-06-10 本 session 验证 | `references/2026-06-10-hamster-v15-end-to-end-validation.md`（**v1.2.0+pic21 净化后首本绘本实战**：8 段平行句式领读型 · 8 Clip · 45s 总时长 · Clip 1 单测端到端 3 分 33 秒 + seed 23741 + md5 0e0cf2 跑通 · 6 个新发现 + 10 条反模式库 + 复用模板）|


## v0.7.1+pic7 → v1.0.0 → v1.1.0 → v1.2.0 变化清单（v1.2.0+pic21 · v7 净化版）

| 维度 | v0.7.1+pic7 | v1.0.0 | v1.1.0+pic20 | **v1.2.0+pic21** |
|---|---|---|---|---|
| SKILL.md 行数 | 568 | ~200 | ~270 | **~550**（v7 净化后 · 路由简化）|
| 主 agent 职责 | 干全部 | 只调度 | 只调度 | 只调度（**v15 唯一入口**）|
| 子 agent 数 | 0 | 4 | 4 | 4 |
| 节奏选档 | 凭印象 + 标版必跑 | 档位表强制 | v15.2 强化（不主动加镜）| 同 v1.1.0 |
| 朗读时长 | 凭语感 | B 子 agent 量化 | 同 v1.0.0 | 同 v1.0.0 |
| 末帧策略 | 标版 2-3s 静默 | 调性 × 系数 + 画面微动 | v15.2 收势约束 6s 3 镜头 | 同 v1.1.0 |
| 翻车处理 | 主 agent 自己改 prompt 重跑 | 报告回主 agent → 重发 C 改 | 同 v1.0.0 | + C/D 续跑模式 |
| 并行度 | 串行 | A+B 并行 | 同 v1.0.0 | + Step 0.5 场景对位 |
| **范式** | v15.1 标版 | v15 4 段 / v7 2图=1Clip 二选一 | v15 导演思维版 / v7 二选一 | **v15 唯一入口（v7 已删）**|
| **seedance 调用** | `--image` 首帧 | v15 走 `--ref-images` / v7 走 `--image`+`--last-frame` | 同 v1.0.0 | **只用 `--ref-images`（首尾帧禁用）**|
| **实战绘本** | 0 | Pic2（部分）| Pic2 8 Clip（v1.0.1+pic10）| **Pic8 Rabbit 8/8 跑通 49.28s（v1.2.0+pic21）**|


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
| C 子 agent 600s timeout | **主 agent 续写**主索引（Python 聚合 clip1-9.json）| 不重发 C |
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
