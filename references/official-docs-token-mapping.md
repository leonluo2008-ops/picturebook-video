# 即梦官方 SOP 文件 · 云盘 token 对照表

## 问题背景
官方导出的文件名与实际内容严重对不上——文件名和内容差了 3 个位置。
本文件由实吃亏验证（2026-05-26），记录正确的 token → 内容对应关系。

## 使用方法
1. 下载时按 token 判断内容，不要按文件名
2. 下载后读首行 `# 标题` 做二次确认
3. 本表是下载的唯一依据，不依赖文件名

## 正确映射（云盘文件夹 token: `TBUNf0P7qlBz43dMvwecPxq6nGe`）

| token | 实际内容（首行标题） | 推荐文件名 |
|-------|---------------------|-----------|
| `K3fDba7h8obp55xq3x9cnS6Sn6b` | video-sop - 即梦（Dreamina）视频创作标准工作流程 | `1-video-sop.md` |
| `U1RsbkaKfo9r3pxVkAAcRibonHf` | video-prompt - 分镜生视频技能 | `2-video-prompt.md` |
| `R4ijbDgbYogAmGx9qHrc74qFnoc` | story-ref-gen - 故事参考素材生成技能 | `3-story-ref-gen.md` |
| `XZDNbx1a2o2kTlxy44CcuSIHnHc` | scene-reflection - 分镜连贯性校验技能 | `4-scene-reflection.md` |
| `JqN6beMjVoaXgRxPlPFcB819npb` | shots-assembly - 分镜组合技能 | `5-shots-assembly.md` |
| `CI6sbrtxpo28NCxhinPcl19mnsh` | shots-timing - 分镜计时技能 | `6-shots-timing.md` |
| `LbhbbPBUtoDstLxnRI1c4TyznJd` | script-chunk - 分镜切分技能 | `7-script-chunk.md` |
| `F702bUy80o7BdYxbpOecM7hsnIb` | ref-extract - 素材挖掘抽取技能 | `8-ref-extract.md` |
| `QnUDbuHI8owXhrxR3PZcR42ynKc` | story-idea - 故事短片大纲创作技能 | `9-story-idea.md` |
| `OuNZbPMtzoHX8VxyrmfcAOCWnQI` | story-script - 故事短片剧本创作技能 | `10-story-script.md` |

## 下载命令模板

```bash
lark-cli drive +download --file-token <token> --output <推荐文件名>
```

## 实测验证记录（2026-05-26）

下载后验证首行，结果：

```
1-video-sop.md        ✅ video-sop
2-story-idea.md       ❌ 实际是 video-prompt（内容错位）
3-story-script.md     ❌ 实际是 story-ref-gen
4-ref-extract.md      ❌ 实际是 scene-reflection
5-script-chunk.md     ❌ 实际是 shots-assembly
6-shots-timing.md     ✅ shots-timing
7-shots-assembly.md   ❌ 实际是 script-chunk
8-scene-reflection.md ❌ 实际是 ref-extract
9-video-prompt.md     ❌ 实际是 story-idea
10-story-ref-gen.md   ❌ 实际是 story-script
```

结论：只有 `1-video-sop.md` 和 `6-shots-timing.md` 两个文件的内容与文件名一致，其余 8 个文件全部错位。

## 教训

不要相信云盘导出的文件名。下载后第一件事永远是读首行 `# 标题` 确认内容。