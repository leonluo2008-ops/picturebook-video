# 即梦官方SOP文件映射表

## 问题说明
官方导出的文件名与实际内容对不上，必须按文件内容判断。
本文件记录正确的 token → 内容对应关系，工作时直接查本表。

## 正确映射（token → 实际内容 → 推荐文件名）

| token | 实际内容 | 推荐文件名 |
|-------|----------|-----------|
| `K3fDba7h8obp55xq3x9cnS6Sn6b` | video-sop（即梦视频创作标准工作流程） | `1-video-sop.md` ✅ |
| `U1RsbkaKfo9r3pxVkAAcRibonHf` | video-prompt（分镜生视频技能） | `2-video-prompt.md` |
| `R4ijbDgbYogAmGx9qHrc74qFnoc` | story-ref-gen（故事参考素材生成技能） | `3-story-ref-gen.md` |
| `XZDNbx1a2o2kTlxy44CcuSIHnHc` | scene-reflection（分镜连贯性校验技能） | `4-scene-reflection.md` |
| `JqN6beMjVoaXgRxPlPFcB819npb` | shots-assembly（分镜组合技能） | `5-shots-assembly.md` |
| `CI6sbrtxpo28NCxhinPcl19mnsh` | shots-timing（分镜计时技能） | `6-shots-timing.md` ✅ |
| `LbhbbPBUtoDstLxnRI1c4TyznJd` | script-chunk（分镜切分技能） | `7-script-chunk.md` |
| `F702bUy80o7BdYxbpOecM7hsnIb` | ref-extract（素材挖掘抽取技能） | `8-ref-extract.md` |
| `QnUDbuHI8owXhrxR3PZcR42ynKc` | story-idea（故事短片大纲创作技能） | `9-story-idea.md` |
| `OuNZbPMtzoHX8VxyrmfcAOCWnQI` | story-script（故事短片剧本创作技能） | `10-story-script.md` |

## 验证方法
下载后读取首行，确认 `# 标题` 与预期内容一致。

## 当前 references/ 目录文件内容（2026-05-26 下载验证）

```
1-video-sop.md        → video-sop ✅
2-story-idea.md       → video-prompt（内容错位，文件名应为 2-video-prompt.md）
3-story-script.md     → story-ref-gen（内容错位）
4-ref-extract.md      → scene-reflection（内容错位）
5-script-chunk.md     → shots-assembly（内容错位）
6-shots-timing.md     → shots-timing ✅
7-shots-assembly.md   → script-chunk（内容错位）
8-scene-reflection.md → ref-extract（内容错位）
9-video-prompt.md     → story-idea（内容错位）
10-story-ref-gen.md   → story-script（内容错位）
```