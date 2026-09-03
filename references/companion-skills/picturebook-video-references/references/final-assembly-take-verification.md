# §25.10 实测底稿 — 工程师批 peer 收尾三件（2026-08-31）

> 主题：peer 收尾断言「final 晚于所有 clip mtime → 应已含全部重生成版；ASR/物理复查记录在 → 全过没？md5 若 differ 以新为准」——三段推理实测逐条翻车。此文件是 SKILL.md §25.10 的证据底稿；回执类验收规则以 SKILL.md 为准。

## 1. 现场（/tmp/pb_video5 工程师批）

| 时间 | 事件 |
|---|---|
| 19:47 | asr_results_final.json（7 clip 全量 ASR，clip1 zh_ok=false） |
| 19:48 | physcheck_results.txt（含 r2clip*/c8v2* 复查帧） |
| 20:29 | clip2 v3 落盘（videos_v3/clip2_v3.mp4 1.63MB） |
| 20:31 | final_engineer.mp4 重拼（11.59MB）+ uguu 上传 ×2 |
| 20:36 | clip2 v4 落盘（videos_v4/clip2_v4.mp4 1.51MB） |
| 20:38 | asr_c2v4.json（clip2 v4 复测 ok）+ check_c2v4/ 帧目录 |
| 20:40± | peer 收尾三件指令；final_engineer.mp4 被复制到 /tmp/ 根 |

## 2. 三段断言 vs 实测

| peer 断言 | 实测 | 结论 |
|---|---|---|
| 20:31 晚于 clip2 20:29 → 含 clip2 重生成版 | PIL 滑动对齐：final∩round1/clip2（旧版）差 **10.4**，∩v3 39.3，∩v4 34.2 → 装的是**旧** clip2 | ❌ 假 |
| ASR/物理记录在案 → 全过没？ | 记录 mtime 19:47/48 早于 clip2 v4(20:36)/clip8_v2(20:29)；clip2 有 20:33/20:38 复测件可采信；**clip8_v2 无任何帧检记录**；physcheck 内还有「c8v2 末帧阴影消失」「r2clip8_mid 屈膝腾空」未平掉项 | ⚠ 混杂：过时记录 + 未验 clip + 存疑项 |
| md5 cd89ecf9…→ differ 以新为准 | 20:31 版 real md5 = `90ccb0640bcc2a9f42be661d841c33eb`（cd89ecf9 全盘不存在）；但「新」里装的还是旧 clip2 | ❌「新」≠「对」 |

## 3. ASR 细节（供层面归因）

- clip1：beam5/beam8 双束均「工程程师Engineer」，zh_ok=false —— 中文滑音/吞字（音频层，同 dancer→dentist 族判例）。r2clip1 帧检「半身、无叠影」只排除画面重影，不排除音频问题。
- clip2 v3：「我看见工程师了!Engineer」；v4：「我看见工程师了,Engineer。」—— eng/zh 双 ok，仅标点漂移（v3!→v4,，非验收项）。
- clips 2-7：eng_ok+zh_ok 全 true。

## 4. uguu hash 字段反证

uguu resp: `{"hash": "170f1c63e52d78e6", size: 11587197}`。对该字节实测：md5=90ccb0…、sha256 前16=36d3bde6…、crc32=3ab42927、md5(前1MB)=5b253b… —— **无一匹配** → hash 是站内存储键，非任何标准文件哈希，验收直接忽略该字段。

## 5. 滑动对齐法完整参数（可复跑）

- 源 clip 时长用 ffprobe 单文件查询（ffmpeg 多输入一炉报 'already specified'）；clip2 旧/v3/v4 均 4.096s。
- 参考帧：候选 clip 自身时间线 t=0.5/1.5/2.5/3.5s 各抽 1 帧；final 在 t0∈[4.4, 5.5] s 以 0.1s 步进滑窗，每 t0 对 4 个偏移抽同偏移帧。
- 距离：PIL ImageChops.difference 灰度图，`sum(hist[i]*i)/(w*h)` 平均差（环境无 numpy 的 fallback）。
- 结果：old2 best=10.4@t0=4.4s；v3=39.3@4.4；v4=34.2@4.5 → 同版判据 ≈10，异版 30+；顺带定位 clip2 起点 ≈4.4s。
- 坑：-ss 超出源时长时 ffmpeg rc=0 但**不产出文件**——先查时长再定窗；参考帧/比对帧同调用内完成（/tmp 写入跨调用不持久）。

## 6. 本地 ops 旁注（本 agent 执行环境）

- 终端单引号 heredoc（`python3 <<'EOF'`）被 gateway 误拦（SyntaxError/EOF 泄漏）→ 复合脚本先 write_file 落盘再 `python3 file.py`。
- 本 agent 进程写 /tmp 的中间产物（抽帧 png、脚本）实测即写即不可见；读他人 /tmp 工作区正常。跨调用复用的中间件一律落 /home/ubuntu/。
- ffprobe 多文件一炉：for 循环逐个查，不能一次传多个路径。
