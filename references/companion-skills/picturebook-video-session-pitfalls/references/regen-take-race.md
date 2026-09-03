# §49 regen 撞车：多写者竞态覆盖 clip + PASS 票与 take 绑定（2026-08-31 医生 clip8 实测）

## 现象
同一修复指令被并行分发到多个 A2A worker 会话，每个 worker 各自提交 seedance task + 独跑 poll.py → `videos/clip8.mp4` 在 30 分钟内被 3 个不同 take 依次覆盖（d9hft✓好 → 0a444459 悬浮复发 → fb6e6b69 全身入画违反半身方案）。16:36-16:41 的「9/9 帧复查 PASS」绑定的是**当时落盘的 d9hft**；之后某 worker 起的 concat 用了被覆盖后的坏 take 合成成片——**成片里 clip8 段男孩全身悬浮**（终拼抽帧 t=28.8/30.5/32.5 实测），而单查 standalone clip 文件当时的快照却是好的。

## Protocol（六步，缺一即翻车）
1. **提交 regen 前先排雷**：`task_clipN.txt` mtime 是否刚被别人写过 + `ps aux | grep poll/submit` + delegation live log 尾部——已有活跃 task 就轮询它，绝不并行重提。
2. **PASS 票与 take 绑定**：复查通过后在 `task_clipN.txt` 写死锁定行（take 的 task_id + md5 + 作废清单），任何后续覆盖都以 md5 对照识别。
3. **成片末段抽帧复查是硬验收**：无论 concat 谁拼的，交付前对 final 的最后一 clip 段（本例 t=28.8/30.5/32.5）抽 3 帧 vision 复核——只查 standalone clip 会被晚到的覆盖骗过。
4. **坏 take 识别三态**：①悬浮复发（旧病）②全身入画（违反半身构图方案——修复 prompt 未生效）③掌心有间隙（击掌未接触）。t=0.05s 单帧即可判别。
5. **救回好 take**：好 take 的 task_id 仍可查（status=succeeded + video_url 长效）→ curl 重拉 → md5 对照锁定行 → 覆盖回 videos/clipN.mp4 → 重跑 concat → 全链复验（ffprobe 32.768s + decode 0 错 + freezedetect 0 冻结 + 成片末段 3 帧 + ASR 核词）→ 重新上传 uguu（旧直链对应坏版本，作废勿再引用）。
6. 多 worker 并发期间，同一工作区产物（prompts/task_clipN/videos/final）一律视为可被他人覆写——**任何「复查过了」的结论都必须带 take md5 才有效**。

## 本例最终交付（存档）
- lock take = `cgt-20260831163342-d9hft`（md5 dd18bbd2b453b759fe8ae7957b0e4a9d）
- 最终成片 final_doctor.mp4 md5 `c217ebb3d6b8c3817d9e2814f1ba2f6f`，8,972,720 B，32.768s，720×1280@24fps
- 直链 https://d.uguu.se/uBvHBqSB.mp4 （回下 md5 逐位一致）
- 作废：v1 0a4444599a5f656601fc6b8057b21a33（悬浮）、5wvch take fb6e6b693884e5ddee5d23d428a8aea3（全身）、旧直链 VOXKxvbC/uBvHBqSB 之前所有链接对应的中途版本，以及混合版 a7fb5e14/45d1d88e/b018913b（混入 0a444459 的合成物）
