# 案例 #23 · readme 文字 vs vision 视觉冲突

**场景**: 领读型绘本角色对位时,readme.txt 写 "2=Mom, 3=Dad",但图 2 视觉证据"红领结=倾向 Dad"。

**翻车**: vision 推断 "红领结=正式=Dad" → 硬套 readme 反向(2=Dad, 3=Mom) = 推翻作者意图。

**修复**: **冲突时默认按 readme 文字** + 报告用户差异 + 让用户拍板。

**判定口诀**: "我看到的" < "作者写的" = readme 是文本层真相,vision 是参考层证据。

**对应**: SKILL.md 约束 5(Step 1 角色对位)。