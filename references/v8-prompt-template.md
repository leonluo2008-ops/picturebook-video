---
name: v8-prompt-template
description: v8 写法核心 prompt 模板 — 1 镜 1 核心动作 + 1 组情绪外化 + 1 运镜 + 方向锚点 + 故事弧 4 步。基于 2026-06-16 Run 跑绘本 8 轮迭代验证，是当前唯一标准的 prompt 写法。
license: Apache-2-2
metadata:
  hermes:
    tags: [v8, prompt-template, anti-pattern, story-arc, 2026-06-16]
  related_skills: [picturebook-video, seedance2.0-tool]
---

# v8 写法核心 prompt 模板

> **唯一标准**（2026-06-16 Run 跑 v8 验证）= 替代 v6/v7/v15 各种 4 段骨架范式
> **3 类反模式 RP-26a/b/c** = 必避
> **方向锚点** = 必带空间目标
> **故事弧 4 步** = 出现 → 转折 → 高潮 → 收尾

---

## 1. v8 4 段骨架（替代 v15/v6/v7）

```
[主体定义 · 1 核心动作 · 1 组情绪外化 · 1 运镜 + 方向锚点]
+ Critical constraints（末段）= 简洁 1 句不堆砌
```

| 段 | 必含 | 必避 |
|---|---|---|
| **1 主体** | 风格 + 主体外观 + 朝向 + 景别 | 不加情绪词修饰主体 |
| **2 动作** | 1 个核心动作 + **方向锚点** | 不用"原地动词" |
| **3 情绪** | 1 组具体身体动作（**不是 1 个情绪词**）| 不用"欢快地/笑着"修饰词 |
| **4 运镜** | 镜头方向 + 主体位移方向 | 不写"定格/微动/末帧"约束 |
| **末段约束** | 简洁 1 句（无主语、无情绪、无修饰） | 不用 4 句堆砌 |

---

## 2. 3 类反模式（RP-26a/b/c · 必避）

### RP-26a 原地动词陷阱

| 反模式 | 正模式 |
|---|---|
| "小狗在花丛里欢快地小跑" | "小狗从画面左侧跑向右侧" |
| "小狗越来越快地飞奔" | "小狗跑出画面" |
| "小狗在雨中笑着跑过草地" | "小狗跑过草地后离开镜头" |

**关键要素**：每个动词都必须带**空间目标**（向 X / 出画面 / 离开镜头 / 追 Y）。

### RP-26b 情绪修饰词陷阱

| 反模式 | 正模式 |
|---|---|
| "欢快地" | "耳朵竖起，尾巴翘起" |
| "笑着" | "嘴角上扬（仅当参考图有表情时）" |
| "脚步轻快" | "腿抬得更高，落地更轻" |

**关键要素**：用 **1 组身体动作** 表达情绪，**不用 1 个情绪词**。

### RP-26c 故事弧缺失

| 反模式 | 正模式 |
|---|---|
| 3 镜头同方向动作 = 节奏平 | 出现 → 转折 → 高潮 → 收尾 |
| 3 个"快"动作 | 好奇 → 加速 → 跑远 → 消失 |

**关键要素**：4 步固定结构（**多镜头必走**）。

---

## 3. 方向锚点规范

### 3 类空间目标（必带 1 个）

| 类别 | 写法示例 |
|---|---|
| **画面内方向** | "toward the right edge of the frame" / "across the meadow from left to right" |
| **出画面** | "exits the frame on the right" / "runs off-screen" |
| **镜头位移** | "camera follows from behind" / "low-angle tracking shot from the side" |

### 反模式（不带方向）

```
❌ "小狗在小跑"（原地）
❌ "小狗在加速"（原地加速）
❌ "小狗在笑"（原地表情）
❌ "小狗跑过"（一过性 = 不动）
```

---

## 4. 故事弧 4 步（多镜头必走）

```
镜头 1（出现 · 开胃）：
  - 主体初次出现，姿态相对静止
  - 1 句简单动作（耳朵动 / 尾巴动 / 眼睛看）
  - 运镜 = 广角建立

镜头 2（转折 · 短句 / 中句）：
  - 主体开始移动
  - 1 句核心动作 + 1 个方向锚点
  - 运镜 = 跟拍 / 中景

镜头 3（高潮 · 中句 / 长句）：
  - 主体移动加速
  - 1 句多动作（仍带方向）+ 1 组情绪外化
  - 运镜 = 加速跟拍 / 低角度

镜头 4（收尾 · 短句）：
  - 主体出画面 / 停下 / 完成动作
  - 1 句最终状态
  - 运镜 = 拉远 / 静止
```

**3 镜头版本** = 出现 + 转折 + 高潮（省略收尾 = 由旁白/TTS 决定）。

---

## 5. 末段约束规范（v15 模板默认段 4 = 反模式）

### 反模式（v15 模板默认段 4）

```
❌ 末帧微动:[主体]定格在[姿态]瞬间
❌ 1s 内至少 1 个动作元素([清单])
❌ 末帧定格前持续微动不得成为定格海报
❌ （隐含"必须微动"反暗示）
```

**根因**：4 句冗余 + 隐含"定格"反暗示 = 模型把"必须定格"当字面执行 = 画面静止。

### 正模式（v8 简洁收尾）

```
✅ "镜头持续[核心动作]循环不切断不冻结"
✅ "画面自然流动有运动感"
```

**判定口诀**：
- 写完 prompt 必 grep 末帧段落冗余 = 0 处
- `grep -E "末帧定格|末帧微动|不得成为定格海报|1s 内至少 1 个动作元素|定格在.*瞬间" clip*-prompt.txt` 期望 0 命中

---

## 6. 完整 v8 prompt 范本（Run 跑 Clip 1 实测）

```
[Originami paper-collage picturebook style. Soft warm pastel palette, hand-folded paper textures with subtle creases and layered paper grain throughout. A small origami dog with a soft, friendly face made of folded paper triangles stands on a patch of green paper grass dotted with bright paper flowers, ears perking up alertly at the sound of a call. --- Action: the dog bursts into a trot, body leaning forward with momentum, legs lifting in quick paper-folded strides, moving toward the right edge of the frame and accelerating; then continuing faster through falling paper rain, colorful folded raindrops streaking past, paws splashing into small puddles on the path, body moving off-frame to the right with tail streaming behind in the wind. --- Mood expressed through motion: alert attention → eager forward momentum → joyful rush into the rain, conveyed entirely through body posture, leg movement, tail position, and direction of travel. --- Camera: starts with a gentle wide establishing shot holding steady on the dog in the center, then transitions to a medium tracking shot following from the side as the dog runs left to right with paper flowers blurring in the foreground, then shifts to a low-angle medium shot from behind as the dog runs away into the rain and exits the frame on the right.

Critical constraints: NO static loop, NO frozen pose at the end, NO last-frame hold. The dog must have continuous spatial displacement across the frame from start to finish — never stopping in place. Camera and subject both in motion throughout.

No human voice, no singing, no narration, no background music, no on-screen text.]
```

---

## 7. 跟铁律的对应关系

| 铁律 | v8 写法对应 |
|---|---|
| #26 参考图驱动 | 段 1 主体 = 严格按参考图 5 项（位置/朝向/景别/姿态/招牌）|
| #27 反凑数 | 末段约束 = 1 句简洁，**不**堆砌 |
| #M1 整本节奏 | 故事弧 4 步 = 出现/转折/高潮/收尾 |
| #M3 旁白-镜头映射 | 1 段 prompt = 1 镜 = 1 段旁白 = 1 句 TTS |

---

## 8. 自检命令

```bash
# 检查 1: 方向锚点
grep -E "toward|exits|off-screen|left to right|from the side|from behind" clip*-prompt.txt
# 期望 ≥ 1 命中 / 镜头

# 检查 2: 末帧段落冗余（必为 0）
grep -E "末帧定格|末帧微动|不得成为定格海报|1s 内至少 1 个动作元素|定格在.*瞬间" clip*-prompt.txt
# 期望 0 命中

# 检查 3: 情绪词（必为 0 = 情绪必须用具象动作表达）
grep -E "欢快地|笑着|轻快地|兴奋地|开心地" clip*-prompt.txt
# 期望 0 命中
```
