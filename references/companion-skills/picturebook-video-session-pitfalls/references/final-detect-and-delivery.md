# 收尾竞态 / A2A 状态速查 / 成片交付 —— 详细协议（§48/§52 配套 · 2026-08-31 医生 DOCTOR + 工程师批实测沉淀）

> SKILL.md §48/§52 是总章；本文件承载收尾段的完整协议与追加实测。

## 残留写入者：诊断三板斧
1. 同名文件**连续两次** md5sum 漂移；
2. `stat` mtime 晚于自己的操作时间；
3. `ffmpeg -v error` 解码报错（边写边读会爆 Invalid NAL unit size）。

残留写入者两种形态：① ffmpeg 未死进程持续 concat 写入；② 残留会话自己的收尾脚本链（症状：agent 未合成却冒出 *_orphan_copy.mp4、成片每隔几分钟被无声覆盖）。写坏的唯一硬症状：`ffprobe format=duration` 返回 **N/A**（moov 缺失）——文件大小正常 + md5 存在都不是证据。交付前补齐：per-clip 与成片 ffmpeg -v error 解码 0 错误 + 交付前最后一次 md5sum 复核（医生批自检通过后成片仍被盖过一次）。

## md5 漂移 ≠ 必然写坏 —— 先查活写入者，勿急着重拼（医生批核心教训）
孤儿收尾链的写入会**收敛且迟到**：医生批 15:14→15:25，对端「下载校验」指令到达时成片 md5 已漂移（a7fb5e14↔cef59993 反复换手），15 分钟后孤儿构建自跑完**收敛回对端期望的 a7fb5e14**——此时人肉重建反而多余。协议：md5 漂移时先 `ps aux | grep -E 'ffmpeg|build_final|asr_'`；已无进程 → 残留构建已死或已跑完，读**最新 mtime 版本**的 md5 对照对端目标值再决定是否动手。

## 不同构建脚本 ≠ 同一 md5（都可以是合法成片）
同一批 8 clips：build_final.sh（concat demuxer 直拼）→ a7fb5e14 / 9279490B；concat.sh（concat filter 重编码 -crf18 -preset medium）→ cef59993 / 9292469B。两版均通过全部检查项。md5 不同 ≠ 被污染——判「写坏」只看上方三板斧 + duration=N/A，「hash 变了」本身不是证据。核对对端期望 md5 前先分清**版本差异**与**写坏**。

## x264 确定性重建验证法
同一批 8 输入 concat filter + -crf 18 -preset medium 重拼两次，md5 逐位一致（cef59993 复现）= 排除编码随机性，污染源只剩并发写。干净重建后必须重传 uguu 并回读 md5 比对（首次直链装的是污染版本）。

## A2A 收尾速查回执五项模板
对端点名「ASR结论 / 物理复查 / freezedetect+时长 / uguu直链 / 下载校验」时：
1. uguu 直链**当场上传**：`curl -F "files[]=@final.mp4" https://uguu.se/upload` 取 `files[0].url`——工作区 uguu_urls.txt 存的多是参考图链 ≠ 成片链（医生批 uguu_urls.txt 全是 8 张参考图 jpg），**勿搬旧链**。
2. 上传后立即 `curl -o /tmp/final.mp4 <直链> && md5sum`，对照对端期望值；uguu 上传回执的 size 字段 = 本地文件大小，可先对。
3. 物理复查（clip5 专项 + 全 clip 手臂数）结论若产自早前会话的 vision 逐 clip 审查，回执注明出处会话（如 @session:default/20260831_151436_2c76a00d）。
4. asr_results.json 被孤儿/子集重跑覆盖时，按 asr_run.log 行级 RAW/PASS 佐证回填——子集重跑覆盖机制见 references/asr-venv-ops.md。
5. 只回所列条目，一行一条带证据，不加叙事。A2A 状态速查纪律：**别按会话记忆报状态，先 ~1 分钟本地实锤**（md5sum + ffprobe + tail 待定日志）；pending 票的 artifact 已落盘就直接本地 vision 亲判就地解锁，不干等远端回票。

## pkill 自杀铁律
`pkill -f 'final_doctor'` 会匹配自身命令行把自己的 bash 干掉（terminal 返回 exit -9/-15）。进程名含目标文件关键词时：先 `ps aux | grep` 拿 PID，再 `kill -9 <pid>` 点杀；pkill 要用方括号技巧（`pkill -f 'asr_check[.]py'`）。

## 工程师批终态对账（2026-08-31 · §48 五问速查实测）
- 先本地实锤再回话：md5 + mtime 告诉你哪份是新版；task_id 落盘文件（task_clipN.txt）逐段对照，别信对端转述的段↔clip 映射（§45 已有此铁律）。
- 速查三问答法：①「20:00 那份用什么拼的」= 看 concat 清单文件 mtime + 逐输入 md5 对当时 take 版本；②「终版 task_id」= ls task_clipN.txt 逐个 cat；③「ASR/物理过没过」= 读最新 asr_results_*.json + physcheck_results.txt，注意结果文件的 md5 绑定（§49 PASS 票绑 take）。

## §52 A2A 终态速查撞上并行终拼：验货不重拼 + 成片本体全检（2026-08-31 工程师批 peer 收尾实测 · §48 变体二续）

### 现象
A2A peer 来令「两份成片不一致，直接重跑 concat 覆盖」；排雷点杀孤儿 `sleep 120` 后动手前，目标成片被**另一并行会话**（同机另一 hermes kernel）在几分钟后完整替换——本会话旧拼（20:00，含 clip2 旧 take）vs 并行会话新拼（20:31，含 20:23 落盘的 clip2 最新 take；videos_v3/ 里还有第三份同段不同 md5 的 take）。同产物两条合规生产线并存，成片里混的哪版 take 目录结论已不可考。

### 裁决：确认写入收敛后只验货不重拼
- 收敛证据：ps 无 ffmpeg/poller/构建进程 + 成片 md5 连续两轮稳定。
- 重拼的代价：丢掉只存在于并行产物里的已验证最新 take（本例 clip2 新 take ASR「我看见,工程师了!engineer」一发过）；重开写撞窗口；违反「收敛且迟到勿盲目重拼」（上文医生批教训的正面面）。

### 成片本体验货五步（不依赖目录结论）
1. 元数据：ffprobe 时长 == Σ native 段时长（4.096×2 + 5.088×6 = 39.712s 精确相等）、h264+aac 双轨、整片 `-v error` 解码 0 错、freezedetect 0 冻结。
2. **成片本体分句 ASR**：按段边界累计窗口 `ffmpeg -ss <起点> -to <终点> -vn -ar 16000 -ac 1` 逐窗双 beam 转写，判 eng 核心词 + zh 含主题词。**同音别字非污染**：建桥→剑桥（jiànqiáo 同音）判 PASS 不变（§46 第 5 步口径），换 clip 只需替换被否决点重新验证。
3. **take 入片以成片内容为准，不以目录为准**：被否决的 take 可能已被并行会话换掉（本例旧 clip2「尼尔污染」take 已不在片）——直接抽成片该段帧+音频验；段内修复点通过了就别信目录旧结论。
4. 拼表 vision 集检三张：a) 段起始帧 2 列拼表（首段大写 / 其余小写、只两行、无旁白词）；b) 风险段尾帧（本例 clip4 尾帧：人物半身裁至底边 = 与参考图一致的合规构图，巨大化工具必须已消失）；c) 修复点专帧（clip8 女孩踏地 + 椭圆接触阴影）。
5. 交付一气呵成：全过后工作目录任何 take 不再动；上传 uguu → 回读 md5 比对 → 覆盖 /tmp 交付位连续跑完（分段跑会在中间被 SIGTERM 掏空 staged 副本）。

### 排雷操作增补（§48 步骤 1 坑位）
- kill 孤儿**勿用 pkill/grep 匹配自己命令行里也含的关键词**（自杀+误杀）：先 `ps aux | grep -E 'sleep|ffmpeg|poll|asr|concat' | grep -v grep` 看 PID，再按 PID 点杀（本例孤儿是 `bash -c 'sleep 120; …'`）。
- 被 SIGTERM 的收尾命令里，前置 cp 的 staged 上传文件不会落盘——重跑上传直接用工作目录源文件，别依赖 staged 副本。

### 工程师批收尾索引（2026-08-31）
- 终版五件套：md5 90ccb0640bcc2a9f42be661d841c33eb / 11,587,197B / 39.712s / 0 冻结 / uguu h.uguu.se/RAAcxzEM.mp4（回读 md5 一致）。
- 全检证据：8 段起始帧拼图全对（首段大写+余小写+无三行）+ clip2 新 take（2a170fba）两轮文字带拼图干净 + clip4 尾帧半身合规 + clip8 专帧踏地有影。
- 分句 ASR：s1 工程师Engineer / s2 我看见,工程师了!Engineer / s3 工程师在剑桥Engineer（=建桥同音）/ s4 带着黄色安全帽 / s5 有图纸 / s6 用好多工具 / s8 把桥建好了——eng+zh 全 PASS。
- take 指定：clip1=cgt-…84xbx / clip2=cgt-…sf5bv / clip3=cgt-…pxv2h / clip4=cgt-…7z46s / clip5=cgt-…h56gz / clip6=cgt-…rrd9f / clip7=cgt-…8zh7q / clip8=v2=cgt-…nrptp（videos/clip8.mp4 与 videos_v2/clip8_v2.mp4 同 md5 8cc7a1e5）。

## 医生批收尾索引（2026-08-31）
- 全过程会话：@session:default/20260831_151436_2c76a00d（§48 竞态复现→收敛→全项 PASS 卷宗；物理复查 clip5 六帧五项 + 全 8 clip 手臂数全 PASS）。
- 最终交付版：a7fb5e148533eb6cfafaa6489729987a / 9279490B / 32.800s / 0 冻结 / uguu h.uguu.se/SzxTHVhA.mp4 / 回读 md5 一致。
- 保留的 cef59993 重编码版备份：/tmp/final_doctor_orphan_copy2.mp4（同批 clips，合法成片）。
- A2A「恢复执行」首查纪律：task_id 全部落盘且状态全 running = 免补传免重提；直接照指令重传已过期 uguu 链接 = 重复烧任务+撞限流。
