"""
Seedance 2.0 MCP Server · picturebook-video v5.0 集成版
========================================================

⚠️ 这是从 seedance2.0-tool/spikes/001-mcp-uguu-server/ 整合过来的精简版
   集成原因（v5.0 2026-06-16）：避免 picturebook-video 依赖 seedance2.0-tool 仓
   单仓安装 = 完整可用，不依赖外部仓

Tools exposed（自动注册成 mcp_seedance_*）：
- generate_video      提交任务，返回 task_id
- check_task          查询任务状态（queued/running/succeeded/failed）
- wait_and_download   同步等待 + 自动下载（绘本单 clip 场景）
- verify_api_key      0 元 list 端点检测 API key 有效性（不扣费）

设计原则（来自绘本实战沉淀）：
- duration [4, 15] 硬限制（inputSchema 强制）
- watermark 默认 'none'（绘本场景专精）
- duration 必须是整数（避开 argparse '7.5' → invalid int 坑）
- 已发任务 = 已扣费 = 绝不重提交（check_task docstring 必含警示）

环境变量（必填）：
- ARK_API_KEY  火山引擎 Ark API Key（由 wrapper.sh 从 .env 加载）
"""

import os
import sys
import json
import time
import hashlib
import asyncio
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# ===== 业务函数委托给 seedance_uploads（单真源）=====
# 所有上传 / Ark API / body 构造逻辑都在 seedance_uploads.py
# 本文件只在 MCP protocol 层面加壳（list_tools / call_tool）
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import seedance_uploads as U  # noqa: E402


# ===== MCP Server 初始化 =====
server = Server("seedance")

# 默认参数
DEFAULT_MODEL = "doubao-seedance-2-0-fast-260128"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"


# ===== 业务包装层（薄壳委托给 seedance_uploads）=====
def _upload_to_uguu(local_path: str, mime_type: str) -> str:
    return U.upload_to_uguu(local_path, mime_type)


def _resolve_url(input_str: str, kind: str) -> str:
    return U.resolve_url(input_str, kind)


async def _upload_to_uguu_async(local_path: str, mime_type: str) -> str:
    return await U.upload_to_uguu_async(local_path, mime_type)


async def _resolve_url_async(input_str: str, kind: str) -> str:
    return await U.resolve_url_async(input_str, kind)


async def _resolve_all_inputs_async(args: dict) -> dict:
    return await U.resolve_all_inputs_async(args)


def _get_ark_key() -> str:
    return U.get_ark_key()


async def _ark_request_async(method: str, url: str, data: dict = None, timeout: int = 60) -> dict:
    return await U.ark_request_async(method, url, data, timeout)


def _build_body(args: dict, resolved_urls: dict = None) -> dict:
    return U.build_body(args, resolved_urls)


# ===== MCP Tools 定义 =====
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_video",
            description=(
                "提交 Seedance 2.0 视频生成任务，立即返回 task_id。"
                "已发任务 = 已扣费，绝不重提交。推荐用 wait_and_download 同步等待。\n\n"
                "[绘本/动画场景推荐参数]\n"
                "  - watermark: 'none'（默认，无 AI 水印）\n"
                "  - duration: 按镜头数算法（5s=2-3 镜 / 8s=3-4 镜 / 12s=4-5 镜 / 14s=5-6 镜）\n"
                "  - ratio: '16:9'（横屏绘本）/ '9:16'（抖音/小红书竖屏）\n"
                "  - generate_audio: true（绘本有声场景 v5.0.6 起 · 自动加音效 + 旁白）；BGM 由 prompt 末尾约束 No background music 排除\n"
                "  - prompt: 必带末尾约束段（No background music, no on-screen text · v5.0.6 起允许人声/音效）\n"
                "  - 多图参考用 ref_images（不用 image+last_frame）\n\n"
                "[通用/社媒场景推荐参数]\n"
                "  - watermark: 'platform'（不加 AI 水印）\n"
                "  - duration: 8-12s\n"
                "  - ratio: '9:16'（抖音/小红书）\n\n"
                "⚠️ 硬限制\n"
                "  - duration 必在 [4, 15]（API 拒绝范围外）\n"
                "  - duration 必为整数\n"
                "  - 已发任务 = 已扣费，绝不重提交同 task_id"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "文字提示词"},
                    "ref_images": {"type": "array", "items": {"type": "string"},
                                   "description": "参考图片（角色参考）。本地路径或 URL。"},
                    "image": {"type": "string", "description": "首帧图片（first_frame）"},
                    "last_frame": {"type": "string", "description": "尾帧图片（绘本场景禁用）"},
                    "video_refs": {"type": "array", "items": {"type": "string"},
                                   "description": "参考视频（动作模仿）"},
                    "audio_refs": {"type": "array", "items": {"type": "string"},
                                   "description": "参考音频（绘本 BGM）"},
                    "duration": {"type": "integer", "minimum": 4, "maximum": 15,
                                 "description": "API 硬限制 [4,15] 秒"},
                    "ratio": {"type": "string",
                              "enum": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "adaptive"],
                              "default": "16:9",
                              "description": "画幅。绘本 16:9 / 抖音 9:16 / 朋友圈 1:1"},
                    "watermark": {"type": "string",
                                  "enum": ["none", "platform", "seedance_ai"],
                                  "default": "none",
                                  "description": "水印策略：'none' 绘本/动画 / 'platform' 社媒 / 'seedance_ai' 测试"},
                    "generate_audio": {"type": "boolean", "default": False,
                                       "description": "绘本默认 false；有声绘本 true"},
                    "resolution": {"type": "string", "enum": ["480p", "720p", "1080p"],
                                   "default": "720p"},
                    "model": {"type": "string", "default": DEFAULT_MODEL,
                              "description": "doubao-seedance-2-0-fast（默认）/ doubao-seedance-2-0（高质量慢）"},
                    "seed": {"type": "integer", "description": "随机种子（-1=随机）"},
                    "camera_fixed": {"type": "boolean"},
                    "service_tier": {"type": "string", "enum": ["default", "flex"]},
                },
                "required": ["duration"],
            },
        ),
        types.Tool(
            name="check_task",
            description=(
                "查询任务状态（queued/running/succeeded/failed）。\n"
                "⚠️ 已发任务 = 已扣费，绝不重提交同 task_id。"
            ),
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string", "description": "Seedance 任务 ID（cgt- 开头）"}},
                "required": ["task_id"],
            },
        ),
        types.Tool(
            name="wait_and_download",
            description="同步等待任务完成 + 自动下载到本地（绘本单 clip 场景用）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "output_path": {"type": "string", "description": "本地保存路径（.mp4）"},
                    "timeout_sec": {"type": "integer", "default": 300, "maximum": 600},
                    "poll_interval_sec": {"type": "integer", "default": 15},
                },
                "required": ["task_id", "output_path"],
            },
        ),
        types.Tool(
            name="verify_api_key",
            description="0 元 list 端点检测 API key 有效性（不扣费）。",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "generate_video":
            # 先并发上传所有本地文件到 uguu
            resolved_urls = await _resolve_all_inputs_async(arguments)
            body = _build_body(arguments, resolved_urls=resolved_urls)
            result = await _ark_request_async("POST", ARK_BASE_URL, body, timeout=60)
            task_id = result.get("id")
            if not task_id:
                raise RuntimeError(f"no task_id in response: {result}")
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task_id,
                    "status": result.get("status", "queued"),
                    "model": body["model"],
                    "duration": body["duration"],
                    "ratio": body["ratio"],
                    "_note": "task submitted. 已扣费。use check_task to query status.",
                }, ensure_ascii=False, indent=2),
            )]

        elif name == "check_task":
            task_id = arguments["task_id"]
            result = await _ark_request_async("GET", f"{ARK_BASE_URL}/{task_id}", timeout=30)
            out = {
                "task_id": task_id,
                "status": result.get("status"),
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at"),
            }
            content = result.get("content") or {}
            video_url = content.get("video_url")
            if video_url:
                out["video_url"] = video_url
                out["_note"] = "video_url 24h 有效，及时下载。过期调 check_task 拿新 URL。"
            if result.get("error"):
                out["error"] = result["error"]
            return [types.TextContent(type="text", text=json.dumps(out, ensure_ascii=False, indent=2))]

        elif name == "wait_and_download":
            task_id = arguments["task_id"]
            output_path = arguments["output_path"]
            timeout = arguments.get("timeout_sec", 300)
            poll = arguments.get("poll_interval_sec", 15)
            deadline = time.time() + timeout

            while time.time() < deadline:
                result = await _ark_request_async("GET", f"{ARK_BASE_URL}/{task_id}", timeout=30)
                status = result.get("status")
                if status == "succeeded":
                    video_url = result.get("content", {}).get("video_url")
                    if not video_url:
                        raise RuntimeError(f"succeeded but no video_url: {result}")
                    client = await U.get_http_client()
                    dl_resp = await client.get(video_url, timeout=120)
                    dl_resp.raise_for_status()
                    data = dl_resp.content
                    out_p = Path(output_path)
                    out_p.parent.mkdir(parents=True, exist_ok=True)
                    with open(out_p, "wb") as f:
                        f.write(data)
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "task_id": task_id,
                            "status": "succeeded",
                            "output_path": str(out_p),
                            "size_bytes": len(data),
                            "md5": hashlib.md5(data).hexdigest(),
                        }, ensure_ascii=False, indent=2),
                    )]
                elif status == "failed":
                    err = result.get("error", {})
                    raise RuntimeError(f"task failed: {err}")
                time.sleep(poll)
            raise RuntimeError(f"timeout after {timeout}s")

        elif name == "verify_api_key":
            try:
                result = await _ark_request_async("GET", f"{ARK_BASE_URL}?page_size=1", timeout=15)
                return [types.TextContent(type="text", text=json.dumps({
                    "valid": True,
                    "key_prefix": _get_ark_key()[:8] + "...",
                    "response_keys": list(result.keys()) if isinstance(result, dict) else str(type(result)),
                }, ensure_ascii=False, indent=2))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({
                    "valid": False,
                    "error": str(e),
                }, ensure_ascii=False, indent=2))]

        else:
            raise ValueError(f"unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e), "tool": name, "arguments": arguments}, ensure_ascii=False, indent=2),
        )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
