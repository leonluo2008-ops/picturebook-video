# picturebook-video 升级指令 · v5.0.2 → v5.0.3

## 给云服 Hermes 的执行说明

你现在已经装了 v5.0.x 的 picturebook-video。用户要求你升级到 **v5.0.3（@ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线）**。

**v5.0.3 的核心变化（4 类铁律升主层）**：

1. **`@ImageN` 必含铁律** = seedance 官方语法 = 模型锚定参考图的唯一方式
   - 主 agent 路径的 SKILL.md / v8-workflow-7steps.md / v8-prompt-template.md 之前都缺这条铁律
   - 现在 v8-prompt-template.md 4 段骨架表段 1 强制 `@ImageN` 必含
2. **多图 Clip 视觉覆盖规则** = 每张参考图必在 prompt 里有 ≥1 个该图独有的视觉特征
   - 自检命令新增检查 5（多图覆盖 grep）
3. **`ref_images` 长度红线** = 列表长度必 = image_index 图数量
   - 缺任一路径 = 不提交
4. **wait_and_download 红线** = 提交获得 task_id 后必立即调 wait_and_download
   - 禁止只调 generate_video 拿 task_id 停手等用户催

**升级意义**：修 4 类主 agent 翻车根因（云服最近一次绘本制作踩中的就是 #1 + #2 + #4）。

---

## Step -1 · 环境适配（必跑）

**重要**：本指令不硬编码路径。在执行后续步骤前，先检测本机实际环境：

```bash
# 1. 检测当前用户名（可能是 ubuntu / luo / 其他）
echo "当前用户: $(whoami)"
echo "HOME: $HOME"

# 2. 检测 HERMES 根目录（不假设是 /home/luo/.hermes）
HERMES_ROOT=$(dirname "$(readlink -f ~/.hermes/config.yaml 2>/dev/null)" 2>/dev/null)
if [ -z "$HERMES_ROOT" ] || [ "$HERMES_ROOT" = "/" ]; then
  HERMES_ROOT="$HOME/.hermes"
fi
echo "HERMES_ROOT: $HERMES_ROOT"

# 3. 检测 picturebook-video skill 仓位置
SKILL_DIR=$(find "$HERMES_ROOT/profiles/huiben/skills/creative/picturebook-video" -maxdepth 0 2>/dev/null)
if [ -z "$SKILL_DIR" ]; then
  # 兜底：找 picturebook-video 目录
  SKILL_DIR=$(find "$HERMES_ROOT" -name "picturebook-video" -type d 2>/dev/null | head -1)
fi
echo "SKILL_DIR: $SKILL_DIR"

# 4. 检测当前版本
echo "当前 SKILL.md commit: $(git -C "$SKILL_DIR" log --oneline -1 2>/dev/null)"
echo "当前 SKILL.md description 字段: $(grep -m1 'description:' "$SKILL_DIR/SKILL.md" 2>/dev/null)"
```

**期望输出示例**：
```
当前用户: ubuntu
HOME: /home/ubuntu
HERMES_ROOT: /home/ubuntu/.hermes
SKILL_DIR: /home/ubuntu/.hermes/profiles/huiben/skills/creative/picturebook-video
当前 SKILL.md commit: 6a7070b fix(picturebook-video): v5.0.2 修复 INSTALL_TEST.sh 路径硬编码 + wrapper 部署位置适配
当前 SKILL.md description 字段: description: "绘本转儿童动画视频标准流程（v5.0 单仓集成 · 2026-06-16）..."
```

---

## Step 0 · 升级前快照（出问题可回滚）

```bash
# 备份当前 skill 仓（避免升级失败无法恢复）
cp -r "$SKILL_DIR" "${SKILL_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
echo "✅ 已备份到 ${SKILL_DIR}.backup-<时间戳>"
ls -ld "${SKILL_DIR}".backup-* | tail -1
```

---

## Step 1 · 拉 dev 分支最新代码

```bash
# 1. 确认当前在 dev 分支
cd "$SKILL_DIR"
git branch --show-current
# 期望：dev

# 2. 拉最新提交
git pull origin dev
# 期望输出末尾：Already up to date 或 Fast-forward

# 3. 验证 commit 是否为 v5.0.3
git log --oneline -1
# 期望：5f4969d fix(picturebook-video): v5.0.3 @ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线
```

**如果 git pull 报错或 commit 不对**：
- ❌ 不是 git 仓 → 本指令不适用，需手动同步
- ❌ 在 main 分支 → 切到 dev：`git checkout dev && git pull origin dev`

---

## Step 2 · 验证 4 类铁律升主层

```bash
cd "$SKILL_DIR"

echo "=== 1. v8-prompt-template.md 4 段骨架表段 1 含 @ImageN ==="
grep -A 1 "1 主体" references/v8-prompt-template.md | head -3
# 期望看到：风格 + 主体外观 + 朝向 + 景别 + **@ImageN 必含**（官方语法，唯一参考帧绑定）

echo ""
echo "=== 2. v8-prompt-template.md 自检命令含 检查 4（@ImageN grep）==="
grep -A 2 "检查 4" references/v8-prompt-template.md | head -5
# 期望看到：# 检查 4: `@ImageN` 必含 + grep -E "@Image[0-9]+" clip*-prompt.txt

echo ""
echo "=== 3. v8-workflow-7steps.md Step 5 含 @ImageN 必含段 ==="
grep -A 1 "@ImageN 必含铁律" references/v8-workflow-7steps.md | head -3
# 期望看到：每段 prompt = 必以 `from X.Xs to Y.Ys @ImageN is the ... shot, ...` 开头

echo ""
echo "=== 4. v8-workflow-7steps.md Step 6 含 wait_and_download 红线 ==="
grep "wait_and_download" references/v8-workflow-7steps.md | head -3
# 期望看到：wait_and_download 同步等待 + 下载 · 禁止只调 generate_video 拿 task_id 停手

echo ""
echo "=== 5. SKILL.md 含铁律 #29 ==="
grep "29.*@ImageN" SKILL.md
# 期望看到：| **29** | **Step 5** prompt 写法 | **`@ImageN` 必含 · 多图 Clip 视觉覆盖** |

echo ""
echo "=== 6. 0 绘本名污染 ==="
grep -nE "(Spider|spider|spider)" SKILL.md references/*.md 2>/dev/null && echo "❌ 有污染" || echo "✅ 0 命中（无 Spider 残留）"
```

**期望：5 项验证全部通过**。任何 1 项失败 = 升级未生效 = 检查 git pull 是否成功 / commit hash 是否为 `5f4969d`。

---

## Step 3 · 跑验收脚本（沿用 v5.0.2 自检能力）

```bash
cd "$SKILL_DIR"
bash INSTALL_TEST.sh
```

**期望**：所有验证项 ✅（包含 wrapper.sh 已部署 + seedance_mcp .env 已配置 + MCP 工具可调用）。

**如果 INSTALL_TEST.sh 报告 wrapper 路径不匹配**（P3 历史问题）：
- 预期自动复制到 `profiles/huiben/bin/`
- 如果还是失败，看 `references/install-script-autodetect.md` 的 Step 3 多候选 wrapper 路径段

---

## Step 4 · 跑一次端到端自测（推荐 · 防主 agent 不读子层）

**手动测 1 段 prompt**，验证主 agent 真的会写 `@ImageN`：

```bash
# 1. 找 1 张本地参考图（任意 JPG）
TEST_IMG=$(find /tmp -name "*.jpg" -size +50k 2>/dev/null | head -1)
if [ -z "$TEST_IMG" ]; then
  echo "⚠️ /tmp 找不到测试图，跳过本步"
  exit 0
fi

# 2. 写 1 段 prompt 草稿（不带 @ImageN）= 旧写法
cat > /tmp/test-prompt-old.txt << 'EOF'
Paper-collage style. A small bear with a yellow banana.
The bear brings the banana close to its mouth.
EOF

# 3. 跑 v8-prompt-template.md 的"检查 4: @ImageN 必含"
echo "=== 检查 4: @ImageN 必含 ==="
grep -E "@Image[0-9]+" /tmp/test-prompt-old.txt && echo "✅ 命中" || echo "❌ 0 命中 → 主 agent 写 prompt 时必报缺 @ImageN 红线违规"

# 4. 清理
rm /tmp/test-prompt-old.txt
```

**期望**：❌ 0 命中 + 看到主 agent 报"缺 @ImageN 红线违规"。如果是 ✅ 命中 = 测试图自带 @ImageN 字符，不算数。

---

## 升级完成判定

**全部满足以下 6 条 = 升级成功**：

- [x] Step -1 环境适配：HERMES_ROOT / SKILL_DIR / 当前 commit 输出合理
- [x] Step 0 备份已创建
- [x] Step 1 git pull 成功 + commit hash = `5f4969d`
- [x] Step 2 五项验证全部通过（v8-prompt-template.md + v8-workflow-7steps.md + SKILL.md 三处都有 @ImageN / ref_images / wait_and_download 红线）
- [x] Step 3 INSTALL_TEST.sh 全 ✅
- [x] Step 4 手动 grep 验证主 agent 路径必走检查 4

**升级失败常见情况**：
- ❌ SKILL_DIR 找不到 → 不是 git 仓 → 本指令不适用，需手动 rsync
- ❌ commit hash 不是 `5f4969d` → git pull 没拉到最新 → 检查 remote 配置
- ❌ Step 2 任一 grep 失败 → 升级未生效 → 重跑 Step 1 + 重新 grep

---

## 升级后主 agent 必走的新规则

**这 4 条铁律 v5.0.3 起在主 agent 路径强约束**：

1. **每段 prompt 开头必含 `@ImageN`**（N = 该镜头对应图编号）
2. **多图 Clip 每个 `@ImageN` 必带 ≥1 个该图独有的视觉特征**
3. **`ref_images` 列表长度必 = image_index 图数量**
4. **提交获得 task_id 后必立即调 `wait_and_download`**

**违反任一 = 红线违规 = 不提交**。

---

## 升级说明汇报给用户

升级完成后，向用户汇报：

```
✅ picturebook-video v5.0.2 → v5.0.3 升级完成
- commit: 5f4969d
- 验证项：全部通过
- 新增铁律：4 类（@ImageN 必含 / 多图覆盖 / ref_images 长度 / wait_and_download）
- 验收脚本：INSTALL_TEST.sh 通过
- 下次跑绘本时，主 agent 路径必走新铁律（不再需要记子层规则）
```

---

## 历史升级链路

| 版本 | commit | 变更 |
|---|---|---|
| v5.0 | 81b5cea | 单仓集成 seedance_mcp（不再依赖 seedance2.0-tool）|
| v5.0.2 | 6a7070b | INSTALL_TEST.sh 路径硬编码修复 + wrapper 路径多候选适配 |
| v5.0.3 | 5f4969d | @ImageN 必含铁律升主层 + 多图覆盖红线 + wait_and_download 红线 |

---

**对应 commit**: `5f4969d` · dev 分支 · origin: `git@github.com:leonluo2008-ops/picturebook-video.git`