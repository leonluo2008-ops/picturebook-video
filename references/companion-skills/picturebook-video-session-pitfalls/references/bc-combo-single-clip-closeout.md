# §53 B+C 组合拳收口（2026-08-31 工程师 clip1 实测 · 单clip全链闭环）

## 触发
单 clip 内置 TTS 反复读坏核心词（v6「Engineerette/Engineered」→ v7 措辞加码后变成更怪的「N.G. Nier」）。**教训：加强措辞≠根治，ASR strict 双 FAIL 后直接上 B+C，不要第 4 版同路径烧钱。**

## 协议
- **B 视觉修复**（prompt vN+1）：标题写死「完整落右半区+边缘留安全边距+禁止贴边出血」+ 半身锁×3 + 负约束（跳跃/悬空/腾空）。
- **C 音频兜底**：
  1. **TTS 预产预验**（不等画面）：直调 `uv run --with edge-tts edge-tts --voice zh-CN-XiaoxiaoNeural --text "核心词中文！English！" --write-media x.mp3`。
     - ⚠️ Hermes 的 text_to_speech 工具不可用：config 的 edge provider 锁 en-US-AriaNeural（读不了中文）；中英混合输入会静默丢中文段。还会吐 **stale cache：不同输入返回同一音频文件**——换 provider 前先 ffprobe 时长有没有变。
  2. 验收两道：silencedetect 确认两段语音都有能量 + faster-whisper 双 beam ASR「中文核心词+英文核心词」双过。
  3. **Seedance 无声画面**：正常 B 版 prompt 提交（generate_audio true 也没关系，音轨整个替换）。
  4. **合成**：从被否决旧 take 抽非语音元素（如「叮」`-ss 0 -t 0.166`）→ `amix(ding@0s + tts@0.65s, normalize=0)` → volume 调到**语音窗 RMS 对齐**其他 clip（窗内 -16.6 vs 基准 -16.6，全轨 RMS 会因静音占比虚低，不能用它对齐）→ `apad whole_dur` 补齐 4.096s 与同批一致 → `-c:v copy` 不重编视频。
  5. PASS 票绑合成 take md5；成片=concat filter 重拼清单换该 clip；成片本体再跑分句 ASR + 帧检。

## 实测数据（clip1 · /tmp/pb_video5）
- v7 画面：半身✅ ENGINEER 全程完整未裁✅（中文行 ~3s 入场，全帧+带内双重 vision 确认）；内置 TTS ASR =「N.G. Nier」FAIL。
- 合成音轨 ASR：「工程师 & Engineer」双 beam strict PASS。
- 成片 v7：md5 dd66106edf81fd0a57d5977bf790b2e3 / 11,654,150B / 39.712s / 0 冻结 / uguu d.uguu.se/uHgAauXR.mp4 回读一致。
