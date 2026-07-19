# SRT 旁白识别铁律 · v5.0.17+ 必读

> **场景**:用户从剪映/字幕软件导出 SRT,喂给 picturebook-video 做时间轴。
> **踩坑**:SRT 内部停顿 0.00s ≠ "两个独立段",而是 "同一句被错误拆段"。
> **优先级**:最高(覆盖 clip_merger.py 默认按 SRT 段数划分的行为)。
> **触发位置**:Step 1 接收 SRT 后,Step 3 跑 srt_parser.py 之前。

---

## 一、核心铁律(必读)

**SRT 段 ≠ narrative unit(叙事单元)。narrative unit = 完整的一句/一段旁白,可能跨多个 SRT 段。**

判定方法:

1. **内部停顿 ≤ 0.1s**(通常 pause_after = 0.00s 或 0.05s)= 同一句被剪映软件错误拆段 → 必须合并
2. **中文段 + 紧接着的英文段 + 停顿 0.00s** = 双语单元(领读型绘本标准写法)→ 必须合并
3. **多段合并后形成完整叙事弧**(主语+谓语+宾语完整)= 1 个 narrative unit → 必须合并

---

## 二、踩坑案例(《妈妈》绘本 · 2026-07-09 实测)

**SRT 原貌**(剪映导出 10 段):

```
段 5  [14.57-16.53] 妈妈的怀抱好温暖         ← pause_after 0.00s
段 6  [16.53-18.33] Mother keeps me warm!    ← pause_after 1.07s
段 8  [23.13-25.37] 妈妈,这朵花送给你        ← pause_after 0.00s
段 9  [25.37-27.23] A flower for Mother!     ← pause_after 0.90s
```

**错误划分**(主 agent 第一版):clip 划分 = SRT 段直接成组,段 5/6 拆给两个不同氛围的图(白天图 + 夜晚图),段 8/9 拆给送花动作 + 情感高潮收尾。

**用户原话纠正**:
> "你对srt文件的理解有问题,最重要是看时间轴和旁白,你难道没发现旁白是中英文混搭,不应该强拆吗?"

**正确做法**:

```
句 5 [14.57-18.33] 妈妈的怀抱好温暖,Mother keeps me warm!  ← 段5+6 合并,1 个 narrative unit
句 7 [23.13-27.23] 妈妈,这朵花送给你,A flower for Mother!  ← 段8+9 合并,1 个 narrative unit
```

**最终划分**:《妈妈》= 8 句 narrative unit(不是 SRT 的 10 段),3 个 clip / 总 32s(差 0s 完美对齐用户 TTS)。

---

## 三、3 步识别流程(Step 1 接收 SRT 后必走)

### Step 1.1 · 通读全部旁白原文(不看 SRT 时间戳)

先把所有 SRT 段的 text 字段合并成一个连续文本,按 "。" / "!" / "?" / 中文逗号断句,找出**完整叙事单元**。

### Step 1.2 · 标注 narrative unit 边界

每个 narrative unit = 完整的一句话(含中英文混搭),可能跨多个 SRT 段。

判定信号:
- SRT 段间 pause_after ≤ 0.1s → 同 unit
- 中文段 + 紧接英文段 → 同 unit(领读型标准结构)
- 完整主谓宾结构 + 时间逻辑闭环 → 1 个 unit

### Step 1.3 · 重写 timeline.json

按 narrative unit 重新划分 timeline,每 unit 给一个独立 idx,duration = 该 unit 内 SRT 段合并后的总时长(含段间停顿)。

**关键**:原始 SRT 文件不修改,timeline.json 是主 agent 的内部数据结构,可以重写。

---

## 四、与 clip_merger.py 的协作

`scripts/clip_merger.py` 默认按 SRT 段数划分 clip,**不识别 narrative unit**。

主 agent 必须在调用 clip_merger.py **之前**重写 timeline.json(按 narrative unit 重新分段)。

---

## 五、跟 v5.0.10 SRT 路径的关系

v5.0.10 SRT 路径 = "用户给 SRT 必走 SRT 解析路径",但 SRT 解析的产物 timeline.json 仍然受 SRT 段数限制。本文件补强:**SRT 段数 ≠ narrative unit 数**,主 agent 必须做 unit identification 这一步。

---

## 六、跟用户确认时机

**4 确认点 #1(clip 划分方案确认)必带 narrative unit 列表**:

```
妈妈绘本 · 8 句 narrative unit(合并 SRT 段 5+6 / 段 8+9)
```

不展示 narrative unit 列表 = 用户无法判断划分方案是否正确 = 容易踩坑。

---

## 七、SRT 拼写错误处理

剪映/字幕软件导出的 SRT 可能含拼写错误(如本次《妈妈》段 7"Goodnigh"少一个 t)。

**默认处理**:旁白照念原样,**不修改 SRT 文件**。如发现明显影响发音或语义错误的拼写,主 agent 应在 4 确认点中标注提示用户决定是否照念。

---

## 版本

v1.0 (2026-07-09 实测沉淀,来自《妈妈》绘本视频 4 确认点 #1 用户纠正)