# Vision 跨图一致性核对 · Step 2 Pattern

> **场景**：Picturebook Step 2 视觉自检时，`vision_analyze` 单图调用与 `browser_vision` 对同一张图返回**互相矛盾**（人物朝向 / 是否有人物 / 文字内容），或需要跨 N 张图比对**朝向突变 ≥90°**（硬约束 #7）。
>
> **来源**：2026-07-15 Bridge 桥绘本实测 · @Image6（女孩朝左/朝右矛盾）、@Image7（有人/无人矛盾）跨 vision 调用打架，靠 contact sheet + 本地 HTTP + browser_vision 解决。

## 4 步法

### Step 1 · 生成 contact sheet

```bash
python3 ~/.hermes/skills/creative/picturebook-video/scripts/contact_sheet.py \
  /path/to/image_dir \
  --out /path/to/image_dir/contact_sheet.jpg \
  --cols 2 --max-width 640
```

按文件名数字顺序拼，每格上方黑字标签文件名（agent 跨图比对定位用）。依赖 PIL。

### Step 2 · 启动本地 HTTP

```bash
cd /path/to/image_dir
python3 -m http.server 8765 --bind 127.0.0.1
```

⚠️ 必加 `--bind 127.0.0.1` —— 避免默认监听 0.0.0.0。

### Step 3 · browser_vision 看 contact sheet（独立像素管线）

```python
browser_navigate("http://127.0.0.1:8765/contact_sheet.jpg")
browser_vision(question="逐格精确核对...")
```

browser_vision 是直接读像素的另一条视觉管线，**比 vision_analyze 的上下文幻觉抗干扰更强**。如某格模糊可单图溯源：

```python
browser_navigate("http://127.0.0.1:8765/6.jpg")
browser_vision(question="只描述这一张...")
```

### Step 4 · 关闭 HTTP

```bash
kill <PID>  # 或 process(action='kill', session_id=...)
```

## 哪个 vision 调用更可信？

| 来源 | 可信度 | 原因 |
|------|--------|------|
| `browser_vision`（基于像素直读） | **最高** | 直接读像素，跨上下文干扰小 |
| `vision_analyze`（单图） | 中 | 偶尔返回矛盾（推测 vs 看像素） |
| `vision_analyze`（多图批量） | 中 | 易丢细节，需独立复核 |

**打架时**：以 `browser_vision` 为准；vision_analyze 多图批量的结果作为**初筛**而非定论。

## 反模式（必避）

- ❌ 同一张图多次 vision_analyze 互相矛盾时反复重试（浪费时间，仍是同一个模型）
- ❌ 信任 vision_analyze 对本地图片的"推测"（如"这是一张卡通小女孩"）而不校验像素
- ❌ contact sheet 拼图后不放文件名标签 —— 跨图比对无法定位
- ❌ contact sheet 用 `--cols 1` —— N 张竖排浪费屏幕高度
- ❌ 跳过 Step 4 关闭 HTTP —— 本地端口长期开放

## 校验清单

- [ ] contact sheet 每格有文件名标签
- [ ] contact sheet 在浏览器中实际渲染清晰
- [ ] browser_vision 看 contact sheet 返回的事实与各 vision_analyze 单图结果交叉验证
- [ ] 跨图朝向矩阵已写入 `image-inventory.md`（参考硬约束 #7）
- [ ] HTTP server 已停（kill PID）
- [ ] image-inventory.md 已读 → 不评价图文矛盾（硬约束 #9 · 素材已审核不挑矛盾）

## 相关

- 硬约束 #7：`references/case-39-orientation-transition.md` + `references/multi-image-facing-mismatch-fix.md`
- 硬约束 #9：`SKILL.md §1`（素材已审核不挑矛盾）
- 配套脚本：`scripts/contact_sheet.py`（本仓内）
