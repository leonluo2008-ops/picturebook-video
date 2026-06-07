#!/usr/bin/env python3
"""
v1.0.2 主 agent 填 v15 4 段骨架模板
- 读 clips/clip{1-9}.json 原料
- 按 v15 4 段模板填 11 变量
- 写出 clips/clip{1-9}-prompt.txt 终稿
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/luo/huiben-projects/20260607-pic4-compress")
CLIPS = ROOT / "clips"

# v15 4 段骨架模板（v1.0.2 主 agent 必用）
V15_TEMPLATE = """主体定义：{主角1}@Image{N}（{feature_1}+{feature_2}+{feature_3}+{action}+{expression}），{背景}@Image{N}（{bg_main_color}+{bg_sub_color}+{bg_texture}+{bg_mood}）；分镜绑定：@Image{N} 作为唯一参考帧；{镜头序列}末帧策略：{end_frame_motion}，末帧 {silence_seconds}s 静默消化时间，末帧 1s 内必须包含至少 1 个动作元素（{end_frame_action}），不得成为定格海报；参考图原有的所有文字（顶部 1/6 画面的{en_color_desc}英文 "{EN_WORD}" 和中文"{ZH_WORD}"字）必须完整保留作为画面元素，模型不得删除或替换这些文字，文字位置锁定在顶部 1/6 画面不要重新生成该区域内容，让文字自然融入场景；段 4 · BGM 段：无任何背景音乐、无旁白人声、无哼唱。段 3 · 风格锁定：{style_keywords}。"""


def build_shot_sequence(time_breakdown, narration_text, target_emphasis, narration_seconds=None):
    """从 time_breakdown 拼出 镜头一/二/三...+拟声 序列"""
    shots_text = []
    for i, shot in enumerate(time_breakdown, 1):
        sfx = shot.get('sfx', '').rstrip('一响') + '一响' if shot.get('sfx') else ''
        action = shot.get('action', '')
        # 加入朗读段
        narration_marker = ""
        if shot.get('narration_text') or shot.get('narration_seconds', 0) > 0:
            target_word = target_emphasis.get('word', narration_text.get('en', ''))
            emphasis_win = target_emphasis.get('emphasis_window', '')
            narration_marker = f'+朗读 "{target_word}"（{shot.get("narration_seconds", 0)}s · {emphasis_win}让小朋友跟读）'
        shots_text.append(
            f"镜头{['一','二','三','四','五'][i-1] if i<=5 else f'镜头{i}'}"
            f"（{shot['start']}-{shot['end']}s · {shot.get('label', shot.get('type',''))}）：{action}，{sfx} {narration_marker}；"
        )
    return " ".join(shots_text)


def build_end_frame_motion(end_frame_microaction):
    """从 end_frame_microaction.specific_motion 提末帧微动具体动作"""
    motion = end_frame_microaction.get('specific_motion', '')
    # 提取「末帧 1s 内：xxx」
    return motion


def _parse_en_color(en_color_raw: str) -> str:
    """
    Pic4 翻车修复（2026-06-07）：

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
    # 步骤 1：去结构化标签 "N=" / "o=" 这种，取 = 后的部分
    after_eq = en_color_raw.split('=')[-1]
    # 步骤 2：去副色 " / o=橙红色" 这种，取 / 前的部分
    main = after_eq.split('/')[0]
    # 步骤 3：去中文逗号后的内容（如果有）
    main = main.split('，')[0].split(',')[0].strip()
    # 步骤 4：保证"色"字结尾（让词组"鲜艳红色"变"鲜艳红色色"读起来通顺）
    if not main.endswith('色'):
        main = main + '色'
    return main


def fill_v15(clip_path):
    """填 1 个 clip 的 v15 模板"""
    clip = json.loads(clip_path.read_text(encoding='utf-8'))

    # 11 个变量
    N = clip['image_index']
    char = clip['characters'][0]
    vf = char['visual_features']
    tp = clip['text_position']
    sk = clip['style_keywords']

    # en_color_desc：经过 _parse_en_color 清洗
    en_color_desc = _parse_en_color(tp.get('en_color', ''))

    variables = {
        'N': N,
        '主角1': char['name'],
        'feature_1': vf.get('feature_1', '').replace('（', '').replace('）', ''),
        'feature_2': vf.get('feature_2', ''),
        'feature_3': vf.get('feature_3', ''),
        'action': vf.get('action', ''),
        'expression': vf.get('expression', ''),
        '背景': '拼贴背景',
        'bg_main_color': '暖橙红/暖橙黄（绘本 No 警示暖色）',
        'bg_sub_color': '米黄/米白点缀',
        'bg_texture': '撕纸毛边+拼贴分层+缝线细节',
        'bg_mood': '严肃警示·温柔坚定',
        '镜头序列': build_shot_sequence(
            clip['time_breakdown'],
            clip['narration_text'],
            clip.get('target_word_emphasis', {})
        ),
        'end_frame_motion': build_end_frame_motion(clip['end_frame_microaction']),
        'silence_seconds': clip['end_frame_microaction'].get('duration_seconds', 1.5),
        'end_frame_action': clip['end_frame_microaction'].get('specific_motion', '')[:60] + '...',
        'EN_WORD': clip['narration_text']['en'],
        'ZH_WORD': clip['narration_text']['zh'],
        'en_color_desc': en_color_desc,
        'style_keywords': '，'.join(sk),
    }

    return V15_TEMPLATE.format(**variables)


def main():
    print("=" * 60)
    print("v1.0.2 主 agent 填 v15 4 段骨架模板 · 9 段")
    print("=" * 60)
    for i in range(1, 10):
        clip_json = CLIPS / f"clip{i}.json"
        if not clip_json.exists():
            print(f"❌ clip{i}.json 不存在")
            continue
        prompt_text = fill_v15(clip_json)
        out_path = CLIPS / f"clip{i}-prompt.txt"
        out_path.write_text(prompt_text, encoding='utf-8')
        print(f"✅ clip{i}-prompt.txt 写出 ({len(prompt_text)} 字符)")
    print()
    print("=== clip1 prompt 预览 ===")
    print((CLIPS / "clip1-prompt.txt").read_text(encoding='utf-8')[:500])
    print("...")


if __name__ == "__main__":
    main()
