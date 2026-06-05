# CHANGELOG - picturebook-video 开发日志

> 长期维护记录。每次更新都必须填写，格式参照 [Keep a Changelog](https://keepachangelog.com/)。

---

## [0.1.0] - 2026-05-26

### 新增
- 初始版本发布：picturebook-video skill（GitHub: leonluo2008-ops/picturebook-video）
- 主工作流 SKILL.md（372行，覆盖6步完整流程 + 衔接设计规范）
- README.md：项目说明、快速开始、目录结构、主要约束
- CHANGELOG.md：开发日志模板
- references/ 目录：13份即梦官方skill参考文档（见README.md目录结构）
- references/clip-continuity.md：火把节实战衔接问题根因分析 + 三种解决模式（模式A/B/C）

### 实战教训
- **火把节Clip 4-6衔接断裂**：每个Clip独立生成，无接力设计，模型从头渲染场景导致clip连接像GIF随机播放
- **修复方案**：导演模式多镜头时间线（模式B）+ 尾帧接力（模式C），衔接必须在分镜阶段设计，不能事后补救

---

## [Unreleased]

### 新增
- 初始版本：picturebook-video skill
- 主工作流 SKILL.md（348行，覆盖6步完整流程）
- references/ 目录：7份参考文档（video-sop / script-chunk / shots-timing / shots-assembly / scene-reflection / video-prompt / clip-continuity）
- README.md：项目说明、快速开始、目录结构
- CHANGELOG.md：本开发日志

## [0.3.0] - 2026-06-05

### 新增（2026-06-05 Say 说绘本踩坑沉淀 · 关键教训 #25-#31）
- **铁律 25** · 旁白语言版本必须用"用户指定版本"不是"图上有啥"（中文版=中文+小写英文嵌入）
- **铁律 26** · 彩色文字"自然融入"不是"必须一直显示"（末帧文字消失 = 合规；至少出现一次 = 硬约束）
- **铁律 27** · 运镜服务于故事，不是固定公式（按画面类型定制 + **运镜三禁**扩展示例）
- **铁律 27 扩展** · 运镜三禁（写 prompt 时**必避**3 类时间/结构公式 + **必写**3 类无数字描述）
- **教训 #28** · 4s 是硬下限不是推荐值（单 Clip `4s ≤ duration ≤ 15s`）
- **教训 #29** · 当前切分表写在 prompt 开头（防错位 Clip 编号）
- **教训 #30** · 并行提交不存 task ID = 100% 灾难（`TASK_ID=$(...)` 必存 + wait 阻塞下载）
- **教训 #31** · ark list 端点 = task ID 丢失时的救援通道（直调 REST，不重提交）
- **启动前必问 5 件事 + 必避 5 条**（关键教训 #31）
  - 1 视频比例 / 2 目标时长 / 3 切分方案 / 4 范式风格（**v10 为领读型默认**）/ 5 运镜规则
- **VERSION_INDEX 索引更新**（v3-v14 范式全景表 + 检索示例）
- **references/versions/v14.md** 实测留痕（Cactus + Good Morning + Good Night）

### 修复
- Q3 检索盲区（旁白/TTS 关键词覆盖）
- 达尔文 Round 2 keep（维度 8 实测表现修复 · 总分 98.95）
- 达尔文 Round 1 keep（维度 6 8→9 · 总分 95.95→96.45）
- 建 templates/ + assets/ 目录（资源整合度 8→10）
- 维度 9 加 Cactus Clip 2-4 v7 完整 prompt 样本

### 文档
- v3-v14 共 12 份 references/versions/vN.md 范式文档
- 2026-06-05 Say 说绘本踩坑对话日志（references/2026-06-05-say-pitfalls.md）
- README 关键教训段扩充到 8 条（图片分析 / 0.3s/字 / duration 整数 / 衔接设计 / 物理上限 / 尾帧接力 / 并行提交 / 实际文件交付）

### 状态
- **绘本默认范式**：v14 骨架 + v10 段 4 音频子策略（领读型）
- **达尔文评估**：Round 2 keep 总分 98.95 / Round 1 keep 总分 95.95→96.45
- **本版本定位**：v3-v14 范式完整沉淀 + 启动前 5 必问铁律 + 任务管理铁律

---

## 更新记录模板

每次更新请在 Unreleased 上方添加新条目，格式：

```
### 日期
#### 新增 / 修复 / 优化 / 文档
- 变更内容简述（链接到具体 commit 或 issue）
```

---

## 更新类型说明

| 类型 | 含义 |
|------|------|
| **新增** | 新增功能、参考文档、触发词等 |
| **修复** | 对工作流/脚本错误的纠正（如 clip 衔接问题、duration 报错等） |
| **优化** | 对现有流程的改进（不改变功能，仅提升质量或可维护性） |
| **文档** | README、注释、变量命名等文档类更新 |
| **实战** | 从具体项目中提取的经验教训（附具体 clip 编号和问题现象） |

---

## [Unreleased]

## [0.2.0] - 2026-06-04

### 新增
- **VERSION_INDEX.md**（2.9KB 速查表）：11 个范式（v3-v14）全景表 + 检索示例 + 范式选择决策 + 演进时间线
- **references/versions/** 子目录（14.9KB 详细日志）：12 个范式文件
  - v3.md / v4.md / v5.md / v6.md / v7.md / v8.md / v9.md / v10.md（早期+绘本里程碑）
  - v11-α.md / v11-β.md（废弃+备选）
  - v12.md / v13.md / v14.md（音频驱动+修复+绘本默认）
- **SKILL.md 顶部加 VERSION_INDEX 入口**（line 14 引用块）

### 文档
- 把"实测留痕"从散落（8+ 处 SKILL.md 全文 grep）变成**集中检索**——遇到问题先看 VERSION_INDEX 速查，再翻具体范式 .md
- 检索场景示例：禁 BGM → v7 / 多图分镜 → v14 / BGM 调性统一 → v10