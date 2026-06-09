#!/usr/bin/env python3
"""
v1.0.3+pic12 主 agent 填 v15 4 段 / v6 5 段骨架模板（修复 pic4 硬编码）

修复 pic4 硬编码（2026-06-07 Pic5 Bird 实战踩坑）：
1. ROOT 路径：从硬编码 /home/luo/huiben-projects/20260607-pic4-compress 改为 --project-dir 参数
2. clip 数量：从硬编码 1-9 改为自动 glob clips/clip*.json
3. bg_mood：从硬编码"严肃警示·温柔坚定" 改为 --tone 参数 + 兜底
4. en_color 字段：从只支持 en_color 字符串 升级为兼容 en_color 字符串 + en_color_pattern 字典

用法：
  python3 fill_v15_template.py --project-dir /path/to/project --version v15 --tone "慈爱温柔"
  python3 fill_v15_template.py --project-dir /path/to/project --version v6 --tone "温情向"

兼容旧调用：python3 fill_v15_template.py（默认走 pic4 路径，向后兼容）
"""
import argparse
import json
import sys
from pathlib import Path

# 默认值（向后兼容 pic4 旧调用）
DEFAULT_ROOT = Path("/home/luo/huiben-projects/20260607-pic4-compress")
DEFAULT_VERSION = "v15"
DEFAULT_TONE = "严肃警示·温柔坚定"  # pic4 No 警示向

# v15 4 段骨架模板
V15_TEMPLATE = """主体定义：{主角1}@Image{N}（{feature_1}+{feature_2}+{feature_3}+{action}+{expression}），{背景}@Image{N}（{bg_main_color}+{bg_sub_color}+{bg_texture}+{bg_mood}）；分镜绑定：@Image{N} 作为唯一参考帧；{镜头序列}末帧策略：{end_frame_motion}，末帧 {silence_seconds}s 静默消化时间，末帧 1s 内必须包含至少 1 个动作元素（{end_frame_action}），不得成为定格海报；参考图原有的所有文字（顶部 1/6 画面的{en_color_desc}英文 "{EN_WORD}" 和中文"{ZH_WORD}"字）必须完整保留作为画面元素，模型不得删除或替换这些文字，文字位置锁定在顶部 1/6 画面不要重新生成该区域内容，让文字自然融入场景；段 4 · BGM 段：无任何背景音乐、无旁白人声、无哼唱。段 3 · 风格锁定：{style_keywords}。"""

# v6 5 段骨架模板（v15 + 文字持续可见段，铁律 #73 + #77）
V6_TEMPLATE = """主体定义：{主角1}@Image{N}（{feature_1}+{feature_2}+{feature_3}+{action}+{expression}），{背景}@Image{N}（{bg_main_color}+{bg_sub_color}+{bg_texture}+{bg_mood}）；分镜绑定：@Image{N} 作为唯一参考帧；{镜头序列}末帧策略：{end_frame_motion}，末帧 {silence_seconds}s 静默消化时间，末帧 1s 内必须包含至少 1 个动作元素（{end_frame_action}），不得成为定格海报；参考图原有的所有文字（顶部 1/6 画面的{en_color_desc}英文 "{EN_WORD}" 和中文"{ZH_WORD}"字）必须完整保留作为画面元素，模型不得删除或替换这些文字，文字位置锁定在顶部 1/6 画面不要重新生成该区域内容，让文字自然融入场景；段 4 · BGM 段：无任何背景音乐、无旁白人声、无哼唱。段 3 · 风格锁定：{style_keywords}。{text_visibility_segment}"""


def build_shot_sequence(time_breakdown, narration_text, target_emphasis):
    """从 time_breakdown 拼出 镜头一/二/三...+拟声 序列（v1.0.6+pic16 修复 · Cat 范式回滚）

    v1.0.6 关键修复（2026-06-09 Pic7 Horse R7 实战沉淀 · Cat 范式回滚）：
    - v1.0.5 我把 target_word 脱敏成"目标词"是**矫枉过正**——Cat 范本里根本没有"+朗读 X"指令
    - Cat 跑通的真实写法：镜头里写"（朗读 1s + 静默 2s 停留，镜头停在画面上让听众消化单词）"
      **不**写"+朗读 'cat'"——seedance 看到"朗读 1s"知道要留朗读时间，但**不强制生成具体朗读**
    - 修复 v1.0.5：target_word 字段在 narration_marker 里**不**直接拼出具体英文
    - C 子 agent action 字段里的"cat 卡片"/"fork 卡片"等具体单词**保留**（C 看图后写的合理推断）
    - 不再硬编码脱敏映射（v1.0.5 的 sanitization_map 撤销）

    Cat 范本参考：assets/example-prompts/cat-clips-1-6-v15.1.txt
    - 镜头里"猫转头看向卡片"（具体动作）+ "（朗读 1s + 静默 2s 停留）"（不写"朗读 cat"）
    - 音效嵌入视觉句：'叮' 一响 + "猫跃入 咚 一声"（v15 段 2 拟声一对一）
    - 段 4 BGM 段：A 档"无任何背景音乐、无旁白人声、无哼唱"（**不**需要 B 档）
    """
    shot_labels = ['一', '二', '三', '四', '五']
    shots_text = []
    for i, shot in enumerate(time_breakdown):
        label = shot_labels[i] if i < 5 else f'{i+1}'
        sfx = shot.get('sfx', '')
        if sfx and not sfx.endswith('一响'):
            sfx = sfx + '一响'
        # v1.0.6：保留 C agent action 字段原样（不脱敏）
        action = shot.get('action', '')
        # v1.0.6：不拼"+朗读 'X'"（Cat 范本里没有），改用 Cat 范本写法"朗读 1s + 静默"
        # 直接用 C 输出的 narration_seconds + emphasis_window 拼成 Cat 风格的"朗读 1s + 静默 2s 停留"
        # 但 Cat 范本写法是嵌入 action 句尾（不在外加 marker）
        emphasis_win = target_emphasis.get('emphasis_window', '')
        narration_marker = ""
        # v1.0.6：narration_marker 改成"朗读 1s + 静默"风格（不写具体目标词）
        if shot.get('narration_seconds', 0) > 0:
            n_sec = shot.get('narration_seconds', 0)
            silence = shot.get('silence_seconds', 2.0)  # 默认 2s
            # Cat 风格："（朗读 1s + 静默 2s 停留，镜头停在画面上让听众消化）"
            narration_marker = f'（朗读 {n_sec}s + 静默 {silence}s 停留）'
        shots_text.append(
            f"镜头{label}（{shot['start']}-{shot['end']}s · {shot.get('label', shot.get('type',''))}）：{action}，{sfx} {narration_marker}；"
        )
    return " ".join(shots_text)


def build_end_frame_motion(end_frame_microaction):
    """从 end_frame_microaction.specific_motion 提末帧微动具体动作（兼容字符串 + 数组）"""
    motion = end_frame_microaction.get('specific_motion', '')
    if isinstance(motion, list):
        return " + ".join(motion[:6])  # 取前 6 个元素
    return motion


def _parse_en_color(en_color_raw: str) -> str:
    """
    Pic4 翻车修复（2026-06-07）· en_color 字符串格式：

    C 子 agent 在 text_position.en_color 字段填的结构化数据形如：
      "N=鲜艳红色 / o=橙红色"
      "N=黄色 / o=橙色"
      "红色"  # 简单情况
    原版直接拼 f"{en_color_raw} 英文" 会出现语法断裂：
      "顶部 1/6 画面的N=鲜艳红色 / o=橙红色 英文"
    修复方向：只取主色名（去结构化标签 + 副色），输出"鲜艳红色色"等流畅词组。

    返回值示例：
      "N=鲜艳红色 / o=橙红色" → "鲜艳红色色"
      "N=黄色 / o=橙色"     → "黄色色"
      "红色"               → "红色色"
    """
    if not en_color_raw:
        return '彩色'
    after_eq = en_color_raw.split('=')[-1]
    main = after_eq.split('/')[0]
    main = main.split('，')[0].split(',')[0].strip()
    if not main.endswith('色'):
        main = main + '色'
    return main


def _parse_en_color_pattern(en_color_pattern: dict) -> str:
    """
    Pic5 Bird 实战新增（2026-06-07）· en_color_pattern 字母级字典格式：

    C 子 agent 在 text_position.en_color_pattern 字段填的字母级配色：
      {"b": "鲜艳红色", "i": "鲜艳蓝色", "r": "鲜艳红色", "d": "鲜艳蓝色"}

    输出："b=鲜艳红色 / i=鲜艳蓝色 / r=鲜艳红色 / d=鲜艳蓝色"

    踩坑教训：原版只支持 en_color 字符串格式，Bird 用了 en_color_pattern 字典，
    字段空 → 兜底"彩色" → 文字颜色失控 = 翻车。fill 脚本升级必加本函数。
    """
    if not en_color_pattern:
        return '彩色'
    parts = []
    for k, v in en_color_pattern.items():
        v = v.rstrip('色')  # 去掉末尾"色"避免重复
        parts.append(f"{k}={v}色")
    return " / ".join(parts)


def _parse_en_color_smart(tp: dict) -> str:
    """
    v1.0.3+pic12 智能路由（Pic5 Bird 实战沉淀）：

    优先读 en_color_pattern 字典（多字母目标词精细配色，如 Bird/Please），
    兜底读 en_color 字符串（单字符目标词，如 No），
    都没有兜底"彩色"。

    fill 脚本必用本函数，不要直接调 _parse_en_color。
    """
    if 'en_color_pattern' in tp:
        return _parse_en_color_pattern(tp['en_color_pattern'])
    elif 'en_color' in tp:
        return _parse_en_color(tp['en_color'])
    return '彩色'


def _build_text_visibility_segment(tp: dict, target_word: str, en_word_fallback: str = '', zh_word_fallback: str = '') -> str:
    """
    v6 段 5 · 文字持续可见段（铁律 #73 + #77）

    必含 3 个微动画 + 时间锚点：
    ① 每字呼吸式明暗交替 0.5s/次
    ② 按朗读节奏字符顺序浮现（0.3/0.6/0.9/1.2/1.5s）
    ③ 整体轻微浮动（0.3s/次·上下 2px 范围）

    踩坑教训（Pic5 Bird 实战）：原 C 子 agent 输出"按朗读节奏字符顺序浮现"但
    没具体时间锚点 = 模板无时间戳 = seedance 不会自动加微动画。修复：本函数
    必带时间锚点（每个字母/字带 0.3s 步进）。

    v1.0.3+pic13 修复（Pic6 Cow 实战）：原兜底 'bird'/'鸟' hardcode 导致非 Bird 绘本
    clip1 全变 "bird/鸟"（铁律 #75 复发）。修复：兜底从调用方传 en_word_fallback /
    zh_word_fallback 进来，调用方从 clip.narration_text 提取；最后兜底才是空字符串
    （让 prompt 字段空缺显形，不静默错位）。
    """
    en_word = tp.get('en_word') or en_word_fallback or ''
    zh_word = tp.get('zh_word') or zh_word_fallback or ''
    en_color_desc = _parse_en_color_smart(tp)
    font_style = tp.get('font_style', '粗体圆润无衬线童趣字体，笔画边缘不规整，撕纸拼贴风格')

    # 字符顺序浮现时间表（v6 段 5 必填）
    char_floats = (
        f"按朗读节奏字符顺序浮现：{en_word[0]}(0.3s) → "
        f"{en_word[1] if len(en_word) > 1 else ''}(0.6s) → "
        f"{en_word[2] if len(en_word) > 2 else ''}(0.9s) → "
        f"{en_word[3] if len(en_word) > 3 else ''}(1.2s) → "
        f"{zh_word}(1.5s)"
    )

    return (
        f"\n\n段 5 · 文字持续可见段（v6 铁律 #73 · #77）：\n"
        f"参考图原有的所有文字（顶部 1/6 画面的{en_color_desc}英文 \"{en_word}\" 和中文\"{zh_word}\"字）"
        f"必须从 t=0 到 t=末帧 全程可见，模型不得删除或替换这些文字，"
        f"文字位置和颜色全程锁定不重新生成该区域内容；\n"
        f"微动画（领读锚点 · 必含）：① 每字呼吸式明暗交替 0.5s/次（\"{en_word}\" 4 字轮流 + \"{zh_word}\" 字）"
        f"② {char_floats} ③ 整体轻微浮动（0.3s/次·上下 2px 范围）；\n"
        f"字体：{font_style}。"
    )


def fill_template(clip_path, version="v15", tone=None):
    """
    填 1 个 clip 的 v15/v6 模板

    Parameters
    ----------
    clip_path : Path
        clip{N}.json 路径
    version : str
        "v15" 4 段 或 "v6" 5 段
    tone : str
        调性（v6 段 1 主体定义的 expression 兜底）
        如 "慈爱温柔" / "严肃警示" / "温情向"
    """
    clip = json.loads(clip_path.read_text(encoding='utf-8'))

    # 11/12 个变量
    N = clip['image_index']
    char = clip['characters'][0]

    # 兼容 C 子 agent 输出：feature_1/2/3 字典 OR color_details+texture 平铺
    vf = char.get('visual_features', {})
    if not vf:
        # 平铺格式回退（BIRD C agent 用了平铺，pic4 C agent 用了字典）
        vf = {
            'feature_1': char.get('color_details', char.get('appearance', '')),
            'feature_2': char.get('texture', ''),
            'feature_3': char.get('appearance', ''),
            'action': char.get('action', '正面对观众'),
            'expression': char.get('expression', ''),
        }

    tp = clip['text_position']
    sk = clip.get('style_keywords', [])

    # 智能路由 en_color 字段（Pic5 Bird 修复）
    en_color_desc = _parse_en_color_smart(tp)

    # 镜头序列
    shot_sequence = build_shot_sequence(
        clip['time_breakdown'],
        clip['narration_text'],
        clip.get('target_word_emphasis', {})
    )

    # 末帧微动（兼容字符串 + 数组）
    efm = clip.get('end_frame_microaction', {})
    end_frame_motion = build_end_frame_motion(efm)
    motion_str = end_frame_motion
    end_frame_action = motion_str.split('+')[0].strip() if '+' in motion_str else (motion_str[:60] + '...' if len(motion_str) > 60 else motion_str)

    # 静默消化时长
    silence_seconds = efm.get('duration_seconds', 1.5)

    # bg_mood：--tone 参数优先
    bg_mood = tone or DEFAULT_TONE

    # EN_WORD/ZH_WORD：tp.en_word / tp.zh_word / tp.en / tp.zh 优先，回退 narration_text
    # v1.0.4+pic14 修复（Pic6 Cow clip4 实战翻车）：C 子 agent 输出字段名是 text_position.en / .zh（不是 en_word/zh_word）
    # 字段名对不上 → 取 None → narration_text 兜底取了朗读目标词（grass）而非显示文字（COW/奶牛）→ 参考图文字错位
    en_word = tp.get('en_word') or tp.get('en') or clip['narration_text'].get('en', '').split()[-1].rstrip('!.,?')
    # v1.0.3+pic13 修复（Pic6 Cow 实战）：zh_word 兜底从 narration.zh 提取，非硬编码 '鸟'
    zh_word = tp.get('zh_word') or tp.get('zh') or clip['narration_text'].get('zh', '').split()[-1].rstrip('!.,?，！？。')

    variables = {
        'N': N,
        '主角1': char.get('name', '主角'),
        'feature_1': vf.get('feature_1', '').replace('（', '').replace('）', ''),
        'feature_2': vf.get('feature_2', ''),
        'feature_3': vf.get('feature_3', ''),
        'action': vf.get('action', ''),
        'expression': vf.get('expression', ''),
        '背景': '拼贴背景',
        'bg_main_color': '米黄做旧纸张（暖黄/赭黄裂纹）',  # 通用绘本默认
        'bg_sub_color': '红蓝撞色点缀（绿叶/撕纸黄块）',
        'bg_texture': '裂纹做旧 + 撕纸毛边 + 纸张纤维',
        'bg_mood': bg_mood,
        '镜头序列': shot_sequence,
        'end_frame_motion': end_frame_motion,
        'silence_seconds': silence_seconds,
        'end_frame_action': end_frame_action,
        'EN_WORD': en_word,
        'ZH_WORD': zh_word,
        'en_color_desc': en_color_desc,
        'style_keywords': '，'.join(sk) if sk else '2D paper collage, 童趣调性',
    }

    if version == "v6":
        # v6 段 5：文字持续可见段
        variables['text_visibility_segment'] = _build_text_visibility_segment(
            tp, clip.get('target_word_emphasis', {}).get('word', en_word),
            en_word_fallback=en_word, zh_word_fallback=zh_word
        )
        template = V6_TEMPLATE
    else:
        template = V15_TEMPLATE

    return template.format(**variables)


def main():
    parser = argparse.ArgumentParser(
        description="v1.0.3+pic12 主 agent 填 v15/v6 模板（修复 pic4 硬编码）"
    )
    parser.add_argument(
        '--project-dir',
        type=Path,
        default=DEFAULT_ROOT,
        help=f'项目根目录（默认 {DEFAULT_ROOT} · pic4 向后兼容）'
    )
    parser.add_argument(
        '--version',
        choices=['v15', 'v6'],
        default=DEFAULT_VERSION,
        help='模板版本：v15 4 段 / v6 5 段（领读型用 v6）'
    )
    parser.add_argument(
        '--tone',
        type=str,
        default=None,
        help=f'调性（v6 段 1 主体定义的 bg_mood 兜底，默认 {DEFAULT_TONE}）'
    )
    args = parser.parse_args()

    clips_dir = args.project_dir / "clips"
    if not clips_dir.exists():
        print(f"❌ 目录不存在：{clips_dir}")
        sys.exit(1)

    clip_files = sorted(clips_dir.glob("clip*.json"))
    # 排除聚合索引
    clip_files = [c for c in clip_files if 'index' not in c.name]

    print("=" * 60)
    print(f"v1.0.3+pic12 fill 脚本")
    print(f"version: {args.version} | tone: {args.tone or DEFAULT_TONE}")
    print(f"project: {args.project_dir}")
    print(f"找到 {len(clip_files)} 个原料 JSON")
    print("=" * 60)

    total_chars = 0
    for clip_path in clip_files:
        prompt_text = fill_template(clip_path, version=args.version, tone=args.tone)
        out_path = clips_dir / f"{clip_path.stem}-prompt.txt"
        out_path.write_text(prompt_text, encoding='utf-8')
        print(f"✅ {clip_path.name} → {out_path.name} ({len(prompt_text)} chars)")
        total_chars += len(prompt_text)

    print()
    print(f"总字符: {total_chars} | 平均: {total_chars // max(len(clip_files), 1)} chars/clip")
    print(f"\n下一步：ls -lh {clips_dir}/clip*-prompt.txt 验证 + 调 seedance 跑视频")


if __name__ == "__main__":
    main()
