# 飞书云盘素材获取（lark-cli drive 接入 SOP）

> 适用场景：用户的绘本图片+旁白放在飞书云盘，需要下载到本地才能喂给 seedance2.0-tool。
> 这是绘本视频工作流的「Phase -1」——Phase 5 之前先把素材拿到。

## 1. 工具与决策

`lark-cli` 已经预装在 `~/.npm-global/bin/lark-cli`。本地没有 `lark-drive` skill，直接用 API。

**核心决策**：身份选 `user-default`（用用户个人身份）而不是 `bot-only`，否则读不到用户个人云盘。

## 2. 一次性绑定（首次）

```bash
# 1. 绑身份（user-default）
lark-cli config bind --source hermes --identity user-default --force

# 2. 触发授权（QR 模式，避免长阻塞）
lark-cli auth login --no-wait --json --domain drive > /tmp/lark-auth.log 2>&1 &
sleep 3
cat /tmp/lark-auth.log

# 3. 从输出拿 device_code + verification_url，生成 QR 给用户扫
lark-cli auth qrcode "<verification_url>" -o /tmp/lark-qr.png

# 4. 用户扫完 → 用 device_code 续上轮询（会阻塞等用户确认）
lark-cli auth login --device-code "<device_code>" > /tmp/lark-poll.log 2>&1 &
sleep 6
tail -10 /tmp/lark-poll.log
```

## 3. 关键踩坑 ⚠️

| 坑 | 现象 | 修复 |
|---|---|---|
| 只用 `--recommend` 不带 `--domain` | 报 `please specify the scopes to authorize` | 必须加 `--domain drive`（或 `all`） |
| QR 链接 10 分钟过期 | 用户扫晚了报 `device code expired` | 重新跑 `--no-wait --json` 拿新 code，旧 code 自动作废 |
| 跑完一次 `auth login` 没拿到 `drive:drive.metadata:readonly` | 后续 `api GET .../files` 报 `Permission denied [99991679]` | **必须用 `--domain drive` 重做授权**，加 scope 是叠加的不是替换 |
| 阻塞模式等太久 | 工具 timeout 被打断，前面的 code 又被作废 | 用 `--no-wait --json` 拿 code → QR → 让用户扫 → 后续 `--device-code` 续轮询 |

## 4. 列出文件夹文件

```bash
lark-cli api GET /open-apis/drive/v1/files \
  --params '{"folder_token":"<FOLDER_TOKEN>"}' \
  --format json
```

返回 JSON 里 `data.files[].name / token / url` 是关键字段。**记下每个 file 的 token**（不是 url，url 带签名有时效）。

## 5. 批量下载文件

⚠️ **路径陷阱**：`lark-cli api GET ... -o <path>` 和 `seedance.py --download` 一样，**`--output` 必须是相对路径**（在当前目录下），传绝对路径会报 `unsafe output path`。

```python
import subprocess, os
os.chdir(target_dir)  # 先 cd 到目标目录
for name, token in mapping:
    subprocess.run([
        "lark-cli", "api", "GET",
        f"/open-apis/drive/v1/files/{token}/download",
        "-o", name  # 相对路径
    ])
```

## 6. 重新授权（scope 缺失时）

授权 scope 是**叠加**的。第一次授权少了 `drive:*`，第二次再跑 `auth login` 加 `--domain drive` 即可，已有的 scope 不会丢。

```bash
lark-cli auth login --no-wait --json --domain drive
# 用户再扫一次码
lark-cli auth login --device-code "<new_code>"
```

跑完用 `lark-cli auth status` 看现在有所有 scope。

## 7. 已踩过的坑汇总（绘本视频场景实测 2026-06-02）

1. **`browser_navigate` 打不开云盘** —— aistar-work 飞书租户需要登录态，bot 工具无 cookie
2. **`lark-cli drive` 子命令不存在** —— 只有 `api GET /open-apis/drive/...`，必须用通用 API
3. **`.env` 安全策略** —— lark-cli 和 seedance.py 都有「output 必须是相对路径」限制（防 path traversal）
4. **QR 生成阻塞** —— 永远用 `--no-wait --json` 拿 code，避免单条命令阻塞 10 分钟

## 8. 验证清单

- [ ] `lark-cli auth status` 显示有 `drive:drive.metadata:readonly` + `drive:file:download` + `space:document:retrieve`
- [ ] `lark-cli api GET /open-apis/drive/v1/files --params '{"folder_token":"..."}'` 返回 `code: 0` + 文件列表
- [ ] 下载文件能用 `file xxx.jpg` 识别为 JPEG
- [ ] 8 张图按 `1.jpg` ~ `8.jpg` 命名（绘本 skill 约定）
