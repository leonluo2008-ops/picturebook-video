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

## 开新分支踩坑

- 本地 `master` 分支 ≠ 上游 `master`!上游默认分支可能是 v5.0.8,而最新工作在 `fix/runtime-stability-2026-06-23` 之类的 fix/feat 分支
- 开新分支前**必查**:`git branch -a` + `git log --all --oneline | head -10` 确认 HEAD 在哪个版本
- 推荐从最新 production 版本(v5.0.9 / v5.0.10 等)的 fix/feat 分支拉新分支,而不是从 master

## 反射

本会话 2 次踩坑(①没 ff 验证就 push origin master 创孤儿 ②huiben 落后 1 commit 用 pull 而非 reset),都已沉淀到本文。