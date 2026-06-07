# uguu 兜底路线 · chevereto 挂了时直接 curl 调 ark API

> **2026-06-07 实战沉淀**（Pic4 No 不绘本 v3 跑通后 chevereto 挂了）· 铁律 #71

## 触发条件

- `seedance.py create --image xxx.jpg` 报 `Error: curl failed:`（chevereto 上传失败）
- `curl -sI "https://chevereto.aistar.work/"` 连续 3+ 次 timeout
- chevereto 图床**整体挂**（不是单图问题）

## uguu 兜底路线（3 步）

### Step 1 · 上传图片到 uguu.se

```python
import urllib.request, ssl, json
ctx = ssl.create_default_context()

def upload_uguu(local_path):
    file_data = open(local_path, "rb").read()
    boundary = "----hermesboundary12345"
    parts = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="files[]"; filename="{os.path.basename(local_path)}"\r\n'.encode(),
        b"Content-Type: image/jpeg\r\n\r\n",
        file_data, b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(parts)
    req = urllib.request.Request(
        "https://uguu.se/upload.php", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "curl/8.0"},
        method="POST",
    )
    r = urllib.request.urlopen(req, timeout=120, context=ctx)
    return json.loads(r.read())["files"][0]["url"]
```

**关键字段**：
- 端点：`https://uguu.se/upload.php`
- multipart field 名：**`files[]`（带方括号）** —— **不是** `file`！
- 响应：JSON，提取 `files[0].url`
- 直链域名：`n.uguu.se` 或 `o.uguu.se` 或 `h.uguu.se`（多 CDN 轮换）

### Step 2 · 直接调 ark API（绕过 seedance.py）

```python
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
MODEL = "doubao-seedance-2-0-fast-260128"

def create_task(image_url, prompt, duration=4, ratio="adaptive", watermark=False, resolution="720p"):
    body = {
        "model": MODEL,
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}, "role": "first_frame"},
        ],
        "duration": duration, "ratio": ratio,
        "watermark": watermark, "resolution": resolution,
    }
    req = urllib.request.Request(
        BASE_URL, data=json.dumps(body).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {ARK_API_KEY}"},
        method="POST",
    )
    r = urllib.request.urlopen(req, timeout=60, context=ctx)
    return json.loads(r.read())  # 返回 {"id": "cgt-..."}
```

**关键参数**：
- `Authorization: Bearer {ARK_API_KEY}`（从 `.env` 读）
- `model: doubao-seedance-2-0-fast-260128`（fast 版便宜）
- `content[0].type: text` + `content[1].type: image_url` + `role: first_frame`
- `duration` 必填整数（4-15，**铁律 #72**）
- `watermark: false`（绘本必禁）

### Step 3 · 轮询 + 下载

```python
def get_status(task_id):
    req = urllib.request.Request(
        f"{BASE_URL}/{task_id}",
        headers={"Authorization": f"Bearer {ARK_API_KEY}"},
    )
    r = urllib.request.urlopen(req, timeout=30, context=ctx)
    return json.loads(r.read())

def download(url, out_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(out_path, 'wb') as f:
        f.write(data)
    return hashlib.md5(data).hexdigest(), len(data)
```

**关键注意**：
- **轮询间隔 5s × 60 次**（5 分钟）—— 实测 90-120s 跑通
- **下载用 urllib 不用 curl**（curl 在某些环境下对 X-Tos-Signature 头处理有问题）
- **video_url 跟 X-Tos-Signature 时效约 24h**（下载后留本地永久）

## 完整 wrapper 脚本

`uguu_ark_wrapper.py`（Pic4 实战沉淀）：

```python
#!/usr/bin/env python3
"""uguu 兜底 + 直接调 ark API（不依赖 chevereto + seedance.py）"""
import os, sys, json, ssl, urllib.request, hashlib

ctx = ssl.create_default_context()

# 加载 .env
ENV_PATH = "/home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env"
for line in open(ENV_PATH, encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ.setdefault(k.strip(), v.strip())

ARK_API_KEY = os.environ['ARK_API_KEY']
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
MODEL = "doubao-seedance-2-0-fast-260128"

# 上面 3 个函数：upload_uguu / create_task / get_status / download
# 然后循环跑 N 个 clip
```

## 批量跑 2 段版本

`run_v3_clip23.py`（Pic4 v3 实战沉淀）：

```python
for n in [2, 3]:
    img = f"{PROJECT}/{n}.jpg"
    prompt_file = f"{PROJECT}/clips/clip{n}-prompt-v3.txt"
    img_url = upload_uguu(img)
    result = create_task(img_url, prompt, duration)
    task_id = result['id']
    for i in range(60):
        time.sleep(5)
        s = get_status(task_id)
        if s.get('status') == 'succeeded':
            video_url = s['content']['video_url']
            break
    download(video_url, out)
```

## 实战验证（2026-06-07 Pic4 No 不绘本）

| 段 | uguu URL | task_id | seed | md5 |
|---|---|---|---|---|
| clip1 v3 | `o.uguu.se/oOtifUFa.jpg` | `cgt-20260607141523-mxclp` | 79679 | c8626196 |
| clip1 v5 | `o.uguu.se/vuVbzrHc.jpg` | `cgt-20260607145646-5488t` | 70331 | 5b0771e6 |
| clip2 v3 | `n.uguu.se/ALuLZfHP.jpg` | `cgt-20260607143134-j8vh7` | — | fb094632 |
| clip3 v3 | `o.uguu.se/VoWJpuWv.jpg` | `cgt-20260607143351-2bcr2` | — | b1e33096 |

**总计 4 段 v3/v5 clip1-3 全部跑通** · uguu 兜底路线 100% 稳定

## 反模式

- ❌ 改 seedance.py 加 uguu 支持（**不对**：seedance.py 是通用工具，改了会被 seedance2.0-tool 维护团队回滚）
- ❌ 用 0x0.st（2026-06 AI botnet spam 关停，无 ETA）
- ❌ 用 catbox.moe（偶发 Broken pipe）
- ❌ 用 file.io（返回 Gatsby HTML 包装页，不是直链）
- ✅ 优先用 uguu.se（已实测稳定）

## 兜底脚本纳入标准工具

**v1.0.4 待办**：
- `picturebook-video/scripts/fill_v15_template.py`（含 _parse_en_color 数据清洗 · 支持 v3/v5/v6 模板变体）
- `seedance2.0-tool/scripts/uguu_ark_wrapper.py`（uguu 兜底 + 直接 curl 调 ark API）
- `seedance2.0-tool/scripts/run_batch_clips.py`（批量跑 N 段 · ≤2/批 · 续跑模式）

## 关联铁律

- 铁律 #58：A+B+D 主 agent · D 改主 agent 用 `seedance.py` 或 `uguu_ark_wrapper.py`
- 铁律 #71：chevereto 挂了用 uguu 兜底（**本 reference**）
- 铁律 #72：seedance 整数时长（设计时长 = 实跑时长）
- 铁律 #75：fill_v15 模板脚本 = 标准工具
- 铁律 #76：send_message 防串扰（附 md5+task_id）
