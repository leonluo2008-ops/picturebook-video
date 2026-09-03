# 口罩修复 v3 终审收尾陷阱 + faster-whisper 环境实测（2026-08-31 牙医 clip3）

> 本文承接 session-pitfalls §47（口罩漏嘴），收录 v3 收尾三陷阱与 ASR 环境实测配方；§46 安装章节的完整环境细节也搬家至此。

## B1. 放大拼表「假阴性 PASS」——先验裁切框再信「全部干净」

§47 要求裁切放大逐帧检，但**裁切框本身可能没框住口罩**：第一版 8 帧拼图（crop 下缘只到眼眉）vision 照样回答「8帧全部干净」——干净只是因为口罩根本不在画面里。本批靠 vision 自述「裁切范围未含口罩」打回重做，但不能依赖运气：

- **两段式拼表审查**：先提交单帧放大图，让 vision 明确回答「裁切范围是否完整包含白色口罩（鼻梁→下巴）」；确认后再拼 8 帧终审，终审提问要求逐帧同时报告「口罩佩戴状态 + 有无嘴/牙/舌/口腔/开口」。
- **有效性判据**：任何「全部干净」结论必须同时明示「口罩完整可见、无裁切遗漏」才算有效；缺这句 = 本轮审查作废，下移裁切框重拼。

## B2. PASS 结论与工件版本强绑定——旧日志不能给新工件背书

asr_v3.log 的 PASS 实为 14:07 对 v2 重摇版的转写，真 v3 14:10:47 才落盘——**结论时间早于工件落盘时间 = 该项检查无效**，回执前当场重跑该单项。

- 版本备份文件名会说谎：`clip3_v3.mp4` 是 v2 重摇版冒名的；真 v3 = `clip3_v3_real.mp4` = 部署的 `videos/clip3.mp4`（md5 f25b3a27add70da7c10a8786653812d7，1,358,468B）。ground truth 只有「部署路径 + md5」，文件名不作数。
- 引用任何 PASS/FAIL 前两步：`md5sum <部署文件>` 确认工件身份 + 日志时间戳与工件落盘时间对账；对不齐 → 当场重跑再回执。

## B3. faster-whisper 环境（2026-08-31 实测配方）

- bare `python3`（系统 3.12）与 Hermes 自身 venv 都**没有** faster_whisper。**解释器定位顺序**：①既往批次现成解释器（如 `/tmp/pb_video/asr_venv/bin/python`——迁移后 /tmp 路径可能已失效，先 import 试）→ ②自建新 venv：`uv venv /tmp/asr_venv --python 3.12` + `env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY uv pip install --python /tmp/asr_venv/bin/python faster-whisper`（本机代理变量会坑安装与运行，全程 -u 掉；uv 从默认 PyPI 能装上）。
- **就绪轮询**：装完不要立刻跑脚本——`while ! /tmp/asr_venv/bin/python -c "import faster_whisper" 2>/dev/null; do sleep 10; done`，import 可用再跑（多会话并发往同一个 venv 安装时滞后明显）。
- **模型已缓存**（download_root=/tmp/pb_audio/models，models--Systran--faster-whisper-small）时，运行加 `HF_HUB_OFFLINE=1` + 去 socks 代理 = 完全离线可跑，绕开 hf 下载/xet/socksio 全部网络路径：
```bash
cd /tmp/pb_video3 && env -u http_proxy -u https_proxy -u all_proxy \
  -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u no_proxy -u NO_PROXY \
  HF_HUB_OFFLINE=1 /tmp/asr_venv/bin/python asr_clip3_v3_check.py videos/clip3.mp4
```
- 判定脚本要点（asr_clip3_v3_check.py）：lower + 去空白标点后查核心词（接受 dentist/dantist/丹提/登提等变体）+ 牙/张嘴中文词在位；牙医旁白实测 RAW `牙医说,张大嘴巴,Dentist。` → PASS。

## B4. 并发会话 + 回执数字时效（与 picturebook-video-references §23.4 同源）

- **双 build 竞态**：同一 /tmp 工作区多会话并行时，回执前 `ps aux | grep -E 'ffmpeg|build_final'` 查竞态——实测两个 build_final_dentist.py 同时在跑（两个 ffmpeg 同写 final_tmp.mp4），产物 md5 中途漂移且 freezedetect 中段误报 10.8s 长冻结；**串行重跑一次 concat 后假冻结消失**（只剩良性段尾静息）。凡 freezedetect 报「中段长冻结」且涉事 clip 单测干净/未复现 → 先怀疑并发构建产物损坏，串行重建复验，别急着判 clip 画面问题。
- **回执数字时效**：换入新 clip 后旧回执的 md5/直链/大小全部作废。流程：①重跑 concat ②重新 upload_to_uguu ③**回下载直链（curl）→ md5 与本地比对一致**才报新直链，uguu 上传返回的 URL 不能默认可用 ④回执明示「旧 md5/旧直链作废」（牙医批实测 EHvxyOux 直链挂着不含真 v3 的旧 final，peer 可能拿上一条回执的直链当最终版）。