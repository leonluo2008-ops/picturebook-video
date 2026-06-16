# picturebook-video 升级指令 · v4.x → v5.0

## 给云服 Hermes 的执行说明

你现在已经装了老版本的 picturebook-video（v3.x 或 v4.x）。用户要求你升级到 **v5.0 单仓集成版**。

**v5.0 的核心变化**：seedance_mcp 已并入 picturebook-video 仓，**不再需要 seedance2.0-tool 仓**。克隆 1 个仓 = 完整可用。

---

## Step 0 · 确认当前状态

先汇报给用户：

```bash
# 1. 当前 picturebook-video 版本
cd ~/.hermes/profiles/huiben/skills/creative/picturebook-video
git describe --tags 2>/dev/null || git log --oneline -1

# 2. 当前 seedance2.0-tool 是否还在
ls ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/ 2>/dev/null && echo "老仓还在" || echo "老仓已删除"

# 3. 当前 MCP wrapper 指向哪里
cat ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh | grep SKILL_DIR
```

把上面 3 条结果告诉用户（让他知道现在是什么状态）。**不要直接动手升级**——等用户确认。

---

## Step 1 · 备份旧版（防升级失败可回滚）

```bash
# 备份 picturebook-video 仓（不是删，是改名备份）
mv ~/.hermes/profiles/huiben/skills/creative/picturebook-video \
   ~/.hermes/profiles/huiben/skills/creative/picturebook-video.bak.v4

# 备份旧 wrapper.sh
cp ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh \
   ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh.bak.v4
```

如果用户在 v3 还在用 `seedance2.0-tool` 仓——**不要删**，保留：
```bash
# 保留旧仓不动（用户可能别的项目还在用）
ls ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/ && echo "保留老仓"
```

---

## Step 2 · 克隆 v5.0

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills

# 克隆 picturebook-video v5.0（单仓含 seedance_mcp）
git clone -b v5.0 https://github.com/leonluo2008-ops/picturebook-video.git \
    $HUIBEN_SKILLS/creative/picturebook-video
```

**如果 git clone 报 `GnuTLS recv error (-110)`**（部分网络环境会碰到）：
```bash
# 切 SSH 兜底（前提：~/.ssh/id_rsa.pub 已加到 GitHub）
git clone -b v5.0 git@github.com:leonluo2008-ops/picturebook-video.git \
    $HUIBEN_SKILLS/creative/picturebook-video
```

**如果没 ~/.ssh/id_rsa.pub**：
```bash
ssh-keygen -t rsa -b 4096  # 一路回车
cat ~/.ssh/id_rsa.pub  # 把输出粘到 https://github.com/settings/keys
# 然后再跑上面的 SSH clone
```

---

## Step 3 · 部署 MCP wrapper.sh

```bash
# 复制新 wrapper.sh（指向 picturebook-video v5.0）
cp ~/.hermes/profiles/huiben/skills/creative/picturebook-video/bin/seedance-mcp-wrapper.sh \
   ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh
chmod +x ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh

# 验证 wrapper.sh 内 SKILL_DIR 路径正确
grep "SKILL_DIR=" ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh
# 预期：SKILL_DIR=".../.hermes/profiles/huiben/skills/creative/picturebook-video/seedance_mcp"
```

---

## Step 4 · 配置 ARK_API_KEY

```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video

# 4.1 如果旧 .env 在 seedance2.0-tool 仓下 · 直接复制过来（保留 key）
if [ -f ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env ]; then
  cp ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool/.env \
     $SKILL_DIR/seedance_mcp/.env
  echo "✅ .env 已从旧仓复制"
else
  # 4.2 全新配置
  cp $SKILL_DIR/seedance_mcp/.env.example $SKILL_DIR/seedance_mcp/.env
  echo "⚠️  需要手动编辑 .env 填入 ARK_API_KEY"
  echo "   nano $SKILL_DIR/seedance_mcp/.env"
fi

# 验证 .env 已配
grep "^ARK_API_KEY=" $SKILL_DIR/seedance_mcp/.env | head -1 | awk -F= '{print "ARK_API_KEY 长度:", length($2)}'
# 预期：ARK_API_KEY 长度: 36 左右
```

---

## Step 5 · 检查 config.yaml 的 mcp_servers 配置

```bash
# 查看 config.yaml 当前 seedance MCP 配置
grep -A 4 "seedance:" ~/.hermes/profiles/huiben/config.yaml
```

**预期**（v5.0 wrapper 已指向新仓，下面的路径不用改）：

```yaml
mcp_servers:
  seedance:
    command: /home/YOUR_USER/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh
    args: []
    env: {}
```

**如果路径不对**（比如指向了旧 seedance2.0-tool 路径），编辑 config.yaml 改成上面格式。

---

## Step 6 · 重启 hermes-agent（让 MCP server 重新加载）

```bash
# 方式 1：如果有 systemctl 管理
systemctl --user restart hermes-gateway 2>/dev/null || true

# 方式 2：手动重启 gateway
pkill -f hermes-gateway 2>/dev/null || true
pkill -f hermes 2>/dev/null || true
# 然后按用户习惯重启 hermes-agent（docker / systemd / 直接启动）
```

**如果不知道怎么重启**——告诉用户：需要重启 hermes-agent 让 MCP server 重新加载新 wrapper。

---

## Step 7 · 跑验收测试（必跑）

```bash
SKILL_DIR=~/.hermes/profiles/huiben/skills/creative/picturebook-video
bash $SKILL_DIR/INSTALL_TEST.sh
```

**7 步全过** = 升级成功：

| # | 检查 | 通过条件 |
|---|---|---|
| 1 | skill 仓结构 | seedance_mcp/ + references/ + SKILL.md 都在 |
| 2 | .env 配置 | ARK_API_KEY 已填 |
| 3 | wrapper.sh 已部署 | 路径指向 picturebook-video |
| 4 | Python 依赖 | mcp / httpx / python-dotenv 都可用 |
| 5 | API key 有效性 | verify 返回 valid=true |
| 6 | uguu.se 图床 | 上传测试图成功 |
| 7 | 端到端视频 | 跑 1 个 5s 视频 succeeded |

---

## Step 8 · 清理（可选 · 等用户拍板再做）

**升级成功后**，可以问用户：

```bash
# 选项 A：删掉旧 picturebook-video 备份（确认升级稳定后再删）
rm -rf ~/.hermes/profiles/huiben/skills/creative/picturebook-video.bak.v4
rm ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh.bak.v4

# 选项 B：删掉 seedance2.0-tool 老仓（如果用户不用别的项目）
rm -rf ~/.hermes/profiles/huiben/skills/creative/seedance2.0-tool

# 选项 C：清理 config.yaml 的 mcp_servers 旧条目（如果有）
# 备份后编辑：cp ~/.hermes/profiles/huiben/config.yaml ~/.hermes/profiles/huiben/config.yaml.bak
# nano ~/.hermes/profiles/huiben/config.yaml
```

**不要直接做清理**——让用户拍板。

---

## 故障时回滚

如果升级后跑不通，立即回滚：

```bash
# 回滚 picturebook-video 到 v4
rm -rf ~/.hermes/profiles/huiben/skills/creative/picturebook-video
mv ~/.hermes/profiles/huiben/skills/creative/picturebook-video.bak.v4 \
   ~/.hermes/profiles/huiben/skills/creative/picturebook-video

# 回滚 wrapper
mv ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh.bak.v4 \
   ~/.hermes/profiles/huiben/bin/seedance-mcp-wrapper.sh

# 重启 hermes-agent
# 然后用户可以继续用 v4.x 老版本
```

---

## 汇报模板

升级完成后，给用户一份简洁报告：

```
✅ picturebook-video 升级到 v5.0 完成

执行步骤：
- 备份：picturebook-video → .bak.v4 · wrapper.sh → .bak.v4
- 克隆 v5.0 单仓（含 seedance_mcp 集成 ~910 行）
- 部署新 wrapper.sh + 复用旧 .env 的 ARK_API_KEY
- 重启 hermes-agent
- 跑 INSTALL_TEST.sh：7/7 通过

端到端验证：
- 视频生成：✅ 5.04s · task_id cgt-XXXXXXXXXXXXX
- uguu 图床：✅
- API key：✅

旧仓 seedance2.0-tool 保留（未删 · 等用户拍板）
旧 picturebook-video 备份保留（.bak.v4）

需要清理吗？可选：
A. 删 picturebook-video.bak.v4（升级稳定后再删）
B. 删 seedance2.0-tool 仓（如果用户不用别的项目）
```

---

## 给云服 Hermes 的元提示

- **不要跳过 Step 0 汇报**——用户要知道升级前的状态
- **备份是必须的**——升级失败可回滚，不备份 = 不可逆事故
- **不要自动清理**——备份和旧仓都保留，等用户拍板
- **INSTALL_TEST.sh 7 步必跑**——7/7 通过才算成功
- **遇到 GnuTLS 错误**——按 Step 2 的 SSH 兜底走，不要重试 HTTPS
- **遇到任何报错**——截图/贴出具体错误给用户，**不要**自己脑补修
