# Picturebook Video · Vision 流程标准（v1.0.0 · 2026-06-16 实战沉淀）

> **本文件是 picturebook-video SKILL.md 的"vision 流程专章"补充**——主 SKILL.md 只列原则，本文件给完整操作 SOP + 反模式 + 串行调用模板。

---

## 核心问题

**native vision 模式下，并行调用 vision_analyze 处理 4+ 张图会 evict 早调用的图**——agent 看到的"screenshot"标注图可能是 1-N 张中的随机子集，不是全部。这导致：
- agent 凭印象在 prompt 里写错角色对位（"白三角巾在大猫身上"——实际是"白肚兜在小猫身上"）
- 重复 vision 调用浪费 token + 时间（2026-06-16 I love you 绘本实测：9 张图重复调 3 轮才看清 6 张）

---

## 串行 ≤ 3 vision 范式（Step 2 必跑）

```python
# ✅ 标准范式（绘本 9 张图 / 3 张一组 / 串行调用）
all_images = ["1.jpg", "2.jpg", ..., "9.jpg"]
batch_size = 3

for i in range(0, len(all_images), batch_size):
    batch = all_images[i:i+batch_size]
    for img in batch:
        result = vision_analyze(img, question=...)
        # 验证 screenshot 标记
        if "screenshot removed" in result or "图片未加载" in result:
            # 单张重试
            retry_result = vision_analyze(img, question=...)
        # 写 image-inventory 时必含 7 维（风格/主体/背景/文字/动作/场景跳变/主体对位）
```

---

## Evict 触发条件（实测）

| 并行数 | 行为 |
|---|---|
| ≤ 3 张 | 通常都能看到 |
| 4-6 张 | **部分 evicted**（最后 2-3 张可能保留）|
| 7+ 张 | **大量 evicted** |

---

## 反模式（必避）

- ❌ 一次 vision_analyze 并行 9 张图 → 6 张 evicted → agent 凭印象推断
- ❌ 看到"screenshot removed"仍按视觉描述推断（"白三角巾在母猫身上"）
- ❌ 重试时还是批量并行（不解决 evict 根因）
- ❌ 跳过 vision 直接看简介写 prompt

---

## 用户纠正时的反思模式（2026-06-16 I love you 绘本实战）

- 用户纠正"3.jpg中的dad，没有'白三角巾'"
- → **立刻重看 3.jpg**（不省 token，vision 一次就够）
- → **承认之前的错误**（"我之前误读为'白三角巾'挂在'大猫'身上"）
- → **反思机制**：为什么看错？（图 evict + 凭印象推断 = 双重错）
- → **修复 image-inventory**（加"我之前误判"段落，避免下次 session 复用错信息）

---

## 跨 skill 适用

- ✅ 绘本视频（本场景）
- ✅ 漫剧分镜（多角色图 vision）
- ✅ AI 短剧（场景图 vision）
- ✅ 任何"多张图同时 vision"的场景

**判定口诀**：**"vision 并发 ≤ 3 / 串行验证 screenshot / 凡 evicted = 重试单张 / 凡凭印象 = 0 prompt"**
