# picturebook-video 升级指令 · v5.0.5 → v5.0.6

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.5 的 picturebook-video。用户要求你升级到 **v5.0.6（绘本有声场景新功能 · 自动加音效 + 旁白，不加 BGM）**。

**v5.0.6 的核心变化（绘本音频策略升级）**：

1. **`generate_audio` 默认值 false → true**
   - 旧版（v5.0.5 及之前）：绘本 = 完全静默 = `generate_audio=false`
   - 新版（v5.0.6 起）：绘本有声场景 = `generate_audio=true` = seedance 自动加音效 + 旁白
2. **prompt 末尾约束简化**
   - 旧版：`No human voice, no singing, no narration, no background music, no on-screen text`
   - 新版：`No background music, no on-screen text`（**只禁 BGM + 文字**，**允许**人声/歌唱/旁白/音效）
3. **BGM 由 prompt 末尾约束排除，不在参数层禁**
   - 用户原话："**不能有音乐，可以有音效，可以有人声。因为后期可以很容易分离人声，但是无法分离音乐**"

**升级意义**：测试 seedance 自动加音效 + 旁白的新能力，BGM 由 prompt 约束排除避免污染音轨。

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

## Step 0 · 升级前快照

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
# 期望看到 v5.0.6 commit hash（升级完成后查具体值）
```

---

## Step 2 · 验证 v5.0.6 5 处必改

```bash
cd "$SKILL_DIR"

echo "=== 1. seedance_uploads.py 默认值已改 True ==="
grep -nE "body\[\"generate_audio\"\] = True" seedance_mcp/seedance_uploads.py
# 期望看到：body["generate_audio"] = True

echo ""
echo "=== 2. seedance_uploads.py 注释说明已更新 ==="
grep -nE "v5.0.6 升级" seedance_mcp/seedance_uploads.py
# 期望看到：v5.0.6 升级 = 自动加音效 + 旁白

echo ""
echo "=== 3. mcp_server.py docstring 已更新 ==="
grep -nE "v5.0.6 起" seedance_mcp/mcp_server.py
# 期望看到：v5.0.6 起 · 自动加音效 + 旁白

echo ""
echo "=== 4. v8-prompt-template.md 末尾约束已简化 ==="
grep -nE "No human voice|No background music|No on-screen text" references/v8-prompt-template.md
# 期望看到：No background music, no on-screen text
# 期望 0 命中：No human voice（已删）

echo ""
echo "=== 5. SKILL.md 铁律 #17 已修订（v5.0.6 标注）==="
grep -nE "v5.0.6 修订" SKILL.md
# 期望看到铁律 #17 后有 "v5.0.6 修订" 标注
```

**期望：5 项验证全部通过**。任何 1 项失败 = 升级未生效。

---

## Step 3 · 跑验收脚本（重点）

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

**额外验证**（v5.0.6 改了 seedance_uploads.py 逻辑，必跑 smoke test）：

```bash
# 必跑 MCP smoke test 验证 generate_audio 默认 True 生效
python3 seedance_mcp/smoke_test.py 2>&1 | tail -20
# 期望：生成任务成功 + status=succeeded
```

---

## v5.0.6 升级后主 agent 必走的新规则

**绘本音频策略**（**v5.0.6 新规 · 用户原话级**）：

| 项 | 状态 |
|---|---|
| **generate_audio** | **true**（默认开） |
| **音效** | ✅ 允许（脚步声/嘎嘎叫等动作声音） |
| **旁白 / 人声** | ✅ 允许 |
| **BGM 背景音乐** | ❌ 严禁（由 prompt 末尾约束排除） |

**绘本 prompt 末尾约束 v5.0.6 简化版**：

```
No background music, no on-screen text.
```

**用户原话（为什么不要 BGM）**：
> "**不能有音乐，可以有音效，可以有人声。因为后期可以很容易分离人声，但是无法分离音乐**"

---

## 升级说明汇报给用户

```
✅ picturebook-video v5.0.5 → v5.0.6 升级完成
- generate_audio 默认值：false → true（绘本有声场景 · 自动加音效 + 旁白）
- prompt 末尾约束：4 词（人声/歌唱/旁白/朗读）已删，只禁 BGM + on-screen text
- BGM 排除机制：由 prompt 末尾约束排除，不在参数层禁
- 验证项：全部通过 + smoke test 成功
- 下次跑绘本时，云服 = 默认 generate_audio=true + 末尾约束只剩 No background music
```

---

## 历史升级链路

| 版本 | commit | 变更 |
|---|---|---|
| v5.0 | 81b5cea | 单仓集成 seedance_mcp |
| v5.0.2 | 6a7070b | INSTALL_TEST.sh 路径硬编码修复 + wrapper 路径多候选适配 |
| v5.0.3 | 5f4969d | @ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线 |
| v5.0.4 | 43d1e87 | 单测必跑 + 用户确认 + 3 并发限流 |
| v5.0.5 | 8977ec8 | 4 确认点流程修订 + 纯文本输出纪律 |
| v5.0.6 | (升级完成后查 git log) | 绘本有声场景 · generate_audio=true + 末尾约束简化 |

---

**对应 commit**：v5.0.6 commit hash（升级完成后由 `git log --oneline -1` 输出确认）