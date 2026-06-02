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

```python
# 标准模式（Red 绘本等：旁白短，氛围优先）
标准公式 = "8s + 8s + 9s + 10s = 35s"

# 不压缩模式（Cactus 绘本等：旁白长，2 段合 1 clip 时 TTS 需要足够时间匹配画面切换）
不压缩公式 = "8s + 9s + 10s + 10s = 37s"
# 原则：合并 clip 总时长 = 各段 TTS 旁白时长之和 + 0.5~1.5s 缓冲
# 不为了对齐"标准 35s"压缩时长——冗余给后期剪辑留余地
```

**8-8-9-10 / 8-9-10-10 分配逻辑**：
- Clip 1（8s）：标题/封面 + 主形象登场，**要稳**
- Clip 2-3（8-9s 或 9-10s）：均匀推进，节奏稳定；旁白长就 9-10s
- Clip 4（10s）：**情感核心**（坚强/自信/友谊），给足余韵

**2026-06-02 关键更新 · TTS 时间对齐优先**：

> 用户原话："合并 clip 时，你要注意画面的切换时间，因为我后期要用 TTS 旁白来匹配画面"

- 当绘本**需要 TTS 后期精准匹配画面**时，**总时长公式让位给 TTS 时长**：
  - 算每段旁白 TTS 耗时（中文 0.3s/字 + 英文 0.3s/词）
  - 合并 clip 时长 ≥ 第 1 段 TTS + 第 2 段 TTS + 缓冲（0.5-1.5s）
  - **不要为对齐"标准 35s"而压缩**——冗余给后期剪辑留余地
- 示例（Cactus 绘本）：
  - Clip 1：第 1 段 "仙人掌 Cactus!" 1.2s + 第 2 段 "一棵绿色的仙人掌 Cactus。" 3.9s + 缓冲 = **8s**（接近标准）
  - Clip 2：第 1 段 2.4s + 第 2 段 5.1s + 缓冲 = **9s**（比标准多 1s）
  - Clip 3：第 1 段 3.6s + 第 2 段 3.9s + 缓冲 = **10s**（比标准多 1s）
  - Clip 4：第 1 段 2.4s + 第 2 段 3.3s + 缓冲 4s = **10s**（同标准，给结尾余韵）
  - 总时长 **37s**（比标准多 2s，但 TTS 切换点完全对齐）

**调整**：
- 段落数 < 4：合并相邻段，每段至少 8s
- 段落数 > 4：每段压到 7-8s 均匀分配，结尾段仍 10s
- **TTS 优先时**：无视上述压缩规则，按旁白时长算

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

**单测必看 5 项**（**AI/人分工**）：
1. 风格锁定（跟原图一致？）→ AI 可查
2. 镜头运镜（推进/拉远自然？）→ AI 可查
3. 收势（结尾稳定定格？）→ AI 可查
4. 无穿帮/崩坏 → AI 可查
5. **音效（无朗读/无 BGM/有卡点/不抢戏）→ 人必须听**（vision_analyze 不支持 mp4 音频）

> 来源：picturebook-video SKILL.md Phase 8 单测 SOP 完整版（2026-06-02 园丁 P1-1 升级）

---

## Prompt 范式（v7 范式 · 见 references/分镜时序-prompt范式-v7.md）

> **2026-06-02 后**：领读绘本 2图=1Clip 合并**必须用 v7 范式**（分镜时序+精准动画+精准音频控制）。**不要再用 v3 连续运镜写法**（无法精准 TTS 切换+音频控制失效）。
>
> 完整 v7 范式 + 模板 + 自检 + 字段说明见：`references/分镜时序-prompt范式-v7.md`
>
> **8 段固定结构**（v7 范式）：
> 1. 分镜引导（`This is a storyboard reference image sequence; render ...`）
> 2-3. shot 视觉分镜（`from X.Xs to Y.Ys @ImageN is the ... shot, in this shot [动作], then [稳态]`）
> 4. 收势词（`final frame: the camera locks completely, ...`）
> 5. 音频描述（`Storyboard Audio Description: X.Xs to Y.Ys [音效1]...`）
> 6. 音频禁令（`No background music, no human voice, no narration, no singing`）
> 7. 风格锁定（`Children's picture book collage illustration style, ...`）
> 8. 句号收尾（`.`）

### 必填参数（seedance.py）

|| 参数 | 值 | 必填原因 |
||------|----|---------|
|| `--image` | 段首图 | 锁首帧 |
|| `--last-frame` | 段尾图 | 锁尾帧 |
|| `--duration` | 8/8/9/10 | 4s≤x≤15s 硬约束 |
|| `--ratio` | `16:9` | 绘本横屏 |
|| `--generate-audio` | **`true`** | v7 范式在 prompt 里精准控制音效（含 No BGM/No voice 禁令） |

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

|| 坑 | 症状 | 修复 |
||----|------|------|
|| **`--download` 是文件路径不是目录** | 4 个 clip 全写到 `output` 文件名上互相覆盖 | 传文件路径 `./output/clip1.mp4`，或传目录后立刻 `mv` |
|| **v3 范式错以为 audio=false** | 静音 + 缺卡点音效 | **v7 范式必须 `--generate-audio true`**，靠 prompt 里的 `No background music, no human voice, no narration, no singing` 禁令段精准控制 |
|| **v3 范式 `soft chime` 嵌入视觉句** | 持续环境音 + 干扰 TTS 的人声 | **改用 v7 范式**：`Storyboard Audio Description: X.Xs to Y.Ys [音效1]...` 独立音频段 |
|| **单页旁白 < 4s 不合并** | 旁白撑不到 4s clip 最低线 | 走 2图=1Clip 合并策略（v7 范式） |
|| **跳过单测门** | 4 个 clip 跑完才发现 prompt 写错 | 单测门 SOP 强制执行 |
|| **`feishu_drive_*` 工具不灵** | 工具 unavailable | 走 §3a lark-cli（不要用 browser） |
|| **device code 10 分钟过期** | 二维码扫了无效 | 用 `--no-wait --json` 拿 code 后立即让用户扫 |
|| **lark-cli 缺 drive scope** | `Permission denied` | `--domain drive` 重授权 |

---

## 相关章节

- SKILL.md §3a/3b：素材接入（飞书云盘速查）
- SKILL.md §5 Step 3：Clip 切分策略（领读型 2图=1Clip）
- SKILL.md §8：分镜生视频（参数默认值表 + 单测门 SOP）
- SKILL.md §9：ffmpeg 拼接 + BGM 合并
