# 案例 #31 · seedance ≤3 并发限流

**场景**: Step 6 seedance 提交时,8 个 Clip 一次性并行。

**翻车**: 8 Clip 并行 = 超 seedance 个人用户限流(官方:个人 = 3 并发 / 企业 = 10) = 部分任务卡死或失败。

**修复**:
1. 按 3 个一组拆批(如 8 Clip = 3+3+2 = 3 轮)
2. 每轮 submit 后**必** wait_and_download 全部完成
3. 下一轮提交前**必**查 status(确保本轮无 failed 任务 = 有就停下汇报用户)

**判定口诀**: "3 并发 / 多轮分批 / 轮间 wait_and_download = 3 必走 = 任一缺失 = 红线违规"。

**官方依据**: `references/seedance-official-docs/1-Doubao_Seedance_2.0_系列教程.docx` line 143 个人用户最大并发数 = 3。

**对应**: SKILL.md 约束 3 / Step 6 workflow 节点 / seedance 官方硬约束。