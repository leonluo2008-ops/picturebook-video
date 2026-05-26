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