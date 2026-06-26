# 案例 #38 · v5.0.13 默认音频翻车（generate_audio 默认值不一致）

> **触发**: 任何场景 v5.0.12 规则下默认音频行为不一致 = 领读型 false / 有声绘本 true = **容易选错导致视频无声或乱生成 AI 旁白**。

## 翻车场景

### Beet Pepper 翻车记录（2026-06-26 实测）

**Step 6 提交时**：
- 用户给了 SRT 文件 → 按 v5.0.12 规则判断为"领读型（外挂 TTS）" → 传 `generate_audio=false`
- 结果：4 个 Clip 全部下载成功，但都是**纯视频无音轨**
- 用户反馈："视频画面非常好，但是没有声音"

### v5.0.12 规则的根因问题

```
旧 v5.0.12 规则：
- 领读型绘本（外挂 TTS）= false
- 有声绘本（无外挂 TTS）= true

问题：
1. "领读型" vs "有声绘本" 在用户场景下分不清楚
2. 如果用户给了 SRT，但实际是"直接发视频"（不带 TTS 后期合成），就误判为 false
3. 默认值依赖 API 默认行为 = 不稳定
```

## v5.0.13 新规则修复

```
v5.0.13 路由规则：
- 路径 A（用户给了 SRT）= generate_audio=true + 段 5 写人声旁白+音效
- 路径 B（用户没给 SRT）= generate_audio=true + 段 5 只写音效
- 路径 C（spike 测试）= generate_audio=false
- 路径 D（用户明确说"不要声音"）= generate_audio=false

核心原则：
- 默认 generate_audio=true（除非用户明确反对）
- 通过段 5 内容（人声 vs 音效）区分路径 A/B
- 永远没有 BGM（硬约束 #1）
```

## 修复要点

1. **Step 6 提交时必须显式传 generate_audio**（不依赖默认值）
2. **路径判断基于用户输入**（有没有 SRT），不是基于"绘本类型"
3. **段 5 内容决定音频类型**：路径 A 写旁白+音效，路径 B 只写音效
4. **末尾约束永远包含"无背景音乐"**（硬约束 #1）

## 检测信号

- 视频下载成功但播放时无声音 → 99% 是 generate_audio 选错了
- 视频有 AI 自动生成的乱旁白 → 是 generate_audio=true 但没写段 5 音频描述

## 修复模板

```bash
# 错误：领读型默认 false
generate_audio=False  # ❌ 翻车

# 正确：有 SRT 路径 A
generate_audio=True   # ✅ 段 5 写人声旁白+音效

# 正确：无 SRT 路径 B
generate_audio=True   # ✅ 段 5 只写音效
```