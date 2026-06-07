# send_message 防串扰铁律（铁律 #76）

> **2026-06-07 Pic4 No 不绘本 clip1 实战**——视频生成正确（md5 95323c4e 验证 No 内容）但首次 send_message 用户看到"Welcome"视频（send_message 串扰 / 飞书 client bug / 用户看历史消息）

## 根因

**未实锤**（可能是以下任一）：
1. **send_message 工具 bug**：附件路径错误，指向了 pic3 历史视频
2. **飞书 client bug**：附件预览显示成历史消息
3. **用户看错消息**：看到的是 pic3 历史 Welcome 消息
4. **种子/参数没真用上**：seedance 实际生成跟 prompt 不一致

**Pic4 实战排查 4 个事实点**（排除前 3 个）：

| 事实 | 验证 |
|---|---|
| 本地 1.jpg 是 No 绘本 | ✅ vision 描述明确"棕熊 Stop 手势 + No/不能" |
| chevereto 上传的就是本地 1.jpg | ✅ md5 一致 `8f693eda71b0b941f362a060d2c2e46f` |
| 我发的 mp4 = pic4 v1-clip1-fixed.mp4 | ✅ md5 `95323c4e`，跟 pic3 9 段 md5 全不同 |
| vision_analyze 多工具看 pic4 视频 | ✅ 确认是 No 内容 |

**用户最终确认**：重发时 1.jpg + 视频 md5 跟原文件匹配，是 No 内容。**根因 = send_message 第一次附件显示错**（飞书 client bug 或工具 bug）。

## 修复方案

### 1. 发视频前必本地 stat+md5 校验

```bash
# 1. 校验文件存在
ls -lh /path/to/v1-clip1-fixed.mp4

# 2. 校验 md5
md5sum /path/to/v1-clip1-fixed.mp4

# 3. 校验视频时长 + 分辨率
ffprobe -v error -show_entries stream=width,height,duration -of default=noprint_wrappers=1 /path/to/v1-clip1-fixed.mp4
```

**目的**：发之前就知道这个视频**到底是什么**（防止"发错视频"反模式）。

### 2. 消息里显式打 文件名 + md5 + task_id + seed + 时长

**发飞书消息模板**：

```
📦 [绘本名] v[N] 视频已生成：

| Clip | 时长 | size | md5 | task_id |
|---|---|---|---|---|
| 1 (No!) | 4s | 1.5M | 95323c4e... | cgt-20260607130857-tbmd2 |
| 2 (No, no, hot!) | 4s | 1.7M | ddd884d0... | cgt-20260607133510-hwkhr |
| ... | | | | |

技术参数：
- model: doubao-seedance-2-0-fast-260128
- ratio: 16:9
- watermark: false
- 总时长: 39s
- 总文件: 21M

MEDIA:/path/v1-clip1-fixed.mp4
MEDIA:/path/v1-clip2-fixed.mp4
...

**自查重点**：
1. 内容是 No 绘本（Stop 手势 + "No/不能"）？
2. 9 段顶部 "No/不能" 文字是否完整保留？
3. 末帧是否有微动？
4. 节奏是否紧凑警示？

如果内容有问题请立刻告诉我哪个 clip 错，如果 OK 我就 push v1.0.2 + 开 PR #3。
```

**关键**：
- **filename + md5 + task_id 必打**（让用户能 100% 验证）
- **version 必打**（"v1 严肃"/"v3 温柔化"/"v5 节奏强化"/"v6 整数+文字全程"——防铁律 #78 串版）
- **技术参数必打**（model/ratio/watermark——辅助验证）

### 3. 同时落地磁盘 + 飞书云盘

**Pic4 实战**：视频只发飞书，没落地云盘 → 用户只能看飞书里那一份，**没法二次验证**。

**修复**：
```bash
# 上传到飞书云盘
lark-cli drive +push \
  --folder-token "PROJECT_FOLDER" \
  --local-dir "./" \
  --if-exists overwrite
```

用户可从云盘二次下载验证（md5 校验）。

### 4. vision_analyze 跟人眼观感不一致时，以人眼为准

**反模式**：vision_analyze 说"是 No 内容" = 一定对。

**修复**：用户目检**永远比** vision 准：
- vision 抽 4 帧（t=0.5/2.0/3.5）+ 看 N 帧 = 100% 覆盖
- 人眼看完整 4s 视频 = 包含声音/流畅度/转场
- **如果人眼 vs vision 不一致 → 相信人眼 + 重新生成**

## 实战验证（2024-06-07 Pic4 No clip1 重发）

| 字段 | 第一次 send | 重发 send |
|---|---|---|
| 文件名 | v1-clip1-fixed.mp4 | v1-clip1-fixed.mp4 |
| md5 | 95323c4e | 95323c4e |
| task_id | cgt-20260607130857-tbmd2 | cgt-20260607130857-tbmd2 |
| 消息内容 | 5 字段表格 + 1 个 MEDIA | 4 字段证据链 + 1.jpg + 视频 + 4 事实 |
| 用户反馈 | "看到 Welcome" | "OK 是 No" |

**关键差异**：第一次只发了视频 + 简短表格。**重发 = 4 个事实点 + 1.jpg + 视频 + 完整证据链**——让用户能多角度验证（看 1.jpg 原图 / 看 1.jpg md5 / 看视频 md5 / 看 4 个事实点）。

## 单 Clip 端到端验证流程（铁律 #79）

**反模式**（Pic4 v1 实战差点踩）：
```
单 clip1 跑通 → 立刻批量跑剩下 8 段 → 用户目检发现 clip1 是 Welcome → 8 段全白跑
```

**修复**（v1.0.3+pic12 铁律 #79）：
```
单 clip1 跑通 → 发飞书（带证据链）→ 等用户目检 → 用户回"OK 是 No" → 跑剩下 8 段
```

**主 agent 必说**：
> "我打算：发您单 Clip → 等您目检 → OK 再批量跑剩下 8 段。"

## 排查模板（用户反馈"内容不对"时）

**4 步排查法**：

| 步 | 验证 | 命令 |
|---|---|---|
| 1. 本地视频内容 | vision_analyze mp4 | mcp_zai_analyze_video |
| 2. 本地 prompt 内容 | 读 prompt.txt | `cat clips/clip1-prompt.txt` |
| 3. chevereto/uguu 上传图 | md5 对比本地 | `md5sum 1.jpg` vs `curl -sL "URL" \| md5sum` |
| 4. 实际 task_id 跑的 prompt | 看 ark list 任务详情 | `seedance.py status <task_id>` |

**4 步全过 + vision 跟人眼不一致 → 飞书 client bug**（重发 + 让用户从云盘二次下载验证）

## 关联铁律

- 铁律 #76：send_message 防串扰（**本 reference**）
- 铁律 #78：多版本原料 JSON 并存策略（发飞书必带版本号）
- 铁律 #79：单 Clip 端到端验证 = 必经环节
- 铁律 #63：vision 和人眼观感不一致风险（以人眼为准）
- 铁律 #65：单 Clip 端到端验证发现的内容-渲染不一致
