# Case #39 · SRT 文件发错（Truck 实测 · 2026-06-28）

## 现象

用户上传素材包 `.7z`，解压后 SRT 文件内容与绘本主题完全不符。例：绘本是 "Truck 卡车"领读型，但 SRT 文件内容是另一本 "Stop 停！" 的旁白。agent 跑完 Step 3（SRT 解析 + clip 划分）甚至提交了 spike 后，用户才发现 SRT 发错了。

## 根因

用户在打包素材时选错了 SRT 文件。agent 解压后没有校验 SRT 文本内容是否与图片/绘本主题匹配，直接进入 Step 3。

## 修复规则

**Step 1 新增前置校验**: 解压素材包后，在进入 Step 2 之前，**先通读 SRT 文本并核对**：
1. SRT 文本中的目标词是否与图片中展示的目标词一致
2. SRT 文本内容是否与绘本主题/图片场景逻辑匹配
3. SRT 段数是否合理（领读型通常 7-10 段，不会是 16 段停/Stop 交替）

**口诀**: "解压先读 SRT，目标词对得上才往下走。"

## 影响

- 浪费: Step 2 vision 自检 + Step 3 SRT 解析 + clip_merger + Step 5 prompt 写作 + verify_prompt + spike 提交 + 下载 + 发飞书
- 本例: 从 Step 1 跑到 Step 6 spike 完成，用户才发现 SRT 错误 → 全部作废重来
