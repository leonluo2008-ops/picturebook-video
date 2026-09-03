# 医生批收尾竞态与构建变体甄别（2026-08-31 · A2A 双会话同盘）

> SKILL.md §48/§48b 的案例底账。牙医批是「单会话孤儿竞态」，医生批升级为「peer hermes kernel + 本地超时孤儿」双写同一 /tmp/pb_video4/ 工作区。

## 现场时间线（本地日志可证部分）
- 15:06–15:09 上一轮（超时的本地会话）提交 seedance、poll 全量下载 8 clip、起 asr_check.py —— **两个实例并存**（15:14 起，模型未缓存，永远跑不出结果）。
- 15:13–15:14 final_doctor.mp4 两度成型：9279490B(`a7fb…`) ↔ final_doctor2.mp4(9292469B，随后消失)。
- 15:14–15:16 /tmp/final_doctor.mp4 出现（上传/拷贝动作痕迹）→ 本会话开局即撞见双写现场。
- 15:18 本会话 kill 两个 asr 孤儿。⚠️ 第一次 `pkill -f 'asr_check.py'` 匹配 hermes 自己的 bash 包装命令文本（命令串里含同字样）→ 自杀 SIGTERM(exit -15)；换非自匹配字符类 `'asr_check[.]py'` 成功。
- 15:22 本会话 concat.sh 重建 → 9292469B / `cef59993…`，与孤儿留下的副本**逐字节相同**（concat filter 构建确定性可复现）。
- 15:27:57 final_doctor.mp4 **再次被覆写**为 9279490B / `a7fb…`——peer kernel 静默重跑 build_final.sh（期间无任何可见前台进程，kill 孤儿时它尚未开始）。
- 15:32 uguu 上传 → 回下 = `a7fb` = peer 预期值。五件套（md5/ffprobe/freezedetect/抽帧）全部改以**回下副本**重跑后收口：freezedetect 0 冻结、ffprobe 32.80s moov 完整、clip5 三帧 vision 复核 PASS。

## 两个构建变体指纹（同一批 8 个源 clip，都合法 · 冲突时先 SIZE 分诊）

| 变体 | 脚本 | 字节大小 | md5 | 总时长 |
|---|---|---|---|---|
| concat demuxer 版 | build_final.sh（`-f concat` + concat_list.txt，re-encode crf18 24fps + faststart） | 9279490 | a7fb5e148533eb6cfafaa6489729987a | 32.80s |
| concat filter 版 | concat.sh（`-filter_complex concat=n=8:v=1:a=1`，re-encode crf18 24fps + faststart） | 9292469 | cef59993cf1b8bd46276a3a1af3f5232 | 32.768s |

判变体：看字节大小（9279490 vs 9292469）一步分诊 → 按对应脚本本地重跑复核 md5。两个变体画面同内容：clip 区域同时间戳帧 PIL 灰度 diff = 均值 0.77–3.34、|d|>30 像素占比 0.0–2.9%（18.2s 帧的 ~2.9% = 帧边界 1 帧漂移；其余帧 <0.05%）。

## 教训
1. **A2A 收尾不是单机事务**：peer kernel 会对同一 workspace 独立重跑同名脚本，pkill 只管本机孤儿。判稳证据永远取自动 download-back 副本，本地快照需 mtime 稳定数分钟才可信。
2. **md5 不符 ≠ 污染**：先 SIZE 分诊变体 → 本地复现复验 → 再定性「变体 / 污染」。销毁 foreign artifact 前必须能证明从现存输入复现不出它，否则可能只是另一个合法变体。
3. **抽帧审计可迁移判定**：变体间像素 diff 为编码噪声 → 逐 clip 审计结论直接继承；内容级差异 → 必须对交付字节重跑 vision。
4. uguu 对相同字节重传不报 dupe（返回 `dupe: false`）——其 dedupe 不可依赖，校验一律以回下 md5 为准。
5. md5 证据必须绑定实际交付字节（上传→回下→核对），不能绑「我某时刻在本地重建的那一版」。
6. **物理铁律审计口径**（peer 点名的医生批重点项）：男孩张嘴配合检查 / 医生口型锁定大笑张嘴 / 压舌板器具 / 无口罩无牙模 + 全员单人物≤2臂2手 —— clip5 用 6 帧加密抽帧（0.3s 间隔），其余 clip 每个抽 3 帧（0.5/2.0/3.5s，PIL 拼表），逐帧逐角色清点肢体；画面文字核对 = 对照该页 L4 锁定大小写（封面页 DOCTOR 全大写是参考图原样，不是 drift）。

## 2026-08-31 晚追加：clip8 悬浮修复轮实证（同盘闭环完成）
- **变体表补第 3 个实测值，且推翻「32.80s」稳定指纹论**：concat demuxer 版（build_final.sh）本轮重跑得 **30.000s / 8156178B / e1ecca…** ≠ Σclip（8×4.096=32.768s）——demuxer 对本批 VFR 源逐 clip 丢约 0.35s（合计 ~2.8s）；此前 32.80s 只是历史源时长下的巧合。concat filter 版（concat.sh）重跑 = 32.768s / 9132556B / 45d1d88e…，与 Σclip 严格相等。
- **变体校验门禁（升级为硬规则）**：合成后必查 `final 时长 == Σ 逐 clip ffprobe 时长`（容差 <0.05s）；不满足 = 构建变体丢帧，一律以 concat filter 版为准重出。此门禁比「认字节大小分诊」稳——字节/md5 随源更新会漂，总时长==Σclip 不会。
- **A2A 速查请求 ≠ 状态快照**：16:24 peer 下达修复指令 → 16:32 同一 peer 速查「修好没」，实际尚未执行（prompt 未改、无新 task、指令时间后零落盘）。收尾期任何「XX 做了没」类速查：先 `find <workdir> -newermt '<指令时刻>'` + 目标文件 mtime 判事实；**有缺口直接在本会话补跑全闭环**（本例改 prompt→submit→poll→9帧复查→ASR→concat filter→uguu→回下校验，约 35 分钟收口），不要只回「没做」让 peer 二次等待。
- 本轮最终交付指纹：新 task `cgt-20260831163342-d9hft`（121s 生成）；final_doctor.mp4 = 32.768s / 9132556B / md5 45d1d88e57edc2eb0a01e34c03e2e530 / uguu https://n.uguu.se/xdtogPwJ.mp4（回下 md5 一致；uguu 对不同字节仍报 dupe:false，延续教训4）。旧悬浮版 clip8 备份：videos/clip8_v1_floating_backup.mp4。
