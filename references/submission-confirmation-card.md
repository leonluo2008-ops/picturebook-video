# Seedance 提交前参数确认卡 + 交付格式

> **来源**: 2026-07-15/17 Bridge→Lavender→Bookstore→Daisy 4 本连续实测沉淀
> **触发**: Step 6.0 调 mcp__seedance__generate_video 前**必输出**(付费生成操作)
> **作用域**: 任何调用 Seedance 2.0 Fast/Flex API 的绘本视频项目

## 一、参数确认卡模板(Step 6.0 必输出)

调 `mcp__seedance__generate_video` 前**必输出以下 ASCII 文本卡**,等用户回 OK 再提交。**这是付费生成操作的硬约束**(每个任务扣费,参数错 = 浪费钱)。

```text
═══════════════════════════════════════
**《<绘本名>》· 视频提交前参数确认**
═══════════════════════════════════════

API Key 已验证有效。确认后直接提交 N 个有声 Clip,不额外做 Spike。

```text
模型：Seedance 2.0 Fast
分辨率：720p
画幅：16:9
音频：开启旁白 + 环境音效
背景音乐：无
水印：无
运镜：非固定镜头
随机种子：-1
Service Tier：不传(Fast 模型不支持)
提交方式：N 个任务

Clip 1
- 时长：Xs
- 参考图：a.jpg + b.jpg

Clip 2
- 时长：Ys
- 参考图：c.jpg + d.jpg + e.jpg

...

这是付费生成操作。回复 **OK** 后,我立即提交并等待下载。
```

## 二、参数清单(逐项解释)

| 参数 | 推荐值 | 反模式 |
|---|---|---|
| **模型** | `doubao-seedance-2-0-fast-260128`(默认) | ❌ 默认不传 = 用上版本模型(可能已下线) |
| **ratio** | `16:9`(绘本横屏)/ `9:16`(抖音竖屏) | ❌ 不传 = API 默认漂移 |
| **duration** | 取整到 [4, 15] 整数(每个 Clip 的 `suggested_duration_s`) | ❌ 非整数 = API 400 |
| **resolution** | `720p`(fast 模型唯一支持) | ❌ `1080p` + fast 模型 = API 400 |
| **seed** | `-1`(随机) | ⚠️ 固定种子可能产生重复画面,debug 才用 |
| **camera-fixed** | `false`(默认) | ❌ 默认 `true` = 镜头不动,违反 v8.1 运镜必写规则 |
| **watermark** | `false`(绘本禁忌 AI 水印) | ❌ 永远不传 `seedance_ai` |
| **generate-audio** | `true`(默认有声) | ⚠️ 用户说"spike/不要声音"才传 `false` |
| **service-tier** | 不传 | ❌ Fast 模型不支持 `flex` |

## 三、提交后交付格式(Step 7 必走)

下载完成 + ffprobe + md5 + 时长校验后,**3 条消息发**:

```
**<绘本名> · Clip 1（Xs）**
任务 ID：`cgt-YYYYMMDDhhmmss-xxxxx`
MEDIA:/home/ubuntu/<project>/outputs/<project>_clip1.mp4

**<绘本名> · Clip 2（Ys）**
任务 ID：`cgt-YYYYMMDDhhmmss-xxxxx`
MEDIA:/home/ubuntu/<project>/outputs/<project>_clip2.mp4

**<绘本名> · Clip 3（Zs）**
任务 ID：`cgt-YYYYMMDDhhmmss-xxxxx`
MEDIA:/home/ubuntu/<project>/outputs/<project>_clip3.mp4
```

**字段顺序**(用户偏好):
1. **标题**:`**<绘本名> · Clip N（Xs）**`(粗体)
2. **任务 ID**:`cgt-...`(带反引号方便复制)
3. **MEDIA 路径**:绝对路径(`/home/ubuntu/...`),不是相对路径

**反模式**:
- ❌ 只发一个 MEDIA 链接 + 一句"已生成"
- ❌ 把 3 个 Clip 塞进同一条消息
- ❌ 不附 task_id(用户无法追溯扣费)
- ❌ 用相对路径(用户机器路径可能不同)

## 四、ffprobe + md5 + 时长校验脚本

```python
from hermes_tools import terminal
import json, shlex
from pathlib import Path

p = Path('/home/ubuntu/<project>/outputs')
for i, exp in [(1, X), (2, Y), (3, Z)]:
    f = p / f'<project>_clip{i}.mp4'
    r = terminal(f"ffprobe -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,channels -of json {shlex.quote(str(f))}")
    d = json.loads(r['output'])
    v = next(x for x in d['streams'] if x['codec_type'] == 'video')
    a = [x for x in d['streams'] if x['codec_type'] == 'audio']
    md = terminal(f"md5sum {shlex.quote(str(f))}")['output'].split()[0]
    print(json.dumps({
        'clip': i,
        'duration': float(d['format']['duration']),
        'expected': exp,
        'resolution': f"{v['width']}x{v['height']}",
        'audio': bool(a),
        'md5': md,
        'size': int(d['format']['size'])
    }, ensure_ascii=False))
```

**判定**:
- 时长差 ≤ 1s ✅
- 分辨率 = 1280x720 ✅(fast 模型)
- audio stream 存在 ✅(generate_audio=true)
- 文件名 ASCII(数字/英文/拼音)✅

## 五、跳过 7 维度审计的情况(用户偏好)

用户说以下任一信号时,**跳过 vision 抽帧和音轨听写**:
- "直接发视频不用检查"
- "你不用检查"
- "直接发"
- "全自动"

仍然**必做**:
- 删空目录/中间文件(`frames/`, `submit_clipN.log` 等)
- 文件名 ASCII
- ffprobe + md5 + 时长校验(防下载失败/参数错)
- 单条消息附 task_id + md5 + 时长(用户偏好)

**反模式**: 忽略用户指令继续做全审计 = 浪费 5+ min + 违背"全自动"语义。

## 六、典型踩坑

| 踩坑 | 后果 | 修复 |
|---|---|---|
| 跳过参数确认卡,直接 submit | 参数错(画幅错/分辨率错) = 整批重做 | 必输出卡等 OK |
| 1080p + fast 模型 | API 400,所有任务失败 | fast 只支持 720p |
| 默认不传 generate_audio | 部分任务无声(API 默认漂移) | 显式传 true |
| watermark='seedance_ai' | 视频带 AI 水印(绘本禁忌) | 永远不传 |
| 调 wait_and_download 5 分钟超时 → 重 submit | 重复扣费 | 二次 wait_and_download,不重 submit |
| 调 mcp_seedance_check_task 循环 50 次 | token 浪费 + loop 警告 | 调 wait_and_download 一次 |
| 任务失败保留旧文件 | 用户困惑"哪个对" | 重发前 `rm clip_2_failed.mp4` |
| 输出 `MEDIA:./clip1.mp4`(相对路径) | 用户找不到文件 | 输出绝对路径 |
| 不附 task_id | 用户无法追溯扣费 | 每条消息必附 task_id |

## 七、版本

v1.0 (2026-07-17 Bridge→Lavender→Bookstore→Daisy 4 本实测沉淀)