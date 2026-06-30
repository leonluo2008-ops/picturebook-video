#!/usr/bin/env bash
# skill-changes-check.sh · SKILL.md 铁律改动守门 (v5.0.9 修复新增)
#
# 目的:把铁律 #26 "禁止擅自加防御性规则到 skill" 自动化。
# 用户问题 6: "agent 会自动修改 skill 规则,导致没有经过验证的规则污染 skill"
#
# 用法:
#   bash scripts/skill-changes-check.sh        # 检查 git working tree vs HEAD
#   bash scripts/skill-changes-check.sh --staged  # 检查 git staged vs HEAD
#
# 输出:列出本次改动涉及的铁律编号 + 必用户拍板才能 commit
# 退出码: 0 = 铁律无改动 / 1 = 有铁律改动需用户拍板

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SKILL_DIR"

STAGED_MODE=false
if [[ "${1:-}" == "--staged" ]]; then
    STAGED_MODE=true
fi

# 抓 SKILL.md 改动行 (新增 / 删除)
if [[ "$STAGED_MODE" == true ]]; then
    DIFF=$(git diff --cached -- '*.md' ':!CHANGELOG.md')
else
    DIFF=$(git diff -- '*.md' ':!CHANGELOG.md')
fi

if [[ -z "$DIFF" ]]; then
    echo "✅ 无 SKILL.md / references/*.md 改动"
    exit 0
fi

# 检测铁律编号改动(新增 / 删除 / 修改)
# 铁律格式: | **N** | ... (在表格行内) 或 **铁律 #N** (在段落里)
# 改动标记: -| **N** | ... (删除铁律) 或 +| **N** | ... (新增铁律) 或 ~ 修改

ADDED=$(echo "$DIFF" | grep -E '^\+\| \*\*[0-9]+\*\*' | grep -oE '\*\*[0-9]+\*\*' | tr -d '*' | sort -u || true)
REMOVED=$(echo "$DIFF" | grep -E '^-\| \*\*[0-9]+\*\*' | grep -oE '\*\*[0-9]+\*\*' | tr -d '*' | sort -u || true)

# 编号连续性检查(picturebook-video 铁律编号从 21 起)
ALL_LAWS=$(grep -oE '\*\*[0-9]+\*\*' SKILL.md 2>/dev/null | tr -d '*' | sort -un)
TOTAL_COUNT=$(echo "$ALL_LAWS" | wc -l)
FIRST_LAW=$(echo "$ALL_LAWS" | head -1)
LAST_LAW=$(echo "$ALL_LAWS" | tail -1)
echo "当前 SKILL.md 铁律总数:$TOTAL_COUNT(编号范围: #$FIRST_LAW - #$LAST_LAW)"

violations=0
if [[ -n "$ADDED" ]]; then
    echo ""
    echo "🆕 新增铁律编号:"
    for n in $ADDED; do
        echo "  + 铁律 #$n"
    done
    violations=$((violations + $(echo "$ADDED" | wc -l)))
fi

if [[ -n "$REMOVED" ]]; then
    echo ""
    echo "🗑️  删除铁律编号:"
    for n in $REMOVED; do
        echo "  - 铁律 #$n"
    done
    violations=$((violations + $(echo "$REMOVED" | wc -l)))
fi

# 编号连续性检查(从 FIRST_LAW 起,L1 - L18 范围内不能断档)
SEQ_BROKEN=""
EXPECTED=$FIRST_LAW
for n in $ALL_LAWS; do
    if [[ $n -ne $EXPECTED ]]; then
        SEQ_BROKEN="$SEQ_BROKEN #$EXPECTED(missing)→"
    fi
    EXPECTED=$((EXPECTED + 1))
done
if [[ -n "$SEQ_BROKEN" ]]; then
    echo ""
    echo "⚠️  铁律编号断档:$SEQ_BROKEN"
    violations=$((violations + 1))
fi

if [[ $violations -gt 0 ]]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "❌ 检测到 $violations 处铁律改动"
    echo ""
    echo "铁律 #26: '禁止擅自加防御性规则到 skill'"
    echo "→ 必先让用户拍板(原话: '不要急着把讲的东西都加到铁律啊')"
    echo "→ 改前必跑:"
    echo "  1. 列出新增/删除铁律给用户看"
    echo "  2. 解释为什么加/删(必带实战案例)"
    echo "  3. 等用户明确确认后才能 commit"
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

echo ""
echo "✅ 铁律无新增/删除,改动属于细化/补正(无需拍板)"
exit 0