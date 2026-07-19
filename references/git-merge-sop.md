---
name: git-merge-sop
description: "picturebook-video 仓库维护的 Git SOP（开新分支 / 合并 main / 多 profile 同步）。与绘本视频制作无关，纯 DevOps 内部踩坑沉淀。"
license: Apache-2-2
metadata:
  hermes:
    tags: [git, sop, devops, hygiene, picturebook-video]
    related_skills: [picturebook-video]
---

# Git 合并 SOP · 2026-06-24 Potato 4 BUG 修复后踩坑沉淀

> **来源**: 本 skill 仓库维护过程的 DevOps 内部踩坑笔记,与绘本视频制作无关。
> **原位置**: SKILL.md §5(L310-353)
> **触发**: 用户说"合并到 main" / "推到 origin/X" / "覆盖 remote X" 任何一种措辞时,必走本文 5 步 SOP。

## 踩坑根因

本地 install 仓的起点 commit(`23fd594 "picturebook-video official install (dev branch)"`)**不在** 远程 `origin/main`(v3.0)或 `origin/dev`(v5.0.11)上 → 三条线**完全独立 commit 历史**。

v5 系列产品本地 install 仓和远程 `dev` 分支的 v5.0.x 是**两套独立演进**,同名不同源 → 跨线合并只能 cherry-pick,不能 ff。

## 5 步强制 SOP

1. **`git fetch origin --prune`** — 同步真实远程分支状态(避免本地缓存过期误判)
2. **`git branch -r`** — 列出全部远程分支,**不**假设远程"只有 main"或"只有 dev"
3. **`git log origin/<branch> --oneline -3`** — 看目标远程分支 HEAD 状态(版本号 / commit message / 起点 author)
4. **`git merge-base --is-ancestor <my-HEAD> origin/<branch>`** — 验证祖先关系(是祖先 → 可 ff;不是 → 只能 cherry-pick,不可直接 push)
5. **选操作模式**:
   - **A · ff merge**(祖先关系 ✅) → `git checkout <X>` + `git merge --ff-only <my-HEAD>` + `git push origin <X>`(无 --force)
   - **B · cherry-pick**(非祖先,跨线合并) → 大量冲突(尤其 SKILL.md/manifest),逐文件手动解冲突,**预期会修整版本号**
   - **C · 强制覆盖**(用户明确授权"直接覆盖"/"随便推") → `git push --force-with-lease`(比 `--force` 安全,会先检查 remote 没被别人改过)
   - **D · 本地软合并**(临时方案) → 本地新建分支,不推远程

**任何 `git push origin <branch>` 前必先做前 4 步**,**不**把本地独立 install 仓的工作直接当 ff merge 推到远程。

## 用户授权"直接覆盖"执行模板

```bash
# 1. 在目标 HEAD 起本地 main(注意: 不叫 master,叫 main 跟远程对齐)
git branch -f main HEAD
git checkout main
# 2. 强制 push(用户授权)
git push --force-with-lease origin main
# 3. 删其他分支
git push origin --delete dev fix/runtime-stability-2026-06-23
git branch -D feature/srt-driven-clip-v5.0.10 master
# 4. 同步远程 HEAD
git remote set-head origin main
```

## 多 profile 同步(主 + huiben 独立副本)

- huiben profile 落后主 profile 1+ commit 时 → `git pull --ff-only` 不行(diverging) → 用 `git reset --hard origin/main` 强制同步
- 同步前**必先确认 origin/main 是用户授权覆盖的最终版本**(否则会丢 huiben 本地独有工作)
- huiben 备份分支(如 `backup-before-v5.0.10-*`)如用户表态"都不需要" → `git branch -D` 全删
- 验证两边一致:`diff <(git log main --oneline -1) <(git log origin/main --oneline -1)` 必须相同

## 远程升级检测流程(v5.0.10.1 → v5.0.16 实战沉淀 · 2026-07-19)

用户问"检查远程仓库是否有新版本"或 huiben 本地仓版本号与 `origin/main` HEAD 不一致时,**必走 5 步检测**(不要直接 `git pull`):

### 1. 检测差距

```bash
git fetch origin --prune              # 同步远程真实状态(必加 --prune,清过期缓存)
git branch -r                          # 看清所有远程分支
git rev-parse HEAD                     # 本地 HEAD
git rev-parse origin/main              # 远程 HEAD
```

差距分类:
- **HEAD 一致** → 已同步,无需动作
- **本地领先** → 本地有未推送工作,问用户是 push 还是丢弃
- **远程领先 1-3 commit** → 走上文 5 步 SOP 判断 ff 还是 cherry-pick
- **远程领先 ≥4 commit / 跨版本号** → **走升级路径**(见下)

### 2. 跨版本升级路径(用户明确授权"丢弃本地改动"时)

```bash
# 1. 检查未提交改动(必须先列给用户看)
git status -s
git diff --stat                        # 看改动范围(行数 + 文件数)

# 2. 强制询问:要不要先备份到 /tmp?
#    (默认推荐备份,但用户说"不要备份"也合法——必走 1 次明确确认)

# 3. 丢弃 + 同步
git reset --hard origin/main           # 丢弃所有 tracked 改动 + 移动 HEAD
git clean -fd                          # 删未跟踪文件 + 空目录

# 4. 验证(必走 3 步)
git status                             # 必须 "干净的工作区"
git log --oneline -3                    # HEAD 必须是 origin/main 的 commit
head -3 SKILL.md                       # version 行必须匹配用户目标版本
```

### 3. 决策树:reset vs merge vs cherry-pick

| 场景 | 推荐命令 | 原因 |
|---|---|---|
| 用户明确说"丢弃本地改动" + 远程是生产版 | `reset --hard + clean -fd` | 最快最干净,无冲突 |
| 用户想保留本地改动 + 远程领先 1-3 commit | `git merge origin/main` 或 `git rebase origin/main` | 保留本地工作,跟远程合并 |
| 用户想保留本地改动 + 远程领先 ≥4 commit / 跨版本 | 走 `references/upgrade-vX-to-vY.md` 升级指南(如有) | 跨版本可能改字段/字段名/规则,不能盲合 |
| 本地独有工作有价值 + 用户没表态 | **停下来问**,不要猜 | 丢工作不可逆 |

### 4. 备份到 /tmp 的标准命令(可选)

```bash
BACKUP_DIR="/tmp/picturebook-video-backup-$(date +%s)"
mkdir -p "$BACKUP_DIR"
git diff > "$BACKUP_DIR/changes.patch"           # 已跟踪改动
# 未跟踪文件单独拷一份(可选)
cp -r <untracked-files> "$BACKUP_DIR/"
echo "$BACKUP_DIR"                                 # 告知用户备份路径
```

### 5. 踩坑记录

- **直接 `git pull`** 会触发 merge / rebase,跨版本升级 = 大冲突 + 难回退 → **禁止**
- **`git clean -fd` 会删所有未跟踪文件**(包括可能有用的参考资料) → reset 后**必须**先列出来给用户看(`git status -s`),用户拍板再 clean
- **跨版本 reset 后必须跑 `head -3 SKILL.md`** 验证 version 行 = 用户目标版本号(防 origin/main 不是真最新)
- **`git fetch --all` 不带 `--prune`** = 远程已删分支还在本地缓存里 → **必加 `--prune`**
- **不列差异就 reset** = 用户可能丢有价值的工作 → 改 `git diff --stat` 必须先跑,让用户看到几行几文件
- **用户说"直接丢弃" ≠ 不询问**:哪怕用户授权丢弃,也要先跑一次"要不要备份到 /tmp?"的二次确认(2026-07-19 huiben 实战:用户先说"丢弃",再答"不要备份"——这两次表态都是必须的,不能合并)

## 开新分支踩坑

- 本地 `master` 分支 ≠ 上游 `master`!上游默认分支可能是 v5.0.8,而最新工作在 `fix/runtime-stability-2026-06-23` 之类的 fix/feat 分支
- 开新分支前**必查**:`git branch -a` + `git log --all --oneline | head -10` 确认 HEAD 在哪个版本
- 推荐从最新 production 版本(v5.0.9 / v5.0.10 等)的 fix/feat 分支拉新分支,而不是从 master

## 反射

本会话 2 次踩坑(①没 ff 验证就 push origin master 创孤儿 ②huiben 落后 1 commit 用 pull 而非 reset),都已沉淀到本文。
