# case-37 · 画面静止反例(v5.0.10 核心新增)

> **状态**: ✅ 工程实测完成, 视频实测待绘本 agent 跑。
> **完整报告**: `cases/lettuce-evals/REPORT.md`(包含 4 个 v8.1 prompt 全文 + verify_prompt.py 验证结果)
> **触发场景**: v5.0.9 prompt 在生菜 SRT 上跑出"画面几乎静止"问题, 驱动 v5.0.10 重构。

---

## 问题描述

用户实测当前 v5.0.9 skill 生成画面"非常呆板, 几乎是静止的", 与设计初衷相反。

**根因**(v5.0.10 诊断):
1. **段 2 思维是"运镜"** — "镜头缓慢推近" 这种写法, 镜头在动但主体本身是死的
2. **段 4 收尾用凝固语** — "镜头持续循环不切断" 让画面趋向凝固
3. **时间锚点缺失** — prompt 没跟旁白时间点对齐, 主体在哪个时间点做什么动作不明
4. **段间停顿被忽略** — 领读型段间停顿是设计意图, 不是切换点, 但 v5.0.9 当作"画面切换点"

---

## 实测对比

### v5.0.9 baseline (3 FAIL)

```
镜头 1: 一颗结球生菜, 中景, 参考图 @Image1
镜头 2: 镜头缓慢推近
镜头 3: 旁白: 生菜 LETTUCE! 一颗圆圆的绿生菜, lettuce
镜头 4: 镜头持续循环不切断
总时长: 6.9s
```

verify_prompt.py 检测:
```
❌ FAIL R1/R4: prompt 缺 SRT 时间锚点
❌ FAIL R3: 凝固语命中 '持续循环不切断'
❌ FAIL R3: 凝固语命中 '持续.*?循环'
⚠️  WARN #37: 单镜头时长倾向
ok: false
```

### v8.1 重写 (4 个 prompt 全 ok)

每个 clip 段 2 含 4-6 个时间点列主体动作, 段 3 用 SRT 时间戳精确锚定, 段 4 保持运动状态过渡。

verify_prompt.py 检测 4 个 v8.1 prompt: 全 ok=true (只有 1 个无害 WARN #37 单镜头时长偏好)

完整 4 个 prompt 见 `cases/lettuce-evals/prompts/clip{1-4}_v81_prompt.txt`

---

## 关键数据(SRT 反推)

- 总段数: 8, 对应 8 张生菜参考图
- 总朗读: 22.5s, 总停顿: 7.766s, 总时长: 30.266s
- **反推速率**: 中文 1.78 字/秒 (vs v5.0.9 默认 4.0 字/秒 → 偏差 125%)
- 段间停顿: 全 ≥ 0.8s (领读型节奏, 不是切换信号)

---

## seedance 实测(留待绘本 agent)

实际视频生成需要 ARK_API_KEY + mcp_seedance_* 工具, 在 huiben profile 环境跑。

绘本 agent 操作步骤 + 视频对比截图归档 → 见 `cases/lettuce-evals/REPORT.md` 末尾"seedance 实测"段。

---

## 关联

- **`cases/lettuce-evals/REPORT.md`**: 完整实测报告(本 case 主文档)
- **`cases/lettuce-evals/prompts/`**: 4 个 v8.1 prompt + 1 个 v5.0.9 baseline prompt
- **`cases/lettuce-evals/timeline.json`**: SRT 解析后的 JSON 时间轴
- **`references/v8-action-template.md`**: v8.1 完整模板
- **`scripts/srt_parser.py`** / **`scripts/clip_merger.py`**: SRT 路径工具
- **`scripts/verify_prompt.py` R1/R3**: 自动化检测
- **case-26**: 参考图是起点不是限制 (v8.1 强化为"动作起点")
- **case-33 升级版**: 旁白优先逐段合并 (v5.0.10 加 SRT 真实秒数)