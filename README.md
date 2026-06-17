# picturebook-video v5.0

> **绘本转儿童动画视频标准流程（导演模式）** · 输入静态图 + 旁白 → 输出完整动画视频 · **单仓含 seedance_mcp 集成**

[![version](https://img.shields.io/badge/version-5.0.0-blue)]()
[![methods](https://img.shields.io/badge/方法论-4-green)]()
[![laws](https://img.shields.io/badge/铁律-28-orange)]()
[![references](https://img.shields.io/badge/references-33-lightgrey)]()
[![single_repo](https://img.shields.io/badge/单仓集成-seedance_mcp-success)]()

---

## 🎯 一句话能力

**接收任意数量静态绘本图 + 双语旁白 → 输出完整动画视频（v8 导演分镜模式 · 参考图驱动 · 简洁写实 · 物理保证连贯）**。

**v5.0 核心升级**：
- ✅ **单仓可用** — `seedance_mcp/` 集成（uguu 上传 + Ark API 调用 + MCP 协议壳），不再依赖 `seedance2.0-tool` 仓
- ✅ v8 prompt 模板（替代 v15 4 段 / v6 5 段 / v7 12 步）
- ✅ 28 铁律按工作流顺序
- ✅ references 87→33 精简
- ✅ scripts 8→2
- ✅ 新增元方法论 `workflow-internal-vs-external-confirmation`

---

## 🧠 4 元方法论（v3.0 起 · 持续迭代）

| # | 方法论 | 核心 | 何时用 |
|---|--------|------|--------|
| **#M1** | **整本节奏** | 节奏从整本视角分配，不在单个 clip 内重复起承转合 | Step 3 合并 Clip 时 |
| **#M2** | **规则推导** | 从作者底层思维提取机制，不是搬运表面结构 | 任何规则制定时 |
| **#M3** | **旁白-镜头映射** | 镜头序列必须按旁白进度同步（v1 翻车沉淀）| Step 5 写 prompt 时 |
| **#M4** | **蒸馏治理** | 跨 skill 沉淀方法论，避免低层陷阱累积 | skill 维护时 |

> 详见 `SKILL.md` 元方法论章节 + `references/{v8-workflow-7steps, rule-derivation-methodology, skill-distillation-governance}.md`

---

## 🚦 28 铁律（v4.0 · 含 v8 新增 #26/27/28）

### Step 1-2 · 接收需求 + vision
- **#1** vision 必全 N 张图不抽样
- **#2** 多图并行 vision 误差 → 分批 ≤ 3 张串行
- **#3** 写 prompt 前必先 vision 参考图（逐图列"有/没有"清单）
- **#4** 跳过冲突参考图 = 复用 + 描述延伸
- **#22** 大小主体的装饰/动作必分别列

### Step 3 · 叙事弧 + Clip 合并 + 时长
- **#5** 画面时长匹配旁白时长
- **#6** 静默 = 编排工具不是铁律（#27 强化）
- **#7** 1 个故事 = 1 个 Clip（不按段拆）
- **#8** 家族词组中文 TTS 必算
- **#9** 多图参考 + 长旁白必拆 Clip（蒙太奇装不下）
- **#10** TTS 速率必校对（5 档对比 · 绘本短句领读默认 1.4/4.0）
- **#11** 整本节奏 = N 个 clip 节奏分配（#M1）
- **#12** 时长 = 真实叙事秒数不凑整（#27 强化）
- **#21** 用户给 TTS = 严格匹配 · 不加冗余 · 不加静默（Seal 海豹第 3 次跨本验证）
- **#25** TTS 速率：1.4/4.0 档默认 · 必跑 5 档对比 · 反推拟合 ≠ 真实速率

### Step 4-5 · JSON + prompt
- **#13** 信任参考图 + 关键引导不堆细节
- **#14** 镜头序列 = 旁白进度的视觉化映射（#M3）
- **#15** 凡引用官方原文必逐字核对（漏 1 字 = 错全意）
- **#16** 不把"建议"升级成"红线"
- **#17** 约束词只对已知出错元素用 · 4 行末尾约束标准
- **#18** 拟声符号生命周期 = 瞬时动作（#M2）
- **#23** readme 文字 vs vision 视觉冲突 = 默认按 readme 文字
- **#25** verify 脚本对手写 v8 必误报 · 走手动 grep 4 项兜底

### Step 5-6 · prompt 写法 + seedance 提交（v8 核心）
- **#26** **视频 = 读者脑补的动画 · 参考图是起点不是限制**（v8 终版 · 跨本验证升铁律）
- **#27** **静默/情节填充 = 编排工具不是义务 · 时长 = 用户 TTS 优先**（v8 终版）
- **#28** **末帧段落冗余 = 反模式 · v8 简洁收尾 = 末段只写 1 句不堆砌**（v8 终版）

### Step 6-7 · seedance 提交 + 端到端验证
- **#19** MCP timeout ≠ 任务失败（status 唯一权威）
- **#20** 不抽帧质检 ≠ 不 vision 参考图（两环节勿混淆）
- **#24** 打包/归档文件名必用 ASCII（严禁中文）

> 详见 `SKILL.md` 顶部纠错表（按工作流 Step 1→7 排序）· 4 个新增铁律 #26/27/28 + #25 升级

---

## 🛠️ 工作流概览（7 步）

```
Step 1 · 接收需求（简介 + 图片 + 平台 + TTS）
         ↓
Step 2 · vision 全 N 张图（不抽样）+ 列"图有/没有"清单 + 通读旁白
         ↓
Step 3 · 标叙事弧 → 合并到 3-5 Clip + 算 TTS（5 档对比 · 1.4/4.0 默认）
         ↓
Step 4 · 写 11 维 JSON（≤ 4 Clip 主 agent 直干）
         ↓
Step 5 · v8 prompt 模板（4 段·简洁写实·不堆砌）+ 手动 grep 4 项验证
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
| 静态图 | ≥ 1 张，任意数量（推荐 3-8 张）|
| 双语旁白 | 文字或 MP3 |
| 目标平台 | 抖音 / 小红书 / 视频号 / 横屏绘本 |
| 可选 | BGM 音乐、TTS 数值 |

### 关键约束

| 参数 | 限制 |
|------|------|
| 单 Clip 时长 | **4s ≤ duration ≤ 15s**（物理硬限）|
| duration | **必为整数**（向上取整）|
| 视频总时长 | = 用户给 TTS（不加冗余 · 用户原话优先）|
| 画幅 | 默认 16:9（绘本）/ 9:16（抖音/小红书）|
| 生成方式 | **单测必跑 + 用户确认 + 3 并发多轮分批**（v5.0.4 沉淀，详 SKILL.md 铁律 #30 #31）|
| 范式 | **v8 prompt 模板**（替代 v15/v6/v7）|

---

## 📂 目录结构（v5.0 · 单仓含 seedance_mcp 集成）

```
picturebook-video/
├── SKILL.md                          # 主工作流（28 铁律 · 4 元方法论）
├── README.md                         # 本文件
├── CHANGELOG.md                      # 开发日志
├── VERSION_INDEX.md                  # 范式版本索引
├── INSTALL.md                        # 安装指南（v5.0 单仓简化版）
├── INSTALL_TEST.sh                   # 一键验收脚本（7 步检查 + 端到端视频）
├── seedance_mcp/                     # 🆕 v5.0 集成（替代 seedance2.0-tool 仓）
│   ├── mcp_server.py                 # MCP 协议壳（自动注册 mcp_seedance_*）
│   ├── seedance_uploads.py           # uguu 上传 + Ark API 调用（569 行 · 真业务）
│   ├── .env.example                  # ARK_API_KEY 模板
│   └── smoke_test.py                 # 冒烟测试（无需 MCP server）
├── bin/                              # 🆕 v5.0 集成
│   └── seedance-mcp-wrapper.sh       # 加载 .env → 启动 mcp_server.py
├── references/                       # 33 份支撑文档
│   ├── v8 写法核心（4 个 · 当前唯一标准）
│   │   ├── v8-prompt-template.md                  # v8 prompt 模板
│   │   ├── v8-workflow-7steps.md                  # v8 7 步工作流
│   │   ├── v8-tts-rate.md                         # v8 TTS 速率方案
│   │   └── v8-rpa-rpb-rpc-three-core-antipatterns.md  # 3 类核心反模式
│   ├── 元方法论支撑
│   │   ├── rule-derivation-methodology.md         # #M2 规则推导
│   │   ├── skill-distillation-governance.md       # #M4 蒸馏治理
│   │   ├── reference-image-as-starting-point.md   # #26 参考图是起点
│   │   ├── story-arc-and-no-fabrication-pitfall.md # 故事弧 + 凭空添加反模式
│   │   ├── workflow-internal-vs-external-confirmation.md  # 流程内不确认（2026-06-16 新）
│   │   └── cross-platform-filename-encoding.md    # #24 跨平台文件名编码
│   ├── 官方原话纪律
│   │   ├── official-quote-4-levels.md             # 官方原话 4 档分级
│   │   └── official-docs-token-mapping.md         # 文档 token 映射
│   ├── 实战工具
│   │   ├── ark-list-rescue.md                     # ark list 端点救援
│   │   ├── lark-cli-drive-access.md               # 飞书云盘访问
│   │   ├── onoma-symbols-disposal.md              # 拟声符号处置
│   │   └── uguu-fallback-route.md                 # 图床 fallback
│   ├── ai-drama-sop/                # 10 个 AI 短剧 SOP（保留作查询）
│   ├── seedance-official-docs/      # 7 个即梦官方文档
│   └── versions/                    # 版本归档
├── agents/                           # 子 agent 架构（L1-A ~ L3-D）
├── assets/                           # 示例 prompt（11 个）
├── scripts/                          # tts_rate_calculator + validate_durations
├── evals/                            # 达尔文评估
└── tests/                            # 测试用例
```

---

## 🎯 适用场景

✅ **适合**：已有静态绘本图片 + 双语旁白，需要转换为儿童动画视频
✅ **核心优势**：v8 导演分镜模式（简洁写实 · 参考图驱动 · 不堆砌约束）

❌ **不适合**：
- 纯文本生成视频（请用 seedance2.0-tool）
- 单张图 → 视频（可用但多图参考价值更大）

---

## 🧬 seedance_mcp 集成（v5.0 起内置）

**v5.0 起 picturebook-video 自带 `seedance_mcp/` 集成**，**不再需要装 `seedance2.0-tool` 仓**。

| 项 | 内容 |
|---|---|
| **真业务逻辑** | `seedance_mcp/seedance_uploads.py`（569 行）= uguu 上传 + 火山 Ark API 调用 |
| **MCP 协议壳** | `seedance_mcp/mcp_server.py`（270 行）= 4 个工具：`generate_video` / `check_task` / `wait_and_download` / `verify_api_key` |
| **wrapper** | `bin/seedance-mcp-wrapper.sh`（30 行）= 从 `.env` 加载 ARK_API_KEY → 启动 mcp_server.py |
| **安装路径** | `git clone` picturebook-video 一份 = 全部就绪 |
| **依赖外部** | 仅 uguu.se（图床）+ 火山引擎 Ark API（视频生成）= 都在 .env 配 ARK_API_KEY 即可 |

**为何独立 seedance2.0-tool 仓可以保留**（你继续优化用）：
- seedance2.0-tool 仓内含 spike 005/006 + 16k CLI 入口（绘本场景不用 CLI）
- picturebook-video 集成版只取核心 ~800 行
- 两仓并行不冲突；如 seedance2.0-tool 升级新能力，可选择性同步进 picturebook-video

**从老版本升级**：v4.x → v5.0 完整步骤见 `references/upgrade-v4-to-v5.md`（9 步：汇报 → 备份 → 克隆 → 部署 → 配 .env → 查 config → 重启 → 验收 → 清理）。

---

## 📜 版本历史

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| **5.0.0** | 2026-06-16 | 🆕 **单仓集成 seedance_mcp**（uguu + Ark API + MCP 壳共 ~800 行）· 不再依赖 seedance2.0-tool 仓 · INSTALL_TEST.sh 7 步一键验收 · mcp_server.py 域名修复（volcsandbox.com → volces.com）|
| 4.0.1 | 2026-06-16 | patch：8 处 references 断链修复 + INSTALL.md Git HTTPS TLS 兜底 |
| 4.0.0 | 2026-06-16 | v8 终版：prompt 模板替代 v15/v6/v7 · #26/27/28 新铁律（参考图起点/简收尾/静默编排）· references 67→33（-50%）· scripts 8→2 · 新增 workflow-internal-vs-external-confirmation 元方法论 |
| 3.0.0 | 2026-06-14 | 4 元方法论 + 20 铁律按工作流顺序重排 · description 1338→986 |
| 2.x | 2026-06-08~13 | v14/v15 范式迭代 · 多 agent 架构搭建 · 达尔文评估引入 |
| 1.x | 2026-05-28~06-07 | 即梦官方 skill 移植 · 衔接设计规范 · 实战踩坑沉淀 |
| 0.1.0 | 2026-05-26 | 初始版本（火把节衔接断裂实战）|

---

## 🔧 维护说明

本项目采用 **持续维护 + 达尔文评估** 双轨模式：

1. **实战沉淀**：每次绘本任务发现的"新坑/新公式/新模板"写入 work/ 笔记，≥ 3 次跨本验证升铁律
2. **达尔文评估**：基线 → Round N → 棘轮优化（每次 keep 必须有量化收益）
3. **元方法论优先**：低层陷阱累积 → 提炼为方法论 → 蒸馏到 skill

> 教训：通用方法论才入 skill，绘本踩坑写 work 笔记。业务 / 方法论 / 铁律三层架构分离。

---

## 📝 实战案例

| 绘本 | 状态 | 关键沉淀 |
|------|------|---------|
| **Grandpa 爷爷**（v4.0 首秀）| ✅ 5 Clip · 32.44s · 8 张图全用 | 验证 v8 prompt 模板 + #26/27/28 铁律 · 流程内不确认方法论 |
| **v5.0 单仓冒烟** | ✅ 1 Clip · 5.04s · 单图参考 | 验证 seedance_mcp 集成 · 单仓可用 · 不依赖 seedance2.0-tool |
| Donkey 驴（v3.0 首秀）| ✅ 5 Clip · 46.46s · 8 张图全用 | 验证 #M3 旁白-镜头映射修复 v1 翻车 |
| Cactus 仙人掌 | ✅ Cat 4a v3 标版 | 长旁白 v15.1 拆分规范 |
| Mango 芒果 | ✅ | 绘本多图 v15 范式 |
| Duck 鸭子 | ⚠️ v6 翻车 → v7 修复 | 拟声符号生命周期（短时出现 0.5s 后消失）|

---

**当前主推范式 = v8**（2026-06-16 起绘本默认 · 替代 v15/v6/v7）· 详见 `VERSION_INDEX.md`
