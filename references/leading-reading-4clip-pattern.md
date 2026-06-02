# 领读绘本 · 4-Clip 合并模板

> **2026-06-02 实测沉淀**：领读型绘本（弱情节、靠画面+旁白推）的标准工作流。
> **三铁律提醒**：本文件是**模式**（workflow skeleton）不是**案例**（test data）。具体目标词/图片编号/旁白内容由项目决定，不复制 cactus 实测数据。

---

## 适用判断

满足以下全部条件才用本模板：

- ✅ **领读/认知/认字绘本**（不是叙事型）
- ✅ 弱情节（无明显"前一幕→后一幕"情节推进）
- ✅ 旁白每段 <8s（按 0.3s/字算）
- ✅ 图片风格统一（同色系/同主体/相邻景别）
- ✅ 总图数 6-10 张（多了需要更细分段）

不满足 → 走标准 1图=1Clip（绘本场景，参考 Step 3 默认策略）。

---

## 总时长公式

```
总时长 = Clip 1 (8s) + Clip 2 (8s) + Clip 3 (9s) + Clip 4 (10s) = 35s
```

**8-8-9-10 分配逻辑**：
- Clip 1（8s）：标题/封面 + 主形象登场，**要稳**
- Clip 2-3（8-9s）：均匀推进，节奏稳定
- Clip 4（10s）：**情感核心**（坚强/自信/友谊），给足余韵

**调整**：
- 段落数 < 4：合并相邻段，每段至少 8s
- 段落数 > 4：每段压到 7-8s 均匀分配，结尾段仍 10s

---

## 单测门 SOP（**强制**）

```
Phase 8 启动
  ↓
【单测】选 Clip 1（开场最具代表性）
  ↓ 提交 + vision 自评
  ↓ 发用户看
  ↓ 用户确认「效果 OK，可以继续」
  ↓
【批量】剩余 N-1 个 Clip 并行提交
```

**单测必看 4 项**：
1. 风格锁定（跟原图一致？）
2. 镜头运镜（推进/拉远自然？）
3. 收势（结尾稳定定格？）
4. 无穿帮/崩坏

---

## Prompt 模板

### 写法：连续运镜 + 首尾帧锁定

**结构**：
- `--image <前图>` 锁首帧
- `--last-frame <后图>` 锁尾帧
- prompt 中间用「镜头推拉 + 暖光晕开」等自然过渡连接

**Prompt 骨架**：

```
@Image1 as the opening frame, [起手动作描述]；
镜头[运镜方式 1]，[中间过渡描述]；
continues to [运镜方式 2] and transitions to @Image2, [中段动作描述]；
final frame: the camera locks completely, the image becomes still, 
no fade, no dissolve, holds to the last frame.
[风格说明：flat cartoon with thick black outlines, vibrant rainbow colors, warm and lively atmosphere]
```

**4 大核心词**（收势阶段必写）：
- `camera locks completely`（镜头锁住）
- `image becomes still`（画面静止）
- `no fade, no dissolve`（不渐隐不淡出）
- `holds to the last frame`（停留至最后一帧）

---

## 必填参数（seedance.py）

| 参数 | 值 | 必填原因 |
|------|----|---------|
| `--image` | 段首图 | 锁首帧 |
| `--last-frame` | 段尾图 | 锁尾帧 |
| `--duration` | 8/8/9/10 | 4s≤x≤15s 硬约束 |
| `--ratio` | `16:9` | 绘本横屏 |
| `--generate-audio` | **`false`** | 旁白后期 TTS，不在 clip 里 |

---

## 调用顺序

1. **Pre-flight** 3a/3b：素材接入（飞书云盘走 lark-cli）
2. **Phase 5** Step 1-4：分镜设计（叙事单元 + 时长 + 组合 + 连贯性校验）
3. **Phase 6**：用户确认
4. **Phase 7**：复用静态图（跳过素材生成主体步骤）
5. **Phase 8 单测**：Clip 1 + 等用户确认
6. **Phase 8 批量**：剩余 Clip 并行提交（**每个 clip 独立文件名**）
7. **Phase 9**：ffmpeg 拼接 + BGM 合并

---

## 常见坑（2026-06-02 实测）

| 坑 | 症状 | 修复 |
|----|------|------|
| **`--download` 是文件路径不是目录** | 4 个 clip 全写到 `output` 文件名上互相覆盖 | 传文件路径 `./output/clip1.mp4`，或传目录后立刻 `mv` |
| **`--generate-audio` 默认 true** | clip 自带说话声/环境音，跟后期旁白冲突 | 强制 `false` |
| **单页旁白 < 4s 不合并** | 旁白撑不到 4s clip 最低线 | 走 2图=1Clip 合并策略 |
| **跳过单测门** | 4 个 clip 跑完才发现 prompt 写错 | 单测门 SOP 强制执行 |
| **`feishu_drive_*` 工具不灵** | 工具 unavailable | 走 §3a lark-cli（不要用 browser） |
| **device code 10 分钟过期** | 二维码扫了无效 | 用 `--no-wait --json` 拿 code 后立即让用户扫 |
| **lark-cli 缺 drive scope** | `Permission denied` | `--domain drive` 重授权 |

---

## 相关章节

- SKILL.md §3a/3b：素材接入（飞书云盘速查）
- SKILL.md §5 Step 3：Clip 切分策略（领读型 2图=1Clip）
- SKILL.md §8：分镜生视频（参数默认值表 + 单测门 SOP）
- SKILL.md §9：ffmpeg 拼接 + BGM 合并
