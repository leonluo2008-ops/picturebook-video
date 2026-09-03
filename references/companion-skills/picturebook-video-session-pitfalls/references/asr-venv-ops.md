# ASR venv 运维速查（faster-whisper · 2026-08-31 牙医批补充）

> SKILL.md §46 是 ASR 发音自检协议总章；本文件是安装/就绪环节的踩坑细节。

## 就绪门（先等 import ready，再跑检测）
- **残留安装进程未收尾就执行检测 → `ModuleNotFoundError: No module named 'faster_whisper'`**（牙医批 asr_clip3_v3_final.log 首次内容即此 Traceback，不是真检测结果）。
- 就绪门（转写前必跑）：
```bash
for i in $(seq 1 40); do /tmp/asr_venv/bin/python -c "import faster_whisper" 2>/dev/null && break; sleep 10; done
```
- READY 之后再跑转写；**不要同时开第二份 `uv pip install` / `pip install`** —— 牙医批 14:29 实测 3 个安装进程并存（uv×2 + bash -lc×1），并发安装只添乱不加速。
- 首装体积 ~114MB（numpy/hf-xet/onnxruntime/ctranslate2/av）属正常，别当卡死反复打断（每次打断都从头再来一轮）。

## 环境变量
- **安装**：必先摘全部代理变量再装，否则 socks 代理让安装期请求挂掉：
```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  uv pip install --python /tmp/asr_venv/bin/python faster-whisper
```
- **运行**：模型已缓存后一律 `HF_HUB_OFFLINE=1` + 摘代理离线跑，最稳。
- ⚠️ **import 就绪 ≠ 模型已缓存**（医生批 2026-08-31 实测）：就绪门只验 `import faster_whisper`，import 通过后离线转写仍会炸 `OfflineModeIsEnabled / LocalEntryNotFoundError`（`/tmp/asr_models` 为空、~/.cache/huggingface 仅 64K 都出现过）。先确认模型缓存；从未下过就先做一次在线引导（成功一次后即可永久离线跑）：
```bash
env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  HF_ENDPOINT=https://hf-mirror.com HF_HUB_DISABLE_XET=1 \
  /tmp/asr_venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8', download_root='/tmp/asr_models'); print('MODEL-READY')"
```
- 转写脚本**模型只载一次、逐 clip 循环复用**（8 clip 全量 <2min），不要每 clip 重载模型。
- 首次安装的完整 CN 网络三件套（清华镜像 / HF_ENDPOINT / HF_HUB_DISABLE_XET）与 uv 一步到位替代命令见 SKILL.md §46。

## 牙医批实测记录
- `asr_clip3_v3_check.py` 输出格式：`RAW: <转写原文>` + `dentist_ok= yayi_ok= zhangzui_ok=` + `VERDICT: PASS/FAIL`。
- 真 v3 转写「牙医说,张大嘴巴,Dentist。」→ PASS。
- **log 时间戳纪律**：旧 log 的 mtime 早于最后一版 clip 落盘时间 = 过期票，必须重跑覆盖后再判（本会话 asr_v3.log 里的 PASS 是 14:07 对 v2 重摇版的转写，早于 14:11 真v3 落盘，不可采信）。

## 医生批实测（2026-08-31 · asr_check.py 批量协议）
- `asr_check.py` 为工作区级通用脚本：默认转写全部 8 clip、模型只载一次、结果落 `asr_results.json`；**传参即子集**（`asr_check.py 1` 只转 clip1）。
- ⚠️ **子集重跑会整文件覆盖 asr_results.json**——JSON 只剩传入的 clip 条目（医生批补跑 clip1 后 2-8 号条目消失）。保 8 clip 全量结论：补跑前 `cp asr_results.json asr_results_full.json`，或一律不传参跑全集。已被覆盖时从 asr_run.log 按行回填逐 clip RAW/PASS（回执仍可如实回报）。
- PASS 判据（本批）：text_clean 含「医生」+ 转写含 doctor 变体（lower 后 `doctor` / `dɔktə` / `dɑktə`，或近音汉字 塔克/多克/道克/达克）——whisper 常把英文尾音节转成近音汉字，按变体匹配勿直判 FAIL。
- **whisper 同音错字是转写噪声不是配音错误**：「医生穿白大挂(褂)」判 PASS（判据只锁核心词+目标词，不修同音字）。
- 8/8 逐 clip RAW 佐证（asr_run.log）：医生,doctor / 这是医生Doctor。/ 医生穿白大挂,Doctor / 我去看医生,Doctor。/ 医生 说 张嘴Doctor / 医生听我的心跳Doctor / 医生帮助我Doctor / 我的医生让我好起来Doctor → 全 PASS，无错词。