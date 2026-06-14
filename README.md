# picturebook-video v3.0

> **绘本转儿童动画视频标准流程（导演模式）** · 输入静态图 + 旁白 → 输出完整动画视频

[![version](https://img.shields.io/badge/version-3.0.0-blue)]()
[![methods](https://img.shields.io/badge/方法论-4-green)]()
[![laws](https://img.shields.io/badge/铁律-20-orange)]()
[![references](https://img.shields.io/badge/references-67-lightgrey)]()

---

## 🎯 一句话能力

**接收任意数量静态绘本图 + 双语旁白 → 输出完整动画视频（导演分镜模式 · 段间尾帧接力 · 物理保证连贯）**。

---

## 🧠 4 元方法论（v3.0 新增 · 核心）

| # | 方法论 | 核心 | 何时用 |
|---|--------|------|--------|
| **#M1** | **整本节奏** | 节奏从整本视角分配，不在单个 clip 内重复起承转合 | Step 3 合并 Clip 时 |
| **#M2** | **规则推导** | 从作者底层思维提取机制，不是搬运表面结构 | 任何规则制定时 |
| **#M3** | **旁白-镜头映射** | 镜头序列必须按旁白进度同步（v1 翻车沉淀） | Step 5 写 prompt 时 |
| **#M4** | **蒸馏治理** | 跨 skill 沉淀方法论，避免低层陷阱累积 | skill 维护时 |

> 详见 `SKILL.md` 元方法论章节 + `references/{holistic-storyboard-thinking, rule-derivation-methodology, narration-shot-mapping, skill-distillation-governance}.md`

---

## 🚦 20 铁律（按工作流顺序 · v3.0 整理）

### Step 1 · 接收需求
- **#1 vision 必全不抽样**
- **#2 N 张图列「图有/没有」清单**
- **#3 通读旁白**
- **#4 算 TTS 时长用真实秒数不凑整**

### Step 2 · 标叙事弧
- **#5 整本节奏优先（#M1）**

### Step 3 · 合并 3-5 Clip
- **#6 单 Clip ≤ 15s 物理上限**
- **#7 duration 必整数（4-15 范围）**
- **#8 段间衔接必设计（模式 B/C）**

### Step 4 · 写 11 维 JSON
- **#9 ≤ 4 Clip 主 agent 直干**

### Step 5 · fill v15/v6 模板
- **#10 v15 4 段导演分镜 + 多图参考 + `--ref-images`**（**绝对不用首尾帧范式**）
- **#11 段 4 必用 B 档音效版**（无 BGM + 有音效）
- **#12 元问题 = 主 agent 拿主意 · 不开问卷**
- **#13 紧凑对齐 TTS（单段静默 ≤ 1.5s）**
- **#14 镜头序列同步旁白（#M3 核心）**
- **#15 末帧微动差异化**（不共用「耳朵轻摆」）

### Step 6 · seedance 提交
- **#16 `--ref-images` 多图 = 蒙太奇**（图 1 主导 80% + 图 2 末 1-2s）
- **#17 prompt 时间锚点无效（铁律）**
- **#18 时长 = 真实叙事秒数不凑整**

### Step 7 · 端到端验证 + 发飞书
- **#19 不抽帧质检**（发实际文件，不发抽帧描述）
- **#20 MCP timeout ≠ 任务失败**（status 唯一权威 · 已扣费必查不重提交）

> 详见 `SKILL.md` 顶部纠错表

---

## 🛠️ 工作流概览（7 步）

```
Step 1 · 接收需求（简介 + 图片 + 平台 + TTS）
         ↓
Step 2 · vision 全 N 张图（不抽样）+ 列"图有/没有"清单 + 通读旁白
         ↓
Step 3 · 标叙事弧 → 合并到 3-5 Clip + 算 TTS（1.0 词/秒 + 3 字/秒 + 0.5s 词间停顿）
         ↓
Step 4 · 写 11 维 JSON（≤ 4 Clip 主 agent 直干）
         ↓
Step 5 · fill v15/v6 模板（段 4 B 档音效默认）+ verify 4 项
         ↓
Step 6 · seedance 提交（--generate-audio true + --ref-images 多图 + 整数时长）
         ↓
Step 7 · 端到端验证 → 发飞书（不抽帧自检）
```

---

## ⚡ 快速开始

### 触发词

当用户说以下关键词时调用本 skill：
- `绘本视频`、`绘本转视频`、`绘本动画`、`绘本生成视频`
- `picturebook video`、`绘本做视频`、`整本故事分镜`
- `整本节奏优先`、`旁白-镜头映射`

### 输入要求

| 参数 | 限制 |
|------|------|
| 静态图 | ≥ 1 张，任意数量（推荐 3-8 张） |
| 双语旁白 | 文字或 MP3 |
| 目标平台 | 抖音 / 小红书 / 视频号 / 横屏绘本 |
| 可选 | BGM 音乐、TTS 数值 |

### 关键约束

| 参数 | 限制 |
|------|------|
| 单 Clip 时长 | **4s ≤ duration ≤ 15s**（物理硬限）|
| duration | **必为整数**（向上取整） |
| 视频总时长 | = TTS + 5s 冗余（用户优先）|
| 画幅 | 默认 16:9（绘本）/ 9:16（抖音/小红书）|
| 生成方式 | **并行提交**，不串行 |
| 范式 | **绝对不用首尾帧范式**（用 `--ref-images` 多图参考）|

---

## 📂 目录结构（v3.0）

```
picturebook-video/
├── SKILL.md                          # 主工作流（1305 行 · 4 元方法论 + 20 铁律）
├── README.md                         # 本文件
├── CHANGELOG.md                      # 开发日志（v3.0.0 2026-06-14）
├── VERSION_INDEX.md                  # 范式版本索引（v15 = 绘本默认）
├── INSTALL.md                        # 安装指南
├── references/                       # 67 份支撑文档（v3.0 大幅扩充）
│   ├── #M 元方法论支撑
│   │   ├── holistic-storyboard-thinking.md        # #M1 整本节奏
│   │   ├── rule-derivation-methodology.md         # #M2 规则推导
│   │   ├── narration-shot-mapping.md              # #M3 旁白-镜头映射
│   │   └── skill-distillation-governance.md       # #M4 蒸馏治理
│   ├── 实战沉淀
│   │   ├── clip-pacing-whole-story-perspective.md
│   │   ├── story-arc-rhythm-paradigm.md
│   │   ├── parallel-wait-and-download-pattern.md
│   │   ├── official-quote-4-levels.md
│   │   └── ... (共 67 份)
│   ├── 模板（v15 / v6 / v7）
│   │   ├── v15-4段骨架-模板.md
│   │   ├── v6-5段骨架-模板.md
│   │   └── v7-12-check.md
│   ├── 音效
│   │   ├── sound-strategy-branches.md
│   │   └── 绘本音效-prompt写法.md
│   └── 即梦官方文档
│       └── seedance-official-docs/
├── agents/                           # 子 agent 架构（v3.0 多 agent）
│   ├── storyboard-style/             # L1-A 风格识别
│   ├── storyboard-narration/         # L1-B 旁白量化
│   ├── storyboard-design/            # L2-C 分镜设计
│   └── video-executor/               # L3-D 视频执行
├── evals/                            # 达尔文评估（基线 + R1 keep）
├── templates/                        # 模板文件
├── scripts/                          # 脚本（validate_durations / verify_filled_prompts）
└── tests/                            # 测试用例
```

---

## 🎯 适用场景

✅ **适合**：已有静态绘本图片 + 双语旁白，需要转换为儿童动画视频
✅ **核心优势**：导演分镜模式（一个 prompt 写多段） + 段间尾帧接力（物理保证连贯）

❌ **不适合**：
- 纯文本生成视频（请用 seedance2.0-tool）
- 单张图 → 视频（可用但 v15 多图参考价值更大）

---

## 🧬 与 seedance2.0-tool 的关系

| Skill | 定位 | 何时用 |
|-------|------|--------|
| **picturebook-video** | 绘本转视频专用 · 跳过 Phase 0-4 | 已有静态图 + 旁白 |
| **seedance2.0-tool** | 通用即梦视频生成工具 · 含 CLI 命令 | 任意视频生成场景 |

两者共享 `references/seedance-official-docs/`，保持同步更新。

---

## 📜 版本历史

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| **3.0.0** | 2026-06-14 | 4 元方法论 + 20 铁律按工作流顺序重排 · 删除维护陷阱章节 · 26 陷阱整合到 4 references · description 精简 1338→986 · CHANGELOG 真实反映本轮优化 |
| 2.x | 2026-06-08~13 | v14/v15 范式迭代 · 多 agent 架构搭建 · 达尔文评估引入 |
| 1.x | 2026-05-28~06-07 | 即梦官方 skill 移植 · 衔接设计规范 · 实战踩坑沉淀 |
| 0.1.0 | 2026-05-26 | 初始版本（火把节衔接断裂实战）|

---

## 🔧 维护说明

本项目采用 **持续维护 + 达尔文评估** 双轨模式：

1. **实战沉淀**：每次绘本任务发现的"新坑/新公式/新模板"写入对应 references
2. **达尔文评估**：基线 → Round N → 棘轮优化（每次 keep 必须有量化收益）
3. **元方法论优先**：低层陷阱累积 → 提炼为方法论 → 蒸馏到 skill

> 教训：通用方法论才入 skill，绘本踩坑写 references/work 笔记。

---

## 📝 实战案例

| 绘本 | 状态 | 关键沉淀 |
|------|------|---------|
| Donkey 驴（v3.0 首秀）| ✅ 5 Clip · 46.461s · 8 张图全用 | 验证 #M3 旁白-镜头映射修复 v1 翻车 |
| Cactus 仙人掌 | ✅ Cat 4a v3 标版 | 长旁白 v15.1 拆分规范 |
| Mango 芒果 | ✅ | 绘本多图 v15 范式 |
| Duck 鸭子 | ⚠️ v6 翻车 → v7 修复 | 拟声符号生命周期（短时出现 0.5s 后消失）|

---

**当前主推范式 = v15**（v14 + 6 必问 + 音效密集型 · 2026-06-05 起绘本默认）· 详见 `VERSION_INDEX.md`
