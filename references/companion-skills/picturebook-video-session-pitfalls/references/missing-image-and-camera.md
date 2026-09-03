# §4 缺图处理 + §5 运镜修改模式（2026-08-04/08-05 实拍原文存档）

> 2026-08-31 为给 SKILL.md 腾空间外迁至此；主 SKILL.md 内只保留一句式摘要。

## §4 Missing Image Handling (2026-08-04 一 batch)

### Phenomenon
User sent a 7z with only 7 images (missing 5.jpg for segment #5「一朵小花」). The SRT had 8 segments but only 7 images.

### Protocol
1. Detect: `ls` shows fewer images than SRT segments → flag in alignment table
2. Report to user: `包里缺了X.jpg（对应段#Y「旁白原文」）`
3. User may send the missing image as a separate message → save to the same directory
4. Re-run alignment table with complete set
5. Proceed normally

### Key: Don't guess or fabricate. Just report the gap and wait for user to supply the missing image.

## §5 Camera Modification Pattern (2026-08-04 九/五/四 batch)

### User Request Pattern
User repeatedly asked: `第N个画面修改运镜，要能显示出X个`

### Effective Camera Patterns
| Pattern | When | Example |
|---------|------|----------|
| **从特写开始缓缓拉远** | Objects are in a grid/row layout | 镜头从特写小鸡开始，然后缓缓拉远，九只黄色小鸡从画面中央排列成三行三列，镜头持续拉远直到九只小鸡全部进入画面 |
| **从全景开始推近再拉远** | Objects should be visible from frame 1; user says "要显示出X个" | 镜头从全景开始，6只黄色小鸡全部在画面中排成一排，然后镜头缓缓推近再拉远穿过画面中央，展示全部6只小鸡 |
| **展示参考图全部内容** | When Seedance keeps getting quantity wrong | 镜头展示参考图 @Image2 的全部内容...镜头保持全景展示参考图画面 |

### Key: When user says `要能显示出X个`, the fix is camera + layout description, not quantity constraint alone.