#!/usr/bin/env python3
"""seedance 直连提交/轮询/下载（MCP 不可用或需要脚本化批量时的标准替代）。

来源：2026-09-02 消防员批实测（3 clips 一轮提交 15s/9s/9s 全过零返工）。
用法：
  1) 写批次清单 <workdir>/batch.json：
     [
       {"prompt": "clip1-prompt.txt", "images": ["vertical/1.png", "vertical/2.png"], "duration": 15},
       {"prompt": "clip2-prompt.txt", "images": ["vertical/5.png", "vertical/6.png"], "duration": 9}
     ]
     （prompt/images 相对 --workdir；duration 整数 [4,15]；单轮 >3 条会被拒绝 = 硬约束 #3）
  2) 提交:      python3 seedance_submit_direct.py --workdir <dir>
  3) 等待+下载: python3 seedance_submit_direct.py --workdir <dir> --wait
     （产物 <workdir>/clipN.mp4；tasks.json / download_results.json 含 md5）

环境：自动加载 <skill仓>/seedance_mcp/.env（ARK_API_KEY / SEEDANCE_BASE_URL / SEEDANCE_MODEL）。
默认参数与绘本标准对齐：ratio=9:16、generate_audio=true（路径 A）、resolution=720p（fast 上限）、watermark=none。
本地参考图由 seedance_uploads.resolve_all_inputs_async 自动传 uguu，无需手动上传。
"""
import argparse, asyncio, hashlib, json, os, sys, time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent  # scripts/ 上一级 = skill 仓根


def load_env():
    env_file = SKILL_DIR / 'seedance_mcp' / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())
    sys.path.insert(0, str(SKILL_DIR / 'seedance_mcp'))
    import seedance_uploads as U
    return U


def submit_batch(U, workdir: Path):
    batch = json.loads((workdir / 'batch.json').read_text(encoding='utf-8'))
    assert 1 <= len(batch) <= 3, '硬约束 #3：单轮 ≤3 并发，超过请拆轮串行'

    async def one(item, idx):
        prompt = (workdir / item['prompt']).read_text(encoding='utf-8')
        imgs = [str((workdir / p).resolve()) for p in item['images']]
        for p in imgs:
            assert Path(p).exists(), f'missing ref image: {p}'
        args = {
            'prompt': prompt,
            'ref_images': imgs,
            'duration': int(item['duration']),
            'ratio': item.get('ratio', '9:16'),
            'generate_audio': item.get('generate_audio', True),
            'resolution': item.get('resolution', '720p'),
            'watermark': 'none',
        }
        resolved = await U.resolve_all_inputs_async(args)
        body = U.build_body(args, resolved_urls=resolved)
        r = await U.ark_request_async('POST', U.ARK_BASE_URL, body, timeout=60)
        tid = r.get('id')
        if not tid:
            raise RuntimeError(f'clip{idx} no task_id: {r}')
        return {'clip': idx, 'task_id': tid, 'status': r.get('status', 'queued'),
                'duration': args['duration'], 'images': item['images']}

    async def run():
        return await asyncio.gather(*[one(it, i + 1) for i, it in enumerate(batch)])

    results = asyncio.run(run())
    (workdir / 'tasks.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print('saved ->', workdir / 'tasks.json')


def wait_all(U, workdir: Path, budget: int = 570):
    tasks = json.loads((workdir / 'tasks.json').read_text(encoding='utf-8'))
    deadline = time.time() + budget

    async def poll():
        pending = {t['clip']: t for t in tasks}
        done = {}
        while pending and time.time() < deadline:
            for clip, t in list(pending.items()):
                try:
                    r = await U.ark_request_async('GET', f'{U.ARK_BASE_URL}/{t["task_id"]}', timeout=30)
                except Exception as e:
                    print(f'clip{clip} poll error: {e}', flush=True)
                    continue
                st = r.get('status')
                if st == 'succeeded':
                    url = r.get('content', {}).get('video_url')
                    if not url:
                        print(f'clip{clip} succeeded but no video_url', flush=True)
                        continue
                    client = await U.get_http_client()
                    resp = await client.get(url, timeout=120)
                    resp.raise_for_status()
                    data = resp.content
                    out = workdir / f'clip{clip}.mp4'
                    out.write_bytes(data)
                    done[clip] = {'task_id': t['task_id'], 'path': str(out),
                                  'size': len(data), 'md5': hashlib.md5(data).hexdigest()}
                    print(f'clip{clip} DONE md5={done[clip]["md5"]}', flush=True)
                    del pending[clip]
                elif st == 'failed':
                    done[clip] = {'task_id': t['task_id'], 'status': 'failed', 'error': r.get('error')}
                    print(f'clip{clip} FAILED: {r.get("error")}', flush=True)
                    del pending[clip]
                else:
                    print(f'clip{clip} {st}', flush=True)
            if pending:
                await asyncio.sleep(15)
        return done, {k: v['task_id'] for k, v in pending.items()}

    done, pending = asyncio.run(poll())
    out = {'done': done, 'pending': pending}
    (workdir / 'download_results.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--workdir', required=True)
    ap.add_argument('--wait', action='store_true', help='跳过提交，读 tasks.json 轮询+下载')
    a = ap.parse_args()
    U = load_env()
    wd = Path(a.workdir).resolve()
    if a.wait:
        wait_all(U, wd)
    else:
        submit_batch(U, wd)
