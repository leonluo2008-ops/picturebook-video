# Prompt 视觉逻辑审查清单（L3 目检层）

> 沉淀自 2026-08-18 饼干 biscuits 8 图 + 巧克力 chocolate 8 图两次实测审查。verify_prompt.py 全部通过（0 failures）后，
> 仍有 3 类视觉逻辑错误只有目检能抓到 —— 本文件是目检层的操作清单。
> 主用途：主 agent 写完 v8.1 prompt 后、提交前的视觉审查（对应 prompt-reviewer 子 agent 清单 #9「视觉逻辑」）。

## 1. 审查顺序（实测跑通的管线）

```
定位 prompt 文件（见 §7 素材定位）
    ↓
读 SRT + timeline.json（拿逐字旁白 + 分段时长 + pause_after）
    ↓
verify_prompt.py 硬规则（--ref-images N --tts-seconds S --generate-audio --has-srt）→ 0 failures 才继续
    ↓
逐镜头 grep 运镜/空间目标（four-piece-shot-spec §10.4 自检脚本）
    ↓
vision 目检参考图 vs prompt 描述（本文件 §3 批量法 / §4 逐图五问）
    ↓
SRT 逐字比对段 3/段 5 旁白文本（含标点）；旁白触发词必须在对应 SRT 段文本内
    ↓
跨 Clip 对位（§5.3 切点检查）
    ↓
输出结构化 JSON {passed, violations[], warnings[], suggestions[]}
    ↓
存档 workdir/prompt-review.json（可追溯）
```

## 2. 三类脚本抓不到的盲区（饼干实测全部命中）

### 2.1 方向词视角翻转（正面朝向主体）

**案例**：prompt 写「松鼠右手把巧克力曲奇**从画面右侧**送到嘴边」。
实图 7.jpg 松鼠**正面朝观众** → 松鼠的右手（持曲奇）位于**画面左侧**，左手端牛奶在画面右侧。方向整个写反。

**规则**：正面朝向（面向观众）的角色，**角色右手 = 画面左侧**（镜像）。写动作方位时二选一：
- ✅ 用画面视角：「把曲奇**从画面左侧**送到嘴边」（先 vision 确认持物手在画面哪侧）
- ✅ 或干脆删方位词：「把曲奇送到嘴边咬一口」

**自检**：prompt 里每个「角色左右手 + 画面方位」组合，都问一句——角色是正面还是侧面？正面=镜像。

### 2.2 部分特征过度概括（some → all）

**案例**：prompt 写「星星饼干表面小孔透出光点」（暗示所有星星饼干都有孔）。
实图 4.jpg 两颗星星只有**右中那颗**有透气孔压痕，左下那颗光滑。动物饼干同理：鱼的眼睛是小孔凹陷，熊/兔是模具压痕非穿孔。

**规则**：参考图中**只有部分个体**拥有的细节，写「**其中一颗/其中一只**有 X」，不要泛化到全体。泛化后 seedance 可能在无孔个体上凭空画孔。

**自检**：写「X 们/X 形饼干都有 Y」之前，vision 确认是否每一个都有 Y；只部分有 → 改「其中」。

### 2.3 形状/成分措辞不精确

**案例**：prompt 写「红/蓝/绿/紫彩色**糖珠**」。实图 1.jpg 是**长条形糖粒**（jimmies），且含黄、白等色——形状（圆珠 vs 长条）和颜色清单都不精确。

**规则**：
- 颗粒物形状要 vision 确认后写：圆珠（nonpareils）vs 长条糖粒（jimmies）vs 块状
- 颜色清单不要凭印象列举——按 vision 实际返回的颜色写，宁少勿错

**同组可查项**：文字位置（印在主体表面 vs 背景空白处——1.jpg 黑「饼干」确实印在顶块饼干表面；这类要逐图确认不能想当然）、署名有无（3.jpg 右上角浅灰 Eric Carle 署名确实存在）。

## 3. 批量 vision 审查法（contact sheet）

N 张参考图逐张 vision_analyze 太贵；拼图批量查更快：

```python
from PIL import Image
for grp, name in [((1,2,3,4),'sheet_a.jpg'), ((5,6,7,8),'sheet_b.jpg')]:
    imgs = [Image.open(f'{i}.jpg').resize((640,400)) for i in grp]
    sheet = Image.new('RGB', (1280,800), 'white')
    for idx, im in enumerate(imgs):
        sheet.paste(im, ((idx%2)*640, (idx//2)*400))
    sheet.save(name)
```

- 每张 sheet 一次 vision_analyze，question 里**逐位编号确认**（左上=N.jpg…），把 prompt 中该组全部可验证断言列成确认问题
- **模糊细节再单图二跳**：哪些个体有小孔、文字印在哪、糖粒什么形状——sheet 上看不清就单图追问（本次 1.jpg/4.jpg 各补了一次单图确认）
- 与 SKILL.md §5 交叉验证法互补：§5 防「图整体认错」（幻觉级联），本节防「图认对了但细节断言错」

## 4. 参考图 vision 逐图五问（巧克力 8 图实测 · contact sheet 不可用/需逐图精查时）

每图固定问 5 项，与 prompt 段 1 逐图描述比对：

1. **英文文字**：内容 / **大小写** / 颜色（纯色 or 渐变拱形）/ 位置
2. **中文核心词**：逐字颜色 / 位置
3. **主体形态**：行×列 / 块数 / 摆放（扇形/叠放）/ 道具（包装纸/锡纸/围兜）
4. **背景**：颜色 / 质感（拼贴/水彩/纹理纸）
5. **画风**：拼贴 / 蜡笔手绘 / 混合媒介

**大小写逐图差异是重灾区**：巧克力实测 Image1 "CHOCOLATE" 全大写 vs Image2-8 "chocolate" 全小写——8 图逐张确认无一错位。

## 5. verify_prompt.py 调用与 WARN 假阳性目录（巧克力实测沉淀）

### 5.1 调用要点

- 脚本实际位置：`~/.hermes/skills/creative/picturebook-video/scripts/verify_prompt.py`（在 picturebook-video 主 skill 内；prompt-reviewer 子 skill 的 SKILL.md 旧指针写"本 skill 内"**已过时**）
- `--ref-images N`：该 Clip 覆盖的参考图数（逐个 @ImageN 数，非最大编号）
- `--generate-audio --has-srt`：双语领读绘本默认组合

### 5.2 WARN 假阳性目录（识别即 dismiss，勿让主 agent 返工）

| WARN | 根因 | 真问题判据 |
|---|---|---|
| #37「单镜头 ≤5s，发现 [15.0] 过长」 | 脚本把头部【总时长：15s】误读为单镜头秒数 | 仅当镜头段内写硬秒数（"前 3s 做 X"）才真 |
| R1/R4 无 MM:SS.mmm 时间锚点 | prompt 用事件锚点「念到 X 词时 Y 动作」= 官方认可等效写法 | 「X 词」不在 SRT 对应段文本内才真（映射断裂） |

### 5.3 `--tts-seconds` 推导 + 跨 Clip 切点检查

- `--tts-seconds S` 从 timeline.json 推导：**S = Clip 末段 end − Clip 首段 start**（不要问用户要）。
- **跨 Clip 对位**：Σ Clip 总时长 ≈ SRT 总时长（±1s）；**切点 = 下一 Clip 首段 start**，两 prompt 覆盖的段不重叠不遗漏。

实测例（巧克力，8 段 SRT 总 25.77s）：
- clip1 = 段 1-5（0.2 → 14.466s + 呼吸 ≈ 切点 15.2s）→ prompt 15s，tts=14.5，ref=5
- clip2 = 段 6-8（15.2 → 25.966s）→ prompt 11s，tts=10.8，ref=3
- 15 + 11 = 26s ≈ 25.77s ✓，切点 15.2s 无重叠 ✓

### 5.4 时长核对

- clip 内：旁白+停顿合计 ⊂ prompt 总时长（留呼吸余量）；段 3 写的呼吸停顿秒数与 timeline.json `pause_after` 对得上（±0.4s 内 dismiss；或建议删掉具体数字改模糊表述）

## 6. 判例库（巧克力 8 图双 prompt 实测）

| 判例 | 结论 |
|---|---|
| 「镜头固定」vs R11 | 合法 4 件套件 1（官方 §2 固定机位）；R11 只看空间目标关键词 + 主体位移 → 脚本 PASS 不算违例 |
| 连续 ≥2 个固定镜头 | 脚本 PASS 但镜头语言同质化 → 视觉 WARN（RP-26c 节奏层），建议换环绕/推近/拉远 |
| 逐图大小写锁定 | 参考**图内实际存在**的大小写变体 → 段 1 逐图如实描述 + 末尾约束「禁止大小写互相变形」双锁 = 标准写法（巧克力：Image1 大写、Image2-8 小写，各自锁定）。与 SKILL.md §16 鱿鱼案不矛盾：§16 禁的是 **prompt 凭空引入图中不存在的大写变体**（SQUID）；图中真有的变体必须如实描述 |
| 旁白触发词 | 「念到 X」的 X 必须在该段 SRT 文本内，否则映射断裂（真 FAIL 级问题，脚本不查） |
| RP-26b 情绪词 | 参考图本身带表情时豁免（图中奶牛本来就在眯眼笑 →「表情满足」可用；图中无表情则必须改成身体动作） |
| 末尾约束段 | 无字幕/Logo/水印/BGM + 「旁白词不得渲染为画面文字」+ 逐图大小写禁变形 = 三锁齐全 |

## 7. 素材定位（用户未给路径时的标准流程）

1. `ls -lat ~/.hermes/cache/documents/` → **mtime 最新的目录** = 当前会话素材目录。
   - 7z 附件命名 `doc_<hash>_视频.7z`，解压产物为 `video_extractN/`（N 递增，一天多包时靠 mtime 区分）。
   - prompt 命名两种：`<theme>_clipN_prompt.txt`（如 `choc_clip1_prompt.txt`）或 `clipN_prompt.txt`。
2. 目录内标准件：`N.jpg`（参考图）、`timeline.json`（SRT 解析产物）、`<主题>.srt`。
3. **干扰目录**（旧绘本素材，勿混）：`~/workspace/video_素材/`、`~/picturebook-video-work/`、各 `*_picturebook/`。
4. 全库兜底：`grep -rl "主题词" --include="*.srt" ~/.hermes/cache/documents/`。

## 8. 结构化输出

- 输出 JSON：`{passed, violations[], warnings[](带 clip 定位), suggestions[](可执行改法), checks{6项清单逐项+证据}, script_result, verified_at, verifier}`，存 `workdir/prompt-review.json`
- violations 为空 + 假阳性已 dismiss → `passed=true` → 主 agent 进 Step 6 提交
