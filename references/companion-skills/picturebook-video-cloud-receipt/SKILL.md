---
name: picturebook-video-cloud-receipt
description: "picturebook-video Step 1 素材接收的飞书云盘 URL 处理约束。2026-07-23 实测踩坑：用户给的 https://aistar-work.feishu.cn/file/TOKEN 是登录态页面，agent 无法直接下载或读取。feishu_doc_read 仅在飞书评论上下文有效，工作区消息通道无效。picturebook-video SKILL.md 应在 Step 1 加 3 步 fallback 协议，本 skill 作为兜底。触发词：绘本视频、picturebook-video、云盘素材、飞书 file URL、aistar-work.feishu.cn。"
---

# picturebook-video Step 1 · 飞书云盘素材接收协议

> **核心约束**（2026-07-23 实测沉淀）：用户给 `https://aistar-work.feishu.cn/file/TOKEN` 形式的链接时，**agent 无法直接读取**。

## 为什么直接读不到

| 工具 | 结果 | 原因 |
|------|------|------|
| `feishu_doc_read(doc_token=TOKEN)` | ❌ 报错"not in a Feishu comment context" | 该工具只在飞书**评论上下文**中工作；Feishu 工作区消息通道不是评论 |
| `curl https://aistar-work.feishu.cn/file/TOKEN` | ⚠️ HTTP 200 但只返回登录引导 HTML | 链接是飞书云盘**网页页面**而非文件直链；需要登录 cookie 才能拿真实内容；file_token 仅在登录态下有效 |

## 3 步 Fallback 协议

当用户给飞书云盘 URL 时，按以下顺序处理：

### Step 1 · 确认可读路径
- ✅ 用户给的是**绝对本地路径**（如 `/home/ubuntu/xxx/绘本.7z`）→ 直接解压
- ✅ 用户**粘贴文本**（旁白 / readme）→ 直接处理
- ❌ 用户给的是 `aistar-work.feishu.cn/file/...` 登录态 URL → 进 Step 2

### Step 2 · 告知限制，给出 3 种可行方案

**方案 A · 本地路径（推荐）**
用户把素材下到本地或已经下载到 `/home/ubuntu/` 下 → 给绝对路径。

**方案 B · 飞书云盘 Token 授权**
按 douyin-ops 流程：跑过 `scripts/init-env.sh` → 写入 `FOLDER_TOKEN` → 走 `larkcli` 命令行读云盘。已有则告诉 folder 名。

**方案 C · 直接贴文件**
- .7z / .zip / .tar：发到飞书消息通道，agent 直接接收
- .txt / .md：直接复制粘贴内容

### Step 3 · 不浪费时间猜测

禁止：
- ❌ 反复尝试不同 fetch 方式（如改 header / 改 User-Agent）
- ❌ 期待 web_browser 工具能登入（无 cookie = 永远停在登录页）
- ❌ 假装读到了

正确做法：1 步告知限制 + 给 3 方案 + 等待用户回复路径。

## 集成位置

应在 `creative/picturebook-video/SKILL.md` Step 1 段顶部插入"飞书云盘 URL 处理"小节，作为 4 确认点流程的前置检查。如 skill_manage 写入失败，留在本 skill 兜底。