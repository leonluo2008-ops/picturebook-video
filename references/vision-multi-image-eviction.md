# vision_analyze 多图并行调用被 evict 现象（2026-06-16 I love you 我爱你 绘本踩坑）

## 现象（必读）

调用 `vision_analyze` **多图并行**（一次 function_calls 块里同时 vision_analyze 5+ 张图）时，**前几张图的图片会被 evict 出上下文**，返回里带 `screenshot removed to save context` 标记。**只有最后 1-3 张图的图能真正被看到**。

## 实际表现（实测 2026-06-16）

- 本绘本 9 张图，**vision_analyze 9 张并行** → 返回里图全部标 `screenshot removed`
- 后续单独 vision_analyze 4 张并行 → 看到 4、5、6 三张，**7、8、9 又被 evict**
- 最后必须 **2 张或 3 张一组串行调用** 才能稳定看到全部图
- 单图调用 100% 稳定

## 根因（推测）

- `vision_analyze` 多图并行时，**图片数据是 base64 内嵌在同一条 message 里**
- 多张大图（绘本每张 ~150KB）一起塞进 = 单条 message token 超上限
- 客户端（或服务端）自动 evict 早先的 image parts，只保留最新的几张
- **不是工具 bug，是 message token 容量限制**

## 修复范式（绘本/任何 N 张图必走）

```python
# ❌ 反模式：N 张图一次 vision_analyze 并行
vision_analyze(1.jpg), vision_analyze(2.jpg), vision_analyze(3.jpg), vision_analyze(4.jpg), vision_analyze(5.jpg), vision_analyze(6.jpg), vision_analyze(7.jpg), vision_analyze(8.jpg), vision_analyze(9.jpg)

# ✅ 正确范式：分批串行调用，每批 ≤ 3 张图
vision_analyze(1.jpg), vision_analyze(2.jpg), vision_analyze(3.jpg)   # 第一批
# 看到 1, 2, 3 后再
vision_analyze(4.jpg), vision_analyze(5.jpg), vision_analyze(6.jpg)   # 第二批
# 看到 4, 5, 6 后再
vision_analyze(7.jpg), vision_analyze(8.jpg), vision_analyze(9.jpg)   # 第三批
```

或者**单图调用最稳**（绘本 9 张图 = vision 9 次 = token 9 次，但 100% 看到全部图）。

## 判定口诀

- 看到 `screenshot removed to save context` 标记 = 图被 evict = 没看到图
- **必重看**（不靠"我以为我看过了"的记忆）
- 单图调用 = 稳 · 2-3 张并行 = 试 · 4+ 张并行 = 必 evict

## 与 Step 2 vision 自检铁律的配合

picturebook-video SKILL.md 铁律 #2 = **vision 必全 N 张图（不抽样）**。

- 这个铁律的精神 = "每张图必看到"
- vision 工具层面 = **"每张图必真正被我看到，不是返回 status 成功就以为看到了"**
- 必跑判定：每次 vision_analyze 返回后**扫一眼返回内容** = 有没有 `screenshot removed` 标记
- 有 = 必重看该图
- 没有 = 真看到了，可以继续

## 反模式（必避）

- ❌ "我 vision 9 张图了"= 凭 status 成功 = **没看到 = 0 信息量**
- ❌ "我描述了图"= 但描述来自前一次会话的缓存记忆 = **跨会话记忆失效 = 凭印象拼 prompt = 翻车**
- ❌ "并行效率高"= 在 vision 场景 = **过早优化 = 信息丢失**
- ✅ "分批 ≤ 3 张串行 + 每次返回都判定有没有 screenshot removed 标记"

## 跨 skill 适用

任何需要 vision N 张图的场景：
- 绘本视频（picturebook-video · 本场景）
- 漫剧分镜（ai-drama）
- 账号运营封面图调研（douyin-ops）
- 多图 prompt 工程（任何 image_gen 场景）
