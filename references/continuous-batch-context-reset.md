# 连续批量工作流 · 压缩上下文重置 SOP

> **来源**：2026-07-15/17 Bridge→Lavender→Bookstore 三连发实测沉淀
> **触发**：用户说 `压缩上下文` / `准备接收新素材包` / `OK，压缩上下文，准备接收新素材包`
> **作用域**：picturebook-video skill 单次任务完成 → 下一个任务的衔接

## 一、触发判定

**必触发本流程的 3 类用户信号**：
1. `压缩上下文`（最常见）
2. `准备接收新素材包`
3. `OK，压缩上下文` / `OK，准备接收新素材包`（短回复模式）

**不要触发本流程的 2 类信号**：
- `重新做这个` / `重做 Clip 3` → 同一个项目，不重置
- `改一下` / `修改 prompt` → 同一个项目，不重置

## 二、上下文重置 4 件套

新项目到达后，主 agent 必须执行以下 4 项重置，**禁止**沿用上一个项目的产物：

| 重置项 | 内容 | 反例 |
|---|---|---|
| 1. 项目产物 | 不复用 `image-inventory.md` / `clips_final.json` / `clip[1-9]_prompt.txt` | ❌ 把上一个项目的 prompt 改几个字当新项目的 prompt |
| 2. 验证结果 | 不复用 `verify_prompt.py` 输出（每个项目 `ref_images` / `tts_seconds` 不同） | ❌ 把上一个项目的 `ok=True` 当新项目前置结论 |
| 3. Seedance 任务 | 不复用 `task_id`（即使模型相同，任务必走新提交） | ❌ 假设前面项目的 task_id 还能用 |
| 4. 主上下文 | **主动保留**的只有"用户偏好记忆"（工作风格 + 偏好），不保留任务产物 | ❌ 在新项目提示词里复读上一个项目的 vision 结果 |

## 三、新项目启动 SOP

### Step 0 · 清理上一项目中间产物

```bash
# 仅保留 outputs/ 和 image-inventory.md 作为项目记录
rm -rf frames/ frames_contact_sheet.jpg submit_clip*.log task_ids.json
# verify_clip*.json 也可删（保留 outputs 即可）
rm verify_clip*.json
```

**保留清单**：
- `outputs/clip[1-9].mp4` （交付物 + md5 证据）
- `image-inventory.md` （图片自检记录，便于用户后续核对）
- `clips_final.json` （项目时间轴）
- `clip[1-9]_prompt.txt` （项目 prompt 记录）

### Step 1 · 接收新素材（不复用旧 vision）

新 7z 到达时，**直接进入新项目目录**，例如：

```bash
mkdir -p /home/ubuntu/<new_project>
7z x -y <新 7z 路径> -o/home/ubuntu/<new_project>
```

主 agent 视觉处理流程：
1. 单图 `vision_analyze` × N（不复用上次项目的视觉记忆）
2. `delegate_task` 派独立 subagent 跨图复核（重点核对方向冲突点，例如"6.jpg 是否有人物"、"1.jpg 大写小写"）
3. `read_file` 读 SRT 文件，重新跑 `srt_parser.py` → `clip_merger.py`（不沿用上次 timeline.json）
4. 写新 `image-inventory.md`（不复用旧版）

### Step 2 · 计算 Clip 划分（重跑 clip_merger）

**禁止**：把上一个项目的 `clips_final.json` 改成新 SRT 的数据
**必须**：重跑 `python3 scripts/clip_merger.py timeline.json --user-tts <新总秒数>`

### Step 3-N · 完整重做 7 步流程

新项目走标准 7 步：
1. Step 1 接收需求 ✅
2. Step 2 vision 自检 ✅
3. Step 3 时长计算 ✅
4. Step 4 Clip 划分 ✅
5. Step 5 prompt 写 ✅
6. Step 6 seedance 提交 ✅
7. Step 7 端到端验证 ✅

**Step 5 警示**：每个项目的提示词结构**几乎不会复用**——8 张图 vs 9 张图 / 单图切换 vs 多图叙事 / 静物 vs 人物场景 = 完全不同主体动作链。模板 copy-paste 是反模式。

## 四、退出流程（用户说"压缩上下文"时）

主 agent 必做的 4 件事：

1. **确认交付**：3 个视频已发 + task_id + md5 + 时长已附
2. **清理中间产物**（见 Step 0 清单）
3. **保留记录**：outputs/ + image-inventory.md + clips_final.json + clip[1-9]_prompt.txt
4. **记忆更新**：把"用户的工作风格"类偏好写入长期记忆（不要写任务产物）

## 五、典型 4 类上下文重置踩坑

### 5.1 沿用 image-inventory.md

```
❌ 把上一个项目的 @Image1-8 描述 copy-paste 到新项目
❌ 假设"参考图都是明亮柔和的儿童绘本全景"
✅ 每个项目重跑 vision_analyze，每张图独立自检
```

### 5.2 沿用 prompt 模板

```
❌ 复用"画面底部的木拱桥"等上个项目的描述
✅ 每个项目根据 image-inventory 写新动作链
```

### 5.3 沿用 seedance task_id

```
❌ 假设 cgt-20260715... 能复用
✅ 每个项目新提交，记新 task_id
```

### 5.4 沿用 SRT 节奏档位

```
❌ 假设"用户都用领读短句档 4.0 字/秒"
✅ 跑 `srt_parser.py` 反推实际速率（每个项目实际速率不同）
```

## 六、用户偏好速查（本会话沉淀）

- 用户用 `压缩上下文` 表达"上一个项目结束，准备下一个"
- 用户说 `OK` 接新素材包 = **不要重复询问 Step 1 已交过的内容**（readme/SRT/旁白确定性问题）
- 用户在每项目都会重复 `OK → 进入 Step 6` 模式，**不要假设"上次的状态保留下来"**
- 3 个项目接连实测验证 ✅

## 七、与其他 SOP 的关系

- **不要**与 picturebook-creator 的批量流程混淆（本 skill 是"绘本转视频"，picturebook-creator 是"绘本创作"）
- **不要**与 ai-drama-sop 9 阶段流程混淆（本 skill 只覆盖视频生成后段，ai-drama-sop 覆盖前期创意）
- 与 Step 7 的关系：压缩上下文 = 上一项目 Step 7 完成后，下一项目 Step 1 重启

## 版本

v1.0 (2026-07-17 实测沉淀，来自 Bridge→Lavender→Bookstore 三连发)