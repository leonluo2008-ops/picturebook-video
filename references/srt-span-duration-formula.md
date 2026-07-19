# SRT 跨度对齐公式（硬约束 #10 · v5.0.19+）

> **来源**：2026-07-11 Morning 早上绘本实测 · 用户原话「35秒肯定有问题，这就是没有跟SRT文件对齐。你是不是有病啊？」

## 1. 核心公式（必走）

```
clip_SRT_span = sum(每段.speech_duration) + sum(每段.pause_after) - last_segment.pause_after
clip_suggested_duration = ceil(clip_SRT_span) → 取整到 [4, 15] 整数
total_actual = sum(clip_suggested_duration) → 必须 vs user_tts 差 ≤ 5s
```

**关键点**：
- `speech_duration` = 段内朗读时长（来自 `timeline.json`）
- `pause_after` = 段间停顿（来自 `timeline.json`，注意是段后停顿不是段前）
- **末段的 pause_after 不计入**（因为后面没段了）
- 然后向上取整到 [4, 15] 区间内的整数

## 2. 反例对照（2026-07-11 Morning 早上绘本实测）

### ❌ 错误做法：只算朗读累加

```
段 1-4：朗读 10.53s → 取整 14s（漏停顿 2.96s）
段 5-7：朗读 7.39s → 取整 14s（漏停顿 2.24s）⚠️ 实际 SRT 跨度 9.63s
段 8-9：朗读 5.66s → 取整 7s（漏停顿 0.70s）

总取整：14+14+7 = 35s
用户 TTS：30s
差：5s（v5.0.10 容差 1.0s 边界外）
→ 用户原话：35秒肯定有问题
```

### ✅ 正确做法：用 SRT 跨度

```
段 1-4：朗读 10.53s + 段间停顿 2.96s = 13.49s → 取整 14s
段 5-7：朗读 7.39s + 段间停顿 2.24s = 9.63s → 取整 10s
段 8-9：朗读 5.66s + 段间停顿 0.70s = 6.36s → 取整 7s

总取整：14+10+7 = 31s
用户 TTS：30s
差：1s（v5.0.10 容差 1.0s 边界 ✅）
```

## 3. 必走工具

**直接跑 `clip_merger.py`** 而不是手工算：

```bash
python3 scripts/clip_merger.py timeline.json --user-tts 30 --align-tolerance 1.0
```

clip_merger.py 内部已经正确实现 SRT 跨度公式（v5.0.19 强化过）。

### ⚠️ 已知 v5.0.19 BUG · 2026-07-13 Rose 玫瑰绘本实测

`scripts/clip_merger.py` 的 `srt_span` 实现与本文档 §1 核心公式**不一致**：

| 来源 | 末段 `pause_after` 处理 |
|---|---|
| 本文档 §1 核心公式（参考依据） | **不计入**（末段后面没段了，静默无意义） |
| `scripts/clip_merger.py` 当前实现 | **计入**（`srt_span = end + tail_pause - start`，见脚本 line 75） |

**实测数据**（Rose 玫瑰绘本，SRT 总跨度 28.333s）：

| 算法 | Clip 1 | Clip 2 | 总 | vs user_tts |
|---|---|---|---|---|
| `clip_merger.py` 直接输出 | 15s | 15s | **30s** | **+1.667s → OUT** |
| 本文档 §1 公式手工算 | 14s | 15s | **29s** | +0.667s → ✅ |

**当前推荐做法**（脚本未修前）：

1. 跑 `clip_merger.py` 获取初步 clip **边界划分**（边界逻辑正确）
2. **手工校核每个 clip 的 `srt_span`**：`sum(speech_duration) + sum(internal_pause_after)`（**不含**末段 pause_after）
3. 如发现 `clip_merger.py` 输出总时长 **OUT of tolerance**，按公式手工修正 `suggested_duration`（ceil 到 [4,15]）
4. 在 4 确认点 #1 输出**手工修正后**的方案，标注"修正原因：clip_merger.py v5.0.19 末段停顿计入 BUG"
5. 报告用户，等待是否授权修脚本（user profile 严禁自作主张改脚本）

**未来修复方向**（需用户明确授权）：

- 把 `srt_span = end + tail_pause - start` 改为 `srt_span = end - start`
- 跑双向测试（旧 prompt FAIL + 新 prompt PASS）
- 同步更新本文档 §1 + §5

**手工算 = 必出错**，因为手工累加时容易只 sum `speech_duration` 漏掉 `pause_after`。

## 4. 校验清单（Step 4 后必走）

- [ ] 跑 clip_merger.py 获取 `clips.json`
- [ ] 校验 `actual_clips_total` vs `user_tts` 差 ≤ 1s（v5.0.10 精确模式）
- [ ] 如果差 > 5s 必停下汇报用户，不能提交 Step 6
- [ ] 差 1-5s 内 v5.0.9 容差合规，但必须在 4 确认点 #1 标出总时长偏差

## 5. 反模式总结

| 反模式 | 后果 | 修复 |
|---|---|---|
| 只算朗读累加 = 漏停顿 | 总时长偏离用户 TTS 5s+ | 用 SRT 跨度公式 = 朗读 + 段间停顿 |
| 手工累加（不用 clip_merger.py） | 必漏停顿 | 必跑脚本 |
| 跳过 pause_after = 0 的段 | 双语停顿丢失 | 即便是 0 也要算 |
| 末段 pause_after 计入 | 多算 0.7-1s | 末段 pause_after 不计入 |

## 6. 完整 timeline.json 示例（2026-07-11 Morning）

```json
{
  "segments": [
    {"idx": 1, "duration": 1.93, "pause_after": 0.90, ...},
    {"idx": 2, "duration": 3.30, "pause_after": 0.70, ...},
    {"idx": 3, "duration": 2.67, "pause_after": 0.73, ...},
    {"idx": 4, "duration": 2.63, "pause_after": 0.63, ...},
    {"idx": 5, "duration": 2.63, "pause_after": 0.70, ...},
    {"idx": 6, "duration": 2.33, "pause_after": 0.77, ...},
    {"idx": 7, "duration": 2.43, "pause_after": 0.77, ...},
    {"idx": 8, "duration": 2.83, "pause_after": 0.70, ...},
    {"idx": 9, "duration": 2.83, "pause_after": 0.00, ...}
  ]
}
```

**3 clip SRT 跨度**：
- Clip 1 = 段 1-4：1.93+3.30+2.67+2.63 = 10.53（朗读）+ 0.90+0.70+0.73+0.63 = 2.96（停顿，不含末段 pause_after）= **13.49s → 取整 14s**
- Clip 2 = 段 5-7：2.63+2.33+2.43 = 7.39（朗读）+ 0.70+0.77+0.77 = 2.24（停顿）= **9.63s → 取整 10s**
- Clip 3 = 段 8-9：2.83+2.83 = 5.66（朗读）+ 0.70（停顿，末段 0.00 不计）= **6.36s → 取整 7s**

总 = 14+10+7 = **31s** ✅