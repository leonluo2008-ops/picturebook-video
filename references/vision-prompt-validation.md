---
name: vision-prompt-validation
description: vision 参考图 vs json 描述核对 — 写 prompt 前必跑的真实案例教训。json 描述可能跟图片实际内容不一致，必须 vision 实物核对 + 列"图有/图没有"清单。
license: Apache-2-2
metadata:
  hermes:
    tags: [vision, prompt-validation, json-vs-image, hallucination, 2026-06-14]
  related_skills: [picturebook-video, storyboard-design]
---

# vision 参考图 vs json 描述核对

> **核心教训**：**json 描述 ≠ 图片实际内容**。写 prompt 前必 vision 实物核对，**不能信 json**。

---

## 1. 真实翻车案例

### 案例 1 · clip5 字卡（参考图 7.jpg）

**json 描述**（之前子 agent 写）：
- "4 large colorful word cards 'duck', 'truck', 'luck', 'buck'"
- "4 word cards arranged in a row"
- "small yellow duck character at the bottom"  ← **错**
- "small duck waves gently at the bottom"     ← **错**

**vision 实际看到**：
- ❌ 不是 4 张小字卡 = 是 **2×2 排列的 4 个大方框**（每个方框含英文+中文+主题图）
- ❌ 不是 row 一排 = 是 2×2 网格
- ❌ **完全没有底部小鸭子**（json 凭空捏造）
- ✅ 有顶部"UCK Family"彩色标题
- ✅ 4 词：duck/鸭子+小鸭、truck/卡车+红车、luck/运气+四叶草、buck/鹿+鹿头

**第一版 prompt 凭空捏造**（跟真实图完全对不上）：
```
4 个彩色字卡"duck" "truck" "luck" "buck"在画面中央依次出现
底部小黄鸭对镜头轻轻挥手
```

**修复后 v2 prompt**（按真实图）：100% 对得上。

### 案例 2 · clip6 数鸭子（参考图 8.jpg）

**json 描述**：
- "3 yellow ducks (1 large + 2 small)"
- "play in water together"        ← **部分错**
- "all looking warmly at camera"  ← **部分错**

**vision 实际看到**：
- ✅ 3 只鸭子 = 1 大 2 小（json 对）
- ❌ 不是"play in water" = **1 大鸭坐大荷叶 + 2 小鸭坐荷叶 + 1 小鸭坐小荷叶**（4 只鸭子站姿）
- ❌ 不是"all looking warmly at camera" = 1 大鸭朝镜头 + 2 小鸭侧身朝左
- ✅ 背景：蓝色水面 + 绿色荷叶

**第一版 prompt 部分捏造**：
```
3 只黄鸭在水面上嬉戏
3 只鸭子一起抬头对镜头温暖地看
```

**修复后 v2 prompt**（按真实图）：100% 对得上。

---

## 2. 根因诊断

| 根因 | 说明 |
|---|---|
| **A · json 是子 agent 凭印象编的** | 之前步骤用 vision 跑过的图，json 描述可能不是最新（"4 word cards in a row"= 误读 2×2 网格）|
| **B · agent 写 prompt 时图没进视野** | 跳过了 vision 直接写 prompt = 凭 json + 印象 = 凭空捏造 |
| **C · json 字段名让人误以为"全"** | "feature_1/2/3" + "background" + "action" + "expression" 看完整 = 跳过 vision 的借口 |

**最危险的是 A + B 叠加**：json 看起来"完整" = 跳 vision = prompt 跟图对不上 = 翻车。

---

## 3. 防御性工作流（写 prompt 前必走 3 步）

### Step 1 · 打开图片（vision 必跑·必全）

**每个图**（不论 json 描述多"完整"）：
- 主体（数量/大小/姿态/朝向/动作）
- 背景
- 文字/小木牌/装饰元素
- 有没有拟声符号
- 有没有持续动作/已发生动作

**反模式**：json 字段看着全 = 跳过 vision = 翻车

### Step 2 · 列"图有/图没有"清单

写到 `image-inventory.md`，每图必含 6 列：

| # | 风格 | **有** | **没有**（警告·prompt 误写会翻车）| 文字 | 动作 |
|---|---|---|---|---|---|
| 7 | 2D/3D 纸艺 | 2×2 字卡网格 + 顶部标题 + 4 词含中文+主题图 | 小字卡、底部小鸭子挥手、4 词一排 | "UCK Family" + 4 词 + 4 中文 | 静态（字卡高亮） |
| 8 | 2D/3D 纸艺 | 1 大鸭坐大荷叶 + 2 小鸭坐荷叶 + 1 小鸭坐小荷叶 + 4 色顶部彩字 | 戏水、3 鸭齐对镜头、动态水花 | "duck/鸭子" | 静态（水波轻微） |

**判定**：
- prompt 里**每个**名词必须在"有"列
- "没有"列 = 警告 = 写 prompt 时**必**避免

### Step 3 · prompt 跟"有"列逐项对照

写完 prompt 后对照"有"列：
- prompt 里的"水面"→ 7.jpg 的"有"列里没水面 = **错**
- prompt 里的"小鸭子挥手"→ 7.jpg 的"有"列里没挥手 = **错**
- prompt 里的"对镜头看"→ 8.jpg 的"有"列里只 1 大鸭对镜头 = **部分错**

---

## 4. 跟 #11 铁律的关系

**#11 铁律原文**（已存在 picturebook-video/SKILL.md）：
> "**写 prompt 前 = 必先 vision 参考图**" + "**写前必 vision 全 N 张图 + 列"图里有/没有"清单**（写到 image-inventory.md）· prompt 里的每个名词必须在"有"列里"

**本 references 文档 = #11 铁律的真实案例支撑**：
- 2 个具体翻车实例
- json vs vision 的 3 类根因
- 写 prompt 前 3 步防御性工作流
- 升级了"image-inventory.md 6 列表格"的具体格式（之前是泛指"有/没有"= 不够具体）

---

## 5. 跨本验证

| 验证次序 | 来源 | 翻车点 |
|---|---|---|
| 第 1 次（绘本中段 clip 翻车）| clip5 v1 = 凭空捏造"4 字卡一排+底部小鸭"（实际 2×2 网格 + 无底部小鸭）| json 错 + 跳 vision |
| 同 session | clip6 v1 = "3 鸭齐对镜头"（实际 1 大对+2 小侧）| json 部分错 + 跳 vision |
| 累计 1 本绘本 2 案例 = 跨本验证 1 次 = 仍在本 reference 中 |

**3 次原则**：跨本验证 ≥ 3 次 = 升 SKILL.md 铁律 · 当前 1 次验证。

---

## 6. 速查

> **写 prompt 前必 vision 实物 + 列"图有/没有"清单 + prompt 逐项对照"有"列 = 避免凭空捏造。**

任何"json 看起来很全"的感觉 = 立刻 vision = 不要信 json。
