#!/usr/bin/env python3
"""
v1.0.2 v3/v4/v5 主 agent 填 v15 4 段骨架模板（多版本）
- v3: 表情软化（5-8s 总时长 · 微动 3-4 元素）
- v4: 末帧静默强化（5-8s 总时长 · 末帧 2-4s 静默 · 镜头数减 1）
- v5: 用户两步推导（5/6/7/8s 总时长 · 末帧静默 2.9-3.8s · 微动 4-6 元素）

用法：
    python3 fill_v15_template.py clip1-v3.json
    python3 fill_v15_template.py clip1-v5.json
"""
import json
import sys
from pathlib import Path

CLIPS = Path("~/.hermes/profiles/huiben/work/20260607-pic4-compress/clips").expanduser()  # v1.0.5+pic18

V15_TEMPLATE = """主体定义：{主角1}@Image{N}（{feature_1}+{feature_2}+{feature_3}+{action}+{expression}），{背景}@Image{N}（{bg_main_color}+{bg_sub_color}+{bg_texture}+{bg_mood}）；分镜绑定：@Image{N} 作为唯一参考帧；{镜头序列}末帧策略：{end_frame_motion}，末帧 {silence_seconds}s 静默消化时间，末帧 1s 内必须包含至少 1 个动作元素（{end_frame_action}），不得成为定格海报；参考图原有的所有文字（顶部 1/6 画面的{en_color_desc}英文 "{EN_WORD}" 和中文"{ZH_WORD}"字）必须完整保留作为画面元素，模型不得删除或替换这些文字，文字位置锁定在顶部 1/6 画面不要重新生成该区域内容，让文字自然融入场景；段 4 · BGM 段：无任何背景音乐、无旁白人声、无哼唱。段 3 · 风格锁定：{style_keywords}。"""


def build_shot_sequence(time_breakdown, narration_text, target_emphasis):
    shots_text = []
    for i, shot in enumerate(time_breakdown, 1):
        sfx = shot.get('sfx', '').rstrip('一响') + '一响' if shot.get('sfx') else ''
        action = shot.get('action', '')
        narration_marker = ""
        if shot.get('narration_text') or shot.get('narration_seconds', 0) > 0:
            target_word = target_emphasis.get('word', narration_text.get('en', ''))
            emphasis_win = target_emphasis.get('emphasis_window', '')
            narration_marker = f'+朗读 "{target_word}"（{shot.get("narration_seconds", 0)}s · {emphasis_win}让小朋友跟读）'
        shot_label = ['一','二','三','四','五'][i-1] if i<=5 else f'镜头{i}'
        shots_text.append(
            f"镜头{shot_label}（{shot['start']}-{shot['end']}s · {shot.get('label', shot.get('type',''))}）：{action}，{sfx} {narration_marker}；"
        )
    return " ".join(shots_text)


def fill_v15(clip_path):
    clip = json.loads(clip_path.read_text(encoding='utf-8'))
    N = clip['image_index']
    char = clip['characters'][0]
    vf = char['visual_features']
    tp = clip['text_position']
    sk = clip['style_keywords']

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
        'bg_mood': '温柔坚定·童趣友善',
        '镜头序列': build_shot_sequence(
            clip['time_breakdown'],
            clip['narration_text'],
            clip.get('target_word_emphasis', {}),
        ),
        'end_frame_motion': clip['end_frame_microaction'].get('specific_motion', ''),
        'silence_seconds': clip['end_frame_microaction'].get('duration_seconds', 2.9),
        'end_frame_action': clip['end_frame_microaction'].get('specific_motion', '')[:60] + '...',
        'EN_WORD': clip['narration_text']['en'],
        'ZH_WORD': clip['narration_text']['zh'],
        'en_color_desc': f"{tp.get('en_color', '彩色')} " if tp.get('en_color') else '',
        'style_keywords': '，'.join(sk),
    }
    return V15_TEMPLATE.format(**variables)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 fill_v15_template.py <clip-N-vM.json>")
        print("例: python3 fill_v15_template.py clip1-v5.json")
        sys.exit(1)
    clip_json = CLIPS / sys.argv[1]
    if not clip_json.exists():
        print(f"❌ {clip_json} 不存在")
        sys.exit(1)
    prompt_text = fill_v15(clip_json)
    out_name = clip_json.stem + "-prompt.txt"
    out_path = CLIPS / out_name
    out_path.write_text(prompt_text, encoding='utf-8')
    print(f"✅ {out_path} 写出 ({len(prompt_text)} 字符)")
