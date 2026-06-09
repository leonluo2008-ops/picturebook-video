# v7 vs v15 范式路由决策（v1.0.4 新增 · Horse 绘本踩坑沉淀）

> **核心问题**：不是所有绘本都调 C 子 agent。领读型绘本走 v7 2图=1Clip 合并 = 主 agent 直拼 prompt。
> **根因**：v15 4 段范式 + `fill_v15_template.py` 只支持**单图 @ImageN**，**2图=1Clip 合并必走 v7 范式**（cactus 8 段结构）。

## 1. v7 范式 vs v15 范式 速查

| 维度 | **v7 范式** | **v15 4 段范式** | **v6 5 段范式** |
|---|---|---|---|
| 适用 | 领读/认知/认字绘本 | 叙事/冒险/收势向 | 领读 + 文字全程可见 |
| 切分 | 2图=1Clip 合并（≤2 张）| 单图 1Clip | 单图 1Clip |
| 段数 | 8 段固定结构 | 4 段骨架 | 5 段（v15 + 文字持续可见段）|
| 调 C？ | ❌ 不调（主 agent 直拼）| ✅ 调 C 产原料 | ✅ 调 C 产原料 |
| 填模板 | 走 `assets/example-prompts/cactus-clip1-v7.txt` 真模板 | `scripts/fill_v15_template.py --version v15` | `scripts/fill_v15_template.py --version v6` |
| 典型 | Cactus 4 Clip 37s / Horse 5 Clip 48s | Pic2 Please 8 Clip 47s | Pic5 Bird 8 Clip 50.66s |
| 范式 prompt 文件 | `cactus-clip1-v7.txt` 8 段 | v15 4 段骨架 | v6 5 段骨架 |

## 2. v7 范式判定 5 条件（**必全过 · 铁律 #89**）

1. ✅ **领读/认知/认字绘本**（不是叙事型）—— 例：单词/字母教学、家族词组集合、动物认知
2. ✅ **弱情节**（无明显"前一幕→后一幕"情节推进）—— 例：同一主角不同动作展示
3. ✅ **旁白每段 < 8s**（按 0.3s/字算）—— 英文 0.3s/词
4. ✅ **图片风格统一**（同色系/同主体/相邻景别）—— 例：Eric Carle 拼贴风全 8 张
5. ✅ **总图数 6-10 张**（多了需要更细分段）

**5 条件任一不满足 → 走 v15 4 段范式 + 调 C**。

**反模式**：绘本有 3 张图风格不同 + 1 段超 8s 旁白 → 强行走 v7 合并 = 翻车（段超 8s 拼一起 = 节奏拖慢 + 风格不统一 = 画面跳）。

## 3. v7 范式 8 段固定结构（真模板）

完整示例：`assets/example-prompts/cactus-clip1-v7.txt`（Cactus Clip 1 已跑通示例 · 任务 ID `cgt-20260602171645-s5fq6`）

```
This is a storyboard reference image sequence; render the following images in time order as separate shots within one continuous video;
from 0.0s to 1.2s @Image1 is the opening shot, in this shot [...], then [稳态];
from 1.2s to 8.0s @Image2 is the second shot, in this shot [...], then [稳态];
final frame: the camera locks completely, [画面描述], the scene holds its final pose;
Storyboard Audio Description: 0.0s to 1.2s [音效1], 1.2s [音效2], 1.2s to 8.0s [持续音/静默];
No background music, no human voice, no narration, no singing;
Children's picture book [风格] style, [主调+辅助], [氛围].
```

**8 段解析**：
| 段 | 必含 | 作用 |
|---|---|---|
| 1 | `This is a storyboard reference image sequence` | 分镜引导（v7 标志） |
| 2-3 | `from X.Xs to Y.Ys @ImageN is the ... shot, in this shot [动作], then [稳态]` | 镜头序列（2 镜头 = 1 段合并） |
| 4 | `final frame: the camera locks completely` | 收势词（不是定格海报 · 含画面微动） |
| 5 | `Storyboard Audio Description: X.Xs to Y.Ys [音效]...` | 音频独立段（精准控制卡点） |
| 6 | `No background music, no human voice, no narration, no singing` | 音频禁令段（v7 关键 · 靠 prompt 控制静音） |
| 7 | `Children's picture book [风格] style` | 风格锁定（Eric Carle / 高饱和暖色 / 童趣调） |
| 8 | 句号 `.` 收尾 | 标记 prompt 结束 |

**11 项自检清单**（v7 真模板全过）：
- ✅ 段数 = 8
- ✅ 分号数 = 7
- ✅ 句号数 ≤ 9
- ✅ 段 4 含 `final frame`
- ✅ 段 5 以 `Storyboard Audio Description:` 开头
- ✅ 段 6 以 `No background music` 开头
- ✅ 段 7 以 `Children's picture book` 开头
- ✅ 段 7 末尾有 1 个句号收尾
- ✅ 视觉段（1-4）无 `no / no BGM / no speech`
- ✅ 无独立 `[Sound effect: ...]` 块（音效写在段 5）
- ✅ 收势词在最后一句画面描述里

## 4. v7 范式总时长公式

| 模式 | 公式 | 适用 | 实测 |
|---|---|---|---|
| 标准模式 | 8s + 8s + 9s + 10s = 35s | 旁白短，氛围优先 | Red 绘本 |
| TTS 优先不压缩 | 8s + 9s + 10s + 10s = 37s | 旁白长，2 段合 1 clip 时 TTS 需要足够时间 | Cactus 绘本 |
| 用户自定义 | 合并段 TTS + 0.5-1.5s 缓冲 | 用户给硬约束（如 Horse R7=14s 实测）| Horse 5 Clip 48s |

**原则**：
- 合并 clip 时长 = **各段 TTS 旁白时长之和 + 0.5-1.5s 缓冲**
- **不**为了对齐"标准 35s"压缩时长 —— 冗余给后期剪辑留余地

**单 Clip 时长边界**：
- **下限**：seedance 4s 物理最低（实测 ≥4s）
- **上限**：seedance **15s 物理上限**（铁律 #90）
- **8s < x ≤ 15s 合法** —— v5 公式档位 5/6/7/8s 是参考范围，**不是上限**

## 5. v7 范式必填 seedance 参数

```bash
python3 seedance.py create \
  --image <段首图> \              # 锁首帧
  --last-frame <段尾图> \         # 锁尾帧
  --prompt "<v7 8 段 prompt 文本>" \
  --duration 8/8/9/10 \            # 整数 · 4s ≤ x ≤ 15s
  --ratio 16:9 \
  --generate-audio true \          # v7 范式必 true（靠 prompt 禁令段控制静音）
  --wait \
  --download ./clip{N}_v7.mp4
```

**--generate-audio 例外**（铁律 #86）：
- 家族词组集合（≥3 词 + 同字母家族重复）= `--generate-audio false` + TTS 音轨对齐
- 长句（words_en ≥ 5 OR words_zh ≥ 8）= 同上
- 普通短句/单词 = 默认 true（v7 范式靠 prompt 禁令控制）

## 6. v7 vs v15 决策树（主 agent 必跑）

```
Step 1 绘本类型判别
  │
  ├── 领读/认知/认字 + 弱情节 + 段 <8s + 风格统一 + 6-10 图？
  │   │
  │   ├── 5 条件全过 → v7 范式
  │   │   ├── 走 leading-reading-4clip-pattern.md
  │   │   ├── 主 agent 直拼 8 段 prompt（不调 C）
  │   │   ├── 真模板：assets/example-prompts/cactus-clip1-v7.txt
  │   │   └── 总时长公式：8s + 8s + 9s + 10s = 35s（标准）
  │   │
  │   └── 任一不满足 → v15 4 段范式
  │       ├── 调 C 子 agent 产 11 维原料 JSON
  │       ├── 主 agent 填 scripts/fill_v15_template.py
  │       ├── 模板：--version v15（4 段）或 --version v6（5 段 + 文字持续可见）
  │       └── 总时长 = B 输出（v5 公式 · 整数 · 末帧静默 ≥ 2s）
  │
  └── 收势/冒险/叙事型 → 必走 v15 4 段 + 调 C
```

## 7. Horse 绘本实战踩坑复盘（v1.0.4 沉淀）

### 错误路径（v1.0.3 之前）
1. 调 C 子 agent 跑 5 段分镜 → C 输出 5 个 clip JSON（schema 包含 image_files.first_frame + last_frame）
2. 想用 `scripts/fill_v15_template.py` 填 v6 5 段 → **fill 脚本只支持单图 @ImageN**（`clip['image_index']` 单值）
3. 拼 v7 8 段结构 prompt → **没真模板**（`references/分镜时序-prompt范式-v7.md` 引用了但仓里**无此文件**）
4. 反复横跳："先拍 5 段 2图=1Clip v15" / "再改 6 段 43s" / "还是 5 段 48s v15"——**没走到 v7 范式真路径**

### 正确路径（v1.0.4 修复）
1. Step 1 启动前 6 必问 #5 范式 → **判 v7**（领读型 + 弱情节 + 段 <8s + 风格统一 + 6-10 图 = 5 条件全过）
2. **不调 C**（v7 不需要 C）
3. 主 agent 直拼 5 段 v7 8 段结构 prompt（真模板 `cactus-clip1-v7.txt` 改字段）
4. `--image` 传 1.jpg + `--last-frame` 传 2.jpg（v7 范式支持 2 图）
5. 单 Clip 14s 合法（8s < 14s ≤ 15s 物理上限）

### 关键修复点
- ✅ Step 3.0 加 v7/v15 路由决策表
- ✅ Step 1 #5 范式行默认改 v7（之前默认 v6）
- ✅ 真模板路径 `assets/example-prompts/cactus-clip1-v7.txt` 在 SKILL.md 强引用
- ✅ 铁律 #89-#92 在新版本速查区抬头可见
- ✅ 文档：v1.0.4 SKILL.md breaking_changes 标记 v7 强路由

## 8. 关联 references

- `references/leading-reading-4clip-pattern.md`（**v7 范式总设计** · 必读）
- `references/长旁白拆分规范-v15.1.md`（**v15 范式拆分** · 触发条件 > 15s）
- `references/v15-4段骨架-模板.md`（v15 4 段结构）
- `references/v6-5段骨架-模板.md`（v6 5 段结构）
- `assets/example-prompts/cactus-clip1-v7.txt`（v7 8 段结构真模板）
- `assets/example-prompts/cactus-clips-2-3-4-v7.txt`（v7 8 段结构 Clip 2-4 真模板）

## 9. 一句话决策口诀

> **领读绘本 = 5 条件全过 → v7 范式 = 主 agent 直拼 = 不调 C = 走 cactus 真模板**
> **叙事绘本 = 任一不满足 → v15 4 段 = 调 C 产原料 + fill 脚本填**
> **8s < x ≤ 15s = 合法长 Clip · 16s+ = 走 v15.1 拆**
