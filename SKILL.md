---
name: picturebook-video
description: 静态绘本转儿童动画视频工作流。输入静态图（≥1张）+ 旁白，输出完整动画视频。严格遵循即梦官方9阶段SOP框架，针对绘本动画场景进行关键适配。适配场景：已有静态绘本图片 + 旁白的半成品素材，直接进入分镜设计阶段。
triggers:
  - 制作绘本动画
  - 绘本转视频
  - 静态图转动画
  - 绘本生视频
---

# picturebook-video · 绘本动画制作工作流

|> 将静态绘本图片转换为儿童动画视频的完整工作流。
|> 输入：静态图（≥1张）+ 旁白；输出：可播放动画视频。
|> 严格遵循即梦官方 SOP 架构（Phase 0-9），针对绘本动画场景进行核心适配。

> 📚 **遇到问题先看范式索引**：[VERSION_INDEX.md](VERSION_INDEX.md) —— 速查 12 个实测范式（v3-v15）的核心/状态/适用场景。详细实测日志在 [references/versions/](references/versions/)。
> 检索示例：找"怎么禁 BGM" → v7 / 找"多图分镜" → v15 / 找"BGM 调性统一" → v10 / 找"运镜调性" → v15（**2026-06-05 起绘本默认**）。

---

## 定位说明

本 skill 针对**已有静态绘本图片 + 旁白**的半成品素材，跳过 Phase 0-4（创意发散 / 内容大纲 / 剧本创作 / 素材挖掘），直接进入：

```
Phase 5: 分镜设计（四步走）
Phase 6: 需求确认
Phase 7: 参考素材生成（注：绘本场景直接复用静态图，跳过本 phase 的主体生成步骤）
Phase 8: 分镜生视频
Phase 9: 视频剪辑/成片
```

---

## ⚠️ 阅读前必须理解的核心差异

| | 官方短剧 SOP | 绘本动画（本 skill） |
|--|--|--|
| **输入** | 剧本（连续动作） | 静态图 + 旁白（独立叙事单元） |
| **图间关系** | 物理连续动作，可设计「接力」 | 每张图独立，无物理连续动作 |
| **clip 衔接** | 靠动作接力 + 剪辑转场 | 靠每个 clip 内部的「叙事收势」设计 |
| **分镜切分** | 从剧本拆分镜头 | 从「静态图 + 旁白」设计叙事单元 |
| **结尾处理** | 动作进行中，下一个 clip 接上 | 必须设计完整的「起承转合」，clip 有头有尾 |

**官方 SOP 的「衔接」机制（scene-reflection 检查动作衔接 + Phase 9 剪辑转场）在绘本动画场景下不适用。**
**解决方案在 Phase 5 Step 1（叙事单元设计）阶段，不在剪辑阶段。**

---

## ⚠️ 启动前必问 6 件事 + 必避 5 条（2026-06-05 Say 说绘本踩坑 · 关键教训 #31 · 启动**最前**）

> **核心问题**：本次踩坑都源于"默认值猜错 + 切分方案擅自定 + 私自延伸单 Clip 改动 + **运镜调性不符**"。
> 修复方案：**启动任何绘本任务前必问 6 件事**，不脑补。

### 6 必问（启动前跟用户确认）

1. **视频比例**？（16:9 / 4:3 / 16:10 / 1:1 / 9:16）
   - 默认 16:9（短视频平台标准）
   - **不查原图比例**——视频模型自动适配

2. **目标时长**？（单 Clip / 总时长 / 短视频 15-30s / 完整绘本 60-90s）
   - **领读型 = 单 Clip 4s**（硬下限）
   - 完整绘本 = 按 skill 公式 8/9/10s

3. **切分方案**？（1图=1Clip / 领读型 4-Clip 合并 / 其他）
   - **领读型默认 = 4-Clip 合并**（`8s+8s+9s+10s=35s`）—— 走 `leading-reading-4clip-pattern.md` 模板
   - **1图=1Clip 仅在 3 条件不满足时**用（旁白<8s + 场景相似 + 弱叙事弧）
   - 切分方案由 skill 默认 + 用户确认（**不擅自合并/拆分**）

4. **运镜调性**？（活泼有动感 / 治愈舒缓 / 动态开合 / 静态展示）
   - **活泼有动感**：多用"快速推 / 砰弹出 / 跳入 / 推脸"等动态词 + 秒级控制
   - **治愈舒缓**：多用"缓推 / 几乎不动 / 留白"等
   - **动态开合**：开篇强动 + 中段稳态
   - **静态展示**：突出动作和表情
   - **必问**——直接决定 prompt 写"3 秒后"vs"快速"
   - **秒级控制允许**（v10 范式就用秒级控制 + 强动感）—— **时间感描述 ≠ 套公式**

5. **运镜规则**？（按画面类型定制 / 套公式 / 强动感开场）
   - 套公式 = ❌（"中景→中近景缓推"模板套所有 Clip = 反模式）
   - 按画面类型定制 = ✅（铁律 27 6 种类型：封面/动作/多人/情感/礼物/动态）
   - **注意**：时间感描述（"3 秒后""砰弹出"等）≠ 套公式——**允许**

6. **范式风格**？（领读型同氛围 v10 / 调性匹配 v8 / 静默治愈 v7 / 强动感 v9）
   - **绘本默认 = v15**（v14 骨架 + 6 必问 + 音效密集型，**2026-06-05 起**）
   - 备选 v14 仍可用（4 段骨架 + v7 静默型）
   - 备选 v7（静默）/ v8（每 shot 调性）/ v9（整 Clip 一致）
   - 详见 [VERSION_INDEX.md](VERSION_INDEX.md) + [v15.md](references/versions/v15.md)

### 5 必避（基于 5 个实测问题）

- ❌ 擅自合并 Clip
- ❌ 套硬编码默认值（4:3 / 8s）
- ❌ 私自延伸单 Clip 改动到全局（用户改 Clip 1 ≠ 全局 4s）
- ❌ **套运镜公式**（"中景→中近景缓推"模板套所有 Clip）—— **2026-06-05 撤回"运镜三禁"**（"3 秒后""砰弹出"等秒级控制 ≠ 套公式，**允许**）
- ❌ 默认重提交 task（先查 ark list 端点找 ID / 问用户）

### 6 必问跟决策权的关系

SOUL.md 的"决策权默认归我"原则**不适用于启动前**：
- ✅ 启动后选范式/选运镜 = 我定
- ❌ 启动前的"切分方案/比例/时长/**运镜调性**/运镜规则/范式风格" = **必须问**

**判断口诀**：
- "用户已经说过 X" → 不问（用 X）
- "skill 里有明确默认值" → 不问（用默认值 + 报告）
- "skill 没有默认值 + 改了不可逆" → 必问
- "skill 没有默认值 + 改了可重跑" → 默认值 + 报告

---

## 启动前检查（Pre-flight） · 关键铁律（Say 说绘本踩坑 · #25 #26 #27 + #28 #29 #30）

> ⚠️ **Phase 5 启动前必读**。本次踩坑全部类级，已写入关键教训 #25-#30。

| # | 铁律 | 简记口诀 | 触发现场 |
|---|------|---------|---------|
| 25 | 旁白语言版本 = 用户指定的那一栏（不是图上有啥）| "用户说 X 版" = "X 版**完整那一行**" | Phase 5 Step 0（看素材表是单栏还是双栏） |
| 26 | 彩色文字"自然融入"，末帧消失合规 | "v2 措辞保留，单测不再报'末帧丢失'为 bug" | Phase 8 单测门 5 项检查（已并入 #3.5） |
| 27 | 运镜服务于故事，不是固定公式 | "看图选运镜，不套'中景→中近景缓推'" | Phase 5 Step 1 写法选择（运镜优先选表置顶） |
| **28** | **4s 是硬下限不是推荐值** | "**收到'4s/6s/8s'反馈只对该 Clip 生效**，不套用所有 Clip" | Phase 5 Step 2 + Phase 8 跑前（算字数×0.3s） |
| **29** | **不猜 · 不擅自延伸用户指令** | "**用户说 A 只做 A**；不凭直觉猜，不直接说'我猜'" | Phase 5-8 全流程（每次回答前自问"这是用户说的还是我猜的"）|
| **30** | **status=succeeded 后必须验证本地文件存在** | "**发飞书前 `ls -lh` 确认文件**，不只看 status" | Phase 8 跑完 wait 命令后（异常/打断场景） |
| **31** | **任务叫停 = 等结果自然完成，不需 kill** | "**Seedance API 不支持中途 cancel**；叫停 = 废弃结果，不是不让跑" | Phase 8 用户喊"停"/"取消"时 |

**详细规则 + PIG/Say 对照示例 + 修复**见下文关键教训 #25 #26 #27。

**Phase 5 启动前 3 个必查 + 4 个必避**（2026-06-05 Say 绘本实测踩坑补强）：

| 必查/必避 | 触发条件 | 修复 |
|---|---|---|
| ⚠️ **必查 A**：每段旁白字数 × 0.3 = 单段时长，**单 Clip ≥ 4s 硬下限** | 写 prompt 计算时长时 | 时长 = max(4s, 旁白字数 × 0.3s) |
| ⚠️ **必查 B**：领读型合并 3 条件**必须同时满足** | 2图=1Clip 决策时 | 旁白<8s + 场景相似 + 弱叙事弧，**3 条 AND** |
| ⚠️ **必查 C**：prompt 文字 = 中文版旁白稿**完整那一行**（不是只中文、不是英文版）| 双栏素材表（中英对照）| 复制完整 `中文 + 小写英文跟读` |
| 🚫 **必避 1**：套"0-Xs / 起承转合"时间轴公式到所有 Clip | 写 prompt 时 | 按铁律 27 运镜定制表选（封面/动作/多人/情感/礼物/动态 6 种） |
| 🚫 **必避 2**：把"4s 硬下限"读成"每条都 4s" | 用户评价"太长" | 4s 是下限不是推荐，**用户说 4s = 觉得当前 8s 太长**，**不**是统一改成 4s |
| 🚫 **必避 3**：合并切分表 vs 拆分切分表混用（脑里还记 6 Clip 写 10 Clip prompt）| 切分方案改过后 | 写每个 prompt 前**先列当次切分表**贴到对话顶部，逐 Clip 引用 |
| 🚫 **必避 4**：并行提交不存 task ID（6 个 task ID 全丢）| 批量提交 2+ 个 task | 每次用 `TASKID=$(...)` 存 + 立刻 `wait $TASKID` 阻塞，或用 ark list 端点挽救 |

---

## ⚠️ 启动前检查（Pre-flight）

1. **下载官方 SOP**：从飞书云盘 `TBUNf0P7qlBz43dMvwecPxq6nGe` 下载所有文件，下载后比对首行 `# 标题` 确认实际内容，**不能按文件名判断**
2. **读取 seedance2.0-tool**：`skill_view(name='seedance2.0-tool')`，了解 CLI 命令格式和参数限制
3. **确认图片和旁白已就绪**：图片已上传到工作目录，旁白是已确认的最终版本

### 3a. 素材在飞书云盘怎么办？

如果用户的图片/旁白在飞书云盘文件夹（`aistar-work.feishu.cn/drive/folder/xxx`），**不要用 browser 打开网页**。完整 SOP 见 `references/lark-cli-drive-access.md`，核心步骤：
- `lark-cli config bind --source hermes --identity user-default`（个人身份，bot 看不到个人云盘）
- `lark-cli auth login --no-wait --json --domain drive` 拿 device_code + verification_url
- `lark-cli auth qrcode "<url>" -o qr.png` 生成二维码给用户扫
- 用户扫完 → `lark-cli auth login --device-code "<code>"` 续轮询
- `lark-cli api GET /open-apis/drive/v1/files --params '{"folder_token":"..."}'` 列文件
- 批量下载到本地工作目录（`--output` 必须是相对路径）

跑完用 `lark-cli auth status` 确认有 `drive:drive.metadata:readonly` + `drive:file:download` 两个 scope，否则列文件会 `Permission denied`。

> **2026-06-02 教训**：本次实测有 5 个坑——lark-cli 不在 skills_list 初查范围内 / `feishu_drive_*` 工具 unavailable / browser 需登录态 / 权限 scope 默认缺 drive:drive / device code 10 分钟过期。**修复**：触发词含「飞书云盘/lark-cli/feishu drive/drive folder」时**先 `skill_view(name='lark-cli')`** 再执行。

### 3b. 素材接入方式速查表（4 种）

| 方式 | 关键词 | 处理方式 |
|------|--------|----------|
| **飞书云盘** | 「lark-cli」「飞书云盘」「feishu drive」「aistar-work.feishu.cn/drive/folder/」 | 走 §3a + 加载 `lark-cli` skill |
| **对话直发** | 用户直接发送图片/文件 | 用 `feishu_doc_read`/`vision_analyze` 读，不需要走云盘 |
| **本地路径** | 「路径」「~/Downloads」「/home/...」 | 直接 `read_file` / `vision_analyze` |
| **API token** | 「OpenAPI」「DID」「附件 token」 | 走对应服务 API（云盘 token 用 §3a lark-cli 流程） |

**判断信号**：
- 用户发 `https://aistar-work.feishu.cn/drive/...` → §3a lark-cli（**不要用 browser**）
- 用户发 `https://aistar.feishu.cn/docx/...` → 飞书文档 `feishu_doc_read`
- 用户发 `https://open.feishu.cn/open-apis/...` → `lark-cli api` 直调
- 用户说「图片发你了」+ 附件 → `vision_analyze`

---

## 创作整体流程（7个阶段）

```
Pre-flight: 启动前检查
    ↓
Phase 5: 分镜设计（四步走）
  ↳ Step 1 叙事单元设计（绘本版分镜切分）
  ↳ Step 2 分镜计时
  ↳ Step 3 分镜组合
  ↳ Step 4 连贯性校验
    ↓
Phase 6: 需求确认
    ↓
Phase 7: 参考素材生成（复用静态图）
    ↓
Phase 8: 分镜生视频
    ↓
Phase 9: 视频剪辑/成片
```

---

## 自动化原则（用户偏好 · 2026-06-03 Ok 好的绘本实测）

> ⚠️ **用户原话**："**你自己按照 picturebook-video 的流程，自动化处理，不是叫你别看图。**"
> 核心原则：**agent 按 skill 流程跑完全部步骤 → 输出最终交付物（提示词/分镜表），不在中间停下来描述中间过程。**

**适用场景**：用户给"素材已就绪 + 让你做绘本视频"类指令。

**自动化跑完的步骤**：
1. ✅ Pre-flight 自查（0 + 1 + 2 + 3）
2. ✅ Phase 5 全部 4 步（叙事单元 → 计时 → 组合 → 连贯性校验）
3. ✅ Phase 6 输出分镜表 + 4 个 Clip 完整 prompt
4. ✅ 11 项自检 + 报告
5. ⏸️ Phase 7 上传 + Phase 8 单测门 **必须停下来等用户拍板**（不可逆 + 收费）

**不自动化的事**：
- ❌ **不**逐张图复述看到什么（用户不需要文字版画面描述）
- ❌ **不**在 Phase 5 步骤 1-4 中间停下来等用户确认（"风格锚点你定"是用户授权）
- ❌ **不**输出过度元描述（"我看了图1-8，发现..."——直接给最终结论）

**风格锚点 / 合并策略 / 时长分配 / 范式选择**——agent 按 skill 默认 + 实测图片观察**自己定**（SOUL.md 决策权归我原则）。用户不同意会**直接说**"改 XX"，不需要预先确认。

> **画外音测试**：每个 Phase 输出前自问"这段话是给用户做决定用的，还是我自说自话？"——是后者就删掉。**只输出对用户决策有用的内容**（如 Phase 6 提示词 + 自检结果 + 阻塞项）。

---

## ⚠️ 工作流原则 · 探索式迭代（2026-06-03 v9→v10→v11 沉淀 · 类级教训）

> **本节是 picturebook-video skill 的核心工作流原则**——不只是绘本视频，**所有"通过实测迭代完善 skill"的工作流**都适用。

### 用户的实际工作流 ≠ skill 默认工作流

**用户原话**（2026-06-03 v11-α 失败后园丁阶段）：
> "我的工作方式就是在和你的对话中，通过实际的测试来探索和不断完善整个 skill。"

**这意味着用户每次对话的工作流**：
```
测试 1 个变体（v10）→ 发飞书看效果 → 用户判断（"v10 路线可行"）→ 沉淀 v10 范式
  → 测试下 1 个变体（v11-α）→ 发飞书看效果 → 用户判断（"几乎没有什么变化"）→ 沉淀 v11-α 失败
  → ...
```

**而 skill 当前默认是"PRD→实现→沉淀"模式**——一次性给完整需求，跑完整流程，输出成片。**两者不匹配**。

### skill 必须支持的工作流特征

| 特征 | 含义 | 当前 skill 表现 |
|------|------|----------------|
| **小步快跑** | 用户每次只改 1 个变体（v10 = 1 个改动 / v11-α = 1 个改动）| ✅ 范式分 v7/v8/v9/v10/v11-α 支持 |
| **每次沉淀** | 每次跑完必须沉淀（成功/失败都沉淀）| ✅ SKILL.md §v9/v10/v11-α 章节有写 |
| **实测 + 用户判断** | 必须人耳听/眼看，不能只靠 AI 量化 | ✅ 单测门 SOP 强调人耳听 |
| **失败也沉淀** | 失败方向（v11-α）也要写进 skill，避免重复踩坑 | ⚠️ v11-α references 文档已加 §10 失败评估 |
| **探索状态管理** | 哪些方向在测、哪些已弃、哪些待验——状态要可见 | ❌ 缺"探索路线图"章节（园丁 Phase 2 建议 P1）|

### 探索式迭代工作流的 3 条铁律

1. **改 1 个变量 → 跑 → 用户判断 → 沉淀**——不要一次改多个变量（v9 改 BGM 写法 / v10 改跨 clip 主题 / v11-α 改微动作 都是各 1 个变量）
2. **失败方向要明确标"已死"**（v11-α）——避免下次又跑同方向；v11-α references 文档 §10 "实测最终结果"段是样板
3. **用户反馈模糊概念时先问"是哪个范围"**——v9 出现根因（"听用户原话要听场景"教训）："clip 内部断层"≠"clip 之间衔接"，必须让用户澄清范围

### 范式版本号约定

每次绘本启动把范式版本号写进 `clips-prompt.json` 的 `version` 字段（如 `"v10-20260603"`）。**版本号是探索式迭代的可追溯性**——未来翻旧项目能知道当时跑的是哪个范式。

### 探索方向归档（园丁 Phase 2 建议 P1，待实施）

skill 当前缺"探索路线图"段。**未来加上**：
```markdown
## 探索路线图

| 范式 | 状态 | 目标 | 验证方式 | 备注 |
|------|------|------|---------|------|
| v7 静默型 | ✅ stable | 安静绘本无 BGM | Cactus 实测 | 默认备选 |
| v8 调性匹配 | ⚠️ deprecated | 复杂多情绪 | Red/Ok 实测 | 有 clip 内部断层问题，被 v9 替代 |
| v9 整 Clip 一致 | ✅ stable | 整 Clip 一段 BGM | Eat 吃实测 | 当前默认 |
| v10 跨 Clip 同主题 | ✅ stable | 领读型同氛围 | Eat 吃实测 | v9 升级版 |
| v11-α 微动作 | ❌ parked → **已死** | 画面动感增强 | Eat clip 2 失败 | 根因是输入限制（不是 prompt） |
| v11-β 改 hold pose | 🔜 planned | 静态图运镜 | 未测 | v11-α 失败后**优先级降** |
| v11-γ 软化 final frame | 🔜 planned | 不冻结 | 未测 | **不建议**（v7/v8 验证过冻结必要）|
| v11-δ 多帧输入 | 🔜 **P0 planned** | 即梦生成中间帧 | 未测 | v11-α 真正解法 |
| v11-ε 换写实风绘本 | 🔜 planned | Dear Zoo 验证 | 未测 | v11-δ 的验证绘本 |
```

**当前实际状态**（已沉淀到本节，路线图段落待正式建档）：

| 范式 | 状态 | 目标 | 实测 | 备注 |
|------|------|------|------|------|
| v7 静默型 | ✅ stable | 安静治愈绘本无 BGM | Cactus | 默认备选 |
| v8 调性匹配 | ⚠️ deprecated | 单 Clip 多情绪 | Red/Ok | 已知断层，被 v9 替代 |
| v9 整 Clip 一致 | ✅ stable | 整 Clip 一段 BGM | Eat 吃 | **当前默认** |
| v10 跨 Clip 同主题 | ✅ stable | 领读型同氛围 | Eat 吃 | v9 升级版 |
| v11-α 微动作 | ❌ **已死** | 画面动感增强 | Eat clip 2 | 用户反馈"几乎没有什么变化" |
| v11-δ 多帧输入 | 🔜 **P0** | 即梦生成中间帧 | 未测 | 真正解法 |

---

## Pre-flight · 启动前检查

### 0. 已知踩坑自查（**必做 · 不做会重蹈覆辙**）

> **来源**：2026-06-02 Red 绘本对话中，**已经踩过 2 次的"封面 ≠ P1"** 错误——memory 里有规则但本轮没查就又踩了。**同类任务前必查**。

```bash
# 1) 查所有已知踩坑关键词
grep -E "封面|页码|首图|最后一张|起始|收尾" \
  ~/.hermes/profiles/huiben/memories/MEMORY.md

# 2) 查本 skill 名下的相关教训
grep -E "绘本|picturebook|Red|领读" \
  ~/.hermes/profiles/huiben/memories/MEMORY.md

# 3) 查风控白名单（每次都要校对）
grep -E "风控|敏感|触.*reject|sensitive" \
  ~/.hermes/profiles/huiben/memories/MEMORY.md
```

**自查发现**相关条目 → **必须先读完再继续**（不是扫一眼，而是把规则应用到本轮任务）。**没有任何踩坑相关条目** → 继续 step 1。

**常见已知踩坑**（持续累积，2026-06-02 快照）：

| 关键词 | 踩坑内容 | 修复 |
|--------|---------|------|
| 封面/P1 分离 | 封面认知页 ≠ P1 单词认知页，必须分开 | 封面=WORD!全大写，P1=Look at the [WORD] |
| 风控白名单 | 仅警察/军队/枪/武器/暴力触发；机械/警笛类拟声**可正常使用** | 绘本消防车/汽车/警车视觉动作 + 警笛/喇叭/vroom 全部可以写 |
| 反模板化结尾 | X! X! X! / Find the X! / I can say X! 模板化结尾 | 结尾让孩子参与动作（看/数/发现/感受），不是喊目标词 |

### 1. 下载官方 SOP

飞书云盘文件夹 token: `TBUNf0P7qlBz43dMvwecPxq6nGe`

> ⚠️ 官方文件名与实际内容对不上，必须按 token 判断。下载后必须比对首行 `# 标题` 确认实际内容。

| token | 实际内容 |
|-------|---------|
| `K3fDba7h8obp55xq3x9cnS6Sn6b` | video-sop（即梦视频创作标准工作流程） |
| `U1RsbkaKfo9r3pxVkAAcRibonHf` | video-prompt（分镜生视频技能） |
| `R4ijbDgbYogAmGx9qHrc74qFnoc` | story-ref-gen（故事参考素材生成技能） |
| `XZDNbx1a2o2kTlxy44CcuSIHnHc` | scene-reflection（分镜连贯性校验技能） |
| `JqN6beMjVoaXgRxPlPFcB819npb` | shots-assembly（分镜组合技能） |
| `CI6sbrtxpo28NCxhinPcl19mnsh` | shots-timing（分镜计时技能） |
| `LbhbbPBUtoDstLxnRI1c4TyznJd` | script-chunk（分镜切分技能） |

### 2. 读取即梦 CLI 工具文档

`skill_view(name='seedance2.0-tool')`

了解命令格式和参数限制：
- `--duration` 必须是整数（向上取整）
- 4s ≤ 单个 clip 时长 ≤ 15s
- 默认 `--generate-audio true`

### 3. 确认素材就绪

- ✅ 工作目录已创建（建议 `{项目名}/`）
- ✅ 图片已上传（建议按 `1.jpg`, `2.jpg` 命名）
- ✅ 旁白已确认最终版本

---

## Phase 5 · 分镜设计（四步走）

> **严格遵循官方 SOP 的四步顺序，每步必须完成才能进入下一步，不能跳步。**
> 本 phase 是绘本动画场景的核心差异化所在。

### Step 1 · 叙事单元设计（绘本版分镜切分）

> 官方 SOP：`script-chunk`（将剧本拆分为单个镜头）
> **绘本动画适配**：输入是「静态图 + 旁白」，不是剧本。本步骤将「静态图 + 旁白」转化为「带叙事弧的 clip」。

#### ⚠️ Step 0（Step 1 启动前必做）· 旁白语言版本确认（铁律 25）

**Say 说绘本 2026-06-05 踩坑沉淀** —— 此步是 Phase 5 第一个动作，跳过就会画错方向：

1. **看素材表是单栏还是双栏**
   - 单栏（只有中文或只有英文）→ 直接用
   - **双栏（英文版 + 中文版）→ 用户给的是中英对照**（绘本常见）
2. **明确用户要哪一版**（用户没说 → 默认中文版 = 中英嵌入小写英文跟读）
3. **画面文字 = 用户指定那版旁白稿完整内容**（不是"删 Y 留 X"）
4. **封面 P1 例外**：用大写英文主词（`PIG!` / `Say!`）做概念强调

**诊断口诀**："用户说 X 版" = "X 版**完整那一行**" ≠ "删 Y 留 X"

**PIG/Say 句式对照**：

| 句 | 英文版（不进画面）| 中文版（**进画面**） |
|---|---|---|
| 封面 | `PIG!` | `小猪 PIG！` |
| 故事 | `A pink pig.` | `粉色的小猪，a pink pig` |
| 跟读 | `pig, dig, big, wig, fig` | `小猪 pig 的 IG 家族，pig、dig、big、wig、fig 大集合！` |

**写 prompt 时**：画面文字描述 = 中文版旁白稿完整复制（不是只复制中文）。

**反例（Say v1 我犯的错）**：用户说"我只要中文版旁白" → 我理解成"画面只留中文，删英文" → 完全错方向。

#### 官方 script-chunk 的输出要素

| 字段 | 内容 |
|------|------|
| 镜号 | 从1开始连续编号 |
| 景别 | 远景/全景/中景/中近景/近景/特写 |
| 画面描述 | 当前镜头中看到的内容，**必须完全基于图片** |
| 台词/音效 | 对应本镜头的旁白 |

#### 绘本版的核心增强：叙事单元设计

每个叙事单元（对应一张图片 + 一段旁白）必须设计完整的**四段式叙事弧**：

| 阶段 | 说明 | 设计要求 |
|------|------|---------|
| **起（开场）** | 这个 Clip 从什么状态开始 | 基于静态图画面，描述起始状态 |
| **承（发展）** | 中间发生了什么动作/变化 | 设计1-2个动作变化，不要只是「静止展示」 |
| **转（转折）** | 叙事的高潮点或关键变化 | 旁白核心信息在这里呈现 |
| **合（收势）** | Clip 结尾的状态 | **必须设计「收势动作」——动作完成/达到目的/稳定状态**，避免「动作进行中被截断」的观感 |

#### Prompt 写法选择：连续运镜 vs 时间轴分镜

> ⚠️ **铁律 27（Say 2026-06-05）**：**运镜服务于故事，不是固定公式**。先按画面类型选运镜，再选写法。**禁止套"中景→中近景缓推 3 秒"模板到所有 Clip**。

**运镜优先选表**（铁律 27 沉淀 · 选完运镜再选写法）：

| 画面类型 | 推荐运镜 | 理由 |
|---|---|---|
| **封面（建立感）** | 缓推 | 主角登场 |
| **角色动作为主**（挥手/举牌/比心/捂嘴呼喊）| **静态或极缓** | 突出动作，不抢戏 |
| **多人场景**（教室/门口/聚会）| 拉远 or 水平 pan | 呈现全员 |
| **情感场景**（睡觉/爱心/月亮/挥手告别）| **几乎不动** | 安静氛围 |
| **礼物/递出/分享** | 缓推 + 微向下倾 | 聚焦 |
| **彩带/挥手/风动** | 静态（让物体自己动）| 不抢动效 |

**禁止**：
- ❌ 一律"镜头推进"的默认动作（v1 错版）
- ❌ 镜头运动跟画面动作抢戏（角色挥手时镜头还在动 = 视觉混乱）

> **核心经验（2026-05-26 {项目名}实测）**：
> 起承转合是叙事弧，不是分镜数量。同一镜头内通过运镜可以完成整个叙事弧。
> 两种写法都正确，关键是**根据叙事内容选择合适的写法**。

##### 写法 A：连续运镜（单线动作/单一情绪）

适用：单人动作、情感特写、传承凝视、单一情绪传递。
结构：整段连续运镜，无时间切分，用「最终定格在XX」控制收势。

**⚠️ 时长分配原则（通用逻辑）**：
- 起/承阶段：**尽量简洁**，不做过多铺陈
- 收势阶段：**给足空间**，确保有「落住」的感觉
- 核心原则：让前段让路给收势——前段不能拖到影响收势的完整性
- 收势的本质：动作/情绪「落住」的瞬间，不是「动作进行中被截断」

**写法核心**：
- 起/承：简洁带过，一句话交代场景+起始动作
- 转：旁白核心信息的视觉化呈现
- 收势：**明确三件事——镜头锁住、画面静止、不渐隐不淡出**

示例：
```
中景深蓝夜空下，小女孩双手握持燃烧的火把，目光凝视火焰，面带微笑。
镜头缓慢推进至面部特写，火光映照脸庞。
最终画面定格：镜头完全静止不动，结尾画面不渐隐不淡出，停留至最后一帧。
温暖插画风格，色彩饱和，叙事完整有悠长余韵。
```

##### 写法 B：时间轴分镜（多段节奏/有转折）

适用：舞蹈高潮、多人物互动、多场景转折。
结构：用 `[00-XXs]` 分段标注不同 shot，每 shot 有不同景别或动作内容。

```
[00-02s] 中景篝火熊熊燃烧，小女孩双手高高举过头顶欢快舞蹈。
[02-04s] 周围村民围篝火半圆形演奏乐器，众人微笑注视。
[04-06.5s] 小女孩舞蹈达高潮，旋转裙摆飞扬。
[06.5-09s] 小女孩定格在双手高举姿态，篝火火焰稳定，镜头拉远全景，保持3秒。
温暖插画风格，色彩饱和，叙事完整。
```

##### 选择决策树

```
情节是单线动作还是多段节奏？
├── 单线动作/单一情绪 → 连续运镜写法
│   └── 示例：小女孩举火把仰望、祖孙传承对视、祈福静默
└── 多段节奏/有转折 → 时间轴分镜写法
    └── 示例：篝火舞蹈（起→承→高潮→收）、多人物互动高潮
```

详细写法见 `references/video-prompt-narrative.md`

#### 「收势」设计的三种模式

根据旁白的叙事功能，选择合适的收势模式：

| 模式 | 适用场景 | 收势设计 |
|------|---------|---------|
| **完成式收势** | 旁白描述的是一个完整动作 | 以「动作完成」收尾：举起火把→火焰燃起稳定；制作火把→完成品举起展示 |
| **进行式收势** | 旁白描述的是持续状态 | Clip 结尾保持运动状态，但给出一个「小目标达成」：队列行进→抵达目的地，举起火把 |
| **悬念式收势** | 需要连接下一个叙事单元 | 结尾留一个未完成的动作/问题，但不做大的情绪起伏，保持平稳期待感 |

#### 输出格式

```markdown
## 图片分析汇总

| 图号 | 场景 | 人物/关键元素 | 色彩/氛围 |
|------|------|-------------|-----------|
| 1.jpg | 白天梯田村庄 | 10+人穿民族服饰，白墙红门，远景 | 绿/白/红，明亮开阔 |

## 旁白匹配

| 图号 | 旁白 | 匹配原因 |
|------|------|---------|
| 1.jpg | 夏天到来时，许多少数民族会相聚庆祝一场热烈而明亮的节日。 | 白天多人民族服饰场景，开场交代 |

## {项目名}分镜清单

### Clip N · [分镜标题]

| 镜号 | 景别 | 画面描述 | 旁白 | 叙事阶段 |
|------|------|---------|------|---------|
| 1 | 中景 | 阳光明媚的乡村庭院，一男一女坐在木凳上整理松木和松脂，男子用柴刀削木棍，女子整理火把材料。 | 人们用松木和松脂制作火把，保证火焰燃烧得又稳又亮。 | 起：开始制作 |

**叙事单元设计说明：**
- 起（00-02s）：男子用柴刀削木棍，女子整理火把材料
- 承（02-04s）：两人配合制作，男子将削好的木棍递给女子，女子用松脂绑缚
- 转（04-06s）：火把制作完成，男子举起火把
- 合（06-07s）：男子用火绒点燃火把，火焰稳定燃烧，火光照亮两人脸庞 → **收势在「火焰稳定燃烧」，不是「制作中」被截断**
```

#### 执行检查清单（Step 1）

- ✅ 每张图都做了分析和旁白匹配
- ✅ 每个叙事单元都有「起承转合」四段设计
- ✅ 每个叙事单元都有明确的「收势」设计
- ✅ 收势模式选择合理（完成式/进行式/悬念式）
- ✅ 画面描述完全基于静态图，没有用旁白臆造画面
- ✅ 旁白核心信息在「转」阶段呈现
- ✅ Prompt 写法选择正确（连续运镜/时间轴分镜）

---

### Step 2 · 分镜计时（shots-timing）

严格遵循官方规则：

| 类型 | 计算方式 |
|------|----------|
| 台词镜头 | 旁白字数 × 0.3 秒/字 |
| 最低保底 | 每镜 ≥1 秒 |
| 情绪节奏 | 快节奏1-3秒，情感戏3-8秒，空镜2-4秒 |
| 景别影响 | 远景/全景偏长（3-6秒），近景/特写偏短（1-4秒） |
| 单Clip硬约束 | 4s ≤ 时长 ≤ 15s |

> ⚠️ `--duration` 参数必须是**整数**，向上取整（`ceil`）。

#### 收势时长分配原则

**核心原则**：时长分配由旁白的叙事功能决定，不是硬编码比例。

根据旁白内容判断：

| 旁白类型 | 旁白在做什么 | 时长分配逻辑 |
|---------|------------|------------|
| **交代型** | 说明背景/引入场景 | 视觉快速交代，重点在收势落住 |
| **动作型** | 描述一个完整动作事件 | 起→承→转→合，顺着动作节奏走，收势是动作完成态 |
| **情感型** | 传递情绪/感受/氛围 | 前段简洁，快速进入情感核心，收势给足余韵 |
| **高潮型** | 情绪到达峰值 | 前段快节奏推进，收势给到峰值后的稳定态 |

**判断优先级**：
1. 这个旁白在叙事功能上是什么？（交代/动作/情感/高潮）
2. 旁白的核心信息落在哪个词/哪个moment？
3. 为了把这个核心信息传递给观众，视觉需要多长来呈现？

**前段不能让路原则**：前段（起/承）不能拖到影响收势的完整性——无论哪种旁白类型，收势都要有「落住」的空间。

#### 输出格式

```markdown
## {项目名}分镜计时表

| 镜号 | 景别 | 画面描述 | 旁白 | 时长(秒) |
|------|------|---------|------|----------|
| 1 | 中景 | 阳光明媚的乡村庭院... | 人们用松木... | 2.0 |
| ... | ... | ... | ... | ... |

**总时长：7.0 秒**
```

---

### Step 3 · 分镜组合（shots-assembly）

严格遵循官方规则：

**硬约束**：每个 Clip **4s ≤ 时长 ≤ 15s**，绝对不能超。

| 情况 | 处理方式 |
|------|----------|
| < 4秒 | 合并到相邻 Clip |
| > 15秒 | 拆分为多个 Clip |
| 场景完整性 | 同一场景尽量不拆分 |
| 情节连贯性 | 同一段连续对话/动作不拆分 |

#### 绘本场景的两种 Clip 切分策略

> ⚠️ **核心更新（2026-06-02 实测）**：原 skill 默认 1图=1Clip 不适合所有绘本。

| 绘本类型 | 切分策略 | 理由 |
|---------|---------|------|
| **叙事型绘本**（有故事弧、起承转合） | 1图=1Clip | 每页是独立叙事单元，clip 间通过画面切换承载情节 |
| **领读型绘本**（弱情节、靠画面+旁白推，如「英文单词教学」「认知启蒙」） | **2图=1Clip（连续运镜合并）** | 弱情节下 1图 1Clip 太碎、时长撑不到 4s 最低线；合并后用 prompt 内时间线运镜衔接两图 |

**领读型合并的判断条件**（同时满足才合并）：
- 旁白<8s 单段（按 0.3s/字计算）
- 两图场景元素相似（同色系/同主体/相邻景别）
- 弱叙事弧（不需要明确的"前一幕→后一幕"情节推进）

**领读型合并的 prompt 写法**（用首尾帧控制衔接）：
- `--image <前图>` + `--last-frame <后图>` 锁住两个关键帧
- prompt 中间用「镜头推进+暖光晕开」等自然过渡连接两图
- **不需要**官方 SOP 的「尾帧接力」模式（那是漫剧场景的物理连续动作接力，绘本场景不适用）

#### 领读型合并的总时长公式（2026-06-02 实测）

合并后总时长 = `Clip1 时长 + Clip2 时长 + ...`，每个 Clip 分配区间：

| 段落位置 | 推荐时长 | 理由 |
|---------|---------|------|
| **Clip 1（开头）** | 8s | 标题+主形象登场，需要稳 |
| **Clip 2-N-1（中间段）** | 8-9s | 均匀推进，节奏稳定 |
| **Clip N（结尾）** | 10s | 情感核心（坚强/自信/友谊），给足余韵 |

**公式**：`总时长 ≈ 段落数 × 8-10s`，向上对齐到 8/9/10s 整数值。

**例**：8 张图分 4 个 Clip → `8 + 8 + 9 + 10 = 35s` ✅

#### 输出格式

```markdown
## {项目名}Clip表

| Clip编号 | 对应图号 | 总时长(秒) | 画面描述 |
|----------|----------|------------|----------|
| 1 | 1.jpg | 7.5 | 白天梯田村庄，多人民族服饰 |
| 2 | 2.jpg | 7.0 | 夜晚火炬光带，村庄星空 |
| ... | ... | ... | ... |

**总Clip数：10个**
**总时长：67.0 秒**
```

---

### Step 4 · 连贯性校验（scene-reflection）

> **强制 gate，必须完成才能进入 Phase 6 需求确认，不能跳过。**

从以下五个维度逐一检查：

| 维度 | 检查内容 |
|------|----------|
| **人物一致性** | 服装/外观/位置/动作衔接 |
| **道具一致性** | 存在性/位置/外观 |
| **场景一致性** | 光线/天气/陈设 |
| **逻辑连贯性** | 情节/时间/物理规则 |
| **色调统一性** | 整体色调风格统一 |

#### 绘本场景的特殊检查项

| 检查项 | 说明 |
|--------|------|
| **叙事收势是否完整** | 每个 Clip 是否都有「收势动作」，而不是「动作进行中被截断」 |
| **收势模式是否一致** | 收势模式（完成式/进行式/悬念式）选择是否与旁白叙事功能匹配 |
| **Prompt写法是否匹配** | 连续运镜/时间轴分镜的选择是否与叙事内容匹配 |

#### 输出格式

```markdown
## {项目名}Clip表（连贯性校验修复版）

## 校验结果
- 发现问题1：[问题描述]
  - 修复方式：[具体修复方式]
- 未发现其他一致性问题

---

[修复后的完整Clip表]

---

## 一致性注意事项
1. [人物XX]在所有Clip中保持[服装/外观]一致
2. [场景XX]在所有Clip中保持[光影/色调]一致
3. [道具XX]位置保持不变
```

#### 执行检查清单（Step 4）

- ✅ 五个维度都做了检查（人物/道具/场景/逻辑/色调）
- ✅ 叙事收势完整性已检查
- ✅ Prompt 写法选择已检查（连续运镜/时间轴分镜）
- ✅ 所有发现的不一致问题都已标注并修复
- ✅ 修复没有改变原分镜的总时长和情节顺序
- ✅ 最后汇总了所有一致性注意事项

---

## Phase 6 · 需求确认

将以下内容汇总给用户做最终确认：

1. 最终旁白匹配表
2. 最终分镜清单（含叙事单元设计）
3. 最终 Clip 表（含时长）
4. 总时长、宽高比、风格确认

> **用户确认所有内容无误后，才能进入 Phase 7-8。**

---

## Phase 7 · 参考素材生成

> **绘本动画场景的特殊适配**：本 phase 跳过「生成角色/场景参考图」的主体步骤，直接复用已有的静态绘本图片。

### 执行方式

1. 确认每张静态图的资源 ID（通过 `seedance.py upload` 上传获取）
2. 将资源 ID 记录到 Clip 表中
3. 进入 Phase 8

---

## ⛔ Phase 8 必读 · 绘本 prompt 三铁律（强制前置 · 不通过不进 Phase 8）

> 来源：2026-06-02 Red 绘本 v1→v2→v3 三轮实测沉淀。
> **不满足这三条 = 画面切快 + 收势失败 = 白跑一轮**。

### 铁律 1 · 句号切分视觉，音效描述必须用分号 / 逗号

**现象**：v2 用句号 `.` 把视觉流程切成多段，模型把每段当成独立小节执行 → 画面节奏被「音效块」压缩。

**修复**：视觉描述用**分号 `;`** 连接，音效描述**嵌入视觉句中间**（用**逗号 `,`** 串接）→ 整段保持单段连续语义。

```
❌ 错误：起始段. 音效块. 推进段. 收势段. 音效块. 风格段.
✅ 正确：起始段含音效副词, 推进段含音效副词; 收势段含收尾音效; 风格段.
```

### 铁律 2 · 收势词（final frame / camera locks / holds）放最后一句画面描述，后面是音频/禁令/风格段

**现象**：v2 在收势词后追加 `[Sound effect: ... chime settling]` → 模型把视觉定格指令当成"中间过渡"，把尾部音效当成收尾 → 收势失败，画面继续动。

**修复**：收势词必须**是 prompt 的最后一句有意义的画面描述**。v3 范式中收势词是绝对末尾（之后只有风格段），v7 范式中收势词在段 4（之后是音频段+禁令段+风格段）。**收势词后面可以接音频控制/禁令/风格段，但不能再追加"画面动作"**。

```
❌ 错误（v3 范式）：final frame: ... holds to the last frame. [Sound effect: chime settling]. 风格段.
✅ 正确（v3 范式）：final frame: ... holds to the last frame, quiet warm chime settles. 风格段.

✅ 正确（v7 范式）：final frame: ...; Storyboard Audio Description: ...; No background music...; 风格段.
```

### 铁律 3 · 否定性指令分场景：视觉段不能用，音频段能用

**现象（旧）**：v2 末尾加 "No speech, no narration, no background music..." 否定句 → 视觉模型不擅长"反向作画"，这句会变成无效描述，反而把最后一段从"画面定格指令"变成"文字说明"。

**修复（旧）**：删除视觉段的否定句。

**v7 新发现（2026-06-02 里程碑）**：**音频段可以使用否定句**。Seedance 视觉模型"不擅长反向作画"，但**音频模型对 `No X / No Y` 的禁令是遵守的**（参考示例 + Cactus 4 段实测通过）。**这是 v6 → v7 的关键突破**。

```
❌ 错误（视觉段）：风格段. No speech, no narration, no background music — only sound effects.
✅ 正确（视觉段）：风格段.
✅ 正确（v7 音频段）：No background music, no human voice, no narration, no singing;
```

### 三铁律自检清单（写完 prompt 后必跑）

- [ ] 整段 prompt 分号串接（视觉段 1 个分号；v7 范式 7 个分号）
- [ ] 收势词（final frame / camera locks / holds）在 prompt 的**最后一句画面描述**里
- [ ] 收势词后面**不追加任何画面动作**（v3 范式直接收尾，v7 范式接音频/禁令/风格段）
- [ ] prompt 里**没有** `[Sound effect: ...]` 独立块
- [ ] 视觉段里**没有** "no speech / no narration / no BGM" 否定句
- [ ] 音频段里**可以有** "no background music" 禁令句（v7 范式）
- [ ] 音效描述**嵌入视觉句中**（用 `,` 串接）或独立音频段（v7 用 `Storyboard Audio Description:`）

**自检不通过 → 改完再提交**。

### 范式选择决策树（v3 / v7 何时用哪个）

```
绘本类型？
├── 领读型（弱情节、靠画面+旁白推）
│   ├── 重复句式 + 整体氛围优先（如 I eat X / Pete the cat / Dear Zoo）
│   │   ├── 需要 TTS 卡点 + 跨 clip 同 BGM → **v10 范式**（领读型同氛围）
│   │   └── 不需要 TTS 卡点 + 跨 clip 同 BGM → **v10 范式**
│   ├── 需要 TTS 后期卡点 + 单 clip 多情绪 → v7 范式（精准分镜时序+精准动画+精准音频）
│   │   详见 references/分镜时序-精准动作-prompt范式.md（v7 章节）
│   └── 不需要 TTS 卡点 + 单 clip 多情绪 → v3 范式（双图连续运镜，散文叙述）
│       详见 references/领读型合并-双图连续运镜.md
└── 叙事型（强情节、起承转合）
    └── 1图=1Clip 标准模式（不在本 skill 范式范围）
```

> **v15 是 2026-06-05 起的绘本默认范式**（v14 骨架升级：4 段 prompt + 启动前 6 必问 + 运镜调性 + v7-Say 音效密集型）。**v14 仍可用**（4 段骨架 + v7 静默型）—— v7/v8/v9/v10 是 v15/v14 段 4 的音频子策略。详见 [references/versions/v15.md](references/versions/v15.md) + [references/分镜时序-prompt范式-v14.md](references/分镜时序-prompt范式-v14.md)。

### 完整 prompt 模板（v3 范式）

```python
prompt_template = """@Image1 as the opening frame, {起始画面描述}, {起始音效副词};
{camera 运镜描述 + 中段音效副词}, transitions seamlessly to @Image2 as the second half, {结束画面描述};
final frame: the camera locks completely, the image becomes still, no fade, no dissolve, holds to the last frame, {收尾音效副词}.
{风格锁定句}."""
```

**3 个分号，1 个句号（收尾），0 个 `[Sound effect: ...]` 独立块，0 个否定句**。

**红苹果示例**（直接可复用）：

```python
prompt_template.format(
    起始画面描述="the bold collaged letters 'RED' in red, blue and yellow paper stand on a yellow paper strip, a small white rabbit looks up at them, soft white background",
    起始音效副词="gentle paper-landing tap-tap-tap as the three letters settle into place",
    运镜="the camera slowly pushes in with a warm light bloom sweeping across the scene, paper textures become more vivid",
    中段音效副词="soft plop as the apple gently appears",
    结束画面描述="a red paper-collaged apple with green stem and brown leaf sits in the center, handcrafted paper-cut style throughout",
    收尾音效副词="quiet warm chime settles",
    风格锁定句="Children's picture book collage illustration style, paper-cut craft with visible paper texture and torn edges, warm and lively atmosphere, bright primary colors, handcrafted feel",
)
```

> **完整 v1→v2→v3 实战对比**见 `references/绘本音效-prompt写法.md`（三铁律的详细来由 + 错版/对版示例）

---

### Phase 8 · 分镜生视频（video-prompt）

### 绘本场景音频策略（先于 5 要素看）

#### 绘本音频三件事（互不替代，先分清再写 prompt）

绘本视频里**音频有三件事**，**互不替代**：

| 类型 | 是否需要 | 写进 prompt | 由谁生成 |
|------|---------|------------|---------|
| **旁白朗读**（人声念文字） | ✅ 需要 | **否**——旁白走后期 TTS（**待探索**：Seedance 2.0 具备旁白能力，尚未找到合适的 prompt 写法，目前不在 clip 里生成） | 后期 TTS 合成 |
| **BGM 背景音乐** | **A 静默氛围型 ❌** / **B 调性匹配型 ✅** | **A 否** / **B 否（不写 BGM 词，让模型自动配纯音乐）** | Seedance `--generate-audio true` 自带生成 / 后期 ffmpeg 替换 |

**⚠️ 2026-06-03 用户实测反转**：绘本 BGM **不是**默认不要，**两种风格任选**：
- **A 静默氛围型**（Cactus 范式）：绘本默认无 BGM，prompt 段 6 写 `No background music`
- **B 调性匹配型**（Red/Ok 好的范式）：Seedance 自动配调性相符纯音乐 BGM，prompt 段 6 **不**写 `No background music`，**只禁人声**

详见 SKILL.md §"BGM 调性策略"章节。
| **音效**（拟声/环境音，配合画面动作） | ✅ 需要 | **是**——短促拟声、卡点环境音 | Seedance `--generate-audio true` 同步生成 |

#### 绘本音频决策树（写 prompt 前必跑）

```
Q1：这个 clip 需不需要人声念旁白文字？
├── 是 → 走后期 TTS 合成，prompt 不写朗读文字（Seedance 2.0 旁白能力待探索）
└── 否 ↓

Q2：这个 clip 需不需要 BGM 持续铺底？
├── 是 → prompt 不写 BGM 词，单独叠音轨
└── 否（绘本默认） ↓

Q3：这个 clip 需不需要拟声/环境音卡点？
├── 是 → --generate-audio true，prompt 嵌入音效副词（看三铁律）
└── 否 → --generate-audio false（绘本场景极少）
```

**绘本默认配置**：`--generate-audio true` + prompt 里**只写音效动作描述**（不写朗读、不写 BGM）。

> ⚠️ 旧版默认值 `--generate-audio false` 是错的。绘本 ≠ 全静音。绘本需要拟声音效（字母落位 tap-tap-tap、苹果出现 plop、消防车警笛呜——），但不需要 BGM 持续铺底，也不需要人声念旁白。三件事**互不替代**。
> 后续若找到 prompt 写法让 Seedance 直接生成旁白，可去掉"后期 TTS"环节——目前待探索。

### Prompt 编写规范（5要素）

严格遵循官方 video-prompt 的5要素格式：

| # | 要素 | 内容 |
|---|------|------|
| 1 | **参考主体引用** | 首帧图片 `seedance.py create --image ./N.jpg` |
| 2 | **场景描述** | 当前 Clip 所在场景，保持与参考图一致 |
| 3 | **分镜动作描述** | 按选择好的写法（连续运镜/时间轴分镜）描述，**必须包含收势设计** |
| 4 | **音效说明** | 短促拟声，**嵌入视觉句中间**（用逗号串接），不要用 `[Sound effect: ...]` 独立块 |
| 5 | **风格一致性说明** | 整体风格与参考素材保持一致 |

### 收势写法核心词

「最终定格」「缓慢拉远」「保持N秒不动」

### ⚠️ 旁白写在 Prompt 里——待后续完善

> **重要纠正（2026-05-26）**：Seedance 模型具备旁白生成能力，当前问题是**还未找到正确的写法**，而非「旁白不能写进 Prompt」。
> 当前策略：旁白在剪辑阶段合成，Prompt 里不写旁白。
> 待完善方向：探索旁白写入的合适写法（如标注位置、语气、时机等）。

### 参数默认值

| 参数 | 默认值 | 绘本场景规则 |
|------|--------|------------|
| 时长 | Clip 表中计算的总时长（必须严格与表中一致，不能超出15秒） | ✅ 同上 |
| 宽高比 | `16:9` | ✅ 同上 |
| 分辨率 | `720P` | ✅ 同上 |
| 模型版本 | `seedance2.0_vip` | ✅ 同上 |
| **`--generate-audio`** | **`true`** ⚠️ 绘本场景带音效（拟声/环境音，非人声、非 BGM） | ✅ 同上 |
| **`--watermark`** | **`false`** ⚠️ 绘本场景必须显式关闭 | seedance.py 默认 `true` 会带 AI 水印，所有绘本 create 命令必须加 `--watermark false`（2026-06-03 Ok 好的绘本实测踩坑：4 个 clip 全带水印返工）|
| **`--ratio`** | **`16:9`** ⚠️ 绘本场景默认 16:9（短视频平台标准） | 用户原话（2026-06-05 Say 说绘本踩坑）："视频比例默认 16:9"。**不要查原图比例**（用户原话："你不用看原图，视频模型会自动处理"）。原图比例（Say 绘本 1920×1200 = 16:10）会被自动适配到 16:9，**不需要裁切预处理** |

> ⚠️ **`--generate-audio` 必须设为 `true`（2026-06-02 二大爷确认）**：
**绘本 ≠ 全静音。绘本需要拟声/环境音配画面（字母落位 tap、苹果出现 plop、消防车警笛等），这些**靠 Seedance 同步生成**。**
> prompt 里**不写朗读**（不写 "A red apple" 这种文字内容）→ 模型不会念旁白。
> prompt 里**不写 BGM**（不写 "playful children's BGM"）→ 不会铺底。
> 详见 `references/绘本音效-prompt写法.md` 的三铁律。
- **v7 范式 build script 必跑项（2026-06-03 Ok 好的绘本实测踩坑）**：
  1. **段 1 引导句不能漏**——`This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video`。**漏掉这段 = Seedance 把 2 图当 1 段独立运镜处理，时序窗失效 + 模型自由发挥铺 BGM**（Cactus 4 段 vs Ok 好的 4 段实测差异：Ok 好的缺引导句 → clip2-4 全带 BGM）。v7 自检脚本要把"段 1 = 引导句"作为 #0 项必检。
  2. **拼接 f-string 易漏字段**（如把 `motion` 字段忘加到 final frame 段），导致"看似通过自检但 prompt 不完整"。**自检脚本要对照模板段数（v7 = 8 段）逐段检查字段存在性**，不能只看关键词字符串。
  3. **v7 模板示例**（来自 references/分镜时序-prompt范式-v7.md）：8 段固定结构 = 引导 + shot1 + shot2 + final frame + Storyboard Audio + No 禁令 + 风格 + 句号。**build script 应把 8 段都做模板变量**，避免漏段。
  4. **写 prompt 前必读 `references/分镜时序-prompt范式-v7.md`**——不要凭印象写。该 reference 已含完整 8 段结构 + Python f-string 模板 + 11 项自检 + Cactus 真实示例。

  5. **绘本场景禁用 MiniMax 生成 BGM（2026-06-03 用户原话）**：用户明确表态"在绘本视频制作时不能使用"。绘本场景需要 BGM 时只能：①让用户自备 BGM.mp3 ②后期 ffmpeg 替换音频流铺 ③完全不加 BGM（绘本默认）。**Seedance 生成的"自带"拟声不算 BGM**（如 chime/whoosh/tap 等短促拟声合规）。

### ⚠️ BGM 调性策略（2026-06-03 用户实测偏好 · 段 6 禁令分两种风格）

> **之前的范式**（Cactus 实测，2026-06-02）：v7 段 6 写 `No background music, no human voice, no narration, no singing` → 绘本默认无 BGM（"静默氛围型"）。
>
> **反转**（Red/Ok 好的绘本实测，2026-06-03）：**Seedance 2.0 可以为每个 Clip 自动配相符调性的纯音乐 BGM**（昨天 Red 绘本效果就非常好）。用户原话："我说的 BGM 和场景相符，是指每一个 clip 场景，不是整个系列绘本。我不要求 Clip 1、Clip 2、Clip 3、Clip 4 保持统一的调性，只需要每一组、每一个 Clip 生成的 BGM 和画面的场景相符就可以了"。

**两种 BGM 风格**（根据绘本调性需求选择）：

| 风格 | 适用场景 | 段 6 写法 | 实测案例 |
|------|---------|----------|----------|
| **A. 静默氛围型（v7）** | 安静 / 治愈 / 睡前 / 单色系调性绘本 | `No background music, no human voice, no narration, no singing;` | Cactus（沙漠绿植 + 仙人掌坚强） |
| **B. 调性匹配型（v8）** | 多情绪场景 / 暖色 / 活泼 / 故事化绘本 | `No human voice, no narration, no singing, no dialogue, no vocal, no humming, no whistling;` **（删除 `No background music`，让 Seedance 自动配调性相符的纯音乐 BGM）** | Red 苹果、Ok 好的（舞台+门口+森林+卧室+彩虹） |

**两种范式**（v7 + v8 双范式并存）：
- **v7 静默氛围型**：参考 `references/分镜时序-prompt范式-v7.md` + `assets/example-prompts/cactus-clip1-v7.txt` + `cactus-clips-2-3-4-v7.txt`
- **v8 调性匹配型**：参考 `references/分镜时序-prompt范式-v8.md` + `assets/example-prompts/ok-clips-1-4-v8.txt`

**v7 → v8 关键升级**（段 5 音频描述）：
```diff
- Storyboard Audio Description: [0.0s] tap-tap-tap; [3.5s] whoosh; [7.0s] chime;
+ Storyboard Audio Description: playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood throughout this shot, [0.0s] tap-tap-tap; gentle warm acoustic guitar, tender send-off mood with soft piano throughout this shot, [3.5s] whoosh; [7.0s] chime;
```

**调性匹配型 BGM 控制三铁律**：
1. **必须禁人声**（`no human voice / no singing / no vocal / no humming / no whistling`）—— BGM 必须是纯音乐，**绝对不能有人声**（用户原话："BGM 一定是纯音乐，不要有人声，这是绝对禁止"）
2. **段 5 必须写 BGM 调性词**（每 shot 加 `[乐器] + [调性形容词] + [场景情绪] throughout this shot`）—— 让 Seedance 知道要生成持续 BGM 配画面调性
3. **不在 prompt 写"play BGM / music"** —— 模型看到"music"会自由发挥，**画面段已经写清楚情绪词足够驱动 BGM 调性**

**调性匹配型 v3 prompt 模板**（Ok 好的实测通过）：
```
Storyboard Audio Description: {bgm_mood_1} throughout this shot, [{t1}] {sfx_1}; {bgm_mood_2} throughout this shot, [{t2}] {sfx_2}; [{t3}] {sfx_3};
```
- `bgm_mood_1` = shot1 调性（乐器+情绪+节奏），如 `playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood`
- `bgm_mood_2` = shot2 调性，可完全不同（绘本不要求系列统一调性）
- `{sfx}` = 该 shot 内具体拟声/环境音卡点（tap/whoosh/chime 等）

**调性词参考库**（写进 BGM 调性词位置）：

| 场景 | BGM 调性词（实测通过） |
|------|---------------------|
| 舞台/聚会/鼓掌 | `playful cheerful ukulele pizzicato strings, light bouncy rhythm with warm celebratory mood` |
| 送别/挥手/出门 | `gentle warm acoustic guitar, tender send-off mood with soft piano` |
| 森林/出发/冒险 | `playful adventurous pizzicato and light flute melody, bright cheerful mood` |
| 室内/共读/理解 | `gentle warm piano with soft strings, calm understanding mood` |
| 餐桌/吃饭/流口水 | `happy hungry bouncy xylophone and pizzicato strings, joyful excited mood` |
| 户外/玩耍/奔跑 | `playful lively accordion and light percussion, energetic outdoor mood` |
| 卧室/晚安/亲吻 | `soft tender lullaby with music box and soft piano, gentle loving bedtime mood` |
| 彩虹/结束/圆满 | `uplifting hopeful warm orchestra with strings and gentle bells, all-is-well ending mood` |

**⚠️ 调性匹配型实测风险**（Ok 好的绘本踩坑，2026-06-03）：
- **必须**有段 1 引导句 + 视觉段调性词 + **音频段 BGM 调性词**（三者缺一不可）
- 缺段 1 引导句 → Seedance 把 2 图当独立单图渲染，模型"自由发挥"铺不同 BGM
- 视觉段无调性词 → 模型只能用"warm color"等通用词，BGM 调性粗糙
- **音频段无 BGM 调性词 → 完全无 BGM**（只有稀疏拟声）—— 这是最容易踩的坑，因为 v7 默认就是"不写 BGM"

**禁用 MiniMax 生成 BGM**（2026-06-03 用户原话禁止）："不要用 MiniMax 去生成 BGM，这是在绘本视频制作时不能使用的"。绘本场景需要 BGM 时只能 ①让 Seedance 自带生成 ②用户自备 BGM.mp3 后期 ffmpeg 替换音频流 ③完全不加 BGM（静默氛围型）。

**调性词参考库**（写进视觉段，引导 Seedance 配 BGM）：

| 调性词 | 场景 | 期望 BGM |
|-------|------|----------|
| `warm celebratory atmosphere` | 舞台/聚会/鼓掌 | 欢快活泼 |
| `tender send-off mood` | 送别/挥手/出门 | 温馨柔和 |
| `bright cheerful ... playful adventurous mood` | 森林/出发/冒险 | 轻快明亮 |
| `quiet calm ... warm understanding mood` | 室内/共读/理解 | 平静温暖 |
| `sunny excited ... joyful hungry mood` | 餐桌/吃饭/流口水 | 欢快跳跃 |
| `bright playful ... lively energetic mood` | 户外/玩耍/奔跑 | 活泼动感 |
| `cozy ... tender loving bedtime mood` | 卧室/晚安/亲吻 | 温柔安静 |
| `magical ... hopeful uplifting all-is-well mood` | 彩虹/结束/圆满 | 升华希望 |

**决策树**（绘本启动时先决定 BGM 风格）：

```
绘本调性？
├── 安静治愈 / 睡前 / 单色系 / 氛围为主
│   └── A. 静默氛围型（No BGM）→ 走 Cactus 范式
│
└── 多情绪场景 / 暖色 / 活泼 / 故事化 / 多 Clip 不同调性
    └── B. 调性匹配型（让 Seedance 配纯音乐）→ 走 Red/Ok 好的 范式
        - 段 1 引导句必须
        - 视觉段必须含调性词
        - 段 6 只禁人声
```

**11 项自检脚本对应**：
- A 风格：段 6 必含 `No background music`
- B 风格：段 6 必含 `No human voice`，**不**含 `No background music`

### ✅ v9 范式 · 整 Clip 一致 BGM（2026-06-03 Eat 吃绘本实测通过）

> **v8 已知问题（已沉淀）**：v8 实现"BGM 与画面精准匹配"（4 Clip 8 段不同 BGM 调性，持续 -27~-34dB），但**clip 内部 BGM 断层**——同一 Clip 内 8-10s 内 BGM 切太碎令人不适。
>
> **用户原话**："虽然同一个 clip 里视频画面是分段的，但实际上画面之间也是合理切分，他们之间也是有转场衔接的。同一个 clip 时间本来就不长，如果 BGM 切换太频繁，会信人不适。"

**v9 修正方向**（✅ 已验证通过）：

| v8（错） | **v9（对）** |
|---|---|
| 段 5 每 shot 一段 BGM 调性词 | **段 5 整 Clip 一段 BGM 主题贯穿** |
| `ukulele shot 1, guitar shot 2`（3.5s 硬切）| `ukulele BGM continues throughout the entire clip, with mood shift during the second half`（同主题渐变）|
| 4 段不同 BGM = 4 Clip × 2 shot = 8 段切换 | 4 段不同 BGM = 4 Clip（**整 Clip 一致**）|

**v9 关键修复**：

1. ✅ 整 Clip **只有一段 BGM 主题**（不按 shot 切）
2. ✅ 必含 `continues throughout the entire clip`（持续标记）
3. ✅ 必含 `with a mood shift toward X during the second half`（软调性变化）
4. ✅ 段 6 禁人声（删 `No background music`）

**AI 量化验证**（v8 vs v9 音量曲线对比）：

| 时间 | v8（按 shot 切） | **v9（整 Clip 一致）** |
|---|---|---|
| 0.0s | -inf | -inf |
| 0.5-3.0s | -52 ~ -34 dB（稀疏）| **-27 ~ -33 dB（持续）** |
| **3.5s（边界）** | **-15 ~ -25 dB（突然出现）** | **-24 dB（平缓延续）** |
| 4.0-7.0s | -16 ~ -23 dB | **-23 ~ -29 dB（持续）** |
| 整 Clip 评价 | shot 边界 BGM 硬切 | **一条平滑曲线贯穿 0.5s-7.5s** |

**v9 完整范式**：见 `references/分镜时序-prompt范式-v9.md`
**v9 真实示例**：见 `assets/example-prompts/eat-clips-1-4-v9.txt`
**v9 自动化脚本**：见 `scripts/build_v9_clips.py`

**v7+v8+v9 三范式并存**（按绘本调性选）：

| 范式 | 适用 | 段 5 BGM 写法 | 段 6 写法 | 决策信号 |
|---|---|---|---|---|
| **v7 静默氛围型** | 安静 / 治愈 / 单色系 | 只写拟声 | `No background music, ...` | "安静"/"沙漠" |
| **v8 调性匹配型** | 多情绪 / 暖色 / 复杂调性 | 每 shot 一段 BGM | `No human voice, ...`（删 BGM 禁令）| "复杂"/"多情绪" |
| **v9 整 Clip 一致型** | 同主题多动作 / 一致性优先 | 整 Clip 一段 + mood shift | 同 v8 | "连贯"/"不要切太碎" / **默认** |

**默认范式**（2026-06-03 起）：绘本启动默认走 **v9**（v8 作为复杂多情绪场景备选，v7 静默型保留）。

**v9 必避反模式**：

- ❌ 段 5 每 shot 一段 BGM 调性词（v8 写法）→ shot 边界 BGM 硬切
- ❌ 段 5 缺 `continues throughout the entire clip` → BGM 不持续铺底
- ❌ 段 5 缺 `mood shift` 软描述 → 整 Clip 同调性无聊
- ❌ 用 MiniMax 生成 BGM 后期铺（用户禁止）

**切换范式方法**：

- v7 → v9：跳过 v8 直接升级（段 5 加 BGM 主题 + 段 6 删 `No background music`）
- v8 → v9：段 5 合并每 shot BGM 调性词为整 Clip 一段 + 加 `continues throughout the entire clip` + 加 `mood shift` 软描述
- v7 → v8：见 v7 升级表（参考 §BGM 调性策略）
- v9 → v10：见下方 v10 章节

### ✅ v10 范式 · 跨 Clip 共享同一 BGM 主题（2026-06-03 Eat 吃绘本 clip2/3 实测通过）

> **v9 已知局限**：v9 解决"clip 内部 BGM 断层"，但**clip 互相不知道对方存在**——clip 1 用 ukulele pizzicato 主题，clip 2 可能 AI 自由发挥生成为 xylophone 主题，**clip 边界会出现调性跳变**。
>
> **用户原话（2026-06-03）**："在之前的基础上，尝试使用提示词来控制 clip2 和 clip3 的 BGM 衔接，让他们具有同样的调性，因为这是儿童领读视频，不需要很准确匹配场景，只要整体氛围达到一定感觉就可以。"

**v10 修正方向**（✅ 已验证通过）：

| v9（错） | **v10（对）** |
|---|---|
| 每个 clip prompt 自由定义 BGM 主题 | **clip 2+ 的 prompt 显式继承 clip 1 的 BGM 主题词** |
| clip 1: `ukulele pizzicato` → clip 2: AI 可能生成 `xylophone` | clip 2: `same warm ukulele pizzicato melody from the previous clip continues` |

**v10 关键修复**（3 件事）：

1. ✅ 引入 `v10_bgm` 字段（继承上一 clip 主题词）
2. ✅ clip 2+ prompt 必含 `same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip`
3. ✅ clip 1 不写 v10_bgm（是主题源），clip 2+ 写 v10_bgm（继承源）

**v10 prompt 模板**（clip 2+ 段 5 写法）：

```diff
+ Storyboard Audio Description: same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip, gently evolving with soft pizzicato strings and xylophone accents, with a gentle mood shift toward a curious warm tone during the second half as the small bear explores the banana and carrot;
```

**v10 关键限制（必读）**：

- **Seedance 不会真去查 clip 1 实际生成的 BGM**——只能靠 prompt 文字约束让它"假设"前一个 clip 用了某主题
- **同一绘本只能选一个 BGM 主题词**（ukulele / xylophone / acoustic guitar 等）—— clip 2+ 都用同一个
- **如果 v10 跑出来两个 clip BGM 还是不同**——说明 Seedance 没遵循 prompt 的"same ... from the previous clip"约束，需要：
  1. 加大种子重复（每次用同一个 `--seed` 不可行，seedance.py 不支持）
  2. 改 prompt 措辞：`continuing the same warm ukulele pizzicato theme from the start to the end of this clip` 更明确
  3. 退到 v9（接受跨 clip 主题变化）

**v10 量化指标**（v9 vs v10 跨 clip 边界对比）：

| 指标 | v9（各自自由） | **v10（共享主题词）** |
|---|---|---|
| clip 2 4.0s 边界 dB | -27.4 | -29.3 |
| clip 3 4.0s 边界 dB | -23.1 | -34.2 |
| 边界 dB 差 | 4.3 dB | 4.9 dB |
| 音量 dB 是否衡量调性 | ❌（dB 是响度，不是音高/音色）| ❌（同上）|
| **人耳调性听感** | clip 2/3 BGM 风格不同 | **同 ukulele pizzicato 主题** ✅ |

**核心结论**：音量 dB 不能量化调性一致性。**调性是否一致只能人耳听**——v10 跑完后必须连续听两个 clip 的 BGM 风格判断。

**v10 完整范式**：见 `references/分镜时序-prompt范式-v10.md`
**v10 真实示例**：见 `assets/example-prompts/eat-clips-2-3-v10.txt`
**v10 自动化脚本**：在 `build_clips.py`（绘本项目目录）加 `build_v10_prompt()` 函数 + CLI `--version v9|v10` 切换。**注意**：`build_v10_prompt` 必须用 `clip.get("v10_bgm") or clip["bgm_theme"]` 兼容 clip 1 缺字段（v10 Eat 吃实测踩坑：直接 `clip["v10_bgm"]` 会 KeyError）。详见 `references/分镜时序-prompt范式-v10.md` §3。

**v7+v8+v9+v10 四范式并存**（按绘本调性选）：

| 范式 | 适用 | 段 5 BGM 写法 | 段 6 写法 | 决策信号 |
|---|---|---|---|---|
| **v7 静默氛围型** | 安静 / 治愈 / 单色系 | 只写拟声 | `No background music, ...` | "安静"/"沙漠" |
| **v8 调性匹配型** | 多情绪 / 暖色 / 复杂调性 | 每 shot 一段 BGM | `No human voice, ...`（删 BGM 禁令）| "复杂"/"多情绪" |
| **v9 整 Clip 一致型** | 同主题多动作 / 一致性优先 | 整 Clip 一段 + mood shift | 同 v8 | "连贯"/"不要切太碎" / **默认** |
| **v10 跨 Clip 同主题型** | 领读型 / 多 clip 同氛围 | 整 Clip 一段 + `same ... from the previous clip continues`（clip 2+） | 同 v8 | "领读型"/"整体氛围一致" |

**v10 实测问题（2026-06-03 Eat 吃绘本 4 clip 跑完）**：

1. **BGM 调性**：✅ 4 clip 调性统一（v10 路线目标达成）
2. **BGM 收势**：❌ 当前每 clip 都写 "quiet warm chime settles" 收势词，**中间 clip 不应有收势**——只有最后 1 clip 用收势
3. **画面动感**：❌ 比 v7/v8/v9 缺动感——待分析是 prompt 写法问题还是 v10 范式副作用

**v10 必避反模式**：

- ❌ clip 2+ 段 5 写自由 BGM 主题词（v9 写法）→ AI 自由发挥破坏同调性
- ❌ 同一绘本用多个 BGM 主题词（ukulele + xylophone 混用）→ 跨 clip 不一致
- ❌ 用音量 dB 量化调性一致性（dB 是响度不是音色）→ 误判 v10 失败
- ❌ 用 MiniMax 生成 BGM 后期铺（用户禁止）
- ❌ **中间 clip 段 5 写 "quiet warm chime settles" 收势词** → 收势只能用在最后 1 clip

**v10 BGM 收势机制（实测沉淀，2026-06-03）**：

- **连跑多个 clip**（如 `clip2 + clip3` 一起跑测试）→ Seedance **自动不收势**（隐式行为）
- **单跑 1 个 clip**（如 `clip1-v9.mp4` 单测）→ Seedance **会按 prompt 收势**
- **多 clip 拼整本绘本**场景下：v10 路线"中间 clip 不应有收势"已在连跑测试中隐式验证
- **实操建议**：v10 范式不需主动改 prompt 收势词，连跑 = 自动不收势 ✅

### ⚠️ v11-α 探索 · 段 2/3 加微动作（2026-06-03 Eat 吃绘本 clip 2 单测）

> **v10 已知问题**：v10 调性统一达成、收势通过连跑验证，但**画面缺动感**（用户反馈"和 v7/v8/v9 相比画面缺少了动感"）
>
> **v11-α 假设**：根因是段 2/3 动作描述太"稳态"（`holds the X pose for the rest of this shot` 写法）→ AI 倾向"安全稳态输出"

**v11-α 最小改动**（✅ 已实测）：

```diff
- in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose for the rest of this shot
+ in this shot the small bear brings the apple close to its mouth, then the small bear holds the apple pose with a warm smile and subtle gentle breathing for the rest of this shot
```

**v11-α 实测结果**（2026-06-03 clip 2 单测）：

- ❌ **画面动感无明显改善**（用户反馈"几乎没有什么变化"）
- **可能根因**（用户推测）：绘本原始图片和剧情的限制——Eat 吃的图是静态 Eric Carle 拼贴风，**没有给 AI 更多动作发挥空间**
- **代码沉淀**：`scripts/build_v9_clips.py` 加 `build_v11_prompt()` + `inject_micro_motion()` 函数 + CLI `--version v11` 切换
- **自动化产物**：`output/clip2-v11.mp4`（2.8M, 9s, seed 76124）

**v11-α 关键教训**：

1. **画面动感不只靠 prompt 动作词**——**原始图片本身的动作空间** 是更基础的限制因素
2. **静态拼贴风绘本**（Eric Carle 类）→ AI 难以生成"动起来"画面，需要换绘本测试
3. **v11-α 改动太小可能看不出差异**——如果还要试 v11，建议叠加 v11-β（camera drift 运镜）
4. **v10 范式作为绘本默认范式仍成立**（v14 段 4 音频子策略）—— v11-α 失败不否定 v10
   **2026-06-05 更新**：绘本默认已升 v15（v14 骨架 + 6 必问 + 音效密集型），v10 仍可作 v15 段 4 的子策略。

**v11-α 必避反模式**：

- ❌ **静态拼贴风绘本**（Eric Carle 类）改 prompt 加微动作无效——根因不在 prompt
- ❌ **改动太小看不出差异**——v11-α 注入"with a warm smile"太轻量，对 AI 影响小

**v11 未来方向**（未做，留作后续）：

- **v11-β**：加 camera drift 运镜（`the camera slowly drifts closer`），可能对静态图有效
- **v11-γ**：换绘本测试——选**写实风**绘本（Dear Zoo / Brown Bear 类有真实动物动作空间）
- **v11-δ**：直接在原图上**多帧变化**——跑前用即梦生成 4 帧中间动作图，作为 v11-γ 的输入

**当前状态**：❌ **v11-α 已实测失败**（2026-06-03 用户反馈"几乎没有什么变化"）—— v10 仍是绘本默认范式，v11-α 不再是后续方向。**真正解法是 v11-δ（多帧输入工作流）**，不是 v11-α 后续优化。详见 `references/分镜时序-prompt范式-v11.md` §10 失败评估 + v11-δ 工作流。

**选择记录**：每次绘本启动把范式版本号写进 `clips-prompt.json` 的 `version` 字段（如 `"v9-20260603"`）。

### ⚠️ v9 出现的工作方法论教训（2026-06-03 用户反馈驱动）

> 用户原话："**听用户原话要听场景，不要脑补到相邻概念**"

**事件 1（v9 出现）**：v8 跑通后用户反馈"clip 内部 BGM 断层"——我**第一次理解错了**，把"clip 内部断层"脑补成"clip 之间衔接"（相邻概念），给出 BGM 跨 clip 衔接方案。用户纠正后才明白：用户原意是**同一个 Clip 内 8-10s 内 BGM 不要切太碎**（一个 Clip 一段 BGM 主题）。

**事件 2（v11-α 失败）**：v10 跑通后用户反馈"画面缺动感"——我**没听场景就脑补到"改 prompt"**（相邻概念），v11-α 改了 prompt 注入微动作，**失败**。用户最终反馈"原始图片和剧情导致的，没有更多的发挥空间"——根因在**输入端**（图片限制），不在 prompt。

**两个事件同源**：
- 都把"症状描述"（断层 / 缺动感）脑补到"相邻概念"（衔接 / 改 prompt）
- 都**没回到用户原始场景**（clip 内部 / 输入端）就出方案
- 都**浪费了 1 轮迭代**——v9 浪费是因为脑补到 clip 衔接，v11-α 浪费是因为脑补到改 prompt

**根因**：用户描述时只说"症状"，我**直接给方案**，**没问"是哪个范围"或"是哪个环节"**。

**修复**（**v12 起执行 · 写进类级工作流原则**）：

- 用户反馈模糊概念时**先问"是哪个范围"**（clip 之间 / clip 内部 / shot 之间 / prompt 端 / 输入端 / 后期拼接）
- 不要直接给出"相邻概念"的方案
- **让用户澄清**比"猜一个并错下去"成本低
- **听用户原话要听场景**——用户描述的是"症状"（断层 / 缺动感），但要回到"发生场景"（clip 内部 / 输入端）再分析
- **"症状 → 根因 → 修复方向"三段式分析**——不要跳过"根因"直接给"修复方向"（v11-α 错的根因：跳过"根因在输入端"直接给"改 prompt"方案）

### 单测门 SOP（2026-06-02 实测偏好）

> ⚠️ **开批量前的强制 gate**。用户明确偏好：避免 4 个 clip 全跑完才发现 prompt 写错。

```
Phase 8 启动
  ↓
【单测】选 1 个 Clip（推荐 Clip 1，开场最具代表性）
  ↓ 提交并 vision 自评
  ↓ 发给用户看
  ↓ 用户确认「效果 OK，可以继续」
  ↓
【批量】剩余 N-1 个 Clip 并行提交
```

**单测重点看（6 项，铁律 26 已并入第 3 项）**——**AI/人分工明确**：

| # | 检查项 | AI 可查？ | 人必须查？ | 工具 |
|---|--------|----------|-----------|------|
| 1 | 风格锁定（跟原图拼贴+手绘一致） | ✅ vision_analyze 截图比对 | 兜底 | vision_analyze / 看图 |
| 2 | 镜头运镜（推进/拉远自然；**铁律 27：按画面类型选，禁止套"中景→中近景缓推"**） | ✅ vision_analyze 拆帧看 | 兜底 | vision_analyze |
| 3 | 收势（结尾稳定定格，无渐隐/淡出/动作截断）| ✅ vision_analyze 看尾帧 | 兜底 | vision_analyze |
| 3.5 | **铁律 26 文字末帧判断**：vision_analyze 报"末帧文字消失"时**先判断**——①参考图所有文字是否至少出现过一次 ②如果出现过了 → **合规**，不是 bug，**不要**加进自检问题列表。**硬约束**：参考图所有文字全程未出现 = bug | ✅ vision_analyze 看首帧+中段+末帧 | 兜底 | vision_analyze |
| 4 | 无穿帮/崩坏 | ✅ vision_analyze 检查每一帧 | 兜底 | vision_analyze |
| 5 | **音效**：①有没有人声念旁白？②有没有 BGM 持续铺底？③有没有拟声/环境音卡点？④音效是否短促不抢戏（0.5-1.5s/段）？ | ❌ vision_analyze **不支持 mp4 音频** | ✅ **必须人耳听** | 飞书 send_message 发视频给用户 |

**v7 范式专项检查**（仅 v7 范式适用）：
- ⑥ **音频控制有效性**（v7 范式必查）：用 `Storyboard Audio Description` 段 + `No X` 禁令段时，**音频是否真的"卡点"**（不是持续铺底）？**是否真的人声静默**（不是"有但是小声"）？**是否真的无 BGM**（不是"有但是被盖住"）？
- ⑦ **音频与画面同步**（v7 范式必查）：音效触发的秒数（如 `1.2s`）是否真的在画面切换的那一帧响起？视觉段的时间窗和音频段的时间窗是否**精确对齐**？
- ⑧ **首末两端精确卡点**（v7 范式必查）：首帧静默（0.0s 之前是否有人声/BGM 残留）？末帧单次 chime（结尾处是否真的"咣"一下结束，不是延续的余音）？

**为什么 5 项必须由人查音效**（2026-06-02 实测教训）：
- `vision_analyze` 工具**只支持图片**（.jpg/.png），不支持 mp4 视频文件
- "Only real image files are supported for vision analysis" 报错实测遇到
- 走 `mcp_zai_analyze_video` 也只能分析视觉，**音频是黑箱**
- **AI 永远查不出**"这段音效是 chimes 还是引擎 vroom"、"卡点在不在画面动作上"、"是否人声朗读"

**SOP**：
1. AI 跑 1-4 项（截图 + vision_analyze）
2. AI 把 mp4 视频**发飞书**给用户（`send_message` + `MEDIA:path` 语法）
3. **人听 + 5 项兜底确认**
4. 用户说"效果 OK" → AI 进入批量

**如果音效不卡点 / 太抢戏** → 调整 prompt 里的音效描述用词（不要加 "BGM" / "music" / "song"，不要用长句描述音效）。
**如果画面切快 / 收势失败** → 检查 prompt 是不是用了句号切分 + 收势词后追加内容（**回到 Phase 8 必读 · 三铁律**）。
**如果任务 failed with OutputVideoSensitiveContentDetected** → 检查 prompt 是否出现"警察/军人/枪/武器/暴力"等**敏感题材本体**（不是机械/警笛类拟声，那些安全）。

**用户没确认前不要批量**——这是踩坑教训，不是优化建议。

### 并行生成规则

> ⚠️ 同批 Clip **一次性并行提交**，不串行分批。但**跨批必须等用户确认**。

---

## Phase 9 · 视频剪辑/成片

> ⚠️ **默认不帮用户拼（2026-06-02 Red 绘本用户明确表态）**：单测门和批量完成后，**只发送所有 clip 文件 + 拼接示例命令**即可，**不主动跑 ffmpeg 拼接**。如用户明确要求拼片，按 §9.1 流程执行。详见关键教训 #16。

### 9.1 视频拼接

```bash
ls -v ./output/*.mp4 > clips.txt
cat clips.txt | while read f; do echo "file '$f'"; done > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy concat_raw.mp4
```

### 9.2 BGM 合并

```bash
ffmpeg -i concat_raw.mp4 -i "bgm.mp3" -shortest -c:v copy -c:a aac output_final.mp4
```

---

## ⚠️ 核心原则：实测结果为准 + 分批确认

**用户明确要求**：
1. 每个 clip 先单独测试，效果满意后再生成下一个（串行测试，不批量）
2. **分批生成时，本批全部完成并发送后，必须等用户确认才能提交下一批**
3. 不要等一个 clip 生成完再生成下一个——同一批内并行，跨批必须等确认

**迭代流程（分批串行）**：
```
生成 Clip N 本批全部完成
  → 发给用户看效果
  → 用户确认满意
  → 再提交 Clip N+1 的本批生成
  → 等待完成 → 发给用户 → 等确认
```

---

## 执行检查清单（完整版）

```
Pre-flight ✅ 官方 SOP 已下载并确认内容
Pre-flight ✅ seedance2.0-tool 已读取
Pre-flight ✅ 图片和旁白已就绪

Phase 5 Step 1 ✅ 叙事单元设计：每个Clip都有「起承转合」
Phase 5 Step 1 ✅ 叙事单元设计：每个Clip都有明确的「收势」设计
Phase 5 Step 1 ✅ 收势模式选择合理（完成式/进行式/悬念式）
Phase 5 Step 1 ✅ 画面描述完全基于静态图
Phase 5 Step 1 ✅ Prompt写法选择正确（连续运镜/时间轴分镜）

Phase 5 Step 2 ✅ 分镜计时：0.3s/字规则正确
Phase 5 Step 2 ✅ 分镜计时：时长严格在4-15s范围内

Phase 5 Step 3 ✅ 分镜组合：每个Clip在4-15s内

Phase 5 Step 4 ✅ scene-reflection：五个维度都检查了
Phase 5 Step 4 ✅ scene-reflection：叙事收势完整性已检查
Phase 5 Step 4 ✅ scene-reflection：Prompt写法已检查

Phase 6 ✅ 需求已确认，用户确认后才能进入下一阶段

Phase 8 ✅ video-prompt：全部5个要素都已包含
Phase 8 ✅ video-prompt：收势设计已包含
Phase 8 ✅ 全部并行生成，没有串行

Phase 9 ✅ ffmpeg 拼接 + BGM 合并完成
```

---

### ⚠️ Seedance 内容风控白名单（2026-06-02 用户最终纠正）

#### 信息源等级（**写在最前，防脑补**）

本节所有规则按**信息源可信度**分层，**优先采用高等级**：

| 等级 | 来源 | 可信度 | 例子 |
|------|------|-------|------|
| **L1 · 用户原话** | 用户在对话中明确说的 | 最高 | "只有警察、军队等敏感词汇容易风控" |
| **L2 · 用户明确纠正** | 用户纠错后的最终版 | 高 | "机械/车辆视觉动作这些是可以使用的" |
| **L3 · 实测任务结果** | 真实任务 succeeded/failed 记录 | 中 | ✅ `a distant 'wee-oo wee-oo' siren as the fire truck rolls in` → succeeded |
| **L4 · 兄弟 agent 沉淀** | 其它 agent 写入的 skill 章节 | 中 | 同上，跨会话参考 |
| **L5 · 自己脑补**（**必须标注 `推断`**） | 没在对话中验证的"理论解释" | **低** | ❌ "机械动作+拟声叠加触发风控"——错的 |

**强制原则**：
- L5（脑补）写进 skill 时**必须打 `推断` 标签**——下一个 task 验证后才能摘标签
- L3（实测）必须**有 task_id 引用**——空口说"我跑过"不算
- L1 跟 L3 冲突时**以 L1 为准**（用户原话 > 实测）
- 上一轮我犯的错：把用户"警笛这一类容易风控"（L1 模糊描述）脑补成"机械/警笛/鸣笛全部触发"（L5 错误扩张）→ skill 章节来回改 3 次。**根因**：没等 L3 实测验证就急着把 L5 写进 skill。

**根因（用户原话 · 2026-06-02 Red 绘本踩坑后澄清）**：
> "只有警察、军队等敏感词汇容易风控，机械/车辆视觉动作这些是可以使用的"

- ❌ **不是**机械/警笛类**拟声词**（vroom / horn / siren 这些**可以正常使用**）
- ❌ **不是**机械/车辆**视觉动作**（ladder extends / wheels roll 这些**可以正常使用**）
- ✅ **真正风控**：**警察/军队/枪/武器/暴力**等敏感题材
- 触发症状：API 返回 `The request failed because the output video may contain sensitive information. Request id: ...`

**绘本/通用素材音效词清单**（2026-06-02 实测 · 修正版）：

| 状态 | 词 |
|------|---|
| ✅ 安全 | `chime`, `rustling`, `plop`, `tap-tap-tap`, `bubble`, `sparkle`, `flutter`, `whoosh`, `bloom`, `settle` |
| ✅ 安全 | `vroom`, `horn`, `siren`, `alarm`, `engine`, `beep`, `beep-beep`（机械/车辆类全部可以写） |
| ❌ 触发风控 | **警察/军队/枪支/武器/暴力**等敏感题材本体 |

**绘本消防车/汽车/警车/军车场景的安全写法**：

```
✅ 安全：a distant 'wee-oo wee-oo' siren as the fire truck rolls in    → task succeeded
✅ 安全：a friendly 'beep-beep' as the small car rolls in               → task succeeded
✅ 安全：soft engine 'vroom' as the car starts                          → task succeeded
✅ 安全：soft gentle chime as the fire truck rolls in                   → task succeeded（绘本风格更温柔）
✅ 安全：soft gentle chime as the small car rolls in                    → task succeeded
```

**唯一真正禁忌**：明确出现"警察/军人/枪/武器/暴力"等敏感题材本体。**绘本里消防车、警车、军车的警笛/喇叭视觉动作 + 拟声**全部可以正常使用。

绘本风格调性建议（不是风控要求）：绘本对童趣有克制，`chime` 替代警笛`是一种**风格选择**，不是安全妥协。

#### ⛔ 信息源等级 L1-L5（本 skill 写章节前必查 · 2026-06-02 类级教训）

> 本节是**类级教训**——不只是风控适用，**所有往本 skill 写新规则的场景**都该用 L1-L5 等级判断。

| 等级 | 来源 | 可信度 | 处理 |
|------|------|-------|------|
| **L1 · 用户原话（明确）** | 用户在对话中明确说的 | 最高 | 直接采用 |
| **L2 · 用户明确纠正** | 用户纠错后的最终版 | 高 | 直接采用 |
| **L3 · 实测任务结果** | 真实任务 succeeded/failed 记录（有 task_id） | 中 | 写进 skill 必须附 task_id |
| **L4 · 兄弟 agent 沉淀** | 其它 agent 写入的 skill 章节 | 中 | 跨会话参考，**但不替代 L1/L2/L3** |
| **L5 · 自己脑补** | 没在对话中验证的"理论解释" | **低** | 写进 skill **必须打 `推断` 标签**——下个 task 验证后才能摘 |

**强制原则**：
- L5（脑补）写进 skill 时**必须打 `推断` 标签**——下一个 task 验证后才能摘标签
- L3（实测）必须**有 task_id 引用**——空口说"我跑过"不算
- L1 跟 L3 冲突时**以 L1 为准**（用户原话 > 实测）

**禁止的脑补模式**：
- ❌ "X 类的 Y 都触发"（用户只说了一个具体词，你扩张成一类）
- ❌ "X 的根因是 Y"（用户没说根因，你自圆其说）
- ❌ "X 跟 Y 一起会触发"（用户说 X 安全，你说 X+Y 危险——除非实测验证）

**检测方法**：写进 skill 章节前问自己"这条规则是从对话里**原样记录**的，还是我**推导**的？"——能区分 L1/L3 跟 L5 才能写。

**本 skill 实测红绘本踩坑事件**（2026-06-02）：
- 用户原话（L1 模糊描述）："警笛这一类的容易风控"
- 园丁脑补成（L5）："机械/警笛/鸣笛全部触发" → 写进 skill
- 兄弟 agent 顺着 L5 写更详细的"黑名单"
- 整个风控章节来回改 3 次
- memory 段也被污染
- 真实答案（L1 纠正）："只有警察、军队等敏感词汇容易风控，机械/车辆视觉动作这些是可以使用的"

---

### 关键教训（{项目名}实战 · 2026-05-26）

1. **绘本图片是「独立叙事单元」**：每张图是独立画面，图间没有物理连续动作，视频生成时每个 clip 从头渲染——这是正常行为，**不是缺陷**
2. **「突然中断」问题的根因**：原 Prompt 只描述「画面里有什么」，没有设计 Clip 结尾的「收势动作」，导致动作进行中就被截断
3. **解决方案在 Step 1（叙事单元设计）**：为每个 Clip 设计完整的「起承转合」，尤其要设计明确的「收势动作」，让 Clip 在「完成状态」结束
4. **scene-reflection 是强制 gate**：必须完成才能进入 Phase 6，跳过会导致收势设计缺失
5. **起承转合是叙事弧，不是分镜数量**：同一镜头内通过运镜可以完成整个叙事弧，不能教条化
6. **Prompt 写法分两种模式，根据叙事内容自动选择**：
   - **连续运镜写法**：单线动作/单一情绪场景，无时间切分，用「最终定格在XX，保持3秒不动」控制收势
   - **时间轴分镜写法**：多节奏/阶段转折场景（舞蹈高潮等），用 `[00-02s]` 分段标注不同镜头
   - 选择维度：情节结构（单线 vs 多段节奏）、镜头需求（推拉连续 vs 景别切换）
7. **收势阶段编写规范**：显式标注「收势阶段」+时长、写出收尾动作质感（镜头锁住/画面静止）、写出收尾方式（不渐隐不淡出，停留至最后一帧）
8. **收势必须明确三件事**：镜头锁住（Camera LOCK）+ 画面静止（No Motion）+ 不渐隐不淡出（No Fade）——Clip 8 v2「画面静止不动」的写法验证有效（2026-05-26实测）
9. **时长分配基于旁白叙事功能**：交代/动作/情感/高潮四种类型各有逻辑，不是硬编码比例
9. **旁白处理**：Seedance 模型具备旁白生成能力，当前问题是还未找到正确写法，标注为「待后续完善」，不是「禁止写旁白」
10. **下载文件路径不固定**：seedance.py download 到 `--download` 指定目录，但文件名需用 task_id 查状态确认实际下载路径
11. **`--download` 参数语义陷阱（2026-06-02 实测）**：seedance.py 的 `--download <path>` 是**完整文件路径**（不是目录）。如果传的是目录名，多个 clip 会**全写到同一个文件**上互相覆盖。正确做法：传**文件路径**（如 `--download ./output/clip1.mp4`），或者传目录路径后**立刻 mv 重命名**。并行生成多个 clip 时，**每个用独立文件名**。
12. **领读绘本总时长公式（2026-06-02 实测）**：合并后总时长 = `Clip1 时长 + Clip2 时长 + ...`，每个 Clip 在 8-10s 区间分配。分配原则：开头要给稳（8s），结尾情感核心要给余韵（10s），中间段均匀（8-9s）。公式：`总时长 ≈ 段落数 × 8-10s`，向上对齐。
13. **单测门 SOP（2026-06-02 实测）**：批量生成前**先做 1 个 Clip 让人看效果**，确认满意后再批量。这是用户的明确偏好——避免全部跑完才发现 prompt 写错。SOP：先 vision 自评 → 发给用户 → 等待确认 → 再并行批量。
14. **Hermes 环境下的 `~` 双重展开陷阱（2026-06-02 实测）**：在 hermes agent 里 `python3 ~/.hermes/skills/.../seedance.py` 调用时，`~` 会被错误展开为 `~/.hermes/profiles/huiben/home/.hermes/skills/...`（profile 目录 + home 子目录 + 原始路径），导致 `No such file or directory`。**修复**：一律用**绝对路径**，例如 `python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py`。同 trap 也适用于所有 `~/.hermes/...` 开头的命令。
15. **绘本音频三件事要分清 + 音效 prompt 写法的三铁律（2026-06-02 Red 绘本 v1→v2→v3 修复）**：
    - 绘本 ≠ 全静音。**三件事互不替代**：旁白（人声念文字，走后期 TTS）/ BGM（持续音乐铺底，默认不加）/ 音效（短促拟声+环境音，配合画面动作）。
    - 旧默认值 `--generate-audio false` 是错的，应为 `true`（让 Seedance 生成音效）。
    - 音效写法的三铁律（v2 踩坑 + v3 修复）：
      1. **不要用 `[Sound effect: ...]` 独立块**——句号 `.` 会把视觉切成多段，导致画面切快、节奏拖乱。
      2. **收势词（final frame / camera locks / holds to the last frame）后不要再追加任何内容**——尾部追加的音效块会覆盖收势指令，导致结尾收不住。
      3. **否定性指令（no speech / no narration / no BGM）放 prompt 末尾会干扰视觉模型**——视觉模型不擅长"反向作画"，这句会变成无效描述。
    - 正确写法：**句号改分号**（视觉单段连续）+ **音效描述嵌入视觉句中间**（逗号串接，副词地位）+ **收势词放最后一句**（不被覆盖）+ **删除否定句**。
    - 详见 `references/绘本音效-prompt写法.md`。

15a. **分镜时序 + 精准动作 v5/v6 范式（2026-06-02 Cactus 绘本实测）**：
    - **v3 范式（双图连续运镜）**：`@Image1 ... transitions seamlessly to @Image2 ...` 散文叙述，**模型自动决定切换时机**——氛围型可以，**TTS 精准卡点不行**。
    - **v3+锚点（带时间锚点 TTS 匹配）**：`as the camera X begins / transitions` 触发式动作，**软触发**——模型不完全遵守，**画面切换时机会偏移**。
    - **v5 范式（分镜时序 + 纯静态）**：用 `from 0.0s to 1.2s @Image1 ... from 1.2s to 8.0s @Image2 ...` **显式分镜时序表** + `Each shot holds steady within its time window` 让模型**精准切换+静止**。**用户验证 v5 精准切换 OK，但缺动画感**。
    - **v6 范式（分镜时序 + 精准动画）**：在 v5 基础上，shot 内部用 `in this shot [动作描述], then [下一动作/holds steady for the rest of this shot]` 让模型**精准运动**。
    - **用户金句**（2026-06-02 Cactus v5 检查反馈后）："能让画面在目标时段精准切换，并静止，那么也可以让画面在目标时段动起来，是吧"——**答：是的，同一机制反过来用**。
    - **8 段旁白 → 8 个动作映射原则**（Cactus 范式）：把动作关联的旁白就近配对，每个 Clip 内做 2 个动作（前 50% 做动作，后 50% 稳态停留）。
    - **决策树**：氛围型 → v3 / 需要 TTS 卡点但不要求动作 → v3+锚点 / 需要 TTS 精准卡点 + 精准动作 → v5/v6（本范式）。
    - 详见 `references/分镜时序-精准动作-prompt范式.md`。

16. **Phase 9 拼片：默认不帮用户拼（2026-06-02 Red 绘本用户明确表态）**：
    - 用户原话："我先自己下载拼接，不需要你拼接"
    - 默认行为：单测门和批量完成后，**只发送所有 clip 文件**（带目录路径），**不跑 ffmpeg 拼接**、**不主动提议拼片**。
    - 拼接时如果用户主动要求，按 §9.1 流程（ffmpeg concat + `-c copy`）执行即可。
    - 反例：把"拼接"自动塞进交付物=把工程化的"我会做"塞给不想要的人。
17. **不要把用户的简短描述脑补成完整理论（2026-06-02 Red 绘本风控错判教训）**：
    - 错版过程：用户原话"警笛这一类的容易风控" → 我脑补"警笛/机械/车辆/鸣笛/喇叭/vroom/horn/siren 全部都触发" → 自圆其说编了一套"机械动作+拟声叠加触发"的伪理论 → 把错版写进 skill 和 memory。
    - 用户最终纠正："只有警察、军队等敏感词汇容易风控，机械/车辆视觉动作这些是可以使用的"
    - 正确做法：
      1. **不脑补**——只记用户**原话**，不扩张。
      2. **不照搬**其他 agent 的"加强版"——它可能跟你的脑补同源。
      3. **不立刻**把"对策"加进 skill——**等下一个真实任务**踩到再沉淀。
    - 遇到"X 类词触发风控"这种模糊信息：**记原话**，加 `(待验证)` 标记，**等真实复现一次**再固化。

18. **水印 + 缺段 1 引导句 → 双 BUG 同时踩（2026-06-03 Ok 好的绘本实测）**：
    - **水印坑**：seedance.py `--watermark` 默认 `true` 必带 AI 水印。绘本是给家长/孩子看的，水印=产品缺陷。**所有绘本 create 命令必须显式 `--watermark false`**——已写进 Phase 8 参数默认值表（绘本场景规则列）。
    - **段 1 引导句漏 → BGM 乱铺**：Cactus 4 段（v7 引导句齐全）实测 0 BGM；Ok 好的 4 段（v7 引导句漏）实测 clip2-4 全铺了不同 BGM。**根因**：缺引导句时 Seedance 把 2 图当独立单图渲染，模型"自由发挥"为暖色绘本铺 BGM 调氛围。**修复**：build_clips.py 模板段 1 写死引导句；自检脚本把"段 1 含 'storyboard reference image sequence'"作为 #0 项必检。
    - **写作约束**：未来新绘本任务执行前，**必读** `references/分镜时序-prompt范式-v7.md` 拿到完整 8 段模板——不要凭印象写。该 reference 已含 Cactus 4 段实测通过的模板示例（cactus-clip1-v7.txt + cactus-clips-2-3-4-v7.txt）。

19. **v8 → v9 范式升级：clip 内部 BGM 断层修复（2026-06-03 Eat 吃绘本实测）**：
    - **v8 已知问题**：v8 按 shot 切 BGM（如 Clip 1 Shot 1 = 0-3.5s ukulele → 3.5s 切 Shot 2 = 吉他钢琴），shot 边界 BGM 突然切换太频繁令人不适。用户原话："虽然同一个 clip 里视频画面是分段的，但实际上画面之间也是合理切分，他们之间也是有转场衔接的。同一个 clip 时间本来就不长，如果 BGM 切换太频繁，会信人不适。"
    - **v9 修复**：
      1. 段 5 整 Clip 一段 BGM 主题（不按 shot 切）
      2. 必含 `continues throughout the entire clip`（持续标记）
      3. 必含 `with a mood shift toward X during the second half`（软调性变化）
      4. 段 6 禁人声（删 `No background music`）
    - **AI 量化验证**：v9 在 3.5s 边界音量 -24 dB 平缓延续（v8 突然出现 -15~-25 dB）——一条平滑曲线贯穿 0.5s-7.5s。
    - **v7+v8+v9 三范式并存**（按绘本调性选）：v7 静默氛围型 / v8 调性匹配型（已知断层）/ **v9 整 Clip 一致型（默认 2026-06-03 起）**。
    - 详见 `references/分镜时序-prompt范式-v9.md` + `assets/example-prompts/eat-clips-1-4-v9.txt` + `scripts/build_v9_clips.py`。
    - **关键工作方法论教训**：用户反馈模糊概念时**先问"是哪个范围"**（clip 之间 / clip 内部 / shot 之间），不要直接给出"相邻概念"的方案。**听用户原话要听场景**——用户描述的是"症状"（断层），但要回到"发生场景"（clip 内部/之间）再分析。**让用户澄清**比"猜一个并错下去"成本低。

20. **v9 → v10 范式升级：跨 Clip 共享 BGM 主题修复（2026-06-03 Eat 吃绘本实测）**：
    - **v9 已知局限**：v9 解决"clip 内部 BGM 断层"，但**clip 互相不知道对方存在**——clip 1 用 ukulele 主题，clip 2 可能 AI 自由发挥生成为 xylophone 主题，**clip 边界调性跳变**。
    - **用户原话**（2026-06-03）："在之前的基础上，尝试使用提示词来控制 clip2 和 clip3 的 BGM 衔接，让他们具有同样的调性，因为这是儿童领读视频，不需要很准确匹配场景，只要整体氛围达到一定感觉就可以。"
    - **v10 修复**（4 件事）：
      1. 引入 `v10_bgm` 字段（继承上一 clip 主题词）
      2. clip 2+ 段 5 必含 `same warm ukulele pizzicato melody from the previous clip continues throughout this entire clip`
      3. clip 1 不写 v10_bgm（是主题源），clip 2+ 写 v10_bgm（继承源）
      4. `build_v10_prompt(clip)` 用 `clip.get("v10_bgm") or clip["bgm_theme"]` 兼容 clip 1 缺字段
    - **v10 关键限制**：**Seedance 不会真去查 clip 1 实际生成的 BGM**——只能靠 prompt 文字约束让它"假设"前一个 clip 用了某主题。**音量 dB 不能量化调性一致性**（dB 是响度不是音色），调性是否一致**只能人耳听**。
    - **v10 适用绘本类型**：领读型绘本（I eat X 系列、Pete the cat、Dear Zoo、Brown Bear 等重复句式）—— 整体氛围一致 > 调性匹配。
    - **v10 决策树信号**："领读型"/"整体氛围一致"/"重复句式绘本"—— 这些信号触发 v10（v9 是默认）。
    - **v10 实测踩坑（2 个）**（写进 references 文档 §6）：
      1. `--ref-images` 多图必须空格分隔（seedance.py `nargs="+"`）—— 逗号分隔会报 `File not found: a.jpg,b.jpg` 错误
      2. `--download` 是文件路径不是目录——多 clip 并行时**每个必须用独立文件名**，否则后一个覆盖前一个
    - 详见 `references/分镜时序-prompt范式-v10.md`（完整 12 段）+ `assets/example-prompts/eat-clips-2-3-v10.txt`（Eat 吃 clip 2/3 完整 prompt）+ `build_clips.py`（项目目录脚本，含 `build_v10_prompt()` + CLI `--version v10` 切换）。

21. **v10 测试方法核心：**v10 跨 clip 调性是否一致**只能人耳听**（dB 不能量化），跑完后必须连续听两个 clip 验证 BGM 风格。**v10 跑通 ≠ 跨 clip 一定同调性**——prompt 写了 "same ... from the previous clip" AI 不一定真遵循，**必须人耳验证**。

22. **v10 跑通 ≠ 完美 · 3 个实测问题（2026-06-03 Eat 吃 4 clip 跑完）**：v10 跨 clip 同主题目标**达成**（✅），但暴露出 3 个新问题——这些是 **v11 设计的起点**：
    1. **BGM 收势位置错误**：v9 模板给每个 clip 都生成 `quiet warm chime settles` 收势词，**v10 范式下只有最后 1 clip 才用收势**，中间 clip 用 `BGM continues softly into the next moment` 软延续。**v11-α 修复**：加 `is_final_clip: bool` 字段 + `build_v11_prompt()` 区分中间/末尾。
    2. **画面缺动感**：v10 4 clip 比 v7/v8/v9 缺动感，可能根因：①稳态描述 `holds the X pose for the rest of this shot` 占比过高 ②v10 范式副作用（同 BGM + 稳态画面 + AI 偏安全输出）③`continues throughout the entire clip` 关键词副作用。**v11-β 修复**：段 2/3 加微动作（`eyes widen with excitement`）+ 改 `hold pose` 为 `slight natural movement`。
    3. **v10 范式边界**：领读型绘本（I eat X / Pete the cat / Dear Zoo / Brown Bear 等重复句式）适合 v10；单一 clip 内多情绪用 v8；静默治愈用 v7；8-10s 静态画面要靠 prompt 写出动感（v11 修问题 3 后可解）。
    - 详细 v11 方向（4 种修复方向 A/B/C/D）见 `references/分镜时序-prompt范式-v10.md` §13。
    - **v11 路线图**：v11-α（修 BGM 收势，10 分钟出结果）→ v11-β（加微动作，对比 v10 看是否改善）→ v11-γ（可选 camera drift 运镜）。**两个问题独立可分开调**，不必同时上。

23. **v10 → v11-α 真实路线（2026-06-03 失败失败）**：v11-α（加微动作）**实测失败**（用户反馈"几乎没有什么变化"）——见 `references/分镜时序-prompt范式-v11.md` §10。**真正解法是 v11-δ（多帧输入工作流）**：跑 Seedance 前用即梦生成 4 帧中间动作图，作为 `--ref-images` 多图输入，让 AI 在多帧间做插值。**核心教训**：
    - "**画面动感**"症状描述**指向输入端**（图片限制），不是 prompt 端
    - 改 prompt 是相邻概念——v11-α 失败后必须把方向切到输入增强
    - **未来不要重复跑 v11-α**——它已死，**v11-δ 才是 P0 真正方向**
    - 完整 v11 路线图见 `references/分镜时序-prompt范式-v11.md` §10 + 主 SKILL.md §工作流原则探索式迭代
    - v11-δ 工作流（4 步）：
      1. 拿原绘本 N 张图（如 eat 1-8.jpg）
      2. 对每张图用即梦生成"动作中间帧"（如 eat 1-mid1.jpg, 1-mid2.jpg, 1-mid3.jpg）
      3. 把"原图 + 中间帧"作为 `--ref-images` 传给 Seedance（**多图必须空格分隔**，逗号会报错）
      4. prompt 引导 AI"在这些帧之间做平滑插值"

24. **⚠️ 旁白语言版本 + 彩色文字 + 运镜定制铁律（2026-06-05 Say 说绘本踩坑 · 关键教训 #25 #26 #27 · 启动前必读）**：

    > **本节是绘本启动 Phase 5 必读三铁律**——Say 说绘本 v1/v2 两轮实测沉淀。

    #### 铁律 25 · 旁白语言版本必须用"用户指定版本"不是"图上有啥"

    **现象**（Say 说绘本 v1/v2）：用户说"我只要中文版旁白"→ 我理解成"画面只留中文，删英文"→ 画错方向。

    **真实规则**（PIG/Say 双栏表对照得出）：
    1. 素材表是**双栏**（英文版 + 中文版）→ 用户给的是中英对照
    2. **中文版格式** = `<中文主旁白> + <小写英文跟读>`（逗号/空格分隔，英文小写嵌入）
    3. **例外：封面 P1** 用大写英文主词（`PIG!` / `Say!`）—— 概念强调
    4. **画面文字必须严格 = 中文版旁白稿内容**：中文保留 + 小写英文跟读保留。**英文版完整句（每行第一栏的独立英文句）不进画面**
    5. **诊断口诀**："用户说 X 版" = "X 版**完整那一行**" = 不是"删 Y 留 X"

    **PIG/Say 句式对照示例**：
    | 句 | 英文版（不进画面）| 中文版（**进画面**） |
    |---|---|---|
    | 封面 | `PIG!` | `小猪 PIG！` |
    | 故事 | `A pink pig.` | `粉色的小猪，a pink pig` |
    | 跟读 | `pig, dig, big, wig, fig` | `小猪 pig 的 IG 家族，pig、dig、big、wig、fig 大集合！` |

    **修复**：
    - Phase 5 Step 1 第一件事：**明确旁白语言版本**（用户没说默认中文版=中英嵌入）
    - 写 prompt 时画面文字描述 = **中文版旁白稿内容完整复制**（不是只复制中文）
    - 封面 P1 例外：用大写英文主词（`小猪 PIG！` / `说 Say!`）

    #### 铁律 26 · 彩色文字"自然融入"不是"必须一直显示"

    **用户原话**（2026-06-05）："彩色文字不需要一直持续出现在画面中，可以根据情节消失"

    **v2 措辞保留**（`references/绘本文字保留铁律-v1v2.md`）：
    ```
    参考图原有的所有文字...作为画面元素自然融入场景，模型自行设计合理的呈现节奏与动效
    ```

    **单测门验收新规**：
    - ❌ **不再**把"末帧彩色字母消失"报为 bug —— 这是 v2 措辞鼓励的正常行为
    - ✅ **硬约束**：参考图所有文字**必须至少出现一次**（不能完全丢失）—— 这才是 bug
    - ✅ 文字淡入淡出 / 随镜头呼吸 / 配合动作出现 / 末帧渐隐 —— 全部合规

    **写 prompt 时的措辞**（沿用 v2 + 加一句自由发挥）：
    ```
    文字作为画面元素自然融入场景，模型自行设计合理的呈现节奏与动效
    （例如淡入、随镜头呼吸、配合动作出现或消失等）
    ```

    #### 铁律 27 · 运镜服务于故事，不是固定公式

    **用户原话**（2026-06-05）："刚才生成视频时的运镜根本不符合领读绘本，运镜要服务于故事，不是固定公式"

    **我之前的问题**（Say 说 v1）：套"起承转合"叙事弧 + 固定"中景→中近景缓推 3 秒"模板到所有 Clip。

    **修复**：运镜按画面内容/情绪**逐图定制**：

    | 画面类型 | 推荐运镜 | 理由 |
    |---|---|---|
    | **封面（建立感）** | 缓推 | 主角登场 |
    | **角色动作为主**（挥手/举牌/比心/捂嘴呼喊）| **静态或极缓** | 突出动作 |
    | **多人场景**（教室/门口/聚会）| 拉远 or 水平 pan | 呈现全员 |
    | **情感场景**（睡觉/爱心/月亮/挥手告别）| **几乎不动** | 安静氛围 |
    | **礼物/递出/分享** | 缓推 + 微向下倾 | 聚焦 |
    | **彩带/挥手/风动** | 静态（让物体自己动）| 不抢动效 |

    **禁止**：
    - ❌ 套"起承转合"模板到所有 Clip（v1 错版）
    - ❌ 固定"中景→中近景缓推 3 秒"公式（v1 错版）
    - ❌ 一律要"镜头推进"的默认动作
    - ❌ 镜头运动跟画面动作抢戏（角色挥手时镜头还在动 = 视觉混乱）

    **写 prompt 时的决策**：
    ```
    1. 看图判断画面类型（封面/动作/多人/情感/礼物/动态）
    2. 按上表选运镜
    3. 写"镜头 X 持续 N 秒"或"镜头几乎不动"
    4. 不要默认写"缓推"
    ```

    #### 铁律 27 扩展 · 撤回"运镜三禁"，改回"按画面类型定制"（2026-06-05 园丁诊断用户纠正）

    > **撤回原因**（2026-06-05 用户反馈）：
    > - v14 写法（"3 秒后""砰弹出"等秒级控制）= **合法**，是 v10 范式的核心
    > - "运镜三禁"把时间感描述（"3 秒后"）+ 秒级控制（"1.5 秒后"）跟"套公式"混为一谈
    > - **真正反模式** = "中景→中近景缓推 3 秒"模板套所有 Clip（v3 prompt 那种）
    > - **秒级控制 + 时间感描述 = 优势**（v10 范式精准控制 + v3 改活泼效果都需要）

    **真正必避的**（仅 1 条）：

    - ❌ **套运镜公式**：`"中景→中近景缓推"` 模板套所有 Clip（不问画面类型直接套）

    **允许的**（之前被禁但实际是优势）：

    - ✅ **秒级控制**：`"3 秒后砰弹出"` `"1.5 秒后推脸"` —— 精准控制
    - ✅ **时间感描述**：`"镜头快速推进"` `"急促的纸张摩擦"` —— 节奏感
    - ✅ **5+ 镜头结构**：分镜时序窗用 `"from 0.0s to 4.0s @Image1"` —— v5/v6 范式

    **按画面类型定制**（铁律 27 主表，**保留**）：

    | 画面类型 | 推荐运镜 | 理由 |
    |---|---|---|
    | **封面（建立感）** | 缓推 | 主角登场 |
    | **角色动作为主**（挥手/举牌/比心/捂嘴呼喊）| **静态或极缓** | 突出动作 |
    | **多人场景**（教室/门口/聚会）| 拉远 or 水平 pan | 呈现全员 |
    | **情感场景**（睡觉/爱心/月亮/挥手告别）| **几乎不动** | 安静氛围 |
    | **礼物/递出/分享** | 缓推 + 微向下倾 | 聚焦 |
    | **彩带/挥手/风动** | 静态（让物体自己动）| 不抢动效 |

    **写 prompt 时的决策**（**新版本，2026-06-05 修订**）：
    ```
    1. **先问运镜调性**（6 必问 #4）：活泼有动感 / 治愈舒缓 / 动态开合 / 静态展示
    2. 看图判断画面类型（封面/动作/多人/情感/礼物/动态）
    3. 按上表选运镜
    4. 写"快速 / 极缓 / 几乎不动 + 时间词"（"3 秒后砰弹出"等）
    5. **不要**套"中景→中近景缓推"模板到所有 Clip
    ```

    **写 prompt 风格参考**（活泼有动感 / Say 绘本实测通过）：
    ```
    镜头一：小熊从画面下方外快速跳入到中央，双脚落地"咚"一声；
    镜头二：双手快速举到脸颊两侧，嘴巴同步张大呈 O 形，"呼呼"纸张被风卷动；
    镜头三：镜头快速从中景推进到脸部特写，文字"说Say!"同步从两侧"砰"弹出，"叮"清脆一声；
    镜头四：镜头缓推持续，文字在画面中自然呼吸，纸张摩擦"沙沙"；
    镜头五（收势）：画面定格...
    ```

    #### 三铁律自检（Phase 5 Step 1 完成前必跑）

    - [ ] **铁律 25**：旁白语言版本确认了吗？画面文字 = 中文版旁白稿内容（不是英文版，不是只中文）
    - [ ] **铁律 26**：文字"自然融入"措辞写了吗？末帧消失是否合规（参考图所有文字至少出现一次）
    - [ ] **铁律 27**：运镜按画面类型定制（不套"0-Xs"时间公式）

25. **⚠️ 必避 4 条 + 时长理解（2026-06-05 Say 绘本实测补强 · 关键教训 #28-#31 · 启动前必读）**：

    #### 教训 #28 · 4s 硬下限 ≠ 每条都 4s

    **用户原话**（2026-06-05）："这个视频 4s 时长完全足够了"

    **我之前的错版理解**：所有 Clip 都改成 4s → 强行塞 2 段旁白到 4s

    **正确理解**：
    - 4s 是 seedance **单 Clip 时长硬下限**（4s ≤ duration ≤ 15s，违反报错）
    - 用户说 4s = 觉得"当前 8s 太长"，**不**是统一改成 4s
    - 单段旁白 × 0.3s/字 ≥ 旁白时长，但**单 Clip 总时长必须 ≥ 4s**
    - 领读型单段旁白 1-3 字 × 0.3s = 0.3-0.9s < 4s → 装不下就要么扩句要么用画面填补

    **修复**：
    - Phase 5 Step 2 算时长：`单段旁白时长 = 字数 × 0.3s`；`单 Clip 时长 = max(4s, 旁白时长之和)`
    - 用户评价"太长"时**只缩该 Clip**，不批量改

    #### 教训 #29 · 合并切分 vs 拆分切分表脑里混用

    **事件**（2026-06-05 Say 绘本）：第二轮已经决定 1图=1Clip 切分（10 Clip），但写 Clip 3 prompt 时**沿用第一轮 6 Clip 切分表的"图 4=Clip 3"映射**，把"图 4 说谢谢"当 Clip 3 跑。

    **根因**：切分方案改过 2 次（6 Clip 合并 → 10 Clip 拆分），但我没在每轮 prompt 开头**贴当次切分表**逐 Clip 引用，沿用脑里旧映射。

    **修复**：
    - 切分方案一旦定，**当次会话所有 prompt 开头贴切分表**（"本轮切分：Clip 1=图 1 / Clip 2=图 2 / ... / Clip N=图 N"）
    - 切分方案变更时**显式声明旧→新映射**（"之前 Clip 3=图 4 → 现在 Clip 3=图 3"）
    - 写 prompt 前**先核对图号与 Clip 编号一一对应**

    #### 教训 #30 · 并行提交不存 task ID = 100% 灾难

    **事件**（2026-06-05）：批量提交 6 个 task 用 `for ... do ... done` 串行，每条用 `tail -1` 抓 Task ID 但**没存到变量** → 6 个 task ID 全丢 → 120 元任务可能重跑。

    **幸运**：ark REST 端点 `GET /api/v3/contents/generations/tasks?page_size=N` 有 list 接口，按时间过滤找回了 6 个 task，**0 元下载**。

    **修复**（必做）：
    ```bash
    # 1. 逐个 task 存 ID + 立刻 wait
    for i in 1 2 3; do
      TASK_ID=$(python3 seedance.py create ... 2>&1 | grep "Task ID" | awk '{print $3}')
      echo "task $i: $TASK_ID"
      python3 seedance.py wait $TASK_ID --download ./out_$i.mp4
    done

    # 2. 或并发存 ID（但 wait 必须串行）
    TASK1=$(... create ...); echo $TASK1 > /tmp/t1
    TASK2=$(... create ...); echo $TASK2 > /tmp/t2
    # ... 等等
    for f in /tmp/t*; do
      python3 seedance.py wait $(cat $f) --download ./out_$f.mp4
    done
    ```

    **禁止**：
    - ❌ `for ... do ... done` 串行命令用 `tail -1` 抓 ID 不存
    - ❌ 后台 `&` 启动后不存 PID/task ID
    - ❌ 假设 6 个 task 一定 succeeded 不查（实际可能 1 个 failed → 5 个白跑）

    #### 教训 #31 · ark list 端点 = task ID 丢失时的救援通道

    **seedance.py 缺失 list 实现**（README 写 `list [--status succeeded]` 但 `cmd_list` 函数没实现 → `python3 seedance.py list` 报 `invalid choice`）。

    **救命通道**：直接调 ark REST 端点：
    ```bash
    # 1. 拿 key
    source /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env

    # 2. 列最近任务
    curl -sS -H "Authorization: Bearer $ARK_API_KEY" \
      "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_size=20" \
      > /tmp/list.json

    # 3. python 解析 + 批量下载（不重提交 = 0 元）
    python3 << 'EOF'
    import json, urllib.request
    d = json.load(open('/tmp/list.json'))
    target = {'task_id_1': 'clip_name_1', ...}  # 按 created_at 映射
    for item in d['items']:
        if item['id'] in target:
            urllib.request.urlretrieve(item['content']['video_url'], target[item['id']])
    EOF
    ```

    **限制**：
    - page_size 默认 10-20，看不到所有历史任务
    - 必须按 `created_at` 时间窗口过滤（最近几分钟内）
    - video_url 24h 过期 → 必须**立刻下载**
    - **不替代教训 #30**（仍然是首选预防）

    #### 4 个必避 + 3 个必查 · 自检（Phase 5 完成前必跑）

    - [ ] 教训 #28：`单 Clip 时长 = max(4s, 旁白字数×0.3s)` 算了吗？用户说"4s"是缩该 Clip 还是全改？
    - [ ] 教训 #29：本轮切分表（Clip N = 图 N）写在 prompt 开头了吗？图号与 Clip 编号一一对应了吗？
    - [ ] 教训 #30：批量 task ID 用 `TASK_ID=$(...)` 存了吗？wait 阻塞下载了吗？
    - [ ] 教训 #31：task ID 丢失时用 ark list 端点救回，不要盲重提（重提 = 重复扣费）

    **配合 #25 #26 #27 三铁律使用**——5 条铁律 + 4 个必避 = 绘本启动必读 7 件套。

25. **⚠️ 时长铁律 28-30（2026-06-05 Say 说绘本 2.0 阶段踩坑 · 关键教训 #28 #29 #30）**：

    #### 铁律 28 · 4s 是硬下限不是推荐值

    **用户原话**（2026-06-05 15:51）："效果是可以的，只是时间太长了，这个视频 4s 时长完全足够了。"

    **我犯的错**：我**直接把"4s"套用到所有 Clip**（包括 Clip 2-10），没意识到——
    - 单 Clip **硬约束** = `4s ≤ duration ≤ 15s`（SKILL.md line 471 + 514）
    - **4s 是硬下限**（不能低于 4s），**不是推荐值**
    - 用户说"4s 完全足够"= **只针对那个 Clip**觉得不需要更长，**不是说所有 Clip 都 4s**

    **修复**：
    - 收到"4s / 6s / 8s"等时长反馈时，**只对该 Clip 生效**，不套用到所有 Clip
    - 旁白字数计算：`<字数> × 0.3 秒/字` = 该 Clip 最小理论时长
    - 单 Clip 时长 ≥ max(旁白字数 × 0.3, **4s 硬下限**)
    - 短视频（多 Clip 投放抖音/小红书）vs 长视频（完整绘本 1 本）的时长分配**完全不同**——见铁律 29

    #### 铁律 29 · 不猜 · 不擅自延伸用户指令

    **用户原话**（2026-06-05 15:54）："我没叫你砍 clip2" + "你TM别乱猜，你好好看skill中clip的计时规则"

    **我犯的错**：
    - 用户说"Clip 1 砍到 4s" → 我**擅自**把 Clip 2-10 也按 4s 处理
    - 用户说"4s 装 2 段旁白"提问 → 我**没看 skill**就直接猜"每段 2s，密度高但省一个 Clip"
    - 我直接说"我猜" → 用户爆粗

    **修复**（**类级沟通铁律**，不只是绘本）：
    - **不擅自延伸**——用户说 A，只做 A，不做 A+B+C
    - **不凭直觉猜**——拿不准时**先看 skill**（看 Step 2 分镜计时规则 / 0.3s/字 / 4s 硬下限 / 合并判断条件）
    - **不要直接说"我猜"**——猜也要说"按 skill 规则推导是 X"或"我不确定，需要你确认"
    - **报告 ≠ 询问**——我说"我打算 X"不是问你"OK 吗？"，但 X 应该是**有 skill 依据的 X**，不是脑补的 X
    - **让用户澄清**比"猜一个并错下去"成本低 10 倍

#### 铁律 30 · status=succeeded 后必须验证本地文件存在

**实测**（2026-06-05 15:55）：seedance.py wait 命令被用户打断后，task 状态是 `succeeded`，但 `--download` 文件**没下载到本地**（`No such file or directory`）。

**修复**：
- wait 命令被中断 / 异常退出后，**不要只看 status**，要 `ls -lh <download_path>` 确认文件存在
- 文件不存在 → 重新跑 `wait` 或手动用 `video_url` 下载
- **发飞书前必跑**：
  ```bash
  ls -lh <expected_mp4_path> || echo "❌ 文件不存在，需重跑"
  ```

#### 铁律 31 · 任务叫停 = 等结果自然完成，不需 kill

**用户原话**（2026-06-05 15:13）："错！停" + "V2 任务已经创建，你无法停止了。"

**实测**：
- v2 任务 `cgt-20260605151205-8f2bm` 用户叫停时已**跑了 1 分钟**
- 用户自己说"已经创建，你无法停止了"——Seedance API **不支持中途 kill**
- 任务继续跑完（大约再跑 1-2 分钟），结果**不采用**

**修复**：
- 用户喊"停"时 → **不要**尝试 `kill` / `cancel`（API 不支持）
- **正确做法**：告诉用户"任务继续跑完，结果废弃即可"，让 ta 知道资源消耗
- 跑完后废弃 mp4 文件（**不下载** / **下载后删** / **下批覆盖**）
- 避免误判：叫停 ≠ 立即停止，是"我**不再依赖这个结果**"

    #### 三铁律自检（Phase 5 + Phase 8 完成前必跑）

    - [ ] **铁律 28**：单 Clip 时长 = max(旁白字数×0.3s, 4s 硬下限)？收到"4s/6s/8s"反馈**只对该 Clip 生效**？
    - [ ] **铁律 29**：用户的指令**只做了 A 没做 A+B+C**？不凭直觉猜、不直接说"我猜"？
    - [ ] **铁律 30**：wait 命令完成后**验证本地文件存在**？发飞书前 `ls -lh` 确认？

---

## 参考文档

| 文档 | 说明 |
|------|------|
| `lark-cli/SKILL.md` | 飞书 CLI 使用规范（访问云盘/文档的官方路径） |
| `seedance2.0-tool/SKILL.md` | 即梦 CLI 命令格式（必读） |
| `references/video-prompt-narrative.md` | Prompt 叙事设计技能——连续运镜 vs 时间轴分镜写法详解 |
| `references/narrative-closure-design.md` | 叙事单元收势设计三种模式（含错误示例 vs 正确示例对比） |
| `references/lark-cli-drive-access.md` | 飞书云盘素材获取 SOP（Phase -1：把云盘文件下载到本地） |
| `references/official-docs-token-mapping.md` | 官方 SOP 文档 token → 内容映射表 |
| `references/分镜时序-prompt范式-v7.md` | **v7 范式完整文档**（静默氛围型，Cactus 实测通过；8 段固定结构 + 11 项必跑自检 + 5 件套句式。2026-06-02 Cactus 4 段实测通过） |
| `references/分镜时序-prompt范式-v8.md` | **v8 范式完整文档**（调性匹配型，每 Clip 配相符 BGM；段 5 加 BGM 调性词 + throughout this shot + 段 6 删 No background music。2026-06-03 Ok 好的绘本 4 Clip 实测通过；**已知 clip 内部 BGM 断层问题**，被 v9 取代） |
| `references/分镜时序-prompt范式-v9.md` | **v9 范式完整文档**（**整 Clip 一致 BGM**，段 5 整 Clip 一段 BGM 主题 + `continues throughout the entire clip` + mood shift 软描述；段 6 删 No background music。**2026-06-03 Eat 吃绘本 4 Clip 实测通过**，3.5s shot 边界无 BGM 断层；AI 量化 -22~-34dB 持续平滑曲线） |
| `references/versions/v15.md` | **v15 范式完整文档**（**绘本默认 2026-06-05 起**：v14 骨架 4 段结构 + 启动前 6 必问 + 运镜调性 + v7-Say 音效密集型；v7/v8/v9/v10 是 v15 段 4 的音频子范式。Say 说绘本 10 Clip 实测通过。配套 6 必问 + 撤回运镜三禁 + 必避反模式） |
| `references/分镜时序-prompt范式-v14.md` | **v14 范式完整文档**（**绘本默认骨架 4 段结构**：主体定义 + 分镜绑定 + 风格 + BGM 段；v7/v8/v9/v10 是 v14 段 4 的音频子范式。2026-06-04 起绘本默认，2026-06-05 起升 v15。文字保留 v2 措辞 + BGM 二选一 + 11 项自检 + 范式决策树） |
| `references/绘本音效-prompt写法.md` | **绘本音效 prompt 写法的三铁律 + v3 vs v7 对比**（2026-06-02 Red v1→v2→v3 + Cactus v6→v7 修复沉淀） |
| `references/leading-reading-4clip-pattern.md` | **领读绘本 4-Clip 切分 + 时长公式 + 单测门 SOP**（指向 v7 范式） |
| `references/2026-06-05-say-pitfalls.md` | **2026-06-05 Say 说绘本踩坑对话日志**（旁白语言版本 / 彩色文字 / 运镜定制 3 个实测素材，对应 SKILL.md 关键教训 #25 #26 #27） |
| `references/2026-06-05-ark-list-rescue.md` | **2026-06-05 ark list 端点救援 SOP**（seedance.py 无 list 实现 → 用 ark REST 端点列任务 + curl 下载，0 元重提。对应 SKILL.md 关键教训 #31）|
| `templates/v7-prompt-template.md` | **v7 范式 Python f-string 模板**（ShotV7/AudioSegmentV7/ClipV7 dataclass + render_prompt() + 11 项自检脚本） |
| `assets/example-prompts/cactus-clip1-v7.txt` | **Cactus Clip 1 v7 实际跑通 prompt**（标题页+绿色仙人掌 · 任务 ID cgt-20260602171645-s5fq6 · 8s · 用户"里程碑"反馈） |
| `assets/example-prompts/cactus-clips-2-3-4-v7.txt` | **Cactus Clip 2-4 v7 实际跑通 prompt**（刺/花/手臂/家庭 · 9+10+10s · 4 种动作模式泛化性验证） |
| `assets/example-prompts/ok-clips-1-4-v8.txt` | **Ok 好的 Clip 1-4 v8 实际跑通 prompt**（舞台+门口+森林+共读+餐桌+户外+卧室+彩虹 · 8+9+9+10s · 8 段不同 BGM 调性） |
| `assets/example-prompts/eat-clips-1-4-v9.txt` | **Eat 吃 Clip 1-4 v9 实际跑通 prompt**（餐桌+苹果+香蕉+胡萝卜+鱼+面包+蛋糕+盛宴 · 8+9+9+10s · 整 Clip 一段 BGM + mood shift 软调性变化） |
| `assets/example-prompts/say-p1-v14-v7.txt` | **Say说 封面 P1 v14+v7 静默型 prompt 草稿**（10 段重复句式 "Say X!" · 纸艺拼贴风 · No BGM · 2026-06-05 准备中） |
| `scripts/build_clip_prompts.py` | v3 范式模板拼接脚本（被 v8 范式取代，保留作历史参考） |
| `scripts/build_v8_clips.py` | **v8 范式自动拼接脚本**（含 11 项自检 + clips-prompt.json 自动化输出 + 默认 --watermark false · 2026-06-03 Ok 好的绘本实测） |
| `scripts/build_v9_clips.py` | **v9 范式自动拼接脚本**（含 v9 专属 11 项自检 + 必检 `continues throughout the entire clip` + `mood shift` 软描述 · 2026-06-03 Eat 吃绘本实测通过） |
| `test-prompts.json` | **达尔文 8 维评估用 3 个测试 prompt**（happy/复杂/边界） |
| `results.tsv` | **达尔文优化循环历史记录**（baseline + 各 round keep/revert） |