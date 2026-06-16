# references 健康度体检（2026-06-16 Run 跑 v8 后沉淀）

> **问题域**：picturebook-video 的 references/ 从 20 → 78 → 84 tracked 持续膨胀，
> 出现 3 类结构性问题：**git tracked 但磁盘丢失 / 跨 skill 错放 / 旧版本未清理**。
> 本文件 = 类级别的"references 健康度体检 SOP"，供每个迭代周期触发使用。

## 3 类已发现的问题（v8 后实测）

### 类型 1：git tracked 但磁盘丢失（最严重）

**触发条件**：上次 commit 写了 12 个新 references，但下次 `ls references/` 只看到 2 个。

**根因**：
- 提交时文件被 `git add` 但**未被真实写入磁盘**（partial write / 工作流异常中断）
- 或被其他工具（cp / mv / 重命名）覆盖时未同步 git 索引
- 或 working tree 与 git index 状态不一致

**检测命令**（每次跑完 v_N+1 后必跑）：
```bash
cd /path/to/skill
echo "=== git tracked 数量 ==="
git ls-files references/ | wc -l
echo "=== 磁盘实际存在 ==="
ls references/*.md 2>/dev/null | wc -l
echo "=== 差异 = 丢失数量 ==="
comm -23 <(git ls-files references/ | xargs -n1 basename | sort) \
         <(ls references/*.md 2>/dev/null | xargs -n1 basename | sort)
```

**修复**：差异列表 = 丢失清单 = 逐个 `git checkout HEAD -- <file>` 还原。

### 类型 2：跨 skill 错放

**触发条件**：references 里有 `1-video-sop` / `2-story-idea` 等编号体系文件，
但内容是"即梦（Dreamina）9 步 SOP" = **属于 ai-drama skill**，**不属于 picturebook-video**。

**检测方法**：
```bash
# 看每个 md 文件第一行，识别"描述自己属于哪个 skill"
for f in references/*.md; do head -1 "$f"; done | sort -u | head -30
```

**判定标准**：
- 标题含 "即梦" / "Dreamina" / "分镜" + "故事" / "漫剧" / "短片" → **跨 skill 错放**
- 标题含 "绘本" / "旁白" / "TTS" / "vision" / "seedance" → **picturebook-video 真实相关**

**修复**：移到对应 skill 的 references/ 目录，或删（如对方 skill 已有副本）。

### 类型 3：旧版本/重复未清理

**触发条件**：references/ 出现：
- 编号 v0.7.0 / v1.0.0 / v1.0.1 / v1.0.3 的备份文件
- 同一份内容的 `.md` + `.docx` 双备份
- 与新版本重叠的 `v6-` / `v7-` 旧模板（被新 v15 范式替代）

**判定标准**：
- 文件名含 `-v0.7.0` / `-v1.0.x` / `pic12-`（旧项目代号）
- `.docx` 与同名 `.md` 同时存在 = docx 是素材，md 是消化版，留 md
- `v6-` / `v7-` 模板但当前范式是 v15 = 旧模板 = 删或移到 `archive/`

## 健康度体检 SOP（每个 v_N 验证完成后必跑）

```bash
# Step 1: git vs 磁盘一致性
echo "tracked: $(git ls-files references/ | wc -l)"
echo "actual:  $(ls references/*.md 2>/dev/null | wc -l)"
diff <(git ls-files references/ | xargs -n1 basename | sort) \
     <(ls references/*.md 2>/dev/null | xargs -n1 basename | sort)
# 任何差异 = 立即 git checkout HEAD -- 还原

# Step 2: 跨 skill 错放检测
for f in references/*.md; do
  first_line=$(head -1 "$f")
  if echo "$first_line" | grep -qE "即梦|Dreamina|分镜.*漫剧|故事短片"; then
    echo "MOVE: $f → 对应 skill"
  fi
done

# Step 3: 旧版本识别
ls references/ | grep -E "v0\.7\.0|v1\.0\.[0-3]|pic12|\.docx$" | head -20
# 这些 = 待清理候选

# Step 4: 报告
# 输出 4 个数字：tracked / actual / cross-skill-mistake / old-version
# 任何一项异常 = 写入下次 commit message
```

## 沉淀原则（新增铁律配套）

- **tracked ≠ 存在** = git 里有不代表磁盘在 = 必须 `ls` 双重确认
- **每个 v_N commit 必须 `git status --short`** 检查 working tree 干净
- **新 references 必须先 `git status` 看是否 untracked** = 防"写了没 add"
- **跨 skill 文件不混合存放** = 谁的 references 谁负责
- **旧版本不堆积** = 升 v_N 时清 v_N-1 的过期文件

## 触发词

- "references 健康度"
- "tracked vs 磁盘"
- "丢了 references"
- "git ls-files vs ls"
- "references 清理"
- "跨 skill 错放"
- "旧版本 references"
- "cleanup references"