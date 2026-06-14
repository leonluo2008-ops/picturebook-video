# 2026-06-05 ark list 端点救援 · 任务 ID 丢失后 0 元重提

> **本文件是应急 SOP**——seedance.py 没有 list 实现，task ID 丢失时的救回通道。

## 适用场景

- ❌ 并行提交 6 个 task 没存 ID（教训 #30）
- ❌ wait 阻塞被打断，task ID 没收到
- ✅ 任务大概率 succeeded（没看到 fail 报错）
- 💰 **重提 = 重复扣费**（每条约 20 元）

## 完整救援流程

### Step 1：拉取最近任务列表

```bash
export HOME=/home/luo
source /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env

# 拉最近 20 条任务（page_size 可调，最大 100）
curl -sS -H "Authorization: Bearer $ARK_API_KEY" \
  "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_size=20" \
  > /tmp/seedance-list.json

# 验证
python3 -c "import json; d=json.load(open('/tmp/seedance-list.json')); print(f'total={d[\"total\"]}, items={len(d[\"items\"])}')"
```

### Step 2：按时间窗口过滤 + 映射 clip 编号

```python
# /tmp/seedance-rescue.py
import json
d = json.load(open('/tmp/seedance-list.json'))

# 关键：按 created_at 排序（最新在前）
items = sorted(d['items'], key=lambda x: x['created_at'], reverse=True)

# 映射：提交顺序 → 已知时间窗口
# 假设 6 个 task 全部在 16:19-16:20 提交
# 按 created_at 时间窗口匹配
target_ids = []
for item in items:
    ts = item['created_at']  # 1780647570 = 16:19:30
    # 过滤时间窗口（unix timestamp）
    if 1780647570 <= ts <= 1780647831:  # 16:19-16:20 窗口
        target_ids.append({
            'id': item['id'],
            'created_at': ts,
            'status': item['status'],
            'video_url': item['content']['video_url'],
            'duration': item.get('duration'),
            'ratio': item.get('ratio'),
        })

for t in target_ids:
    print(f"{t['created_at']} | {t['id']} | {t['status']} | {t['duration']}s {t['ratio']}")
```

### Step 3：批量下载到本地

```python
import urllib.request, os

# 映射：按 created_at 顺序 → clip 编号
mapping = {
    'cgt-20260605161930-w7zr8': 'clip4',  # 最早 = clip 4
    'cgt-20260605161941-k4m2x': 'clip6',
    # ... 等等
}

for t in target_ids:
    clip_name = mapping.get(t['id'])
    if clip_name and t['status'] == 'succeeded':
        out = f'/home/luo/huiben-projects/20260605-folder-test/output/{clip_name}-4s-16x9.mp4'
        print(f"Downloading {clip_name}...")
        urllib.request.urlretrieve(t['video_url'], out)
        print(f"  -> {os.path.getsize(out)} bytes")
```

## 关键限制

| 限制 | 说明 |
|---|---|
| **page_size 默认 10-20** | 看不到所有历史任务，**只用于最近 1 小时内** |
| **video_url 24h 过期** | 找到后必须**立刻下载** |
| **按 created_at 过滤** | 不是按 task ID 前缀过滤（task ID 时间戳部分可读） |
| **必须映射 clip 编号** | 时间窗口内可能混着其他 task（如 v1/v2 错版），按提交顺序映射 |
| **不替代教训 #30** | 预防（存 task ID）远比救援重要 |

## 与 seedance.py 配合

```bash
# seedance.py 也能 wait 已知的 task ID
python3 /home/luo/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/seedance.py wait \
  cgt-20260605161930-w7zr8 \
  --download /home/luo/huiben-projects/20260605-folder-test/output/clip4-4s-16x9.mp4
```

如果 seedance.py 报错，curl 下载更直接（见 Step 3）。

## 实测战绩

- 2026-06-05 Say 说绘本：6 个并行 task ID 丢失 → ark list 救回 → **0 元重提** 6 个 4s 720p 视频
- 耗时：list 查询 5s + 6 个 URL 下载 30s = 35s 完成
- 对比：6 个 task 重提约 120 元 + 6 分钟生成时间
