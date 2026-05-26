# video-prompt - 分镜生视频技能

> 来源：云盘 jimeng-2026-05-26-1840-video-prompt.md

---

## 技能描述

将校验完成的Clip表中的每个Clip，翻译成AI能直接执行的视频生成提示词，然后调用视频工具**并行生成所有视频片段**。

**它是 Phase 8「分镜生视频」的核心技能**，完成参考素材生成和用户确认后，调用本技能批量生成所有视频片段。

---

## 核心原则

1. **完全忠实于Clip表**：Prompt必须完全基于分镜描述，不增加不删减内容
2. **一致性优先**：明确要求保持参考主体的外观、服装、场景与参考图一致
3. **清晰动作描述**：用动作动词明确描述镜头内的动态变化
4. **并行生成**：所有Clip一次性并行提交，不串行分批

---

## Prompt编写规范

每个Clip的Prompt必须包含以下要素（**按此顺序**，顺序混乱会导致模型权重分配错位）：

| 顺序 | 要素 | 作用 | 示例 |
|------|------|------|------|
| 1 | Subject（主体） | 焦点是谁/什么 | `A young girl in ethnic clothing` |
| 2 | Action（动作） | 具体在做什么 | `lifts torch above her head` |
| 3 | Environment（环境） | 在哪发生 | `terraced fields at night` |
| 4 | Camera（运镜） | 镜头怎么动 | `tracking shot, cinematic movement` |
| 5 | Style（风格） | 视觉美学 | `flat 2D cartoon illustration` |
| 6 | Lighting/Mood（光/氛围） | 光线和情绪 | `golden hour backlighting, warm` |

### Prompt示例

```
<subject>男主_遗忘事务所</subject>坐在办公桌后，<subject>女主_遗忘事务所</subject>坐在对面，场景保持<subject>办公室_遗忘事务所</subject>一致。
男主抬头看向女主，女主慢慢抬头说出台词，女主推过表格给男主。
台词：女主说"我想忘记他"，男主说"填写详细信息"。
整体风格保持冷灰写实色调，人物动作自然流畅。
```

---

## 工具选择规则

| 情况 | 命令 |
|------|------|
| 纯文生视频 | `text2video` |
| 已有首帧参考图 | `image2video` |
| 多参考素材（角色+场景+动作） | `multi_modal2video` |

### ⚠️ 重要互斥规则

`--image`（first_frame）和 `--ref-images` **互斥**：同时使用会触发 API 报错：

```
first/last frame content cannot be mixed with reference media content
```

两个场景互斥，只能二选一。

### 参数默认值

| 参数 | 默认值 |
|------|--------|
| 时长 | Clip表中计算的总时长（必须 ≤15s） |
| 宽高比 | 16:9 |
| 分辨率 | 720P |
| 模型 | seedance2.0_vip |

---

## 输出格式

```markdown
# {故事名称}视频生成任务清单

| Clip编号 | 输出ID | 生成命令 | 参考素材 | 时长(秒) | Prompt |
|----------|--------|----------|----------|----------|--------|
| 1 | [output_id] | [命令类型] | [参考主体/参考图ID列表] | X | [Prompt完整内容] |
| 2 | ... | ... | ... | ... | ... |

## 总信息
**总Clip数：** N个
**预计总时长：** XX 秒
```

---

## 执行检查清单

- ✅ 确认每个Clip的Prompt完全忠实于分镜描述，没有新增内容
- ✅ 确认所有参考主体都已正确引用，资源ID已填入对应参数
- ✅ 确认每个Clip时长都 ≤ 15秒，严格遵守硬约束
- ✅ 确认所有输出ID命名规范，每个ID唯一
- ✅ 确认所有生成任务并行提交，没有串行分批
- ✅ 确认工具命令选择正确（image2video/multi_modal2video/text2video）
- ✅ 确认宽高比、分辨率等参数设置合理