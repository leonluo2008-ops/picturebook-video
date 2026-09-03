# Terminal Python 直调 seedance_uploads.py 完整模板
# 2026-08-29 画家实测验证
# 用途：MCP 工具长 prompt 被静默丢弃时的可靠绕过

import sys, os, json, time, urllib.request
sys.path.insert(0, os.path.expanduser('~/.hermes/skills/creative/picturebook-video/seedance_mcp'))
from seedance_uploads import upload_to_uguu, build_body, ark_request

# 1. 加载 .env（必须 export 到 os.environ，否则 get_ark_key() 报 KeyError）
env_path = os.path.expanduser('~/.hermes/skills/creative/picturebook-video/seedance_mcp/.env')
for line in open(env_path):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ[k.strip()] = v.strip()

# 2. 上传参考图（upload_to_uguu 接本地路径，返回 uguu URL）
img_urls = [upload_to_uguu(p, 'image/jpeg') for p in ['/path/1.jpg', '/path/2.jpg']]

# 3. 读 prompt 文件
with open('/path/to/clip.txt') as f:
    prompt = f.read()

# 4. 构造 body（build_body 自动跳过第三方网关不认的 watermark/service_tier）
args = {'prompt': prompt, 'ref_images': img_urls, 'duration': 7, 'ratio': '9:16',
        'generate_audio': True, 'seed': -1}
body = build_body(args)

# 5. 提交
result = ark_request('POST', os.environ['SEEDANCE_BASE_URL'], data=body)
task_id = result.get('id', '')
print(f'task_id={task_id}')

# 6. 轮询 + 下载
for i in range(40):
    time.sleep(15)
    d = ark_request('GET', f"{os.environ['SEEDANCE_BASE_URL']}/{task_id}")
    st = d.get('status', '')
    if st == 'succeeded':
        # 视频 URL 在 d['content']['video_url']，不是 d['output']['video_url']
        video_url = d['content']['video_url']
        urllib.request.urlretrieve(video_url, '/path/to/output.mp4')
        print('DOWNLOADED')
        break
    elif st == 'failed':
        print(f'FAILED: {d}')
        break

# 关键点：
# - upload_to_uguu() 接本地路径（不是 URL），返回 uguu URL
# - build_body() 内置第三方网关兼容逻辑，不要手动传 watermark 参数
# - Ark API 视频URL在 content.video_url（不是 output.video_url）
# - .env 三变量必须 export 到 os.environ
# - 可同时提交多个 task（并行轮询）
