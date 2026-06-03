# v7 范式自检脚本的 12 项实测版本

> 来源：2026-06-03 Ok 好的绘本视频 build_clips.py 实测沉淀。
> 用途：v7 prompt build script 的**真正能跑通**的 12 项自检（不是 11 项理论版）。

---

## 实测发现的 2 个 #0/#12 项（11 项理论版漏掉）

| # | 检查项 | 期望 | 踩坑案例 |
|---|--------|------|---------|
| **#0** | 段 1 引导句 `This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video` | ✅ **必含** | 漏掉 = 模型把 2 图当 1 段独立运镜处理，**时序窗全部失效**——因为模型认为只有"1 段"需要切换。|
| **#12** | final frame 段含 `motion` 字段（`holds to the last frame` 等价表达）| ✅ 必含 | build script 拼接 f-string 时易漏把 `motion` 加到 final frame 段——**11 项关键词自检会误判通过**，但 prompt 实际不完整。|

## 完整 12 项自检

```python
def real_check(prompt, duration):
    issues = []
    # #0: 段 1 引导句
    if "This is a storyboard reference image sequence" not in prompt:
        issues.append("#0 缺段 1 引导句")
    # #1: 分号串接
    if prompt.count(";") < 3:
        issues.append(f"#1 分号数 < 3（实为 {prompt.count(';')}）")
    # #2: 收势词
    if "holds to the last frame" not in prompt:
        issues.append("#2 缺收势词")
    # #3: 收势指令
    if "no fade, no dissolve" not in prompt:
        issues.append("#3 缺 'no fade, no dissolve' 收势指令")
    # #4: 无独立音效块
    if "[Sound effect:" in prompt:
        issues.append("#4 有独立音效块")
    # #5: 视觉段无否定句
    visual_part = prompt.split("Storyboard Audio")[0]
    for neg in ["No speech", "No narration", "No BGM", "No background music", "no human voice"]:
        if neg in visual_part:
            issues.append(f"#5 视觉段有否定句: {neg}")
    # #6: 时序窗
    if "0.0s to" not in prompt:
        issues.append("#6 缺时序窗")
    # #7: 多 shot
    if prompt.count("from") < 3:
        issues.append(f"#7 时序窗 < 3")
    # #8: @Image 引用
    if "@Image1" not in prompt or "@Image2" not in prompt:
        issues.append("#8 缺 @Image1/@Image2 引用")
    # #9: 音频段
    if "Storyboard Audio Description" not in prompt:
        issues.append("#9 缺 Storyboard Audio Description 段")
    # #10: No 禁令
    if "No background music" not in prompt:
        issues.append("#10 缺音频段 No 禁令")
    # #11: 风格锚点
    if "Children's picture book" not in prompt:
        issues.append("#11 缺风格锚点")
    # #12: final frame 段 motion 字段
    if "no motion" not in prompt and "holds steady" not in prompt:
        issues.append("#12 final frame 段缺 motion 字段")
    # duration 硬约束
    if not 4 <= duration <= 15:
        issues.append(f"#13 duration {duration}s 超出 4-15s")
    return issues
```

## 教训

1. **关键词存在性自检 ≠ 字段完整性自检**——`holds to the last frame` 是**收势词**（必含），但 **`motion` 字段**是另一回事（描述 shot 内部动作）。两者都在 final frame 段，但自检要把它们当**两个独立项**检查。
2. **段 1 引导句是 v7 范式区分 v3 的关键**——v3 是连续运镜散文（不需要段 1），v7 是分镜时序（**必须段 1 声明"我是分镜"**）。**漏段 1 = 退化成 v3**。
3. **数字缩写 `1.2s` 不应被算作句号**——用 `re.sub(r'\d+\.\d+s', '', prompt).count('.')` 排除。

## 实测通过样例

> 完整 build script 见 `references/build-v7-clips-script.md`（已沉淀）。

**4 个 Clip 跑通**（Ok 好的绘本 · 总时长 36s · 全部 12 项自检通过）：

| Clip | 时长 | 图 | 旁白 | 自检 |
|---|---|---|---|---|
| 1 | 8s | 1+2 | Ok. / Ok, Mom! | ✅ 12/12 |
| 2 | 9s | 3+4 | Ok, let's go! / Ok, I see. | ✅ 12/12 |
| 3 | 9s | 5+6 | Ok, let's eat! / Ok, let's play! | ✅ 12/12 |
| 4 | 10s | 7+8 | Ok, good night! / All is Ok! | ✅ 12/12 |
