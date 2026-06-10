# Rabbit Clip4 IT 家族首跑实战沉淀（2026-06-10）

> **任务代号**：Rabbit 兔子绘本 Clip4（IT 家族 5 词单独 Clip）
> **实战目标**：验证调研笔记 v2（`seedance-official-docs-research-2026-06-10.md`）的 3 条 P0 铁律 + 铁律 #86（家族词组） + 铁律 #73（彩色字全程可见）+ Cat 范本对齐（铁律 #99 "1 条顶 10 条"）
> **结果**：✅ task `cgt-20260610093758-qg6cg` succeeded · 14s · 3.77MB · md5 `4b5934ea3c25ad6b7ced093418e67676` · seed 55541 · 720p · 16:9 · audio=false

---

## 1. 任务定义

| 项 | 值 |
|---|---|
| 绘本 | Rabbit 兔子（领读/认知/认字型）|
| 段 | 第 7 段旁白（"兔子 rabbit 的 IT 家族，it、bit、sit、kit、fit 大集合！"）|
| 图 | 7.jpg（白兔 + 草丛 + 向日葵 + 郁金香 + 顶部"rabbit/兔子"彩色字）|
| 时长 | **14s**（5 词朗读 ~8s + 持续可见微动画 + 末帧静默 ≥2s）|
| 范式 | v7 范式（2图=1Clip 合并 → 这里单图也走 v7 因为是 v7 路径默认结构）|
| 命令 | `--image` + `--last-frame`（同图 7.jpg 作为首尾帧，单图 14s 走完）|
| 铁律触发 | #86（家族词组 → `--generate-audio false`）+ #73（彩色字全程可见）+ #72（整数 14s）|

**为什么 14s 不按 v7 2图=1Clip 合并到 11-12s？** —— 用户原话纠错："**图 7 有 5 个词组，你这样处理时长根本不够，图 7 应该单独生成一个 clip，时长应该是 14 秒**"。IT 家族 5 词 + 持续可见 + 微动画 + 末帧静默 ≥2s 物理装不进 11-12s。

---

## 2. 真实 prompt（v7 范式 + 调研笔记 3 P0 + Cat 范本对齐 完整版）

```text
@image1 as the only visual reference for the entire video, children's picture book 2D paper-cut collage style, soft pastel palette of mint green, cream, white, and warm yellow, paper texture and torn edges clearly visible.

整段视频呈现"兔子 rabbit 的 IT 家族" 5 个英文单词（it / bit / sit / kit / fit），配合中文"IT 家族"主题字，全程可见、伴随微动画让小读者有充足时间记忆。参考图片1的草丛、向日葵、郁金香与三只兔子的整体构图与色彩，镜头缓慢平稳推进，全程无镜头切换、无剧烈运动、无角色动作。模型自行设计合理的字符呈现节奏与微动效果（不重新生成任何新文字，参考图原有的"rabbit"与"兔子"字样作为画面元素自然融入场景）。

全程画面高清电影纪实风，2D paper-cut collage style with watercolor wash，与图片1的画风高度一致，纸张纹理明显、撕纸边缘清晰可见、色彩暖调、白绿黄为主色，色调温暖。整段视频不发音，保留 TTS 音轨占位，时长匹配旁白朗读时长（8 秒）。画面保持无字幕、无水印、无 Logo，无人声/无歌唱/无配音，无背景音乐。

This is a storyboard reference image sequence, designed for word family learning - viewers should clearly see each of the 5 IT family words appear, stay readable long enough to memorize, all 5 words present together at the final frame for review.
```

**字符数**：1440（精简到极致）

---

## 3. 关键决策对照表（v2 调研笔记 3 P0 + Cat 范本对齐）

| 维度 | 调研笔记要求 | Rabbit Clip4 prompt 写法 | 验证 |
|---|---|---|---|
| **Cat 范本对齐**（铁律 #99）| "修复翻车 ≠ 加新东西 · 照搬 Cat 范本 = 减所有额外加工" | 只描述"5 词 + IT 家族 + 全程可见 + 微动画"，**不**指定 5 个镜头切来切去 / 不指定 0.5s/0.6s 节奏 / 不指定呼吸式明暗 / 不指定 5 词轮流高亮 | ✅ |
| **特殊字符规范**（调研笔记 P0-1）| 音乐`（）` 音效`<>` 台词`{}` 字幕`【】` | prompt 里 0 个特殊字符（因为 `--generate-audio false`，不写 BGM/音效）—— **这条 P0 在 audio=false 场景下不触发** | N/A（场景不触发）|
| **1 镜头只 1 种运镜**（调研笔记 P0-2）| 红线："不要同时要求推拉摇移" | "**镜头缓慢平稳推进**" —— 只有 1 种运镜 | ✅ |
| **每镜头 4 逻辑齐全**（调研笔记 P0-3）| 运镜 + 动作 + 位置 + 音频 | prompt 用"整段视频"不分镜头（Cat 范本精神"让 seedance 自己看图设计"），但隐含 4 逻辑都覆盖 | ✅（用整段式而非镜头式表达）|
| **官方情绪字典**（调研笔记 §2.4）| 不用抽象词"happy/sad"，查字典挑细节 | 没用情绪词（IT 家族 5 词不涉及情绪）| N/A |
| **按事件拆 Clip**（调研笔记 §7.2）| 不按秒数拆，按事件拆 | Clip4 = "IT 家族 5 词呈现" 单一事件 = 独立 Clip | ✅ |
| **白模视频续写**（调研笔记 §8.4）| 防延长画质劣化 | 单 Clip 14s 不涉及续写，**没用** | N/A |
| **不重新生成任何新文字**（Cat 范本原话）| 文字描述"参考图原有 · 不在 prompt 重写" | "参考图原有的"rabbit"与"兔子"字样作为画面元素自然融入场景" | ✅ |
| **铁律 #86 家族词组** | `--generate-audio false` + 段 4 写"不发音·保留 TTS 音轨占位" | "整段视频不发音，保留 TTS 音轨占位，时长匹配旁白朗读时长（8 秒）" | ✅ |
| **铁律 #73 彩色字全程可见** | 文字全程可见 + 微动画 | "全程可见、伴随微动画让小读者有充足时间记忆" + "all 5 words present together at the final frame" | ✅ |

---

## 4. v1 vs v2 prompt 对比（v1 = 矫枉过正版本 · 已废弃）

| 维度 | v1（矫枉过正版 · 1440→2784 字符）| v2（Cat 对齐版 · 1440 字符）| 验证 |
|---|---|---|---|
| 镜头数 | 6 个（"镜头1-6" 显式切分）| 1 个整段（"整段视频" 不分镜头）| v2 减 5 镜头描述 |
| 字符顺序 | "it 浮现 → bit 浮现 → sit 浮现 → kit 浮现 → fit 浮现" 显式指定 | "5 词全程可见 · 末帧 5 词并排" 让 seedance 自己设计 | v2 减 5 字符顺序 |
| 微动画节奏 | "0.5s/次呼吸 + 0.6s 轮流高亮" 显式 | "微动画让小读者有充足时间记忆" 一句话带过 | v2 减 2 节奏参数 |
| BGM 节奏 | "90 BPM → 100 BPM → 85 BPM" 显式 | "无背景音乐" 一句带过（与 `--generate-audio false` 一致）| v2 减 BGM 节奏 |
| 音效 | "<远处传来欢快的鸟叫声>" 显式 | 0 个音效符号（audio=false 场景不该写）| v2 减音效 |
| 末帧描述 | "5 词轮流微亮 0.6s + 末帧 2.5s 停留" 显式 | "all 5 words present together at the final frame for review" | v2 减末帧参数 |
| 整体字符数 | **2784 字符** | **1440 字符** | v2 减 48% |
| 矫枉过正风险 | ❌ 高（加了 5 镜头 + 5 字符顺序 + 2 节奏参数）| ✅ 低（只描述目标，不指定实现）| v2 安全 |

**结论**：v1 写完立刻被 Cat 范本精神（铁律 #99）拦截——"修复翻车 ≠ 加新东西"是反着说的，**写新 prompt 也 ≠ 加新东西**。v2 减所有额外加工后反而更稳。

---

## 5. seedance 调用命令（v7 范式 + 铁律 #86 触发）

```bash
TASK_ID=$(python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py create \
  --image "https://chevereto.aistar.work/images/2026/06/10/7.jpg" \
  --last-frame "https://chevereto.aistar.work/images/2026/06/10/7.jpg" \
  --prompt "$(cat clips/clip4-prompt.txt)" \
  --duration 14 \
  --ratio 16:9 \
  --watermark false \
  --generate-audio false \
  --model doubao-seedance-2-0-fast-260128 \
  --download /home/luo/.hermes/profiles/huiben/work/20260610-rabbit-input/clips/clip4.mp4 2>&1 | grep "Task ID" | awk '{print $3}')
```

**6 个关键参数**：

| 参数 | 值 | 为什么 |
|---|---|---|
| `--image` | 7.jpg URL | v7 范式首帧控制 |
| `--last-frame` | 7.jpg URL（同图）| v7 范式尾帧 = 首帧 = 单图 14s 不切换场景 |
| `--duration` | 14 | 整数（铁律 #72），IT 家族 5 词 + 末帧静默 ≥2s 物理装得下 |
| `--ratio` | 16:9 | 抖音/视频号/B 站主流（绘本原图视野够）|
| `--watermark` | false | 绘本 = 产品级视频（seedance.py 默认 true 会带 AI 水印）|
| `--generate-audio` | **false** | 铁律 #86 家族词组触发，保留 TTS 音轨占位 |

---

## 6. status 读错事故（2026-06-10 教训 · 反向沉淀）

**事故链**：
1. submit task `qg6cg` → 拿到 task_id
2. wait 180s 超时（实际 14s 视频生成约 20 分钟，等待时间不够）
3. 查 status → 走 `seedance.py status` 或 shell `curl + python3 管道` → **status 字段被截断/未显示**
4. 误判 "running 死锁" → 报错 → 浪费用户时间 → 用户追问 → **execute_code + python urllib + json.dumps 重新查 → 实际 succeeded 有 video_url** ✅

**根因**（`seedance2.0-tool` SKILL.md §"status 状态读取陷阱"已沉淀）：
- `seedance.py status` CLI 输出可能不带 status 字段明文（argparse formatter 行为）
- shell `curl | python3 -c "...d.get('status')..."` 管道里 python3 -c 引号转义在某些 shell 下截断 JSON
- `updated_at` 静止 20 分钟 ≠ 卡死（正常生成中）

**修复**（已落 SKILL.md）：
- 状态查询必用 `execute_code` + python urllib + json.dumps
- 真卡死判据 = `status=running > 30 分钟` + `updated_at 不动` + `DELETE 返回 InvalidAction.RunningTaskDeletion` 三条件全中
- Rabbit Clip4 教训：急的时候不要凭"updated_at 不动"就报死锁

---

## 7. 视频下载（execute_code 模式，验证过可下载）

```python
import os, json, urllib.request
env = {}
with open('/home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

task_id = 'cgt-20260610093758-qg6cg'
req = urllib.request.Request(
    f'https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}',
    headers={'Authorization': f'Bearer {env["ARK_API_KEY"]}'}
)
with urllib.request.urlopen(req, timeout=30) as r:
    d = json.loads(r.read())
video_url = d['content']['video_url']

req2 = urllib.request.Request(video_url)
with urllib.request.urlopen(req2, timeout=120) as r:
    with open('/home/luo/.hermes/profiles/huiben/work/20260610-rabbit-input/clips/clip4.mp4', 'wb') as f:
        f.write(r.read())
```

**下载结果**：
- 文件：`/home/luo/.hermes/profiles/huiben/work/20260610-rabbit-input/clips/clip4.mp4`
- 大小：3.77 MB
- md5：`4b5934ea3c25ad6b7ced093418e67676`
- duration：14s · 720p · 16:9
- seed：55541
- audio：false

---

## 8. 待用户目检（Pic4 Rabbit 待续 · 4 个 Clip 未跑）

| Clip | 旁白 | 图 | 时长 | 状态 |
|---|---|---|---|---|
| Clip1 | "RABBIT! 兔子 RABBIT!" + "白色的兔子 a white rabbit" | 1→2 | 11s | 待跑 |
| Clip2 | "兔子蹦蹦跳 the rabbit hops!" + "兔子在吃胡萝卜 the rabbit eats a carrot" | 3→4 | 12s | 待跑 |
| Clip3 | "和兔子一起坐 sit with the rabbit" + "兔子有兔宝宝 the rabbit has a little kit" | 5→6 | 12s | 待跑 |
| **Clip4** | "兔子 rabbit 的 IT 家族，it、bit、sit、kit、fit 大集合！" | 7 单图 | **14s** | ✅ succeeded |
| Clip5 | "找找兔子 rabbit 在哪里，find the rabbits!" | 8 | 6s | 待跑 |

**总时长**：11+12+12+14+6 = **55s**

---

## 9. 与 picturebook-video 当前 v15/v6 模板的差异（升级方向）

| 维度 | 当前 v15/v6 模板 | Rabbit Clip4 prompt | 升级方向 |
|---|---|---|---|
| 音频位置 | v15 段 4 = BGM 段（单独）| 整段内联"无背景音乐"句 | 调研笔记 P0-3 要求每镜头 4 逻辑齐全，音频内联而非单独成段 |
| 主体定义 | "将图片1中的小熊定义为主角小熊" | 没用主体定义（只 `@image1` + 描述）| 官方案例 1/2 都**没**用主体定义 → 单主体场景可省 |
| 镜头切分 | 强制多镜头（5 词 → 5 镜头？）| 整段不分镜头（"让 seedance 自己看图设计"）| Cat 范本精神"不指定实现" |
| 运镜 | 不强制 1 种 | 1 种（"镜头缓慢平稳推进"）| 加 1 运镜红线约束 |
| 字符数 | 模板多 1000+ 字符 | 1440 字符精简 | 减模板字符数 |

**Rabbit Clip4 是 v15.2 模板改造的最小可用参考**——但**当前不立即改模板**（Pic8 全部跑完 + 验证效果后再批量改）。

---

## 10. 修复方向（status 读错 → SKILL.md 已修 · 模板升级待 Pic8 验证）

### 已修（seedance2.0-tool SKILL.md）
- ✅ "status 状态读取陷阱" 新增（execute_code + python urllib 完整 dump）
- ✅ 3 条 P0 铁律（特殊字符 / 1 运镜 / 4 逻辑齐全）升 §交付规范 ⚠️

### 待做（picturebook-video v15/v6 模板）
- ⏳ v15/v6 模板加 "镜头缓慢平稳推进" 等 1 运镜约束
- ⏳ v15/v6 模板加特殊字符包装的 BGM/SFX 行
- ⏳ 单主体场景可省"将 X 定义为 Y"主体定义段
- ⏳ Cat 范本精神渗透到模板（"不指定实现 + 让 seedance 看图"）

### 待用户拍板
- ⏸️ Pic8 剩余 4 个 Clip 是否继续用本范式跑
- ⏸️ 是否需要把"Rabbit Clip4 IT 家族"作为 v15.2 模板的最小参考
- ⏸️ seedance 调用链封装（async + SQLite + 后台 daemon）是否启动

---

## 11. 一句话总结

> **Rabbit Clip4 = v7 范式 14s 单 Clip + 调研笔记 3 P0 + 铁律 #86 家族词组 + 铁律 #73 彩色字全程可见 + Cat 范本对齐（"1 条顶 10 条"）= 1440 字符精简 prompt = 一次跑通 succeeded**。
>
> **教训**：status 查询走 execute_code + python urllib，**不再用 shell 管道**（JSON 截断风险，已沉淀到 seedance2.0-tool SKILL.md）。
