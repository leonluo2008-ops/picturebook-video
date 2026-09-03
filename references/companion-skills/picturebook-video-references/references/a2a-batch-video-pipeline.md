# A2A 委托批量出片管线 — 实测沉淀（2026-08-31 舞蹈家批次）

> 配套 SKILL.md §23。场景：peer（A2A）下发指令式整批任务，素材包已解压到 `/tmp/pb_video2/`（8 张 1920x1200 横版 jpg + `舞蹈家.srt` + prompts/ + videos/）。上一批同规格沉淀在 `/tmp/pb_video/`（清洁工），**上一批目录是整套脚本模板的复用源**：submit.py / poll2.py / prompts/ / tasks.json / build_final.py(v1,已弃用) / asr_venv/。

## 0. 本批实测基准数据（复用作对齐）

| 项 | 值 |
|---|---|
| 渠道 | aigc.learningcat.cn，`ARK_BASE_URL=<base>/ark/v3/contents/generations/tasks`，`SEEDANCE_MODEL=doubao-seedance-2-0-fast-260128` |
| 3 变量加载 | 提交前从 `~/.hermes/skills/creative/picturebook-video/seedance_mcp/.env` 全量读入 os.environ（ARK_API_KEY / SEEDANCE_BASE_URL / SEEDANCE_MODEL），缺一即 assert |
| 提交 | 8/8 一次成功。uguu `files[]` 上传 → `build_body` content=[{type:text},{image_url, role:reference_image}]；逐项 assert body 无 resolution/service_tier/watermark、ratio=9:16、generate_audio=True、duration=int |
| clip 时长指派 | ceil(SRT 跨度)：4/4/4/4/5/4/5/5（合并句段5+6、段8+9、段10+11按跨度和）→ 原生实际 4.096×5、5.088×3 |
| 合成 | `ffmpeg -f concat -safe 0`，crf18 24fps，aac192k 48000，+faststart → 35.775s / 720x1280 |
| 复检 | freezedetect=n=0.003:d=1 零冻结；silencedetect -35dB 仅 1 处 1.82s 句间自然停顿（原生旁白节奏） |
| 画面抽检 | 逐 clip 抽中段帧（`ffmpeg -ss 2 -vframes 1`）vision 检查：大小写锁定/无第三行/无旁白词污染/满屏无黑边白边 8/8 通过 |

## 1. 重复批次事件与核对法（防重复计费）

本轮 tasks.json 最终 16 条：本会话 11:59:50-12:00:22 提交 8 个 task_id，另一来源于 12:00:56-12:01:27 又提交 8 个，网关查证两组全部 succeeded。疑似 peer 侧同一指令并行触发。

**核对代码（提交后必跑）**：

```python
# 1) tasks.json 条数 == 预期 clip 数（submit.py 是 append 制，不去重；error 条目无 task_id 需过滤）
entries = [t for t in json.load(open('tasks.json')) if 'task_id' in t]
assert len(entries) == EXPECTED_N, f'发现重复提交: {len(entries)} 条'

# 2) 未知 task_id 查网关真伪
from seedance_uploads import ark_request, ARK_BASE_URL
r = ark_request('GET', f'{ARK_BASE_URL}/{tid}')   # status: queued/running/succeeded/failed
```

**poll 换绑陷阱**：`status_map = {t['clip']: t for t in tasks}` 对重复 clip 号做 dict 后值覆盖 → 轮询按后一批 task 轮询并下载后一批产物。本批即如此（下载内容仍全部通过验证），回执须如实注明两组并列、实际采用的是哪组。

## 2. 合成 v2（现行标准）与 v1 事故对照

```bash
# v2: concat demuxer 原生直拼（8 clip 顺序 1→8，无 tpad/无截断/无转场/无 BGM）
printf "file 'videos/clip%d.mp4'\n" $(seq 1 8) > concat_list.txt
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -preset medium -crf 18 -r 24 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart final.mp4

# 验证
ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 final.mp4
ffmpeg -v error -i final.mp4 -vf "freezedetect=n=0.003:d=1" -f null -   # 无输出=无≥1s冻结
```

v1（`/tmp/pb_video/build_final.py`）= 按 SRT 边界 trim+tpad 补帧裁齐 → 2.08s freeze + 3.85s 死寂 + clip8 只剩 1s，被用户否决。**只留在历史里作反例，勿再用。**

## 3. 发音 ASR 自检（faster-whisper 遗留环境）

- openai-whisper 无；**`/tmp/pb_video/asr_venv/bin/python3` 有 faster-whisper**，small 模型已缓存在 `/tmp/pb_audio/models`（download_root 复用即零下载）。脚本头需 `os.environ['HF_ENDPOINT']='https://hf-mirror.com'`。
- 用法：逐 clip 直接 `model.transcribe(clipN.mp4, language='zh', beam_size=5)`，判定 dancer_ok = 文本含 {dancer, dance, danser, 丹瑟…} 任一；`Dancer/DANCER/Dancers` 大小写复数 = whisper 转写噪声不判失败；zh_ok = 「舞蹈」逐句在位。本批 8/8 通过。环境换了（/tmp 被清）就如实报"无法自检"，不要装作查过。

## 4. 回执要素清单（对 peer 汇报）

1. 渠道 + model + 提交方式（uguu files[] / build_body 直调，无 resolution/service_tier/watermark）
2. 成片：路径、字节数、总时长、720x1280、24fps、freezedetect/silencedetect 结论
3. 逐 clip 表：task_id、时长、大小；与"本会话提交的 8 个"严格一致（发现第二组即触发 SKILL.md §23.1 核对流程并如实并列上报）
4. 发音自检结论（ASR 或明确说明无法自检）
5. 画面抽检结论（大小写/无多余文字/满屏）
