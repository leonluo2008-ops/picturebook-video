---
name: picturebook-video-session-pitfalls
description: "Session-specific pitfalls for picturebook-video workflow — 9:16 conversion fixes, multi-image clip split rules, action-element position anchoring, narration-action-word pollution (mask-mouth semantic leak), tail text/case drift, vehicle native text, slow narration, MEDIA delivery discipline, vision batch/hallucination traps, R11 keyword traps, text preservation, quantity control, stale-process race on concat, ASR venv ops, final integrity five-check, halfbody-crop→floating legs, regen take race (multi-writer), parallel final-build reconciliation (verify don't rebuild; final-file sentence ASR + take-in-final check). Companion to the bundled picturebook-video skill."
metadata:
  hermes:
    tags: [picturebook-video, pitfalls, vision-hallucination, r11-keyword-trap, batch-production, text-preservation, camera-modification, chinese-character-misidentification, core-word-retention, repeated-failure-tolerance, vertical-blank-space, sensitive-content-detection, integrity-check, asr-ops]
    related_skills: [picturebook-video]
---

# picturebook-video Session Pitfalls

> **Companion skill** to the bundled `picturebook-video`. Captures session-specific learnings that don't belong in the main skill's SKILL.md.

## §31 Reference-Video Reproduction (视频 → 绘本视频 · 2026-08-21 轻松学英文实测)

### Trigger
User sends a **reference video** (not an image pack) and asks "能不能做出这样的视频 / 先做个样片看看". Common case: a children's bilingual word-cognition video (每页一个词 + 顶部中英文字 + 萌系卡通 + 儿歌节奏). This is a NEW input path vs the standard image+SRT flow — the reference images come from **extracting video frames**.

### Workflow
1. **ffprobe 看规格**: resolution / duration / aspect (判断是否竖版 9:16).
2. **ffmpeg 抽帧**: `ffmpeg -i in.mp4 -vf "fps=1/3" frames/f_%02d.jpg` (每 3 秒一帧，覆盖全片).
3. **vision_analyze 逐帧**: identify each page's subject animal + top text (English + 中文) + style.
4. **选一帧做参考图**: pick a frame with clear subject + complete text.
5. **清理播放器 UI 叠加（关键）**: video frames often carry a **semi-transparent white play button** (player UI overlay, NOT reference content) in the center.
   - Clean with PIL ring-fill: take the ring of pixels 8-12px outside the button bbox, average them, fill the button region.
   - ⚠️ **Vision model over-reports the overlay (陷阱 #16)**: after ring-fill, vision may STILL claim "还有播放按钮". Verify by `crop`-zooming the button region alone — if the region has no bright pixels (mean<200, bright px=0), it's clean and the vision read is a false positive. Don't redo on a single vision read.
6. **复刻格式**: one word per page + top two-line text (English repeated twice + 中文 repeated twice, e.g. `pig pig / 小猪 小猪`) + cute cartoon + nursery-rhyme rhythm.
7. **先静默 spike 验证画面** (路径 C, generate_audio=false), then add audio once the visual is approved.

### Audio decision
Reference video is **nursery-rhyme rhythm** (not narration). Offer the user two options:
- **A. 儿歌风**: 欢快儿歌 BGM + 念核心词 (closest to the reference video)
- **B. 领读风**: 温柔女声领读 + 音效 (closer to the picturebook positioning)

### Key pitfalls
- Play-button cleanup + vision false-positive = 陷阱 #16; use crop-zoom self-check, don't redo on single vision read.
- If the reference frame is already vertical (e.g. 720x1048 ≈ 9:16), feed it directly + `ratio=9:16` for full-frame (火锅流程, no vertical-force phrasing).
- Reference video is "pure word cognition" (no full-sentence narration) — simpler than 领读绘本: one word per page suffices, no need for a full narrative arc.

## §32 Vision Batch Concurrency + Flaky-Service Fallback (2026-08-25 飞机实测)

### Phenomenon
Step 2 vision on an 8-image pack: firing **all 8 vision_analyze calls in parallel** → 6 failed with `Connection error`. Retrying in **batches of 3-4** succeeded consistently. One stubborn image (7.jpg) failed **3 consecutive times** (Connection error → 503 → 500) before succeeding on a 4th attempt minutes later. The file itself was never the problem.

### Protocol
1. **Step 2 vision: batch 3-4 images per round, not all N at once.** Parallel bursts of 8 trip the vision provider's connection handling; 3-4 per batch works reliably.
2. **Single-image repeated failure (503/500/Connection)**: verify the file first with PIL — `Image.open(path).size` + `.mode` returning normal dimensions (e.g. 1920x1200 RGB) = file is intact, it's a vision-service hiccup, NOT a broken asset. Don't re-download / re-extract / fabricate the description.
3. **Proceed with the alignment table anyway**: mark the pending image `⏳ vision 待补` in its row. Structure is still confirmable from the SRT segment number + the book's consistent pattern (same word pair on every page). Confirm with the user, continue to Step 3/4. Don't block the whole batch on one image's vision.
4. **Re-try vision before Step 5** (prompt writing needs the per-image description) — by then the service has usually recovered. 7.jpg succeeded on the 4th attempt this way, and its description turned out to matter (only image with nose pointing RIGHT + girl in window = 「我坐飞机」).
5. Keep the vision question prompt **identical across retries** (same structured 5-point ask) so recovered results are directly comparable.

### Key
- 8-wide parallel vision = self-inflicted connection errors; 3-4 per batch is the durable pattern.
- Vision flakiness ≠ asset problem: the one-command PIL file check disambiguates.
- The alignment table can go out with a pending row; vision is only hard-required before Step 5 prompt writing.

## §1 Vision Hallucination Cascade (Snow翻车 · 2026-08-03)

### Phenomenon
On collage-style (Eric Carle) images, vision hallucinated 2.jpg (paper snowflake cutouts) as "snowy field with tree stumps". This caused a **1-position offset cascade** — every image description was wrong, and the video had missing/misplaced images.

### Root Cause
Collage/papier-collé textures trigger vision hallucinations:
- White paper snowflakes → "snow/ground"
- Blue textured background → "sky"
- Paper grain → "bark/tree stumps"

### Fix Protocol
1. User reports "images missing/wrong" → immediately re-vision ALL N images
2. Ask precise: `"Describe ONLY what you actually see. Is this X or Y? Be precise."`
3. Produce corrected image-vs-segment alignment table
4. Rewrite all Clip prompts with accurate descriptions
5. Re-submit to seedance

### Prevention
- Step 2: for collage images, ask a **confirmation round**: `"Describe ONLY what you actually see"`
- Cross-validate vision descriptions against filenames + SRT segment numbers
- If description seems off (paper snowflakes → "snowy field"), flag and re-ask

## §2 R11 Spatial Target Keyword Trap (All 4 batches · 2026-08-03)

### Phenomenon
`verify_prompt.py` R11 uses exact keyword matching. Natural language variants don't match:
- ❌ `从画面四周向中央轻轻飘落` → misses `画面中央`
- ❌ `从左向右横移` → misses `从左侧`
- ✅ `穿过画面中央` → hits `画面中央`
- ✅ `从左侧向右横移` → hits `从左侧`

### Root Cause
`verify_prompt.py` `check_camera_four_piece()` at lines 448-464 uses `re.escape(kw)` exact match against a keyword whitelist.

### Required Spatial Target Keywords
```
画面左侧, 画面右侧, 画面中央, 画面顶部, 画面底部,
画面左, 画面右, 从左侧, 从右侧, 从顶部, 从底部,
由近及远, 由远及近, 由左, 由右,
穿过, 横穿, 飞越, 跑过,
出画面, 跑出画面, 飞出画面, 走出画面, 游出画面, 驶出画面,
离开镜头, off-screen, out of frame, exits, runs off,
消失在天际, 消失于, 消失,
镜头跟随, 镜头横移, 镜头跟拍,
camera follows, camera pans, camera tracks
```

### Required Camera Movement Keywords
```
横移, 推近, 跟拍, 固定, 平视, 侧面, 低角度, 特写, 全景, 中景,
俯拍, 仰拍, 拉远, 摇镜, 跟焦,
camera follows, tracking shot, pan, tilt, zoom in, zoom out,
dolly, from behind, from the side, low-angle, high-angle,
fixed camera, static shot, wide shot, close-up, medium shot,
from above, from below, aerial, panning
```

### Fix
When writing prompt §2 camera descriptions, **use exact whitelist phrases**:
- ✅ `镜头从左侧向右横移扫过...` (hits `从左侧`)
- ✅ `镜头缓慢推近到...，穿过画面中央` (hits `推近`+`画面中央`)
- ✅ `镜头从天空缓缓向下俯拍到...全景，穿过画面中央` (hits `俯拍`+`全景`+`画面中央`)

### Quick Debug
When R11 FAILs, read `verify_prompt.py` lines 448-464 (`space_keywords` + `camera_keywords` lists) and rewrite using those exact words.

### Static-Subject R11 Fix (黑板/墙/风景/家具 · 2026-08-17 黑板实测)
When the subject is a **static object** (blackboard, wall, scenery, furniture), R11 still FAILs "缺空间目标" — because the script judges **subject displacement**, and a static object has none. **The fix is NOT to make the object move**; it's to attach a space-target keyword to the **camera movement** or the **surface/local-element effect**:

| Scene | ❌ R11 FAIL | ✅ R11 pass |
|---|---|---|
| static subject + camera push-in | 「镜头缓慢推近。黑板整体轻微上下浮动」 | 「镜头**由远及近**缓慢推近**至画面中央**。黑板整体轻微上下浮动」 |
| static subject + surface effect | 「黑板绿色表面泛起轻微光泽波动」 | 「黑板绿色表面**从画面中央**泛起轻微光泽波动」 |
| static subject + local element | 「ABC 字母逐个轻微弹跳」 | 「ABC 彩色字母**从画面左侧**逐个轻微弹跳**至画面中央**」 |

**Rule**: for static-subject shots, put a space-target keyword (`画面中央 / 由远及近 / 从画面左侧…至画面中央`) in the **camera sentence** or the **surface/local-element action sentence**. Writing only "主体轻微浮动/弹跳" has no displacement → R11 FAILs. Always re-run `verify_prompt.py` after patching and confirm 0 failures.

**⚠️ Cover-page static subject = highest-frequency first-draft R11 miss (2026-08-27 玉米 CORN 复核)**：绘本第一图（封面/单词卡）几乎总是"贴纸式静态主体 + 标题"（单独一根玉米/苹果/蜡烛居中），没有天然位移 → 首稿段 2 镜头 1 极易只写"苞叶/叶片轻微摆动"（无空间目标）→ verify 报 FAIL R11 缺空间目标，再补一轮。**预防 = 首稿就给封面表面/局部元素动作句带上白名单空间词**，例如玉米封面写"绿色苞叶从画面左侧向右侧方向轻轻摆动横穿画面中央"（命中 画面左侧+画面中央+横穿），别等 verify 报错再 patch。根因 = 事件驱动（模板写"主体轻微摆动"）而非动作驱动（写"从画面X边缘Y动作"）。

### Additional Literal-Keyword Traps (2026-08-17 黑板/书/粉笔/圆规 4-batch 全踩)
Beyond the static-subject rule, these exact literal variants FAIL R11 and must be rewritten to whitelist words:
- ❌ `白纸中央` → ✅ `画面中央`（"X中央" 一律不匹配，必须写 "画面中央"）
- ❌ `从左到右` → ✅ `从画面左侧到画面右侧`（"从左到右" 不在关键词表）
- ❌ `居中` 单独 → ✅ `居中占据画面中央`
- ❌ `从画面左侧移动到画面右侧` 里的 `移动到` 不匹配 → ✅ 用 `从画面左侧到画面右侧`（动词用 `到`/`穿过`/`横穿`，不用 `移动到`）
- 静态主体镜头段默认安全写法：`固定平视镜头。{主体}居中占据画面中央，...` 或 `镜头由远及近缓慢推近至画面中央。` —— 每个镜头段先保证含 `画面中央` 或 `由远及近` 再写动作，可避免反复 patch。
- 多图 clip 里每个镜头段都要自查一遍（clip1 常漏最后一个镜头），别只修报错的那一个。

### R11 有两个独立 FAIL 消息——"缺运镜" vs "缺空间目标"，且不只发生在静态主体（2026-08-19 馒头 STEAMED BUN 实测）
R11（镜头 4 件套）实际会报**两种不同**的 FAIL，且都**不只**发生在静态主体——动态主体（馒头/动物/人在原地微动）一样会命中：
- `FAIL R11: 镜头 N 缺运镜 (镜头 4 件套缺件 1)` = 该镜头段**开头没有任何运镜动词**（横移/推近/跟拍/固定/平视/特写 等）。即使主体本身在动（馒头呼吸起伏/弹跳），只要段 2 镜头段没写运镜词 → 照样 FAIL。
- `FAIL R11: 镜头 N 缺空间目标 (镜头 4 件套缺件 3)` = 主体/镜头位移没写空间目标（从画面 X 边缘 / 穿过画面中央 / 由近及远 等）。

**通用修法（馒头批一次过）**：写 prompt 时给**每一个**段 2 镜头段开头统一前缀运镜动词（别等 verify 报错再逐条 patch，clip 常漏最后一个镜头）：
- 静止/缓慢镜头 → `固定平视镜头。{主体}…`（"固定"+"平视"都在白名单，一次满足件 1）
- 特写→拉远 → `镜头从特写…缓缓拉远至…全部进入画面`
再在主体动作句补一个空间目标（`从画面中央`）满足件 3。馒头批第一个 verify 全 FAIL"缺运镜"（4 clip 全挂），补 `固定平视镜头` 前缀后仅 clip3 镜头2 又报"缺空间目标"，再补 `双手从画面中央捧起…` 即全 OK。**结论：每个镜头段都写成 `运镜词 + 动作 + 空间目标` 三件套齐备再提交。**

### Rhyming-Word / Phonics Grid Pages (book/look/cook/hook · 2026-08-17 书实测)
A recurring content type in phonics picturebooks: a segment's narration is a **rhyming word family** (`book、look、cook、hook，都押 OOK！`) and the reference image is a **2×2 flashcard grid**, each card = one word + 中文 + illustration (book/书本, look/看, cook/烹饪, hook/挂钩). When writing the prompt for such a page:
- **Describe each card's word individually** in §1 — they are 4 separate text elements, not one. `左上 book/书本（打开的书）、右上 look/看（大眼睛）、左下 cook/烹饪（冒蒸汽的锅）、右下 hook/挂钩（金属钩）`.
- **⚠️ HARD RULE: per-word binding, NOT rhyme-only.** The narration reads 4 words in sequence; each word must bind to its OWN card. If you write "四张卡片一起弹跳" or "念到「OOK」时四张卡片依次轻微弹跳", Seedance animates all 4 cards together and the audio doesn't map to the right card → user rejects: "音频和画面中单词没有对应". Correct: bind each word to its specific card in §2, §3, AND §5:
  - §2: `念"book"时左上 book 卡片弹跳高亮，念"look"时右上 look 卡片弹跳高亮，念"cook"时左下 cook 卡片弹跳高亮，念"hook"时右下 hook 卡片弹跳高亮，念"都押 OOK"时四张卡片一起轻微弹跳`
  - §3: list each word separately — `段 7 念"book"：左上卡片弹跳高亮` / `段 7 念"look"：右上卡片弹跳高亮` / ...
  - §5: N words = N sounds, each tied to its card — `音效：念"book"时左上卡片配"叮"声，念"look"时右上卡片配"叮"声，念"cook"时左下卡片配"叮"声，念"hook"时右下卡片配"叮"声，四个"叮"声节奏递进`
- The shared rhyme `OOK` is only the FINAL emphasis (all four bounce together on "都押 OOK"), not the primary binding.
- The 中文 on each card is the word's translation (书本/看/烹饪/挂钩), distinct from the page's own `book/书` title text — don't conflate them.
- Static-object R11 fix applies here too: the cards are static, so put space keywords in the camera/effect sentence (`四张卡片从画面中央依次轻微弹跳`).
- **判定口诀**: 旁白里并列 N 个独立词（逗号/顿号分隔的单词列表）= 画面必须有 N 个对应元素，且每个词绑定到各自元素，不能"一起动"。

## §3 Seedance Quantity Control Instability (2026-08-04 九/五/四/一 实测)

### Phenomenon
Seedance consistently fails to render exact quantities (9 ducks, 5 chicks, 4 rabbits, 1 duck). It either adds extra objects or drops some. Multiple retries with the same prompt don't help.

### Root Cause
Seedance treats quantity as a "suggestion" rather than a hard constraint. When the prompt describes a scene with movement (ducks walking, chicks wiggling), Seedance may generate additional objects to "fill" the visual space.

### Fix Protocol (priority order)
1. **Split into independent short clip (4-6s)**: Extract the problematic quantity scene into its own clip with only 1 reference image + simple description. Reduces Seedance's generation burden. E.g., 9 ducks → 4s standalone clip with only 2.jpg.
2. **Use `从全景开始` camera**: Write `镜头从全景开始，X全部在画面中，然后镜头缓缓推近再拉远` — everything visible from frame 1, avoids Seedance adding objects during zoom-out.
3. **Exact row/column layout**: Write specific counts like `后排5只、前排4只交错排列` or `3行3列`, never vague `排成两行`.
4. **Explicit quantity constraints**: State `只有X个` and `不增加也不减少` in both §1 and §2.
5. **Do NOT retry same prompt >2-3 times**: If quantity is still wrong, change strategy (split clip / change camera), don't keep retrying.

### Example: 9 ducks fix
```
❌ Before (in 10s clip with 2 other scenes): 九只黄色小鸭在绿色草地上排成两行
→ Seedance generated 5-7 ducks

✅ After (4s standalone clip, only 2.jpg):
镜头展示参考图 @Image2 的全部内容，九只黄色小鸭在绿色草地上，后排5只、前排4只交错排列，镜头保持全景展示参考图画面，小鸭们一摇一摆，橙色小脚交替迈步，严格保持参考图中后排5只前排4只共九只小鸭，不增加也不减少小鸭数量。
→ Still failed on first try, but shorter clip + simpler scene improved consistency
```

## §4 缺图处理 / §5 运镜修改（详见 references/missing-image-and-camera.md）
- 缺图（图数 < SRT 段数）：对位表标缺、只报差异「包里缺了X.jpg（对应段#Y）」等用户补图，不猜不编。
- 用户要「显示出X个」= **运镜+排列修，不是数量约束修**：特写缓拉远 / 全景推近再拉远 / 展示参考图全部内容（完整模式表见 references）。

## §6 Vision Misidentifying Chinese Characters as Numerals/Letters (2026-08-05 七 SEVEN 实测)

### Phenomenon
Vision model consistently misidentifies the Chinese character "七" as:
- The Arabic numeral "7" (on 1.jpg, 5.jpg, 7.jpg)
- The lowercase letter "t" (on 2.jpg, 3.jpg, 4.jpg, 6.jpg)

This caused prompt text descriptions to say "数字7" or "字母t" instead of "汉字'七'", which meant Seedance had no reason to render the correct character.

### Root Cause
Vision model's text recognition is unreliable for distinguishing Chinese characters from visually similar Latin/numeral glyphs, especially in hand-drawn/crayon-style children's illustrations where strokes are thick and rounded.

### Fix Protocol
1. **Always ask a follow-up question** when vision reports a character that could be ambiguous: `"Is this the Chinese character 七 (meaning seven) or the Arabic numeral 7 or the letter t?"`
2. **Cross-reference with context**: If the image is about learning numbers and has bilingual text (English + Chinese), the second element is almost certainly the Chinese character, not a numeral or letter.
3. **Write the exact character in the prompt**: Use `汉字"七"` not `数字7` or `字母t`.

### Prevention
- For any bilingual number-learning image (SEVEN/seven + character), assume the second text element is the Chinese character unless proven otherwise
### Key: 2 retries max on the same approach. After that, the definition of insanity applies.

## §11 Vertical Mode Blank Space Prevention (2026-08-05 六 SIX 实测)

### Phenomenon
User got increasingly frustrated after 3 rounds of retrying the same issue (text preservation) with no improvement. User said: "兄弟，你今天不在状态呀" and "请你干活认真点，ok？"

### Root Cause
Agent kept retrying the same approach (stronger prompt wording) instead of recognizing a model capability boundary and changing strategy.

### Protocol
1. After 2 failed retries on the same issue, **stop and reassess** — is this a prompt engineering problem or a model capability boundary?
2. If model capability boundary (text preservation, quantity control), **change strategy** — recommend post-processing, split clips, or alternative tools
3. If prompt engineering problem, **change approach** — different camera pattern, different layout description, not just stronger wording
4. **Acknowledge the failure to the user** — don't pretend the third retry will magically work

### Key: 2 retries max on the same approach. After that, the definition of insanity applies.

## §18 Pronunciation Fix — Chinese & English TTS (2026-08-06 挖掘机实测 · 用户反复纠正3轮)

### Phenomenon
User reported 3+ times: "挖掘机的视频音频挖掘机发音不准确" — Seedance's built-in TTS mispronounced both the English "excavator" and the Chinese "挖掘机" (specifically the character 机 was read as third tone jǐ instead of first tone jī).

### Root Cause
Seedance's TTS engine doesn't have reliable pronunciation for either English multi-syllable words or Chinese multi-character words. Without explicit pronunciation guidance in the prompt, the TTS defaults to its (incorrect) internal model.

### ⚠️ HARD RULE: Apply pronunciation guidance to EVERY §5 occurrence
Do NOT add it to just the first `人声旁白` line. Every single line in §5 must have the full pronunciation annotation. The user will notice if even one line is missing.

### Fix Protocol — English
Add IPA notation with stress marking to EVERY `人声旁白` line in §5 (音频描述):
```markdown
人声旁白：「挖掘机 EXCAVATOR！」— 温柔女声，语速偏慢，领读节奏清晰，excavator 读作 /ɪkˈskeɪvətər/ 重音在第二个音节，「EXCAVATOR」处语调上扬。
```

### Fix Protocol — Chinese
Add pinyin with tone marking to EVERY `人声旁白` line in §5:
```markdown
人声旁白：「挖掘机在挖土，excavator」— 温柔女声，「挖掘机在挖土」处语气带力量感。中文「挖掘机」读作 wā jué jī（挖一声、掘二声、机一声），注意「机」是一声 jī 不是三声 jǐ，每个字清晰饱满。
```

### ⚠️ HARD RULE: Do NOT embed pinyin in the narration text itself
❌ Wrong: `人声旁白：「挖掘机(wā jué jī) EXCAVATOR！」` — TTS will read the pinyin aloud as gibberish
✅ Correct: `人声旁白：「挖掘机 EXCAVATOR！」` — clean narration text, pinyin only in the description after the dash

### Key Elements
1. **English**: IPA + stress marking (`/ɪkˈskeɪvətər/ 重音在第二个音节`)
2. **Chinese**: Pinyin + tone per character (`wā jué jī（挖一声、掘二声、机一声）`)
3. **Common error correction**: Explicitly state the wrong pronunciation (`注意「机」是一声 jī 不是三声 jǐ`)
4. **Apply to EVERY occurrence** in §5 — not just the first one

### Common Error-Prone Chinese Words
| Word | Correct | Common Mistake |
|------|---------|----------------|
| 挖掘机 | wā jué jī (1st-2nd-1st) | 机 as 3rd tone jǐ |
| 推土机 | tuī tǔ jī (1st-3rd-1st) | 机 as 3rd tone jǐ |
| 缆车 | lǎn chē (3rd-1st) | 车 as 3rd tone chě |
| 马车 | mǎ chē (3rd-1st) | 车 as 3rd tone chě |
| 热气球 | rè qì qiú (4th-4th-2nd) | 气 as 3rd tone qǐ |

### Prevention
- For any English word that could be ambiguous (multi-syllable, unusual spelling), add IPA + stress marking in §5
- For any Chinese word where a character could be misread (especially 机/车/气), add pinyin + tone marking in §5
- The pronunciation guidance goes in §5 only (音频描述), not in §1-4 (visual descriptions)
- **Double-check every §5 line** before submitting — missing even one line will cause the user to reject the batch

## §19 Vertical Mode Fill-Frame for First Clip (2026-08-06 挖掘机实测 · 用户反复纠正4轮)

### Phenomenon
User requested 4+ times: "视频1的竖版上下不要留白" — the first clip in 9:16 mode had blank space at top and bottom. Each retry with slightly different wording still failed.

### Root Cause
Seedance generates 9:16 video from reference images but doesn't automatically fill the vertical frame. Without explicit "fill the frame" instructions, it leaves empty space above and below the subject.

### ⚠️ HARD RULE: Use exact fill-frame wording
The following wording was tried and STILL failed. The most effective approach is:
1. Change shot type: `中景` → `近景` or `特写`
2. Add: `画面严格固定为9:16竖屏比例。将参考图放大并裁剪，使[主体]充满整个画面，上下左右均不留任何空白区域。`
3. Apply to ALL shots in the affected clip

### Fix Protocol
Change camera description from generic `中景固定镜头` to fill-frame close shot:

```markdown
❌ Before (generic medium shot):
镜头 1（挖掘机 @Image1 + 段 1 旁白「挖掘机 EXCAVATOR！」）：中景固定镜头从画面中央平稳建立。挖掘机在画面中央...

✅ After (fill-frame close shot):
镜头 1（挖掘机 @Image1 + 段 1 旁白「挖掘机 EXCAVATOR！」）：画面严格固定为9:16竖屏比例。将参考图放大并裁剪，使挖掘机主体充满整个画面，上下左右均不留任何空白区域。挖掘机在画面中央...
```

### Key Elements
1. **Change shot type**: `中景` → `近景` or `特写` — closer framing naturally fills more of the frame
2. **Add fill instruction**: `画面严格固定为9:16竖屏比例。将参考图放大并裁剪，使[主体]充满整个画面，上下左右均不留任何空白区域。`
3. **Apply to ALL shots** in the affected clip — not just the first one
4. **Only for Clip 1** (the first clip in the batch) — unless user specifies otherwise

### Prevention
- For any 9:16 video where the subject is a single vehicle/machine (not a landscape), use fill-frame wording for Clip 1
- This is especially important for construction vehicles (excavator, bulldozer) and other large subjects that look small in medium shot
- Don't apply to landscape/aerial subjects (hot air balloon, cable car) where medium shot is appropriate

## §20 Core Word Grouping — One Group Per Image (2026-08-06 热气球实测 · 用户反复纠正2轮)

### Phenomenon
User repeatedly corrected: "画面中只出现一组核心词" — the prompt described core words as two separate groups (`「hot air balloon」字母和「热气球」中文装饰文字`), causing Seedance to render them as two independent text elements on screen.

### Root Cause
Seedance treats each described text element as a separate rendering instruction. When the prompt says `「hot air balloon」字母和「热气球」中文装饰文字`, Seedance renders TWO text groups on screen. The user wanted ONE combined group.

### ⚠️ HARD RULE: Always use slash format for bilingual text
```markdown
❌ Wrong (two groups):
画面上方有彩色「hot air balloon」字母和「热气球」中文装饰文字。

✅ Correct (one group):
画面上方有彩色「hot air balloon/热气球」装饰文字。
```

### Apply to ALL sections
- §1 (段1): Every `@ImageN` description that mentions text
- §4 (收尾): The `保留参考图中的...文字` line
- §5 (音频描述): Any text references

### Prevention
- Always use `「core_word/中文」装饰文字` format — one group, slash-separated
- Never use `「X」字母和「Y」中文装饰文字` — that's two groups
- This applies to ALL bilingual picturebook videos, not just hot air balloon
- Check ALL images in the clip, not just the first one

### Phenomenon
Clip 1 of the "三" batch (小鸡+青蛙) failed with error:
```
OutputVideoSensitiveContentDetected: The request failed because the output video may contain sensitive information.
```

### Root Cause
Seedance 2.0 has a content moderation filter that can trigger on certain visual elements — possibly the "三" character (three horizontal lines resembling tally marks), or the combination of animals (chicks/frogs) in a children's educational context. The exact trigger is opaque.

### Fix Protocol
1. **Re-submit with identical prompt** — the first retry often succeeds (this session: first attempt failed, second attempt with same prompt succeeded)
2. If second attempt also fails, **simplify the prompt** — remove any potentially ambiguous descriptions
3. If still failing, **split the clip** into smaller segments to isolate the problematic content

### Key: This is a transient moderation filter, not a permanent block. Always retry once before changing the prompt.

## §13b Copyright-Restriction Misdetection — multi-image CLIP is the trigger, single-image split is the fix (2026-08-25 飞机 AIRPLANE 实测)

### Phenomenon
A 3-image 11s clip (图6 马赛克拼贴客机 + 图7 舷窗小女孩 + 图8 山丘全景) failed **3×** with:
```
OutputVideoSensitiveContentDetected.PolicyViolation: The request failed because the output video may be related to copyright restrictions.
```
The §13 "retry identical prompt" heuristic did NOT apply: identical retry failed, simplified prompt retry failed — 2 wasted submits.

### Root cause — the combination, not the images
All 3 reference images submitted **individually as single-image 4s clips succeeded on FIRST try**. The trigger was the multi-image combination (3 refs + 11s), NOT any single image's content. You cannot predict which image is "the problem" by looking — there isn't one.

### Protocol (for the PolicyViolation/copyright variant)
1. Identical retry (1 submit) → if same copyright error, **skip prompt-simplification entirely** (it did not help here; §13's step 2 is for the generic "sensitive information" variant).
2. **Split into single-image clips** (one SRT segment each, 4s floor). The split is simultaneously the diagnostic AND the fix — each single-image clip passes first try with narration/audio preserved per segment.
3. Deliver the split clips as the final clips (4s each is acceptable output, not a temporary probe — user accepted 11s → 4s+4s+4s without objection).
4. If a split single-image clip then shows a white strip (horizontal full-scene ref), fix per §29b.

### Key
- Error message distinction: "may be related to copyright restrictions" (PolicyViolation) ≠ generic "sensitive information" — the copyright variant did NOT respond to prompt simplification.
- ⚠️ Do NOT burn 3 submits on a multi-image clip once the first retry hits the same copyright error. Split at strike 2.
- Duration factor: 11s combined also failed while 4s single passed — both image count and length contribute. When in doubt, shorter + fewer refs is safer.
- ⚠️ **Counterexample — do NOT pre-emptively split healthy 3-image clips** (2026-08-25 公交车 batch, same session): clip1 (3-img 10s), clip2 (3-img 11s), clip3 (2-img 7s) ALL succeeded **FIRST TRY**, no copyright errors. So "3-image + ~11s" is NOT a universal trigger — the airplane flip was specific to that clip's image set. Only split AFTER the copyright error actually fires (strike 2); don't degrade a healthy flow by pre-splitting every 3-image clip.
- **Directional-prevention — write facing aligned with movement so L3 never flags 倒飞**: when the subject has a clear facing (vehicle nose), write movement direction MATCHED to it — `车头朝右 → 从画面左侧向右侧驶`, `车头朝左 → 从画面右侧向左侧`. Apply the aligned direction in BOTH §2 (镜头) and §3 (旁白-动作对应). If an L3 review still reports a direction mismatch, check the OUTPUT frame FIRST: seedance auto-corrects facing (airplane rendered nose-left flying left regardless of prompt wording), so don't re-run a visually-correct clip over a review flag.

## §14 Chinese Character "三" Misidentification (2026-08-05 三 THREE 实测)

### Phenomenon
Vision model consistently describes the Chinese character "三" as:
- "Three horizontal blue lines stacked vertically"
- "Three horizontal dark blue bars"
- "Three horizontal strokes"
- "Tally marks"

It never identifies it as the Chinese character "三" (meaning three).

### Root Cause
Vision model's text recognition treats "三" as a geometric shape (three parallel lines) rather than a written character, especially in hand-drawn/crayon-style illustrations where it appears as simple strokes.

### Fix
1. **Cross-reference with context**: If the image is about learning the number three and has English text "THREE"/"three" + a three-stroke symbol, that symbol IS the Chinese character "三"
2. **Write the exact character in the prompt**: Use `三横汉字"三"` not `三横线` or `三横条`
3. **Describe it as a character, not a shape**: `汉字"三"` in every prompt section

### Prevention
- For any bilingual number-learning image with English + a simple multi-stroke symbol, assume it's the Chinese character
- The pattern holds for 一 (1), 二 (2), 三 (3), 四 (4), 五 (5), 六 (6), 七 (7), 八 (8), 九 (9), 十 (10)

## §11 Vertical Mode Blank Space Prevention (2026-08-05 六 SIX 实测)

### Phenomenon
When re-submitting a clip in 9:16 (vertical) mode, Seedance sometimes generates the video with blank/empty space at the top or bottom — the image content doesn't fill the vertical frame.

### Root Cause
Seedance treats the reference image as a starting point and may not stretch/crop it to fill the vertical aspect ratio. Without explicit "fill the frame" instructions, it leaves empty space.

### Fix
Add these phrases to every prompt section when using 9:16:
- §1: `画面充满整个竖屏无空白` after each @ImageN description
- §2: `画面填满不留白` at the end of each camera description
- §3: `画面填满不留白` in key node descriptions
- §4: `画面填满不留白` in the ending description

### Example
```
@Image1 展示封面标题页：蓝色天空和绿色草地背景填满整个竖屏画面...画面充满整个竖屏无空白。
镜头1（@Image1 + 段1旁白）：...画面填满不留白。
```

### Key: Always add fill-frame instructions when switching to 9:16. Don't assume Seedance will auto-fill the frame.

### ⚠️ 横版参考图 → 9:16 letterbox 黑边 · fill-frame 无效 · ffmpeg blur-fill 兜底 (2026-08-19 馒头 STEAMED BUN 实测)
**现象**: 参考图是**横版单主体构图**（单个馒头居中、横版插画），seedance 9:16 输出把横版内容嵌在竖屏中央，上下留大黑边（letterbox）。`cropdetect` 实测内容区 `720:456:0:414`（y=414~870），远小于 720×1280 全屏。
**根因**: seedance 对参考图比例有粘性。**竖向构图参考图（三馒头/蒸笼/三动物围桌）会自动填满竖屏；横版单主体参考图无论怎么强调都不填满**。本会话 §11/§19 的 fill-frame 措辞（"画面填满不留白"+"背景铺满竖屏"）对横版参考图**无效**——这是模型能力边界，重写 prompt 强化措辞不解决（按 2 次上限验证同一思路仍失败，白烧一次 seedance，需回退）。
**判定**: 先 `ffmpeg -vf cropdetect=limit=16:round=2:reset=0 -frames:v 30` 检测内容区，内容区明显小于全屏即 letterbox。
**修复（ffmpeg blur-fill，一次成型，不烧 seedance，保留音轨）**:
```bash
ffmpeg -y -i clip1_v2.mp4 -filter_complex \
"[0:v]crop=720:456:0:414,split=2[c1][c2];[c1]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=lr=20:lp=6[bg];[bg][c2]overlay=(W-w)/2:414[vout]" \
-map "[vout]" -map 0:a -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k clip1_v3.mp4
```
crop 参数换成 cropdetect 测出的实际值（这里 720:456:0:414）。音轨保留、时长不变、内容清晰完整。
**高发区**: **Clip1（封面/单主体横版图）最常见**。判断依据 = 该 clip 的参考图是否横版单主体构图 → **直接预判走 blur-fill，别先重写 prompt 白试**。
**⚠️ 2026-08-19 馒头实测推翻 blur-fill 为最优解**: 用户明确拒绝 ffmpeg blur-fill 输出（\"clip1视频也不是我想要的9：16竖版\"），他要的是 **seedance 原生满屏竖版**。正确修法见 §29 —— 横版参考图**去掉所有 fill-frame/放大裁剪/铺满竖屏措辞，只设 `ratio=9:16`，让 seedance 自己构图**（火锅/汉堡流程实测一次通过，零后处理）。blur-fill 仅当 seedance 重跑仍无法接受时才作最后兜底，且要跟用户说明这是后处理而非原生竖版。

## §12 Batch Production Pattern (2026-08-03 4-batch + 2026-08-04 4-batch + 2026-08-05 2-batch)

This session processed 4 batches back-to-back: Snow → Sea → Scarf → Rain. Each batch followed the same pattern:
1. Receive .7z (8 images + SRT)
2. Step 2: ls → vision all 8 → read SRT → alignment table → confirm
3. Step 3: srt_parser → clip_merger → confirm
4. Step 5: write prompts → verify_prompt.py → confirm
5. Step 6: submit 3 clips → wait_and_download → deliver

**Key efficiency**: After the first batch, subsequent batches went faster because the workflow was already established. The user confirmed quickly with `确认` each time.

## §7 Reference Image Text Preservation Failure (2026-08-05 七 SEVEN 实测)

### Phenomenon
Reference images contain core text (e.g. "SEVEN"/"seven"/"七" as the target word), but Seedance 2.0 consistently fails to render it in the generated video — even after 3 rounds of increasingly explicit prompt instructions.

### Test Results
| Round | Prompt strategy | Result |
|-------|----------------|--------|
| v1 | No text preservation mention | ❌ Text missing |
| v2 | §1: `保留参考图中的SEVEN文字和七汉字作为画面元素` | ❌ Still missing |
| v3 | §1+§2+§3: `必须清晰可见地保留在画面中` + `始终保留在画面中` repeated in every lens | ❌ Still missing |

### Root Cause
Seedance 2.0 has limited ability to preserve text elements from reference images. Even with explicit "must remain visible" instructions, the model prefers generating "clean" (text-free) frames. This is a **model capability boundary**, not a prompt engineering issue.

### Response Protocol (priority order)
1. **Be honest with the user**: Explain that Seedance cannot reliably preserve reference image text. Do NOT keep retrying with stronger prompt wording — it won't help.
2. **Recommend post-processing**: Suggest the user add text overlays in 剪映 (Jianying) or another video editor after generation.
3. **If text is non-negotiable**: Consider alternative video generation tools that handle text better, or split the workflow (generate video without text, overlay text in post).

### Key: Do NOT retry >2-3 times with stronger wording. The model simply doesn't support this capability reliably. Report the limitation and move to post-processing.

## §16 Action Trigger on Core Word Only (2026-08-06 推土机 clip3 实测)

### Phenomenon
User corrected: `视频中只能有核心词，不要出现其它文字` — the action triggers in §2 were firing on full Chinese phrases (e.g., `念到「推土机推泥土」时铲子向前推土力度加大`), but the user wanted them to only fire on the English core word (`bulldozer`).

### Root Cause
The prompt's §2 action triggers used the full Chinese narration phrase as the trigger point, which meant the action was tied to the Chinese text rather than the core English word. The user's intent was that only the core word pair (`bulldozer/推土机`) should drive the action emphasis.

### Fix Protocol
1. Change all §2 action triggers from full Chinese phrases to just the English core word:
   - ❌ `念到「推土机推泥土」时铲子向前推土力度加大`
   - ✅ `念到「bulldozer」时铲子向前推土力度加大`
2. Change §3 (旁白-动作对应) similarly:
   - ❌ `段5 念"推土机推泥土，bulldozer"：铲子推土对应"推土机推泥土"`
   - ✅ `段5 念"推土机推泥土，bulldozer"：铲子推土对应"bulldozer"`
3. Keep the full narration in §5 (音频描述) — that's the TTS text, not an action trigger

### Prevention
- When writing §2 action triggers, always use the **English core word** as the trigger point, not the full Chinese phrase
- The Chinese narration is the TTS audio; the English core word is the action trigger
- This applies to all bilingual picturebook videos where the user wants only core words

## §17 "跑得飞快" Camera Pattern (2026-08-06 高铁 clip2 实测)

### Phenomenon
User rejected two versions of the "高铁跑得飞快" clip:
- v1: Speed lines + body vibration (not enough "飞快" feel)
- v2: Continuous speed lines + fast body swinging (still not enough)
- v3 (accepted): Train sliding from right to left across the frame

### Root Cause
Speed lines and vibration don't convey "fast" to the user. The user wanted the subject to actually **move across the frame** — entering from one side and exiting the other.

### The "跑得飞快" Camera Pattern
When the narration says something is fast (跑得飞快/好快/飞快):

```
镜头 N（@ImageN + 段 N 旁白「...跑得飞快...」）：中景固定镜头。主体在画面右侧，车身从画面右侧向画面左侧方向快速滑动穿过画面（像在向前飞驰），车尾速度线持续向后喷射，车轮快速转动。念到「跑得飞快」时车身滑动速度最快一次强调。念到「core_word」时速度线密集喷射一次强调。
```

### Key Elements
1. **Subject enters from one side** (画面右侧) — not already centered
2. **Slides across the frame** (向画面左侧方向快速滑动穿过画面) — not just vibrating in place
3. **Speed lines trail behind** (车尾速度线持续向后喷射) — reinforces direction
4. **Wheels spin fast** (车轮快速转动) — mechanical detail
5. **Peak speed on the trigger word** — the moment of maximum speed

### Prevention
- For any "fast" narration, use the slide-across-frame pattern, not vibration/speed-lines-only
- The subject must have a clear entry point and exit direction
- Speed lines alone are insufficient — the subject itself must move

## §15 3-Layer Core Word Retention Pattern (2026-08-05 七/六/十/三 4-batch)

### Phenomenon
Across 4 batches in one session, Seedance consistently dropped text elements from reference images. Generic "保留文字" was too vague. Each batch required 2-3 retries before text appeared.

### Root Cause
Seedance treats text as optional decoration unless the prompt explicitly anchors it at 3 levels. A single mention in §1 is insufficient.

### The 3-Layer Pattern

**Layer 1 — Per-image text in §1 (段1):**
For each `@ImageN`, describe text with exact words, colors, and position:
```
@Image1 展示封面标题页：...顶部必须保留彩色大写"SEVEN"（S红色、E蓝色、V绿色、E橙色、N黄色，白色描边）和下方蓝色汉字"七"...
```
❌ Generic: `顶部保留文字"SEVEN"和"七"`

**Layer 2 — Per-shot retention in §2 (段2):**
Every camera shot repeats the instruction:
```
镜头1（@Image1 + 段1旁白）：...参考图顶部的"SEVEN"和汉字"七"必须始终清晰可见保留在画面中，不可移除。
```
❌ Only in §1, assume it carries through

**Layer 3 — Retention in §3 + §4:**
```
段1念"七 SEVEN！"：...顶部"SEVEN"和汉字"七"保留在画面中。
镜头4末尾：...顶部"seven"和汉字"七"保留在画面中。
```

### Core Word Simplification (User Preference)
When user says "核心词只要一组" or similar, simplify to just the word pair:
```
❌ 顶部必须保留彩色小写"three"（t红色、h蓝色、r绿色、e橙色、e黄色）和下方三横蓝色汉字"三"
✅ 顶部必须保留"three"和汉字"三"
```

### Batch Efficiency
Always start at Layer 3 to avoid 2-3 retry cycles per batch. The first attempt should already have per-image + per-shot + per-segment retention.

## §8 Ratio Change After First Generation (2026-08-05 七 SEVEN 实测)

### Phenomenon
User requested 16:9 first, then after seeing the result asked to redo in 9:16 (vertical for Douyin).

### Protocol
1. Accept the change without questioning — ratio changes are normal in batch production
2. Re-submit with the new ratio parameter only (prompt content stays the same unless user also requests other changes)
3. Use `wait_and_download` for the new batch

### Key: Don't ask "why" or "are you sure". Just change the ratio and re-submit. The user is iterating on the output, not making a mistake.

## §9 Targeted Segment-Level Camera Modification (2026-08-05 七 SEVEN 实测)

### Phenomenon
User requested: `第2条视频7条小鱼的画面需要改变镜头` — a specific segment within a multi-segment clip needs a camera change, while other segments in the same clip stay unchanged.

### Protocol
1. Identify which segment (by SRT segment number) and which image it maps to
2. Change ONLY that segment's camera description in §2 and §3
3. Leave all other segments' camera descriptions untouched
4. Re-run verify_prompt.py
5. Re-submit only the affected clip

### Example
Clip 2 had 4 segments (气球/苹果/鱼/小女孩). User wanted only the 鱼 segment changed:
- Before: `镜头3（@Image7 + 段7旁白）：镜头从左侧向右横移，7条彩虹鱼在水中摆尾游动...`
- After: `镜头3（@Image7 + 段7旁白）：镜头从特写一条红色小鱼开始，然后缓缓拉远，7条彩虹鱼在水中摆尾游动...由近及远展示全部7条鱼...`

### Key: Minimal change — only touch the segment the user mentioned. Don't "improve" other segments.

## §21 Seedance duration HARD LIMIT 15s — clip_merger can suggest 16s (2026-08-16 宇宙飞船实测)

### Phenomenon
`clip_merger.py` split 8 SRT segments into two clips, each `suggested_duration=16s`. Submitting both to `mcp__seedance__generate_video` was REJECTED:
```
Input validation error: 16 is greater than the maximum of 15
```

### Root Cause
Seedance `duration` must be an integer in **[4, 15]** (API hard bound). `clip_merger` rounds segment sums up via `ceil` and does NOT clamp to 15 — it happily emits 16s when a segment group's speech+pauses exceed 15s.

### Fix Protocol
1. **Always check `suggested_duration`** from `clip_merger` output before submitting. Any clip ≥16s must be manually re-split.
2. Re-split manually into ≤15s groups: e.g. a 2-clip/16s+16s layout → 3 clips (段1-3 / 段4-6 / 段7-8) with durations 13/13/8.
3. Compute each new group's duration from SRT timestamps (end of last segment − start of first) then `ceil`; keep ≤15.
4. Re-write prompts for the new groups, re-run `verify_prompt.py`, then submit.
5. The auto-merger `--max-clip 15` does NOT force a split if a natural boundary doesn't fall before 15s — you must re-split by hand when it overshoots.

### Prevention
- After every `clip_merger` run, grep the `suggested_duration` values for any `>=16` and re-plan those groups before writing prompts.
- The `picturebook-video` workflow's ≤3-image-per-clip rule usually keeps clips under 15s, but long SRT segments (7-8s each) can still sum past 15 — check every time.

## §28 clip_merger.py — read results via `--out` file; `clip_idx` is 1-indexed (2026-08-19 馒头实测)

### Phenomenon
- `json.loads` on `clip_merger.py`'s **stdout** fails (JSONDecodeError at char 1) — the script prints human-readable summary text before/interleaved with the JSON block, so you can't `find('{')` + `loads` it.
- A display loop that printed `Clip{clip_idx+1}` produced **off-by-one labels** (Clip2–Clip5 for a 4-clip result), so the clip numbering reported to the user was wrong.

### Root cause
- `clip_merger` writes non-JSON progress/summary lines to stdout ahead of the JSON object.
- The JSON's `clip_idx` field is **1-indexed** (first clip = `1`), so adding `+1` overshoots every label by one.

### Fix
1. Always run `clip_merger.py timeline.json --user-tts <TTS> --out clips.json`, then read/parse **the file** (`read_file` / `json.load`) — never parse stdout.
2. When reporting clip numbers to the user, print `clip_idx` directly (first clip = 1). Don't add `+1`.
3. Sanity-check the clip count + each `suggested_duration` from the JSON file before writing prompts (ties into §21's ≥16s check).

## §29 Horizontal ref → 9:16 letterbox bars: do NOT write fill-frame phrasing; feed horizontal + ratio=9:16 (2026-08-19 馒头实测 · 用户点名参照火锅流程)

### Phenomenon
User: "Clip竖版不美观，与其它视频不一致" — Clip1 (three single-horizontal-bun refs) had **top/bottom black bars**; the horizontal strip sat centered in a 720×1280 canvas. Clip2/3/4 (vertical-subject refs) auto-filled.

### Root cause — MY prompt caused it
I wrote the 陷阱 #19/§11 fill-frame opener: `画面严格固定为9:16竖屏比例。将参考图放大并裁剪，使主体充满整个画面，上下左右均不留任何空白区域。` On **horizontal** ref images this tells seedance to preserve the horizontal composition and pad it into a vertical canvas → letterbox. Retrying with MORE fill-frame wording (`背景水彩色块必须向上下延伸铺满整个竖屏`) still produced bars. ffmpeg blur-fill "fixed" the bars but the user rejected it: **"clip1视频也不是我想要的9：16竖版"** — they want the **seedance-native** full-vertical look, not a post-processed pad.

### The 火锅/汉堡 workflow that WORKS (user explicitly said "按照火锅绘本的视频重新做")
- Reference images are ALSO **1920×1200 horizontal**.
- **Do NOT write any "fill the 9:16 frame / 放大裁剪 / 不留空白 / 铺满竖屏" phrasing in the prompt.**
- Just feed the horizontal ref + `ratio=9:16` → seedance **natively outputs 720×1280 full-frame** (subject/background fill the vertical canvas), zero post-processing.
- Verified: 720×1280, background fills top-to-bottom, subject centered, no bars.

### Anti-pattern
❌ Adding "将参考图放大并裁剪…不留空白" or "背景铺满竖屏" for **horizontal** refs → letterbox bars that NO prompt-stronger-wording removes.
✅ Leave the ref alone; only set `ratio=9:16` in generate_video. Let seedance compose the vertical frame natively.

### When fill-frame wording IS still useful
Only for **vertical-native single subjects** seedance renders small/centered with dead space (§19/§11: construction vehicles). NOT a blanket instruction — for horizontal refs it's actively harmful. Judge per ref-image aspect ratio (run `identify`/PIL on refs before writing §1).

### User preference signal
User rejected ffmpeg-blur-fill as the first fix — they want seedance-native full vertical, not a post-processed pad. Re-submit with the correct (火锅-style) prompt first; blur-fill is a last-resort fallback, clearly labeled as post-processing.

## §29b Horizontal FULL-SCENE refs (ground content at image bottom) → bottom WHITE strip, NOT letterbox — bottom-fill wording IS the fix (2026-08-25 飞机 AIRPLANE 图8 实测)

### Distinguish from §29
- §29 case: **横版单主体居中图** (馒头/居中插画) → top/bottom **black bars**; any fill-frame wording is harmful; feed horizontal + ratio=9:16 only.
- §29b case: **横版全景场景图** whose content includes ground/landscape at the image bottom (山丘/房子/湖) → seedance keeps the horizontal composition and pads ONLY the bottom with a **pure-white strip** (measured: bottom 10% of frame = 100% white via PIL), no black bars. Text and subject render fine — only the bottom is blank.

### Detection — PIL, not cropdetect
`ffmpeg cropdetect` (a dark-border detector) returned **NOTHING** for the white strip on a light background. Use PIL white-ratio analysis instead:
```python
from PIL import Image
import numpy as np
a = np.array(Image.open('frames/clip3c.jpg').convert('RGB'))
h = a.shape[0]
print((a[int(h*0.9):,:,:] > 245).all(axis=2).mean())  # ~1.0 → bottom 10% pure white strip
```

### Fix (native re-run, zero post-processing — consistent with §29's user preference)
Re-submit the same single-image clip with **scene-extension wording** in §1 + §2 + tail constraint:
- §1: `绿色山丘从画面中下部一直延伸到画面底部边缘…画面底部完全被绿色山丘填满不留白`
- §2: `下方绿色山丘填满画面底部一直延伸到画面底边`
- tail: `绿色山丘必须填满画面底部，画面底部不留任何空白`
Verified first re-run eliminated the strip (bottom 15% white = 0.0%), text intact, no black bars.

### Key
- Scene-extension wording (extend existing bottom content to the frame edge) WORKS for full-scene refs, while §29's banned 放大裁剪/铺满竖屏 phrasing stays banned for single-subject refs. Judge by ref-image composition: does the image's own bottom edge contain scene content?
- White-strip detection is a PIL job; don't rely on cropdetect for light-background blanks.

## §30 Narration-word pollution bound to the scene element → 陷阱#2 fallback after ONE failed text-lock (2026-08-19 馒头 热腾腾实测)

### Phenomenon
Clip3 图6 (蒸笼馒头, narration "热腾腾的馒头，steamed bun") — seedance rendered **"热腾 med bun"** into the title: narration word 热腾腾 became on-screen text and swallowed the `ste` of "steamed bun". The polluting word is **semantically bound to the image's core action** (蒸汽/热 = the animated element), so the model treats it as the label to display — stronger than §27's incidental pollution.

### Why it beat the §27 defense stack
Escalated through §27's L1→L4 layers AND the 火锅-style "只保留参考图中已有的文字元素" tail constraint — **three full re-submits, all failed identically**. When the narration word is tied to the scene element being animated, no prompt wording separates them. Model capability boundary (same class as §7 text preservation / §19 quantity).

### Correct protocol (user chose this)
1. **After 1 failed text-lock re-submit on the SAME image+word**, stop — don't burn a 4th token spend. Assess as capability boundary.
2. **Fall back to 陷阱#2** (seedance-prompt-pitfalls): re-do the WHOLE clip with §5 audio = **音效 only, NO 人声旁白** (`--no-srt`). Without narration text in the prompt, seedance can't render it into the frame → title stays clean (verified: 图6 steamed bun/馒头 two-line clean after trap#2).
3. Deliver the trap#2 clip + hand the user a TTS narration script (MiniMax 绘本女声, speed 0.95, softer +2, per-segment `<#pause_s#>` aligned to SRT spans) to 合成 in 剪映.

### Trap#2 verify_prompt invocation nuance
- Run `verify_prompt.py ... --generate-audio --no-srt` (sets has_srt=False → R10 only requires `音效：`, skips `人声旁白：`).
- **R7 still requires the `+ 段 N 旁白` binding** in §2 shot headers — keep `镜头 N（主体 @ImageN + 段 N 旁白）：`. Dropping `+ 段 N 旁白` to avoid mentioning narration FAILs R7. Only the §5 audio block omits 人声旁白.
- 段3 (R8) still lists full narration for timing; the `只保留参考图中已有的文字元素` tail constraint covers the render risk.

## §22 R3 "保持...稳定" False Positive (2026-08-16 海龟/白鲸实测)

### Phenomenon
`verify_prompt.py` R3 (anti-freeze) FAILs on the phrase `龟壳保持稳定不晃动` / `身体保持稳定不动` — even though that wording is INTENTIONAL (preventing the "jumping/jittering" the user hates, per jump-prevention rule) and NOT a freeze-inducing ending phrase.

### Root Cause
R3's regex matches `保持.*?稳定` (the old v5.0.9 "freeze-ending" phrase). It is a **simple substring match and cannot tell intent** — a body-part-stability instruction trips it just like a real freeze phrase would.

### Fix Protocol
Rewrite the anti-jump instruction WITHOUT the `保持...稳定` combo:
- ❌ `龟壳保持稳定不晃动`
- ✅ `龟壳稳定不动` (drop the word `保持`)
- ✅ `龟壳稳定不动不晃动`

### Prevention
- When writing §2 body-part-stability lines for the jump-prevention rule, use `稳定不动` / `稳定不动不晃动`, never `保持稳定`.
- Same trap for other `保持X` phrases that are intentional — if R3 fires on a line you WANT, just rephrase to drop `保持`.
- This coexists with the jump-prevention rule: keep the stability intent, just avoid the trigger substring.

### Cross-sentence variant — fill-frame wording trips R3 too (2026-08-19 冰淇淋 ICE CREAM 实测)
A **silent, cross-sentence variant**: the 9:16 fill-frame instruction `画面严格保持9:16竖屏比例…稳定不动不晃动` ALSO triggers R3's `保持.*?稳定`, even though "保持9:16" and "稳定不动" live in *different sentences*. The regex `.` matches the sentence-ending `。`, so the two words bridge across the boundary.

**Symptom that makes it hard to find**: `grep -noE "保持.{0,6}稳定"` returns NOTHING (words too far apart for a short lookahead), yet verify_prompt still FAILs R3. A short-window grep is a false negative. You must either grep with a wide `.` window (`保持.*?稳定` with `-P`), or test each FROZEN_LANGUAGE_PATTERN one at a time, to locate the bridge.

**Root cause**: the fill-frame opener from 陷阱 #19/§11 canonically used `画面严格保持9:16竖屏比例` — "保持" — and the jump-prevention wording (§22) uses "稳定不动". Combined in one §2 shot, `保持.*?稳定` matches across the sentence period.

**Fix**: change the fill-frame opener to **`画面严格固定为9:16竖屏比例`** (drop "保持"). R3-safe, keeps the fill-frame semantics. Apply batch-wide with:
```
sed -i 's/画面严格保持9:16竖屏比例/画面严格固定为9:16竖屏比例/g' prompt_clip*.txt
```
then re-run verify_prompt. (Note: this is the wording §19 already uses, so standardize on `固定为` everywhere.)

**Batch verification gotcha**: when looping verify_prompt across a batch, `grep -E "FAIL|✅"` can return NOTHING on success because the script prints a leading `⚠️  1 warnings:` line before the JSON `ok`. Use `--quiet` and parse the JSON `.ok` field for a reliable per-clip pass/fail summary:
```
verify_prompt.py prompt_clipN.txt --ref-images 2 --tts-seconds <dur> --generate-audio --no-srt --quiet | python3 -c "import sys,json;print('ok' if json.load(sys.stdin)['ok'] else 'FAIL')"
```

### 段 4 收尾默认模板也会踩 R3「保持…稳定」(2026-08-27 胡萝卜实测)
区别于上面 §22 的「跳防/稳定不动」句——火锅流程 **段 4 收尾照抄的模板** 也会触发 R3 的 `保持.*?稳定`。典型：`绿叶保持轻轻摆动，根部稳定微点` / `绿叶保持柔和左右摆动，根部稳定`。修复 = 具体动作别带「保持…稳定」连击，改用「持续…轻轻摆动」：
- ❌ `绿叶保持轻轻摆动，根部稳定微点`
- ✅ `绿叶持续轻轻摆动，根部跟着微微点一下`
- ✅ `绿叶持续柔和左右摆动，根部轻轻点点`
段落可保留「保持微动」这种抽象主语（不触发正则），只是别让同一具体动作句里同时出现「保持…稳定」。

### Reconciling 陷阱 #2 (音效-only §5) with R10 via `--no-srt` (2026-08-19 冰淇淋实测)
When following `seedance-prompt-pitfalls` 陷阱 #2 (绘本领读 §5 writes ONLY 音效; narration handled by MiniMax TTS separately, NOT in the seedance prompt, to prevent narration rendering into the frame), verify_prompt's R10 would FAIL because path A (has_srt default True) requires `人声旁白：`.

**Fix**: pass **`--no-srt`** (sets `has_srt=False`). R10 then only requires `音效：` and skips the `人声旁白：` check — the correct invocation for the 陷阱 #2 workflow:
```
verify_prompt.py prompt_clipN.txt --ref-images 2 --tts-seconds <dur> --generate-audio --no-srt
```
**Note**: R8 still requires 段3 to contain `段 N 念"完整旁白原文"` — so full narration stays in 段3 (R8-compliant, drives the TTS timing) while §5 stays 音效-only (陷阱 #2-compliant, no narration text for seedance to render). The `禁止生成任何额外文字或字符，只保留参考图中已有的文字元素` tail constraint covers the narration-in-段3 render risk.

## §23 Reference Image Text — preserve EXACT case (2026-08-16 白鲸 clip1 实测)

### Phenomenon
User rejected clip1: `Clip 1 中的文字与参考图不一致`. Vision re-check showed reference image 1 had the title in **ALL-CAPS `BELUGA`** (B红/E黄/L绿/U草绿/G青/A红, 中文「白鲸」白+黄), but the prompt §1 wrote it as lowercase `beluga/白鲸`.

### Root Cause
The prompt's §1 text description was written lowercase to satisfy the "core word lowercase-only" preference, but the reference image itself uses UPPERCASE for the cover/first image. Seedance renders the prompt's case, so the output text diverged from the reference. The user wants the on-screen text to MATCH the reference image.

### Fix Protocol
1. When a user says "文字与参考图不一致", **re-vision every image** and ask specifically about case: `英文是全大写还是小写？逐字读出。`
2. Preserve the reference image's exact case in §1's `「X/中文」` description per image:
   - Cover/first image `BELUGA` (uppercase) → write `「BELUGA/白鲸」`
   - Later images `beluga` (lowercase) → write `「beluga/白鲸」`
   - Different images in the same clip can have different case — write each image's true case.
3. Update the §4 retention line to list both cases: `保留参考图中的「BELUGA/白鲸」和「beluga/白鲸」文字作为画面装饰元素。`
4. Re-verify + re-submit only the affected clip.

### Nuance vs. "lowercase-only" preference
The core-word-lowercase rule is about the WORD PAIR normalization when the user wants clean output. But when a reference image is UPPERCASE and the user flags a mismatch, **matching the reference image wins** — it's what the user is comparing against. Check the actual reference image case with vision before writing §1; don't blindly force lowercase on the first/cover image.

### Nuance — SRT 旁白大小写 ≠ 画面标题大小写；异常页不一定是封面 (2026-08-27 黄瓜 CUCUMBER 实测)
Two traps when determining per-image case at Step 2/5:

1. **SRT 旁白的大小写绝不等于画面标题的大小写。** Cucumber 书 SRT 段1 旁白文字是 `黄瓜 CUCUMBER！`（全大写），但参考图 1.jpg 画面标题实际是**小写 `cucumber`**（两个独立 crop 放大都确认 lowercase c-u-c-u-m-b-e-r）。旁白的大小写是"朗读文本"——大小写发音完全相同，纯粹是分镜文案的写法，不代表画面。**判定画面标题 case 的唯一依据 = crop 放大核实的参考图，绝不从 SRT 文本推断**（即使 SRT 段1 恰好写了全大写）。
2. **异常的大小写页可以是书中间的一页，不是只有封面。** 黄瓜书 8 图里唯独 **6.jpg 是 `Cucumber`（首字母大写）**，其余 7 图全是小写——不是封面图。写 prompt 前必须**逐图 crop 核实 case**，不要只核实封面、其余统一小写（会造成 6.jpg 标题跟参考图不符）。核实到"中间某页独树一帜的大小写"是完全正常的，按图保留即可。

**crop 找标题带时的附带坑（§39 crop-region caveat 延伸）**：6.jpg 我先裁了底部带去核实 case，结果 vision 读到的是**黄瓜切片果肉表面压印的 "CUCUMBER"**（主体表面的装饰/自然纹理文字 = 干扰项，不是标题），差点误判 case。crop 前先从全帧 vision 读出**标题文字到底在哪一带**（全帧 reads location 可靠、case 才不可靠），只裁标题真正所在的那一带；别把主体表面的装饰字/压印字当成页面标题。

### 跟 §40c 的关系
主体自带文字（车身/切面/表面的装饰字）是画面里的"别的文字组"，跟页面标题两码事。核实标题 case 时忽略它们；写 prompt 时若参考图确有主体自带文字，按 §40a 保留，不要用"画面只有两行文字"把它们也抹掉。

## §24b R10 literal `人声旁白：` prefix is REQUIRED — even when adding verbatim/pronunciation instructions (2026-08-17 圆规实测)

### Phenomenon
When adding verbatim-read enforcement to §5 (音频描述), writing `人声旁白必须逐字照读原文，禁止改动加词省略："..."` made `verify_prompt.py` FAIL R10:
```
FAIL R10: 路径 A(有 SRT) 但 prompt 缺 '人声旁白：' — ...否则 seedance 会自己猜测旁白内容
```

### Root Cause
R10 uses **literal substring match** on `人声旁白：` (label + full-width colon). Writing `人声旁白必须...` (label run together with the instruction, no colon) does NOT match `人声旁白：`. The enforcement note must come AFTER the literal `人声旁白："原文"` label, not replace it.

### Fix Protocol
Keep the literal `人声旁白："原文"` prefix, then append the enforcement note after the dash:
```
✅ 人声旁白："圆规画大圆，也画小圆，compass" — 必须逐字照读原文，禁止改动加词省略，中文...语速平稳，最后英文"compass"清晰读出。
❌ 人声旁白必须逐字照读原文："圆规画大圆..."（标签和指令连写无冒号，R10 不匹配）
```

### Prevention
- The `人声旁白：` literal prefix (with the full-width colon) is non-negotiable — always write it verbatim, followed by the quoted narration, then the enforcement/pronunciation instruction after the dash.
- Same trap class as §2's R11 literal-keyword matching: these verifier rules are regex/literal substring matches, they cannot parse intent or run-on phrasing. (Contrast §18: pinyin goes in the description after the dash, never in the narration text.)

## §25 Two More Text-Fidelity Failure Modes — wrong Chinese char + text-group duplication (2026-08-17 蜡笔实测)

Two distinct seedance text failures from the 蜡笔(crayon) batch that are NOT covered by the existing text-preservation/case rules (#7/#15/#20/#23):

### 25a. Seedance renders a WRONG Chinese character (错字)
**Phenomenon**: Reference image 2 had 中文「蜡笔」, seedance rendered it as「叉笔」(a real-but-wrong character pair — "叉" substituted for "蜡"). This is **character-level corruption**, not a dropped/missing text (#7) and not a case mismatch (#23).

**Root cause**: seedance's text rendering sometimes substitutes a visually-similar or phonetically-confusable character for the target one, especially in hand-drawn/crayon style where strokes are thick.

**Fix**: pin the character's component structure + forbid errors, in §1 AND the §4 retention line:
```
@Image2：...第二行必须精确书写中文"蜡笔"二字（蜡字左边虫字旁右边昔字，笔字上面竹字头下面毛字），深青/蓝绿色，禁止写错成"叉笔"。
...
保留参考图中的"CRAYON""蜡笔"文字作为画面装饰元素，中文"蜡笔"二字必须精确书写，禁止写错。
```
**Key**: describe the char by its radical/component composition (`虫字旁+昔`, `竹字头+毛`), not just the character name — this gives seedance enough structural info to render it correctly. Re-vision the generated frame to confirm the char is now correct before re-submitting further.

### 25b. Seedance DUPLICATES a single text group into two (文字重复)
**Phenomenon**: Reference image 5 (a crayon box) had ONE text group at top (crayon/蜡笔). seedance rendered **TWO identical groups** — one at top, one floating mid-frame. User flagged "文字与参考图不一致".

**Root cause**: distinct from #20/#7 (where the PROMPT described two groups → two rendered). Here the prompt described ONE group, but seedance spontaneously duplicated it. This is seedance's own instability, not a prompt-writing error.

**Fix**: explicitly constrain to a single top group and forbid repetition, in §1 for every image AND §2 for every shot:
```
@Image3：...仅在画面顶部一组两行文字——第一行"crayon"小写彩色拼贴字母（紫橙绿红），第二行必须精确书写中文"蜡笔"二字，禁止写错、禁止在画面其他位置重复出现文字。
...
镜头 1（@Image3 + ...）：...顶部仅保留一组"crayon"字母和"蜡笔"中文轻微弹跳，画面其他位置不出现文字。
```

### Prevention
After a "文字与参考图不一致" report, re-vision the generated frames and CLASSIFY which failure mode before fixing:
- (a) wrong character (25a) → pin char components
- (b) duplicated group (25b) → constrain "仅顶部一组，禁止重复"
- (c) dropped/missing text → #7/#15/#23
- (d) case mismatch → #23
The fix differs per mode — don't apply the generic "保留文字" stronger wording to all of them.

## §27 Narration-Word Pollution of On-Screen Title Text (2026-08-18 饼干/蛋糕/巧克力 三本实测)

### Phenomenon
Seedance renders **narration words into the on-screen title text**, corrupting or replacing the reference image's original "English + 中文" two-line title. This is the single highest-frequency rework cause in this batch — distinct from dropped text (#7/#15), case mismatch (#23), wrong char (#25a), or duplication (#25b). Here the title is present but **contaminated by a narration word**.

| 绘本 | 参考图标题 | 视频实际渲染 | 污染源 |
|------|-----------|-------------|--------|
| 饼干 图4 | biscuits + 饼干 | **小动动uits** + 小动动饼干 | 旁白"小动物饼干" |
| 蛋糕 图3 | cake + 蛋糕 | **一块三角**（英文丢失） | 旁白"一块三角蛋糕" |
| 蛋糕 图4 | cake + 蛋糕 | **巧克力蛋糕**（英文丢失） | 旁白"巧克力蛋糕" |
| 蛋糕 图6 | cake + 蛋糕 | cake + **蜡烛** | 旁白"蜡烛" |
| 蛋糕 图7 | cake + 蛋糕 | cake + **切蛋糕** | 旁白"切蛋糕" |
| 巧克力 图7 | chocolate + 巧克力 | chocolate + **淋在蛋糕上** / **淋蛋糕** | 旁白"淋在蛋糕上" |

**规律**: 旁白里出现的中文名词/动作词（尤其与画面主体相关时）被模型当作"该显示的文字"渲染进画面，覆盖或增补标题。英文标题相对稳定，**中文标题最易被污染**。

### Defense Wording (strength increases per layer — stack as needed)
- **L1 · per-image lock in §1**: `此图标题文字固定为"chocolate"和"巧克力"，不得改动。`
- **L2 · per-image case lock** (multi-image case differs, e.g. 图1=CHOCOLATE 大写 / 图2-8=chocolate 小写): `@Image1 保留大写CHOCOLATE，@Image2-5 保留小写chocolate，禁止大小写互相变形。`
- **L3 · narration-word ban in tail constraint**: `旁白词（一块/剥开/白/黑等）不得出现在画面文字中，不得添加或改动任何文字。`
- **L4 · two-lines-only** (most effective when pollution is stubborn): `此图画面只有两行文字：上方"chocolate"、下方"巧克力"，不得出现第三行文字，不出现"淋"字或任何其他汉字。`

> L4 wins when the model keeps rendering a narration action word (e.g. "淋") as a third line. Explicitly stating "只有两行文字 + 不出现X字" resolves it.

### Rework Protocol (mandatory)
1. **抽帧逐段检查文字**: per clip, extract a frame per segment (e.g. clip1 seg1-5 → t=1/4/8/12), vision reads exact English case + 中文, compare to reference title.
2. **Build a 参考图文字 vs 视频实际文字 table**, mark polluted segments.
3. **Re-do ONLY the polluted clip** (not the whole book), strengthening that segment's text lock (stack L1-L4).
4. **Re-check the polluted segment** after re-submit before delivering.

### Default Aspect Ratio (2026-08-18 user correction)
- **Default is vertical 9:16** (Douyin/Xiaohongshu), NOT 16:9. User explicitly corrected this.
- 720p / no AI watermark / audio on (旁白+音效) / no BGM.

### Related
- R11 camera whitelist: "环绕" is NOT in the whitelist → FAIL. Use "缓慢推近" instead.
- L3 subagent timeout but output on disk → see §26.

## §26 L3 prompt-reviewer subagent timeout — result already on disk, don't re-dispatch (2026-08-18 蛋糕 Cake 实测)

### Phenomenon
The L3 `prompt-reviewer` subagent (delegated at Step 5.5) timed out at 600s (`status=timeout`, no summary) while doing per-image vision verification of 8 reference images. The delegation result came back as `(no summary — status=timeout)`.

### Root cause
The reviewer does 8+ `vision_analyze` calls (one per reference image) plus reads prompt/SRT/timeline files. On a slow vision model or network, that easily exceeds the 600s subagent cap. The timeout is on the **return channel**, not the work.

### Recovery protocol — timeout ≠ no output
1. **`tail` the live transcript** first: `cache/delegation/live/<delegation_id>/task-0.log`. The subagent usually writes its full structured review to a JSON file in the project dir (`prompt-visual-review.json`) and prints the result to the transcript right before the timeout.
2. **If the JSON is on disk, `read_file` it** and use that as the review verdict. The review is complete and valid — the timeout only killed the return message.
3. **Do NOT re-dispatch** the reviewer. Re-dispatching re-runs all 8 vision calls (wasted tokens + another 10 min) for a result you already have.
4. Proceed normally: fix the violations/warnings the JSON reports, re-run `verify_prompt.py`, re-submit.

### Key
- The reviewer's `prompt-visual-review.json` is the source of truth; the delegation timeout is just a delivery failure.
- Check the transcript/disk BEFORE assuming the review failed. A "timeout" result can still carry a complete, actionable review.

### Refinement — JSON may never be written; verdict lives in the transcript tail, and L3 must never be the critical path (2026-08-25 飞机/公交车/消防车 3连实测)
- **The reviewer often times out at 600s BEFORE writing `prompt-visual-review.json`.** Both 公交车 and 消防车 came back `status=timeout` with NO JSON on disk. The review was still complete — recover it from `tail -40 cache/delegation/live/<id>/task-0.log`: the transcript shows it ran verify_prompt.py (all OK), read clips.json, and cross-checked every reference image (orientation / color / case / text) against the prompt before dying. If those cross-checks matched, treat L3 as ✅ and move on. **Never re-dispatch** (re-runs 8 vision calls + another 10 min for a verdict you already hold).
- **Prevention**: add to the delegation goal `注意控制时间，快速完成，不要卡在最后一个 action` and state the JSON write is OPTIONAL — it should emit its verdict in the transcript/summary early rather than burn the clock on the final file write.
- **Operational rule — dispatch L3 in parallel, never block submission on it.** fast 模型 clips generate in ~1–2 min, so a 3–4-clip batch finishes while L3 is still mid-flight. Fire the L3 delegation at the SAME moment you show the user the Step 5 prompt-confirmation, and **submit seedance the instant the user says 确认** — L3's async result arrives after videos are generated. Apply an L3 flag only if it contradicts the ACTUAL generated output (e.g. §13b direction mismatch is auto-corrected by seedance — check the output frame before re-running a visually-correct clip).

## §24 User-Supplied Audio Track Replacement (2026-08-17 圆规实测 · seedance TTS 发音彻底不可救时的兜底)

### Phenomenon
Even with §18's pronunciation guidance (IPA/pinyin pinned verbatim) AND a "必须逐字照读原文，禁止改动加词省略" line, seedance's built-in TTS STILL mispronounced Chinese near-phrase words like `大圆/小圆`. User rejected: "大圆和小圆的发音还是不对". Two re-submits wasted tokens. At this point the reliable fix is NOT another seedance re-submit — it's the user's own TTS.

### The User-Audio Fallback Workflow
When the user says "我给你一个音频文件，按我音频里的音轨修改" (usually their own TTS for the whole book):

1. **Check the audio duration vs SRT total.** If `audio.duration ≈ SRT total_duration` → the audio is timecode-aligned to the SRT segments (per-segment narration in order). This is the load-bearing assumption.
   - 圆规 example: SRT total 32.2s, user audio 32.235s → aligned.
2. **Identify which clip to replace** (ask user if ambiguous — full-book audio could map to multiple clips). For a single-clip replacement, extract the audio segment spanning that clip's SRT segments:
   ```
   clip2 = seg4(start 11.133) + seg5(end 19.833) → cut 11.133 to 19.833
   ffmpeg -y -i user_audio.mp3 -ss 11.133 -to 19.833 -ar 44100 -ac 1 clip_vo.wav
   ```
   ⚠️ **Use the SRT segment start/end (milliseconds), NOT the clip's video duration** — the clip length includes ceil-rounding tail/breathing that the audio doesn't. Cutting by clip duration misaligns the narration.
3. **Replace the clip's audio track**, voice from 0, pad tail to clip duration:
   ```
   ffmpeg -y -i clipX.mp4 -i clip_vo.wav \
     -filter_complex "[1:a]adelay=0|0,apad=pad_dur=<clip_duration>[a]" \
     -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest \
     clipX_v3.mp4
   ```
4. Verify output duration ≈ clip duration (`ffprobe`), deliver to user, confirm pronunciation fixed.

### Key Decisions
- **Don't keep re-submitting seedance for a word the built-in TTS can't pronounce.** After 2 failed pronunciation re-submits, pivot to the user-audio route — it's what the user is offering and it always wins.
- **Ask before assuming which clip(s) the audio maps to** when it's a full-book track and the user's intent isn't 100% clear (clarify: replace one clip / whole book / partial).
- **Replacing the clip audio drops seedance's sound effects too.** Tell the user the original 音效 is gone; they can re-mix in 剪映 if needed.
- The user-audio route is a clean `ffmpeg` pipeline — reproducible, no token cost, deterministic. Prefer it over repeated seedance retries once TTS mispronunciation is confirmed as a model capability boundary.

### Multi-Clip / Partial-Book Replacement (2026-08-17 课桌实测 · 用户只替换部分 clip)

When the user supplies a **full-book audio track but only wants SOME clips replaced** (e.g. "只替换 clip1 和 clip2（段1-5）"), the workflow extends §24 to multiple clips from one track:

1. **Clarify the exact clip set** — don't assume whole-book. User may want only the clips whose TTS was bad (often the first 1-2 clips).
2. **For each target clip, cut its own segment** from the SAME full-book track using that clip's SRT segment start→end:
   ```
   clip1 = seg1(start 0.066) + seg2 + seg3(end 8.4)  → cut 0.066 to 8.4
   clip2 = seg4(start 9.1) + seg5(end 15.266)        → cut 9.1 to 15.266
   ffmpeg -y -i user_audio.mp3 -ss <clip_start> -to <clip_end> -ar 44100 -ac 1 desk_clipN_vo.wav
   ```
   ⚠️ Each clip's cut uses ITS OWN SRT segment boundaries — the segments are contiguous in the track, so consecutive clips' cuts tile the track with no overlap/gap.
3. **Replace each clip's audio independently** (same `apad=pad_dur=<that clip's duration>` + `-shortest` command as §24), producing `clip1_v3.mp4`, `clip2_v3.mp4`, etc.
4. **Verify each output duration ≈ its clip duration** before delivering.

**Combined text+audio failure** (user says "文字和音频都有问题"): handle BOTH in one pass — re-submit the affected clips with pinned text (§25a/25b/23) AND replace their audio with the user track. The re-submitted clip (new video) is the base for the audio swap, so the order is: re-submit for text → download → replace audio → deliver. Don't do two separate rounds.

## §34 Action-element position misplacement — water cannon rendered spraying from the WHEELS (2026-08-25 消防车 喷水实测)

### Phenomenon
Ref 6.jpg shows water spraying from a **roof-mounted cannon above the cab**. Seedance rendered the water **shooting out of the front wheel area**. User: "视频中的水从轮子里面喷出来，不合理". The action element (where the water comes OUT) got spatially re-bound to a nearby vehicle part.

### Fix protocol
1. **Re-vision the reference image** asking precisely where the action element sits: `银色水炮架设在车体哪个位置？水从哪个具体位置喷出？喷射方向？车轮附近有没有水/喷水装置？` (answer: 车顶驾驶室正上方、炮口朝前、向前下方喷、车轮附近无喷水装置).
2. **Anchor the position in §1 AND §2**: `银色水炮架设在车顶驾驶室正上方、炮口朝前` + `车顶驾驶室正上方的银色水炮炮口持续向前下方喷出`（位置名词反复出现）。
3. **Add a negative ban in the tail constraint**: `水只能从车顶驾驶室正上方的银色水炮炮口向前下方喷出，禁止水从车轮、轮子或车身内部喷出。`
4. ⚠️ **After fixing the position, RE-VERIFY ALL checks** — the position fix alone let a text-pollution bug slip through (v2 fixed position, Chinese title corrupted to 消喷水; v3 fixed text and passed). Redo = full checklist (text/position/orientation/fill/duration), never just the item you changed.

## §35 Narration ACTION-word pollution of Chinese title — radical-decomposition + ban-word combo (2026-08-25 消防车 消喷水实测)

### Phenomenon
§27 variant: the polluting word is an **action/scene verb** (喷水), not a noun. Title 消防车 → **消喷水** (third char replaced by the action word). Highest-risk case: the image IS the action scene (spraying/flying/running) and the narration says the action word — the model maps the verb onto the title.

### Fix — stack BOTH §27 L4 ban-word AND §25a radical decomposition
```
此图画面只有两行文字：上方"fire truck"、下方"消防车"三字，中文"消防车"三字必须精确书写（消字三点水旁加肖、防字耳刀旁加方、车字），禁止写错，不出现"喷"字或任何其他汉字。
```
- L4 禁字 (`不出现"喷"字`) kills the substitution; radical decomposition (`消字三点水旁加肖…`) gives seedance the glyph structure so it renders the RIGHT char, not a similar one.
- Also strip per-letter colors from §1 on a rework (`下方"消防车"三字` without colors) — fewer text details = less for the model to corrupt.

### Key lesson
Action-scene clips (喷水/起飞/奔跑) need the STRONGEST text lock from the first submission — the action verb in narration is a standing invitation to title pollution. Write the L4 + radical lock upfront, don't wait for the rework.

## §36 Delivery discipline — MEDIA paths + full re-verification after redo (2026-08-25 消防车实测)

1. **MEDIA delivery**: every delivery message MUST include `MEDIA:/abs/path.mp4` lines in the SAME reply. Omitting them = user sees no video ("没有看到视频" — happened once when the summary table went out without MEDIA lines). Template: verification table + md5 + MEDIA lines; offer .7z bundle as fallback if media doesn't render.
2. **Redo = full re-verification**: when re-submitting a fixed clip, re-check ALL of: text (case / exact Chinese / two lines / no pollution) + action-element position + orientation + frame fill + duration. v2 verified only the water position and shipped a polluted title; v3 full check passed. Never validate only the item you changed.

## §37 Physically-impossible render (water from wheels) + narration-word pollution on the SAME rework (2026-08-25 消防车 clip3 实测 · 两轮修复)

### Phenomenon
Fire-truck clip (ref 图6 = roof water cannon spraying forward-down) — v1 rendered the water **spraying out of the front wheel hub area** (physically impossible). User: "视频中的水从轮子里面喷出来，不合理。"

### Round 1 fix — pin the exact source + ban wheel water
- §1: `银色水炮架设在车顶驾驶室正上方、炮口朝前`
- §2: `车顶驾驶室正上方的银色水炮炮口持续向前下方喷出…`
- Tail: `水只能从车顶驾驶室正上方的银色水炮炮口向前下方喷出，禁止水从车轮、轮子或车身内部喷出`
- ✅ water source fixed (roof nozzle confirmed by frame vision)
- ⚠️ BUT the tail phrase `禁止水从车轮…喷出` + narration `喷水` got rendered INTO the Chinese title: 消防车 → **消喷水** (§27 pollution again — "喷水" is semantically tied to the scene element being animated, exactly §30's binding rule)

### Round 2 fix — L4 lock on the Chinese title (standard §27 stack)
- §1: `中文必须是"消防车"三字` + tail L4: `此图画面只有两行文字：上方"fire truck"、下方"消防车"三字，中文"消防车"三字必须精确书写（消字三点水旁加肖、防字耳刀旁加方、车字），禁止写错，不出现"喷"字或任何其他汉字。旁白词（喷水等）不得出现在画面文字中`
- ✅ all clean: 消防车 exact, water from roof, two lines only

### R3 trap during round 1
`两个车轮保持静止不带水` FAILs R3 (凝固语 `保持.*?静止`). Rewrite as `两个车轮干净不带水珠` (drops 保持+静止).

### Lesson
When fixing a physically-wrong element, **stack the §27 L4 text lock in the SAME submission** — the fix wording itself (水炮/喷水/车轮) feeds the title-pollution mechanism. Two rounds = two seedance burns. Also: for any "water/liquid from a specific source" scene, explicitly pin the source position AND ban alternative sources; seedance otherwise picks a visually-simple location (wheel hub).

## §35 Long multi-image clip: narration-word title pollution AND per-page case drift → split the clip (2026-08-25 直升机 clip1 实测 · 3 rounds)

### Phenomenon
4-image 15s clip (图1-4, helicopter book). Two independent breaks surfaced on the TAIL pages (图3, 图4):
1. **Narration-word pollution replacing the title entirely**: 段3 图3 top text became `大旅翼 直升机` (旁白"大旋翼" misspelled) — English `helicopter` **disappeared**; 段4 图4 top text became `长尾巴 直升机` — English gone, narration word in the title slot. (Harsher than §34's 消防车→消喷水: here the narration stocked BOTH lines and deleted the English.)
2. **Case drift on tail**: after L4-locking narration pollution away, 图4's English came out `HELICOPTER`/`Helicopter` (uppercase / first-letter cap) though 图2/图3 rendered lowercase correctly — seedance's per-page case control degrades toward the END of a long multi-image clip.

### Fix — SPLIT the clip (§32 logic, but for quality not copyright)
Split the 4-image 15s clip into **clip1a (图1-2) + clip1b (图3-4)**. With only 2 images per task, seedance held EVERY page's case and clean text on the first try: 1a → 段1 HELICOPTER uppercase + 段2 helicopter lowercase both correct; 1b → 段3/段4 both lowercase helicopter, zero pollution. Splitting shortens each task's span and removes the tail-drift window.

### Text-lock wording that worked (L4 max on every page + a global case rule)
Per page §1: `顶部英文标题为小写"helicopter"十个字，下方"直升机"三字` (spell out case + char count). Per 镜头 §2: `此镜头顶部保留小写英文"helicopter"和中文"直升机"，必须全部小写，禁止出现大写字母，禁止把 helicopter 写成 HELICOPTER`. Global §末尾: `只有第一页图1是大写HELICOPTER，其余所有页面英文一律小写helicopter，绝不允许大写` + explicit ban list `大旋翼、大旅翼、长尾巴、一架、... 翼、尾巴、旋翼`.

### Slow-down narration (voiced-rate fix, applied 消防车 clip3? no — 直升机 clip2/clip3)
User: "音频的语速太快了". seedance TTS ignores bare "语速偏慢". Working formula (per §5 + a global line):
- Per line: `朗读节奏明显放慢，语速比正常说话慢很多，每个字每个音节清晰饱满，停顿充分，舒缓亲切，[w]读/[IPA]/重音在首音节且拖长，慢读`
- Global §5 end: `整段旁白要求：全局语速明显放慢，每句之间留出充分呼吸停顿，朗读节奏舒缓不急促，适合三到六岁宝宝跟读`
Vary speed across users — some demand even slower; confirm by hearing, not just by prompt wording.

## §38 Multi-page/long clip → TAIL-segment text drift (case bleed + narration pollution + English word vanishing); split to ≤2-image clips (2026-08-25 直升机 实测 · 3-round learn, biggest rework of the session)

### Phenomenon
15s **4-image** clip (图1-4, 段1-4). Every page should be two lines: 图1 uppercase `HELICOPTER`, 图2-4 lowercase `helicopter`, Chinese `直升机`. Real output across rounds:
- **Round 1**: tail segments badly polluted — 段3 rendered `大旅翼 直升机` (narration 大旋翼 misspelled into title) and 段4 `长尾巴 直升机`; **the English word vanished entirely** in those tail frames.
- **Round 2** (L4 two-lines-only lock added): pollution cleared, BUT 段4 English flipped to full **`HELICOPTER` uppercase** — 图1's casing bled across the clip to the tail.
- **Round 3** (stronger "只有第一页大写，其余一律小写" wording): 段4 improved to **`Helicopter`** 首字母大写 — closer but still not the required all-lowercase.

### Root cause — seedance tail-drift in multi-image tasks
Seedance holds per-image text fidelity well for the FIRST ~2 images of a multi-image task, then **drifts on TAIL images** — both casing (page-1's uppercase title leaks toward the tail) and narration-word pickup (旁白词 merge into the title, sometimes displacing the English word entirely). Same multi-combo fragility as §13b/§32 — the combo, not any single page, is the liability. 3 rounds of stronger wording only got 段4 from `HELICOPTER` → `Helicopter`; prompt strength can't beat it.

### Fix that reliably worked — split to ≤2-image clips
Split the 4-image 15s clip into TWO ≤2-image clips: 段1-2 图1-2 → 6s, 段3-4 图3-4 → 8s. **Both returned clean on the first try**: 图1 uppercase / 图2 lowercase (short clip holds the case differentiation), 图3-4 all lowercase, Chinese 直升机, zero narration pollution. This is the same surgical-split principle as §32/§13b.

### ⚠️ Conditional — do NOT pre-emptively split healthy clips
公交车/消防车 3-image clips (some with mixed-facing subjects) passed FIRST TRY with correct tail text (harness §13b's counterexample). Only split when a **long (≥10s) multi-image clip legitimately FAILS tail text** (case bleed or narration pollution in a later page) — split at strike 2, don't degrade healthy flow by pre-splitting every 3+ image clip. When splitting a clip whose pages carry different case (图1 uppercase vs 图2 lowercase), a 2-image group holds it; a 2-image all-lowercase group (图3-4) is trivial.

### §27-L4 note for mixed-case clips
When the tail page must stay lowercase while page-1 is uppercase, also write the global rule into §1 + §2 tail blocks AND the final lock (`只有第一页大写，其余页一律小写，绝不允许写成 HELICOPTER`). But don't rely on it for a 3+ image clip — rely on the split. Split is the only thing that made it deterministic.

## §42 Scene-bound narration replacing the ENTIRE English title → single-image 4s split (can beat 陷阱#2) (2026-08-27 黄瓜 CUCUMBER 实测)

### Phenomenon — harsher than §27/§34: English lines GONE, replaced by Chinese narration phrases
A **3-image 12s clip** (5.jpg 切片盘 / 6.jpg 咬瓜 / 7.jpg 三根黄瓜; all lowercase `cucumber` except 6.jpg = `Cucumber` 首大写). First submission output:
- 段5: top two lines correct (`cucumber`+黄瓜) **but a THIRD line** `黄瓜片像小绿花` appeared.
- 段6: **English `Cucumber` vanished entirely** → `脆脆的` + 黄瓜 (all-Chinese).
- 段7: **English `cucumber` vanished** → `大黄瓜小黄瓜` + 黄瓜.
- clip4 (single-image 数黄瓜片): mild — `一片` + numeral `3` appeared (ref only had 蓝1红2).

Polluting words (脆脆的 / 大黄瓜小黄瓜 / 黄瓜片像小绿花 / 一片) are all **semantically bound to the scene action** (bite/count/size) — §30's "strongest" class, and here it **displaced the English line entirely**, which §30/§35 didn't register.

### Fix that worked FIRST TRY — single-image 4s split + "必须保留英文" + ban-word L4 (no 陷阱#2 needed)
Split clip3's 3 segments into **three single-image 4s clips** (3a/3b/3c) and re-lock each page. Key wording additions beyond the standard L4 two-lines-only:
- `必须保留英文cucumber` / `必须保留英文Cucumber` — demand the English line EXIST, not just ban the Chinese word.
- Expanded per-page ban: 段6 `禁止旁白词"脆脆的"`; 段7 `禁止"大黄瓜""小黄瓜""大""小"`; clip4 `禁止"一片""两片""三片"和数字"3"`.
- Keep `此图画面只有两行文字…禁止出现第三行文字` (kills the 第三行 variant).

Result: **all three split clips clean on first re-submit**, including 段6 holding `Cucumber` 首大写 and clip4 showing only cucumber/黄瓜/1/2.

### Refinement to §30
§30 called scene-bound words (`热腾腾`) a capability boundary requiring 陷阱#2 (drop `人声旁白` → 音效-only + MiniMax TTS). **This session proves single-image 4s split + "必须保留英文" + ban-word is a cheaper mid-tier fix that CLEARS scene-bound pollution WITHOUT dropping narration.** Escalation sequence when narration re-renders as Chinese title text on a multi-image clip:
1. Restrengthen wording (only helps the "extra third line" variant when top two lines are already correct — §30's 段6 English-vanishing needs step 2).
2. If **English fully disappeared → split to single-image 4s clips** + add `必须保留英文…` + per-page ban-word. RE-VERIFY every page's case post-split (the anomalous 首大写 page only held after the split — split is both pollution fix AND case fix).
3. Only if a single-image split still pollutes → escalate to 陷阱#2.

### Related
- §23 (same session): SRT 旁白大小写 ≠ 画面标题大小写; an anomalous-case page can sit mid-book, not only cover. Case determination = crop-verify per image, never infer from SRT text or the other pages.

## §39 Verification disambiguation — crop+magnify before judging case; PIL white-threshold false-positives (2026-08-25 直升机/消防车 实测)

### Crop+magnify is REQUIRED before trusting a case reading
`vision_analyze` on a full frame reads colorful lowercase `helicopter` as `Helicopter`/`HELICOPTER` **nondeterministically** — same page across two frames gave different case; and the same frame disagreed between a full-frame read and a top-crop read. Before accepting a case mismatch OR re-running seedance over it, decide the case deterministically:
```python
crop = im.crop((0,0,w,int(h*0.25))).resize((w*2,int(h*0.25)*2), Image.LANCZOS)  # top text band, 2x
```
then vision_analyze the CROP with `"首字母是 h 还是 H？全小写还是全大写？逐字母读。"` Crop reads case reliably; full-frame reads don't. (Corollary: a crop showing "no text" can be a region artifact — check the RAW frame, not just the crop, before concluding text is missing.)

**⚠️ Crop-region caveat (2026-08-27 玉米 CORN 实测 §39 case-verify)**: the "top text band" (`0–0.25h`) heuristic is WRONG for many 绘本 pages where the two-line text (corn/玉米) sits **mid-frame or lower** (corn 段7「我啃玉米」text at left-mid/right-lower, 段8 at bottom-center). Cropping `0–0.45h` returned "no text" and forced a second crop. **Locate the text region FIRST from the earlier full-frame vision read** — full-frame vision reliably says WHERE the text is even when it misreads the case — then crop THAT band (e.g. `im.crop((0,int(h*0.5),w,int(h*0.85)))`). Per-image text position differs; verify the crop covers the text before trusting a "no text" reply. Crop-region miss ≠ the字 is gone — don't conclude missing/miscased text from a bad crop band.

### PIL bottom-white is a FALSE POSITIVE on sky/cloud scenes
The §29b PIL heuristic `bottom-10% mean(>245)>5%` flags a bottom blank strip — but for sky/cloud compositions the white pixels are **clouds** (lower-corner cloud shapes), which is NORMAL, not a strip. 直升机 clip1 measured 10-28% bottom"white" and was fine (blue sky + corner clouds). When PIL >5%, CONFIRM with vision: `底部是纯白空白带，还是蓝天+白色云朵？` Only act on a true blank band. Sky scenes: don't burn a seedance re-run on a PIL false positive.

### Slow-speech reinforcement for TTS (消防车/直升机 fix)
When a clip's narration reads too fast, writing `语速偏慢` per §5 line was INSUFFICIENT. The fix that landed: per-line `朗读节奏明显放慢，语速比正常说话慢很多，每个字清晰饱满，停顿充分` AND a global block after the sounds: `整段旁白要求：全局语速明显放慢，每句之间留出充分呼吸停顿，节奏舒缓不急促`. Use both together on the re-submit.

## §40 Reference images with vehicle-body NATIVE text (roof sign) + stubborn letterbox that only the single-image split fixes (2026-08-25 出租车 实测 · 5-clip delivery)

### 40a. 车顶灯牌/车体自带文字是参考图文字，必须保留并允许
Certain books carry text ON the subject (出租车的车顶灯牌 TAXI/taxi; buses may carry body text). This is **reference-image-native text**, part of "只出现参考图中的文字" — do NOT strip it as 旁白污染/额外文字. The reference image has **TWO text groups**: the main two-line title (taxi/出租车 顶部) AND the body sign (车顶灯牌 taxi或TAXI黑字; 图4 even makes the roof sign the SUBJECT with 白色 TAXI+出租车). Correct handling:
- §1 per image: keep both — `顶部 taxi/出租车` AND `车顶保留参考图中的灯牌黑字\"TAXI\"`.
- Tail: state the sign is reference-native and must be kept: `车顶灯牌只保留参考图自带的 taxi 字`.
- Watch case on the SIGN too (图2 roof sign lowercase `taxi`, 图3/5/8 灯牌大写 `TAXI`, 图4 灯牌大写白字) — vision per image and write each sign's true case, don't force one.
- ⚠️ Pre-check with vision BEFORE writing prompts: `车顶/车身有没有自带文字（灯牌/标志）？` — a roof sign you didn't anticipate either gets dropped (user: "参考图的车灯字不见了") or, if you write the generic "画面只有两行文字，禁止其他文字", you actively strip reference-native text.
- 图4 is the "roof sign close-up" page (narration 段4 出租车顶上有灯牌): there the SIGN text IS the page's primary text — describe it as such.

### 40b. Stubborn letterbox — multi-content BRIGHT-bg horizontal refs resists scene-extension AND 纵向填满; ONLY the single-image split works
消防车/直升机 splits (§34/§38) worked via scene-extension/≤2-image splits. This NEW failure: **图7 (taxi+penguin, pale sky) + 图8 (taxi+red-roof house, white sky)** — light-bright multi-content horizontal refs. Seedance output **wide-empty top AND bottom** (99.7% bottom-white, letterboxed composition centered on a thin horizontal band). Escalated through:
- §29b scene-extension (`蓝绿马路铺到画面底部边缘`, `天空延伸到顶部边缘`) → **still 99.7% white** (v2)
- Added `画面必须垂直满屏，内容纵向放大填满整个竖幅，顶部天空延伸顶部边缘、底部马路延伸底部边缘，上下绝不能出现白色边距` → **still 99.7% white** (v3)
Two rounds, both failed identically — seedance will NOT pull these bright multi-content horizontal compositions into a vertical fill (they have no vertical anchor; it defaults to centering the whole strip). This is a model capability boundary, NOT a wording problem (§11 rule: 2 rounds → change strategy).

**Fix that worked — split to SINGLE-image 4s clips (✓ both native full-screen, bottom 0.0%):**
- clip3a = 图7 企鹅 (段7, 4s) → full-screen, blue-green road fills bottom
- clip3b = 图8 红顶房 (段8, 4s) → full-screen, grey road fills bottom
Single-image tasks let seedance compose using that image alone; with one subject it fills the vertical frame natively (same reason §13b/§34 single-image splits succeeded, and consistent with §38's "reduce image load per task").

### Detection / decision rule
- §29b says: full-scene horizontal ref whose bottom has scene content → scene-extension wording works. 
- **NEW carve-out**: if the ref is BRIGHT/multi-content (pale sky + one vehicle + building faces) with no strong bottom anchor, scene-extension wording FAILS repeatedly (2 rounds, 99.7% bottom-white persists). Judge from the reference image: strong ground mass at the bottom (山丘/树连成一片) → extension works; scattered/light refs → plan the single-image split from the start.
- Single-image 4s clips are acceptable final output (user accepted the 5-clip delivery: clip1a/1b/clip2/clip3a/clip3b).
- Clip3 (this 8s 2-image group) was only ever needed for 段7+段8; splitting cost one extra seedance task but ended the rework loop.

### 40c. Roof-sign presence → low-risk, don't over-verify
- Vision will report the sign as "extra text" if you ask broadly. When a vehicle book shows a roof/body sign, EXPECT it and fold it into the prompt; against the post-generation frame, accept the sign as correct when it matches the reference (don't flag taxi-sign TAXI as pollution — it's native).

## §41 Cover-page direction MIRROR + stubborn sky-fill letterbox + title-`i` decoration quirk + friction workflow (2026-08-25 出租车 图1/图2 封面系列 · ~9 burns)

Three distinct, transferable problems hit the taxi COVER page (图1 大写TAXI 朝左) that §40 did not cover, plus a user-friction signal worth embedding.

### 41a. seedance MIRRORS left-facing vehicles to the right — fix with STILL display, not drive
图1 (cover, nose LEFT) kept coming out facing RIGHT across 双图clip→单图→full-wording (6+ burns). Right-facing 图2 came out right in single-image but got flipped LEFT when packed in the same clip as 图1. Root: **seedance has a bias toward rightward motion**, so a LEFT-facing DRIVING subject is the worst case — it mirrors to face-right-and-march-right.
- RELIABLE FIX for a stubborn left-facing subject: **make it a STILL display, not a drive** — `车身停靠展示，不做水平行驶移动，仅车轮/车身极轻微微动`. Removing the "行驶方向" pressure kills the mirror (a cover page is naturally a still intro anyway). This is the only thing that finally held 朝左.
- Avoid packing an opposite-facing (left) page into the same clip as a right one — the pair triggers a wholesale horizontal mirror of the whole clip.
- Direction lock that counted: `车头方向必须与参考图完全一致朝左，不得左右镜像翻转` + per-shot `保持这个朝向…绝不可镜像翻转朝右`. (WPS: "保持"+静止 also trips §22 R3 — write `停靠展示` instead of 静止 to dodge the freeze regex.)

### 41b. Cover-page sky-fill letterbox — the phrase that finally worked is "整幅9:16画布满幅铺满"
图1 was a sky-dominant horizontal cover. It refused to fill 9:16 (centered strip + wide white borders) even with:
- §29b scene-extension (`马路/天空延伸到画面底部边缘`) → still ~100% white top & bottom (v2, v3)
- `画面必须垂直满屏，内容纵向放大填满整个竖幅` → still ~100% (v3)
Two+ rounds, identical failure — same capability boundary class as §40b.

THE working phrase (held it to top=0.0% / bottom=0.0%, text+朝左 clean) was an explicit full-canvas declaration in §1 + 每镜头 + 末尾:
`9:16 竖幅画面。整幅画布由与参考图相同的浅蓝天空纹理从顶部到底部满幅铺满…画面四边没有任何边框、没有任何白色背景、没有任何留白` + a `满屏关键：整幅9:16画布由参考图同款天空满幅铺满，画面四边绝对禁止任何白色背景/边框/边距/留白/空白竖条` tail line.
For sky-dominant horizontal covers, this beat scene-extend wording. (Note the high-quality model `doubao-seedance-2-0` returned 404 — only `-fast-260128` is available; don't plan a slow-model escape hatch, it isn't there.)

### 41c. seedance "i"/"I" dot-decoration quirk — LOW value to fight
Across the book, seedance decorated dot letters: uppercase `I` in `TAXI` gained a Roman-numeral `II` (twice), lowercase `i` in `taxi` gained a yellow coin/badge/smile circle (twice), all despite strong wording `i的圆点必须是普通圆点，不得替换成硬币/徽章/笑脸`. It's a tiny one-letter artifact, near-impossible to purge reliably, and its cost-per-fix (1 seedance burn ≈ the whole clip) far outweighs the visual benefit. **Accept it, or budget exactly ONE extra burn max** — flag it in the delivery note to the user rather than looping.

## §43 MCP generate_video 参数丢失时的 Python 直调 fallback (2026-08-28 洋葱 ONION 实测)

### Phenomenon
MCP `generate_video` tool 的 `prompt` 和 `ref_images` 参数被静默丢弃——工具返回 "must provide at least one of: prompt, ref_images, image, video_refs, audio_refs, draft_task_id"，但调用者确实传了这两个参数。

### Root cause — 长 prompt 静默丢弃（画家 2026-08-29 确认）

**确认：prompt 超 ~1000 字符时 MCP 工具静默丢弃 prompt 和 ref_images 参数。** 画家绘本实测：Clip 1 用完整 prompt（~1000 字符）首次 MCP 调用**成功**（拿到 task_id），但 Clip 2-4 连续 **10+ 次** MCP 调用全部返回上述错误。用 4 字符短 prompt（"test"）测试 → **成功**提交。**无 preceding 400 错误**——第一次长 prompt 调用就吞参数。

**根因 = MCP 工具对 prompt 参数长度有隐式截断/丢弃**。短 prompt 能过、长 prompt 被静默丢弃 = 工具层面的 bug。clip1 成功可能是该次调用的 prompt 碰巧更短或 MCP 内部状态偶然通过。

**两个已知触发场景**：
1. **长 prompt 静默丢弃**（画家 2026-08-29）：prompt ~1000+ 字符 → 直接吞参数，无 preceding 错误
2. **400 后参数缓存异常**（洋葱 2026-08-28）：传 `service_tier=default` → 400，之后所有调用也吞参数

### 判定 + 绕过
- MCP 连续 2 次返回 "must provide at least one of" 且确认传了参数 → **立即停止重试 MCP**
- **绕过方案 A（delegate_task）**：委派子 agent 提交——子 agent 的 MCP 调用可能不受此限制（本次画家实测中子 agent 正在执行）
- **绕过方案 B（Python 直调，最可靠）**：用 terminal 跑 Python 直接调 `seedance_uploads.py`，绕过 MCP 协议层（见下方 Fallback 代码）

### Fallback — 按 MCP 参数丢失时的绕过方案
当 MCP 连续 2 次返回 "must provide at least one of" 且确认传了参数 → **立即停止重试 MCP**，按优先级选择绕过：
1. **delegate_task**（快速尝试）：委派子 agent 提交——子 agent 的 MCP 调用在全新上下文中，可能不受主 agent 的参数丢弃问题影响（本次画家实测正在使用此方案）
2. **terminal Python 直调**（最可靠，不经过 MCP 协议层）：

```python
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.hermes/skills/creative/picturebook-video/seedance_mcp'))
from seedance_uploads import upload_to_uguu, ark_request, build_body, ARK_BASE_URL

# 1. 上传本地图片到 uguu
urls = [upload_to_uguu(img_path, 'image/jpeg') for img_path in img_paths]

# 2. 构造参数 + resolved_urls 映射（key = 原始本地路径）
args = {
    'prompt': open(prompt_file).read(),
    'ref_images': img_paths,
    'duration': 10,
    'ratio': '9:16',
    'generate_audio': True,
    'watermark': 'none',
}
resolved = {img: url for img, url in zip(img_paths, urls)}

# 3. build_body 构造完整 API 请求体
body = build_body(args, resolved_urls=resolved)
if 'watermark' in body:
    del body['watermark']  # 第三方网关不认 watermark 字段

# 4. ark_request(method, url, data) — 第二个参数是 URL 不是 body!
resp = ark_request('POST', ARK_BASE_URL, body)
task_id = resp.get('id', resp.get('task_id', str(resp)))
```

### 关键注意点
1. **`ark_request` 签名是 `ark_request(method, url, data)`** — 第二个参数是 URL 字符串（用 `ARK_BASE_URL`），不是 body dict。传错会报 `URLError: unknown url type: {'model'>`
2. **`build_content` 的 `resolved_urls` key 必须是原始本地路径**（跟 `args['ref_images']` 列表一一对应），value 是 uguu 上传后的 URL
3. **第三方网关不认 `watermark`/`service_tier`/`resolution`/`camera_fixed`** — `build_body` 已自动跳过 watermark（none/platform 不传），但 `service_tier` 如果出现在 args 里也会被忽略
4. **环境变量必须先 export**：先 `source seedance_mcp/.env && export ARK_API_KEY SEEDANCE_BASE_URL SEEDANCE_MODEL`
7. **已有 task 的下载仍用 MCP `wait_and_download`**（只需 task_id，不涉及参数丢失问题）
8. **第三方网关返回的 task_id 在 `resp['id']`**（不是 `resp['task_id']`）
9. **工作目录含中文路径时 terminal 工具会 blocked** — 先 `cp -r` 到 ASCII 路径（如 `/tmp/onion_video/`）再跑 Python
10. **MCP `ratio` 参数也会被静默丢弃**（2026-08-29 运动员实测）：长 prompt 多图时加 `ratio=9:16` 导致 prompt/ref_images 被截断。Python 直调天然支持 ratio，不受此限制。
11. **第三方网关不认的参数不传**（2026-08-29 运动员实测）：`watermark`→400、`service_tier`→400、`resolution`→fast模型不认。Python 直调时 body 里不包含这些字段即可。
12. **第三方网关 image_url 必须带 `role: reference_image`**（2026-08-29 运动员实测）：不带 role→400"role must be specified for image contents"。官方 API 可能不需要，但网关强制要求。Python 直调 content 构造时每张图加 `"role": "reference_image"`。

### 判定时机
- MCP `generate_video` 返回 "must provide at least one of: prompt, ref_images..." 但你确认传了这些参数 → **第 2 次同样报错时立即切换 Python 直调**
- 不要在 MCP 上反复重试（本会话 8 次全部失败）

### 41d. User friction on confirmations/delivery — embed in every 绘本 batch
Across books, the user twice signaled impatience (`怎么这么慢？`, `直接发视频我`). Applied rules:
- Pre-split long/opposite-facing/bright-composition clips (§38/§40b/§41a/b) so per-book rework drops book-over-book.
- **Send final MP4s via `MEDIA:` the moment they're ready** — don't hold them behind narration or a confirm wall. "直接发视频我" = deliver, stop explaining.
- Use `clarify` only for a REAL fork (accept-imperfect vs rework), not per-prompt sign-off once the pattern is established.
- When a stubborn page survives ~4-5 burns (图1: 6+), surface the tradeoff to the user early (clarify: accept-minor-flaw vs keep-reworking) rather than silently burning more tokens.

## §44 Multi-image clip text-position cross-contamination — seedance renders each page's text at EVERY page's position (2026-08-29 运动员 ATHLETE 实测)

### Phenomenon
3-image 14s clip (图6 跳远 / 图7 领奖台 / 图8 蓝衣奔跑). Reference images have the SAME two-line text ("athlete"/"运动员") but at **different positions per image**:
- 图6: 文字在画面**中下方**（沙坑上方）
- 图7: 文字在**领奖台前方**（底部中央）
- 图8: 文字在**画面正上方**白色云朵底块内

Seedance rendered text at **every position in every shot** — e.g., 图8's shot showed text BOTH at the top cloud AND at the bottom (a position from another image). The generic末尾约束 "只保留参考图中已有的文字元素" was too vague for multi-image clips where the same text appears at different positions.

### Root cause
Seedance treats the prompt's text descriptions as a **global template** for all shots in the clip, not per-image. When §1 describes text positions per @ImageN, but the tail constraint just says "保留参考图中的文字" without anchoring WHICH text goes WHERE, seedance renders text at all mentioned positions in all shots.

### Fix protocol
1. **In §1, bind text position to EACH @ImageN individually**: `此图画面文字严格等于参考图：画面中下方只有…两行文字，位置、颜色、字体与参考图完全一致，禁止在画面其他位置生成任何文字。`
2. **In the tail constraint, list EVERY image's text position explicitly**: `@Image1的"athlete"和"运动员"在画面中下方，@Image2的"athlete"和"运动员"在领奖台前方，@Image3的"athlete"和"运动员"在画面正上方云朵底块内。严禁在参考图文字位置之外生成任何额外文字或字符。`
3. **Re-vision the re-do output** per frame to confirm each shot's text is ONLY at its reference position before delivering.

### Prevention
When a multi-image clip has the SAME core-word text at **different visual positions per image** (common in 领读绘本 where the word moves around the page), the generic "只保留参考图中的文字" tail constraint is insufficient. Always **enumerate per-image text positions** in the tail constraint. This is a subset of the broader §15 3-layer pattern — Layer 1 must include per-image position binding.

## §45 Partial clip re-generation after delivery feedback (2026-08-31 清洁工 regen 实测)

### Trigger
成片交付后用户/peer 反馈「某几句核心词读错 + 前后半段语速不一致」→ 只重生成受影响 clip（本例 clip4~8 共 5 个），clip1~3 保留，按原 SRT 时间轴重新合成。

### 工作区复用 Protocol
1. 上次的 `submit.py` / `poll.py` / `build_final.py` / `prompts/` / `tasks.json` 都留在项目目录（如 /tmp/pb_video/）——直接复用，不重写脚本。
2. ⚠️ **先备份 tasks.json**（`cp tasks.json tasks_round1.json`）：poll.py 读取**整个** tasks.json，新任务 append 后会把旧任务一并轮询并**重下载旧 clip**（本例 clip1~3 被自动重下，md5 未变所以无害；但若旧 task 已被网关清理则会误标 failed）。更稳妥：重生成轮单独用一个 tasks 文件。
3. poll.py 的 sleep 默认 25s；指定 20s 间隔+10min 上限时，改 `time.sleep(20)` 再跑（foreground 上限 600s，>10min 必须 background+notify）。

### Prompt 最小改动原则（只改段 5）
音频问题的重生成：**只改段 5（音频描述）**，段 1~4（视觉/动作/收尾）逐字保留——已验证出片的画面部分别动，改了反而引入新风险。段 5 加码堆栈（在 §18 的 IPA+pinyin 基础上）：
- **原文锁死**：`人声旁白："SRT原文逐字" — 温柔女声，这句话必须逐字朗读引号内旁白原文，一个字都不能改、不能漏、不能加`（⚠️ 指令放 `人声旁白："原文"` 之后——标签连写指令会挂 R10，见 §24b）
- **核心词写死**：`必须清晰准确地读出英文单词 X，发音严格为 /IPA/，重音在第 N 音节，X 个音节完整清晰` + **变体禁词清单**（`严禁读成 clean、cleaning、clear、kleen、克里纳等任何变体`——把最可能的误读词全列出来）+ `不能含糊、不能吞音、不能只读半个词`
- **慢速统一**：`朗读明显放慢，语速放慢，节奏舒缓，每个字发音清晰饱满，句尾自然停顿，语速从头到尾保持一致`（用户反馈「前后语速不一致」时，逐 clip 都写与全片统一为慢速）
- 音效限定、大小写锁、`无字幕、无Logo、无水印、无背景音乐` 尾串原样保留
- verify_prompt（--generate-audio）全部 ok=true 后再提交（本例一轮 5/5 成功，无丢参无 401）

### 重要认知
- 核心词读错是**概率性**的：round1 的 prompt 已含 IPA 仍读错 → 重生成 = 同结构 prompt 加码措辞即可，别整段换模板。
- 合成截短 native clip 时必须做**尾词截断检查**（§46 第 4 步）：clip8 native 6.08s 被截到 4.567s，word_timestamps 证实 "cleaner!" 结束于 4.42s，留 0.15s 余量 = 没截掉核心词。

### A2A peer 转述的编号先核实（硬约束 #7 的 peer 版）
Peer 消息写「句5（拖地）=clip4（图4）」与素材实际结构矛盾（round1 报告 clip4=扫地·落叶）。**处理 remote 转述的任务前：先 vision 实锤涉事参考图的动作内容 + 从上一版成片抽帧核对段边界画面**（本例 14.5s=扫地 ✓ 18s=拖地 ✓），确认正确的 段↔clip↔图 映射后再重生成——本例按素材本体对位执行，避免了按错误转述错位重烧 5 个 clip。转述文字 ≠ ground truth。

## §46 faster-whisper ASR 发音自检（有 ASR 就转写核对，合成前把关）

### Why
用户/peer 会问「如能提取音频粗检就核对发音」。核心词读错重新生成一次 ≈ 一个 clip 的成本；合成后再发现 = 白烧一次拼接。ASR 是零 token 的把关器。

### 安装（CN 网络环境，独立 venv 不碰 Hermes venv）
```bash
python3 -m venv /tmp/asr_venv
/tmp/asr_venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple faster-whisper
```
- PyPI 直连必挂 → 必带清华镜像 `-i`；模型下载三件套（HF_ENDPOINT=hf-mirror.com + HF_HUB_DISABLE_XET=1 + 摘全部代理变量）缺一即挂；`small`+int8 CPU 足够。细节/离线跑 → references/asr-venv-ops.md

### 检测 Protocol
1. 提音：`ffmpeg -i clipN.mp4 -vn -ar 16000 -ac 1 clipN.wav`
2. **合成前逐 clip 检**：转写文本 lower 后包含核心词 = PASS；读成别的英文词会被转写成那个词（cleaner→clear 则文本出现 clear）。拿一个已知好片（用户没批评过的 clip）做参照对照。
3. **合成后整片复核**：按 SRT 句时间轴圈区间（如句5/6=12→22s），确认区间内核心词仍可辨。
4. **截断检查**（合成截短 native clip 时必做）：`word_timestamps=True` 拿尾词结束时间 vs 合成保留时长，余量 >0.1s = 未截断。
5. 判 PASS 只看英文核心词与句序——whisper 转写中文常出繁体字形（清潔工/掃地），不影响发音判定。

### Key
- 本例 6/6 PASS（含曾经的两个错读 clip）→ 才跑 build_final.py，零返工交付。
- 报告里直接给逐 clip 转写原文 + PASS/FAIL 表，用户可肉眼复核。
- uv 一步到位替代 venv：`HF_ENDPOINT=https://hf-mirror.com uv run --default-index https://pypi.tuna.tsinghua.edu.cn/simple --with faster-whisper --with "httpx[socks]" python3 ...`（httpx[socks] 兜掉环境代理变量引发的 socksio ImportError；hf-xet 从 PyPI 直拉会超时，必须 --default-index 换清华）。
- bare python3/Hermes venv 均无 faster_whisper（配方 → references/mask-mouth-final-review.md §B3）；**安装/就绪/离线 run 踩坑全配方 → `references/asr-venv-ops.md`**（旧 log 早于最新 clip 落盘 = 过期票必重跑；转写前过 import 就绪门）。

## §47 口罩人物 + 旁白含「张嘴」词义 → 口罩上被画出嘴（牙医 clip3 2026-08-31 · v3 通过）

**根因**：画外音动词词义被 seedance 锚定到画面人物（generate_audio=True 时旁白文本与视觉共用语义空间）——旁白「张大嘴巴」驱动人物口罩上长出嘴/牙/舌，只改画面动作描述压不住（v1/v2 连续两版复发；同 pipeline 无此词义的 clip4 口罩全程干净）。**修复链四步缺一不可**：①动作写死单一动作（右手指桌面牙齿模型），删一切人物面部/嘴部动作 ②张嘴表意物显式化（牙齿模型上排抬起张开、全程不闭合）③段 3 写明「『张大嘴巴』旁白描写的是牙齿模型的动作，人物嘴唇闭合口罩覆盖」④段 5 声明「讲解性画外音，人物不说话不张嘴」断 TTS→口型联动。**验证**：全帧检漏小面积伪影，必须裁切面部区放大拼 ≤0.5s 间隔连续帧逐帧检；高风险帧=旁白动词落点附近；A/B 对照法（拿无该词义 clip 对照）一次定位触发条件。**收尾三陷阱（拼表假阴性 / PASS 与工件版本绑定 / ASR 环境）→ references/mask-mouth-final-review.md**
- **放大拼表前先验裁切框**（v3 复审补教训）：终审拼表第一版裁切框截高了、根本没含口罩 → vision 给误导性「干净」。先单帧确认框内含口罩区域（不含就下移 crop 窗口），再批量切帧拼表。v3 终审 = 8 帧 0.0→3.5s 2×4 拼表逐帧检全干净 = PASS，协议成立。

## §48 收尾竞态：残留后台进程抢写成片 + 成片完整性校验（牙医 2026-08-31 实测）

### 现象
长会话前台超时留下的**孤儿后台任务**（含 A2A 委派的「一条龙」）在重跑收尾时迟到撞车：ffmpeg moov 搬移阶段报 `Unable to re-open …tmp… for shifting data` → trailer 写失败；坏文件唯一硬症状 = `ffprobe duration` 返回 **N/A**（moov 缺失），大小正常+md5 存在均非证据。（牙医案例细节 → references/final-detect-and-delivery.md）

### Protocol
1. **重跑 finish 类脚本（concat/os.replace/上传）前先排雷**：`ps aux | grep -E 'ffmpeg|build_final|uv pip|asr_|bash -li' | grep -v grep`，按 PID 点杀上一轮孤儿（勿 pkill 匹配自身关键词），委派在外同产物「一条龙」确认已死再动手。
2. tmp 输名按轮次唯一，目标先落轮次名再 `mv`；concat 后必 `ffprobe duration`（N/A = moov 坏，删重合）。
3. 交付五件套：md5 + 大小 + ffprobe 时长 + freezedetect 0 冻结 + uguu 直链回读校验（命令模板见 references/final-detect-and-delivery.md）。

### A2A 状态速查 / 恢复执行 / 收尾交付 —— 详细协议见 references/final-detect-and-delivery.md
恢复指令到达先 ls 落盘产物再动手（task_id 全落盘=免补传免重提）。孤儿竞态三板斧、收敛且迟到勿重拼、md5 版本差异≠写坏、回执五项模板、ASR 子集重跑覆盖陷阱——全在该 reference（医生批实测沉淀）。

**§49 regen 撞车 + take 锁定**（多 worker 竞态覆盖 clipN、成片混入坏 take、PASS 票必须绑 take md5）→ 六步协议见 references/regen-take-race.md。

**§50 新批次解压落点纪律**（2026-08-31 工程师批实测：新包 7z 误解压进旧批工作目录 /tmp/pb_video4，包内 8×同名 1-8.jpg + 同名 SRT **静默覆盖**旧批「医生」批原素材；crop2x/prompts/videos/final 因文件名不同幸免）。铁律：① 解压前必须先 `ls <目标目录>` 确认目标为空、或不含与本包同名文件（本流程素材命名固定 = 1-8.jpg + <主题>.srt，撞车概率极高）；② 新批一律新建目录（/tmp/pb_video<N+1> 取未用号）；③ 若已误覆盖：源 7z 仍在 ~/.hermes/cache/documents/（doc_*.7z 按 mtime 对应当批）→ 解到独立目录回拷同名文件即恢复完整，恢复后 md5 抽查；④ 上传包与工作目录文件同名 ≠ 同内容，跨目录 cp 必先核对归属。

**§51 poller 双开竞态止血（2026-08-31 工程师批实测）**：同轮收尾里 poll_all 被启动了两次 → 两个进程同写 poll.log + 同 videos/clipN.mp4（多写者抢写，§45/§48 变体）。止血与恢复协议：① 任何 poll/concat/finish 脚本启动前先 `ps aux | grep -E 'poll_.*\.py|concat|asr_check|ffmpeg'`，发现双进程先全部 kill（拿 PID 点杀）；② kill 后对已落盘 clip 逐个 `ffprobe duration` 验完好（能读出时长=半写未伤，N/A=弃重下）；③ 余下未落盘任务改用**单写者 poller**：只下自己名下文件、先写独立 tmp 再 `os.replace` 原子改名，绝不触碰已验证产物（本批 7 文件验完好 + clip8 单写者补齐 = 零重传零返工）；④ 兜底原则：已验证的 take 文件任何脚本都不得重写，重下载一律 tmp+rename。

**§52 A2A 速查撞上并行终拼：验货不重拼 + 成片本体全检（2026-08-31 工程师批 peer 收尾 · 全文 → references/final-detect-and-delivery.md §52）**
点杀孤儿后目标成片被另一并行会话几分钟内换成含最新 take 的合规构建 → ps 干净 + md5 两轮稳定 = 收敛，**验货不重拼**（重拼=丢已验证 take+重开写撞窗）。五步：ffprobe 时长==Σ native 段长+解码0错0冻结 → 成片分句 ASR（同音别字非污染：建桥→剑桥 jiànqiáo 同音）→ take 入片以成片内容为准不以目录为准 → 拼表三张（段起始帧大小写分流/风险尾帧半身裁切=合规/修复点踏地+接触阴影）→ 全过即上传回读覆盖 /tmp 一气呵成（排雷点杀勿 pkill 自身关键词；SIGTERM 会掏空 staged 副本）。
