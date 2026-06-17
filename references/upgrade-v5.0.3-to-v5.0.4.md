# picturebook-video 升级指令 · v5.0.3 → v5.0.4

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.3 的 picturebook-video。用户要求你升级到 **v5.0.4（单测必跑 + 用户确认 + 3 并发限流）**。

**v5.0.4 的核心变化（2 条新铁律 · 主 agent 路径强约束）**：

1. **铁律 #30 · 提交前必跑 spike clip + 用户目检确认**
   - 批量提交前必跑 1 条 spike clip（480p + 最短时长 4s + 无 BGM = 最低费用）
   - 必须发飞书等用户目检确认（"OK / 通过 / 可以批量"类信号）
   - 不许自判"应该 OK" / 不许沉默默认通过
2. **铁律 #31 · 每轮 ≤ 3 并发 · 多轮分批**
   - seedance 个人用户最大并发 = 3（官方限流 · `references/seedance-official-docs/1-Doubao_Seedance_2.0_系列教程.docx` line 143）
   - N 个 Clip 拆成 `ceil(N / 3)` 轮串行（如 8 个 Clip = 3 + 3 + 2 = 3 轮）
   - 禁止 8 个 Clip 一次性并行提交

**升级意义**：修 v5.0.3 之后又出现的"云服直接 8 并行提交"翻车（v5.0.3 没禁并行 = 没根治）。

---

## Step -1 · 环境适配（必跑）

```bash
echo "当前用户: $(whoami)"
echo "HOME: $HOME"

HERMES_ROOT=$(dirname "$(readlink -f ~/.hermes/config.yaml 2>/dev/null)" 2>/dev/null)
if [ -z "$HERMES_ROOT" ] || [ "$HERMES_ROOT" = "/" ]; then
  HERMES_ROOT="$HOME/.hermes"
fi
echo "HERMES_ROOT: $HERMES_ROOT"

SKILL_DIR=$(find "$HERMES_ROOT/profiles/huiben/skills/creative/picturebook-video" -maxdepth 0 2>/dev/null)
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR=$(find "$HERMES_ROOT" -name "picturebook-video" -type d 2>/dev/null | head -1)
fi
echo "SKILL_DIR: $SKILL_DIR"

echo "当前 commit: $(git -C "$SKILL_DIR" log --oneline -1 2>/dev/null)"
```

---

## Step 0 · 升级前快照（出问题可回滚）

```bash
cp -r "$SKILL_DIR" "${SKILL_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
echo "✅ 已备份到 ${SKILL_DIR}.backup-<时间戳>"
```

---

## Step 1 · 拉 dev 分支最新代码

```bash
cd "$SKILL_DIR"
git pull origin dev
git log --oneline -1
# 期望看到 v5.0.4 commit hash（升级完成后看具体值）
```

---

## Step 2 · 验证 2 条新铁律升主层

```bash
cd "$SKILL_DIR"

echo "=== 1. SKILL.md 含铁律 #30（单测必跑）==="
grep "30.*提交前单测" SKILL.md
# 期望看到：| **30** | **Step 6** 提交前单测 | **提交前必跑 spike clip + 用户目检确认**

echo ""
echo "=== 2. SKILL.md 含铁律 #31（3 并发）==="
grep "31.*并发限流" SKILL.md
# 期望看到：| **31** | **Step 6** 并发限流 | **每轮 ≤ 3 并发 · 多轮分批 · 严禁超 seedance 个人用户限流**

echo ""
echo "=== 3. v8-workflow-7steps.md Step 6 含 Step 6.0 单测段 ==="
grep -A 1 "Step 6.0 · 必走 · 单测" references/v8-workflow-7steps.md | head -3
# 期望看到：Step 6.0 · 必走 · 单测（spike clip + 用户目检确认）

echo ""
echo "=== 4. v8-workflow-7steps.md Step 6.1 含 3 并发 ==="
grep -A 2 "Step 6.1 · 批量提交" references/v8-workflow-7steps.md | head -3
# 期望看到：核心约束：seedance 个人用户最大并发 = 3

echo ""
echo "=== 5. README.md line 131 不再写"并行提交" ==="
grep "生成方式" README.md
# 期望看到：**单测必跑 + 用户确认 + 3 并发多轮分批**（v5.0.4 沉淀，详 SKILL.md 铁律 #30 #31）

echo ""
echo "=== 6. 铁律口诀含"单测必跑 + 用户必确认 + 3 并发不多跑" ==="
grep "单测必跑 + 用户必确认 + 3 并发不多跑" SKILL.md && echo "✅ 命中" || echo "❌ 0 命中"
```

**期望：6 项验证全部通过**。任何 1 项失败 = 升级未生效 = 检查 git pull 是否成功。

---

## Step 3 · 跑验收脚本（沿用）

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

---

## 升级完成后主 agent 必走的新规则

**v5.0.4 起在主 agent 路径强约束的 5 条铁律**（#29 #30 #31 + 之前 #19 MCP timeout + 4 词末尾约束）：

| 编号 | 铁律 | 关键约束 |
|---|---|---|
| #29 | `@ImageN` 必含 | 每段 prompt 开头必含 + 多图覆盖 + ref_images 长度匹配 |
| #30 | 单测必跑 | 跑 1 条 spike clip + 用户目检确认 + 才批量 |
| #31 | 3 并发 | 每轮 ≤ 3 + 多轮分批 + 严禁超官方限流 |

**违反任一 = 红线违规 = 不提交**。

---

## 升级说明汇报给用户

升级完成后，向用户汇报：

```
✅ picturebook-video v5.0.3 → v5.0.4 升级完成
- 新增铁律：2 条（#30 单测必跑 + #31 3 并发限流）
- 验证项：全部通过
- README.md 已同步：删掉"并行提交"误导，改成"单测必跑 + 用户确认 + 3 并发多轮分批"
- 下次跑绘本时，主 agent 路径必走单测 → 用户确认 → 才批量（每轮 ≤ 3）
```

---

## 历史升级链路

| 版本 | commit | 变更 |
|---|---|---|
| v5.0 | 81b5cea | 单仓集成 seedance_mcp |
| v5.0.2 | 6a7070b | INSTALL_TEST.sh 路径硬编码修复 + wrapper 路径多候选适配 |
| v5.0.3 | 5f4969d | @ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线 |
| v5.0.4 | (升级完成后查 git log) | 单测必跑 + 用户确认 + 3 并发限流 |

---

**对应 commit**：v5.0.4 commit hash（升级完成后由 `git log --oneline -1` 输出确认）