#!/usr/bin/env python3
"""
contact_sheet.py — Step 2 视觉自检 · 跨页接触表生成器

用途：
  - 把 N 张绘本参考图拼成一张 2 列 (or K 列) contact sheet
  - 每格左/上方标文件名（便于跨图比对）
  - 输出 JPG 给 vision_analyze 或 browser_vision 做"一次性跨图核对"

使用：
  python3 scripts/contact_sheet.py <图目录> --out contact.jpg --cols 2 --max-width 640

适用场景：
  - vision_analyze 单图调用与 browser_vision 对同一张图结果不一致
    → 拼 contact sheet 后用 browser_vision 一次看完 = 跨图一致性核对
  - 需要快速看 N 张图的顺序/朝向/构图差异
  - Step 2 视觉自检的"5 项必查"中朝向突变跨图比对

依赖：Pillow
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DEFAULT_LABEL_HEIGHT = 28
DEFAULT_CELL_HEIGHT = 380


def build_sheet(
    image_dir: Path,
    out_path: Path,
    cols: int = 2,
    max_width: int = 640,
    cell_height: int = DEFAULT_CELL_HEIGHT,
) -> int:
    """Return number of images included in the sheet."""
    suffix_set = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    paths = sorted(
        [p for p in image_dir.iterdir() if p.suffix.lower() in suffix_set],
        key=lambda p: (
            int(p.stem) if p.stem.isdigit() else p.stem
        ),
    )
    if not paths:
        raise SystemExit(f"no images in {image_dir}")

    rows = (len(paths) + cols - 1) // cols
    cell_w = max_width + 20  # 10px 左右 padding
    cell_h = cell_height + DEFAULT_LABEL_HEIGHT

    canvas = Image.new("RGB", (cell_w * cols, cell_h * rows), "#dddddd")
    draw = ImageDraw.Draw(canvas)

    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((max_width, cell_height))
        r, c = divmod(i, cols)
        x0 = c * cell_w + (cell_w - im.width) // 2
        y0 = r * cell_h + DEFAULT_LABEL_HEIGHT + (cell_height - im.height) // 2
        canvas.paste(im, (x0, y0))
        draw.text((c * cell_w + 12, r * cell_h + 6), p.name, fill="black")

    canvas.save(out_path, quality=92)
    return len(paths)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a contact sheet for picturebook reference images."
    )
    parser.add_argument("image_dir", type=Path, help="Directory containing the N images")
    parser.add_argument("--out", type=Path, default=Path("contact_sheet.jpg"))
    parser.add_argument("--cols", type=int, default=2)
    parser.add_argument("--max-width", type=int, default=640)
    parser.add_argument("--cell-height", type=int, default=DEFAULT_CELL_HEIGHT)
    args = parser.parse_args()

    count = build_sheet(
        args.image_dir,
        args.out,
        cols=args.cols,
        max_width=args.max_width,
        cell_height=args.cell_height,
    )
    print(f"wrote {args.out} with {count} images ({args.cols} cols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
