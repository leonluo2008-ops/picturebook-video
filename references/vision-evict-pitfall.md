# vision_analyze 并行 Evict 翻车 + 视觉证据误读陷阱（2026-06-16 绘本"I love you 我爱你"实战沉淀）

> **核心命题**：vision_analyze 在 native vision 模式下**并行调用多张图时，早调用的图会被后调用的图 evict（覆盖）**——agent 看到的"screenshot"标注图可能是 1-N 张中的随机子集，**不是全部**。这导致 agent 凭"印象"在 prompt 里写错角色对位 = 凭空捏造 = 翻车。

---

## 一、翻车现场（2026-06-16 I love you 我爱你绘本）

### 翻车症状

- 收到 9 张绘本图 → 一次 vision_analyze 并行调用 9 张图 → **实际看到 3 张 + 6 张"screenshot removed"**（evicted）
- agent 凭印象报告："2=Dad, 3=Mom（白三角巾）"
- 用户纠正："3.jpg中的dad，没有'白三角巾'"
- 重新看 3.jpg 实际是：**趴着大橘猫（身上黑条纹·无装饰）+ 小猫戴白肚兜骑在背上**

### 实际根因（2 层）

| 根因层 | 描述 | 修复 |
|---|---|---|
| **L1 · vision evict** | native vision 模型在一次上下文窗口里只能容纳有限张图，后调用的覆盖早调用的 | **串行 vision + 每张图独立调用 + 验证 screenshot 标记** |
| **L2 · agent 凭印象判断** | agent 看到"screenshot removed"时仍按视觉描述推断，编造没看到的细节 | **凡未真正看到图的视觉特征 = 必须标"未 vision" + 不准在 prompt 写** |

---

## 二、Evict 触发条件（实测）

| 触发 | 行为 |
|---|---|
| 一次 vision_analyze 并行 ≤ 3 张图 | 通常都能看到（context 够）|
| 一次 vision_analyze 并行 4-6 张图 | **部分 evicted**（最后 2-3 张可能保留）|
| 一次 vision_analyze 并行 7+ 张图 | **大量 evicted**（只能看到最后几张）|

**反模式**：9 张图一次并行调用 = 6 张 evicted = 翻车

---

## 三、修复范式（Step 2 vision 必跑 · 4 步走）

```
Step 2.1 · 串行 vision（每次 ≤ 3 张图）
   ↓
Step 2.2 · 验证 screenshot 标记（每张图都返回"screenshot"才算看到）
   ↓
Step 2.3 · 失败重试单张（不批量重试，浪费 token）
   ↓
Step 2.4 · 凡"screenshot removed" 或 未 vision = 标"未 vision" + 不写进 prompt
```

### 实操命令（绘本 9 张图标准流程）

```python
# ❌ 反模式（9 张图一次并行 = evict 翻车）
for i in range(1, 10):
    vision_analyze(f"{i}.jpg", question=...)
    # 一次性 9 个 tool_calls 并发 → 后调 evict 早调

# ✅ 正确范式（3 张一组 + 串行验证）
for batch in [(1,2,3), (4,5,6), (7,8,9)]:
    for img_id in batch:
        result = vision_analyze(f"{img_id}.jpg", question=...)
        # 验证：result 含 "screenshot" 字符串 = 看到
        # 验证：result 含 "screenshot removed" 或 "图片未加载" = evict → 重试单张
    # 批次内串行（不并行）= 避免 evict
```

---

## 四、用户纠正时的反思模式（2026-06-16 实战沉淀）

### 反模式（agent 凭印象判断）

- ❌ "我看到 3.jpg 大猫戴白三角巾" → 实际是 **小猫** 戴白肚兜，**大猫无装饰**
- ❌ "白三角巾 = 围嘴 = 母猫哺乳" → 推断错误：白肚兜不是大猫的围嘴，是小猫的肚兜（小孩/小辈特征）
- ❌ 把"室内米黄墙红领结" = Dad / "户外蓝天白三角巾" = Mom → 视觉推断与 readme 文字冲突时没看清图就猜

### 正确范式（用户纠正 → 重看验证 → 报告修正）

- ✅ 用户纠正视觉识别错误 → **立刻重看那张图**（不要省 token，vision 一次就够）
- ✅ **重看结果 + 用户纠正的描述** → 双重验证 → 写修正后报告
- ✅ **承认之前的错误**（"我之前误读为'白三角巾'挂在'大猫'身上"）→ 不辩护，不解释
- ✅ **反思机制**：为什么之前看错？（答：图 evict + 凭印象推断 = 双重错）

---

## 五、Step 2 必跑自检清单（强化版）

写 image-inventory 前必跑：

```markdown
## Step 2 自检清单

- [ ] 9 张图 = vision 9 次？或 ≤ 3 张/批 + 串行？
- [ ] 每张图返回都含 "screenshot" 标记（不是 "screenshot removed"）？
- [ ] 凡 "screenshot removed" 或缺失 = 立即重试单张？
- [ ] 重试单张后还是 evicted = 标 "vision 失败" + 兜底描述 + 不写进 prompt？
- [ ] 每张图的"有/没有"清单都明确写出（不能只写"有"列）？
- [ ] 凡 "有" 列元素都被某镜头引用（0 浪费）？
- [ ] 凡凭印象推断的元素（没真正看到的）= 标"未验证" + 不写进 prompt？
```

---

## 六、对 SKILL.md 的关联

- **铁律 #2 vision 必全 N 张图** → 强化为**串行 ≤ 3 张/批 + 验证 screenshot 标记**
- **铁律 #3 写 prompt 前 = 必先 vision** → 强化为**未 vision 的图 = 0 prompt 元素**（不能凭印象）
- **决策树 Step 2 应变** → 新增"vision evict 部分失败"场景

---

## 七、跨 skill 适用

- ✅ 绘本视频（本场景）
- ✅ 漫剧分镜（多角色图 vision）
- ✅ AI 短剧（场景图 vision）
- ✅ 任何"多张图同时 vision"的场景

**判定口诀**：**"vision 并发 ≤ 3 / 串行验证 screenshot / 凡 evicted = 重试单张 / 凡凭印象 = 0 prompt"**
