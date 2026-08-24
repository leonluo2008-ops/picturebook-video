"""v5 冒烟测试：直接 import 时让 wrapper 路径正确 + dotenv 自动加载"""
import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 路径自动探测：基于本文件位置，不硬编码用户名/机器（跨电脑通用）
SKILL_MCP_DIR = Path(__file__).resolve().parent
ENV_FILE = SKILL_MCP_DIR / ".env"

load_dotenv(ENV_FILE)
print(f"ARK_API_KEY loaded, len={len(os.environ.get('ARK_API_KEY',''))}", flush=True)
print(f"SEEDANCE_BASE_URL={os.environ.get('SEEDANCE_BASE_URL','<默认官方>')}", flush=True)
print(f"SEEDANCE_MODEL={os.environ.get('SEEDANCE_MODEL','<默认>')}", flush=True)

sys.path.insert(0, str(SKILL_MCP_DIR))
import mcp_server
from mcp_server import call_tool

PROMPT = """A cute cartoon cat sitting on a wooden chair, paper craft collage style, simple background, 5 second test clip.

保持无字幕。
不要生成水印。
不要生成 Logo。
无人声、无歌唱、无配音、无朗读。"""


async def main():
    print("=== generate_video ===", flush=True)
    r = await call_tool("generate_video", {
        "prompt": PROMPT,
        "image": "https://n.uguu.se/bOYFChCy.jpg",
        "duration": 5,
        "ratio": "16:9",
        "watermark": "none",
        "generate_audio": False,
    })
    print(r[0].text, flush=True)
    data = json.loads(r[0].text)
    if "task_id" in data:
        tid = data["task_id"]
        print(f"task_id={tid}", flush=True)
        print("=== wait_and_download ===", flush=True)
        r2 = await call_tool("wait_and_download", {
            "task_id": tid,
            "output_path": "/tmp/pic_v5_test.mp4",
            "timeout_sec": 240,
            "poll_interval_sec": 20,
        })
        print(r2[0].text, flush=True)


asyncio.run(main())
