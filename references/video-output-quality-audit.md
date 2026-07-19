# 视频成片质量审查 SOP（v1.0 · 2026-07-15 Bridge 桥绘本实测）

> Step 7 端到端验证的详细执行规范。当用户要求"审查成片质量"或主 agent 完成 Step 6 下载后自主验证时使用。

## 1. 审查 7 维度

| # | 维度 | 检查内容 | 适用 Clip |
|---|------|----------|-----------|
| 1 | **文字正确性** | bridge/BRIDGE 大小写是否与参考图对应；中文"桥"是否有乱码/错字；文字是否闪烁/变形/重拼 | 全部 |
| 2 | **风格一致性** | 全帧是否保持统一绘本风格（色彩/线条/笔触）；与参考图风格是否一致 | 全部 |
| 3 | **主体稳定性** | 桥/人物主体位置是否稳定；多图 Clip 中主体形象是否一致 | 全部 |
| 4 | **分镜序列执行** | prompt 设计的多镜头序列是否被正确执行（如人物退场→倒影→背影） | 含多镜头的 Clip |
| 5 | **肢体/人物** | 人物手臂数量/手指/腿部是否正常；有无多余人物 | 含人物的 Clip |
| 6 | **画面动态** | 水面涟漪/花草摇摆/云朵飘动/光影移动等是否可见；运镜（横移/推近）是否有效 | 全部 |
| 7 | **音轨确认** | ffprobe 确认有 audio stream（不虚构听写内容） | 全部 |

## 2. 执行步骤

### Step A · ffprobe 元数据

```bash
for clip in outputs/bridge_clip{1,2,3}.mp4; do
  ffprobe -v quiet -print_format json -show_streams -show_format "$clip" | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d['streams']:
    print(f\"codec={s.get('codec_name')} type={s.get('codec_type')} w={s.get('width')} h={s.get('height')} dur={s.get('duration')}s channels={s.get('channels')}\")
print(f\"format_duration={d['format'].get('duration')}s\")
"
done
```

检查项：分辨率（期望 1280x720）、时长（与 clip 分配时长 ±1s）、有 video stream + audio stream。

### Step B · ffmpeg 逐秒抽帧

```bash
mkdir -p frames/extra
# 每个 clip 按秒抽帧（duration=N → N 帧）
for i in $(seq 0 $((DURATION-1))); do
  ffmpeg -y -i "outputs/bridge_clip${CLIP}.mp4" -ss "${i}" -frames:v 1 "frames/extra/clip${CLIP}_t$((i+1)).jpg" 2>/dev/null
done
```

### Step C · SRT 文件检查

确认中文文本无乱码、英文 bridge/BRIDGE 拼写正确。

### Step D · 逐 Clip Vision 检查（vision_analyze）

对每个 Clip 的关键帧用 vision_analyze 检查：

**每个 Clip 至少检查 3 帧**（首帧、中帧、末帧）。含多镜头序列的 Clip（如 Clip3 的退场→倒影→背影）**必须每秒检查 1 帧**，确认序列过渡。

Vision prompt 模板（按维度定制）：
- **文字检查**：「画面顶部文字是红色大写BRIDGE还是小写bridge？中文"桥"字正确吗？有无乱码/拼写错误/文字变形？」
- **序列检查**（多镜头 Clip）：「按照分镜设计，这里应该是[X段]。请检查：画面是[预期内容]吗？」
- **肢体检查**：「女孩手臂数量是否正常？手指？腿？有无多余人物？」
- **动态检查**：「水面是否有涟漪/波纹？花草是否摆动？」

### Step E · 参考图对比

用 vision_analyze 逐一检查参考图，确认文字内容/主体特征，然后与视频帧对比一致性。

## 3. 输出格式（严格 JSON）

```json
{
  "passed": false,
  "per_clip": {
    "clip1": {
      "file": "bridge_clip1.mp4",
      "duration": "6.08s",
      "resolution": "1280x720",
      "has_audio": true,
      "text_check": { "passed": true, "details": "..." },
      "style_stability": { "passed": true, "details": "..." },
      "subject_stability": { "passed": true, "details": "..." },
      "dynamic_check": { "passed": true, "details": "..." },
      "limb_check": { "passed": true, "details": "..." }
    }
  },
  "violations": [],
  "warnings": [
    { "id": "W1", "clip": "clip1", "severity": "low", "description": "...", "evidence": "..." }
  ],
  "evidence": {
    "videos_checked": [...],
    "frames_inspected": { "clip1": [...], "clip2": [...], "clip3": [...] },
    "reference_images_checked": [...],
    "srt_content_verified": "..."
  }
}
```

## 4. 关键判定规则

- **passed = false 当且仅当 violations 数组非空**。warnings 不影响 passed 但必须列出。
- **Violation（FAIL 级）**：文字乱码/拼写错误、肢体异常（多臂/少臂）、多余人物、分镜序列未执行、风格跳变
- **Warning（WARN 级）**：运镜效果偏弱、过渡偏缓、动态不够明显（但不影响可用性）
- **音轨**：确认有 audio stream 存在即可，**绝不虚构听写内容**——不猜测旁白说了什么

## 5. Clip3 多镜头序列验证（特殊场景）

当 Clip 包含人物退场→倒影→背影等跨图序列时，**必须逐秒抽帧验证**：

| 时间段 | 预期画面 | 验证方法 |
|--------|----------|----------|
| 前段（如 t1-t4） | 人物在桥上（正面/侧面） | vision 确认人物存在、外貌一致 |
| 中段（如 t5-t7） | 无人物，桥与水面倒影 | vision 确认无人 + 倒影可见 + 涟漪动态 |
| 后段（如 t8-t12） | 人物背影，双手扶栏 | vision 确认背对镜头 + 肢体正常 + 双手位置 |

## 6. 效率优化

- **Contact sheet 先行**：先用 `scripts/contact_sheet.py` 生成总览图，vision 一次扫描全局
- **批量 vision**：独立的检查项可以并行调用 vision_analyze
- **按需深入**：contact sheet 发现异常时才逐秒抽帧深入
