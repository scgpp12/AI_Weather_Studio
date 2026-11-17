# 把人物视频资源库里每张图的提示词全文收成一份库，附上用户在幕布的打分和意见。
# 出视频时按编号查提示词。用法：python 人物视频资源库/prompts/收集提示词.py（在 ClaudeUsers 下跑）
import json, glob, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]          # 人物视频资源库
BASE = ROOT.parent                                          # ClaudeUsers
SCORES = BASE / '幕布平台' / '用户确认' / 'AI_Weather_Studio_打分和选择.jsonl'
OUT = ROOT / 'prompts' / '提示词库.jsonl'

score = {}
if SCORES.exists():
    for line in SCORES.read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line)
            score[r.get('编号')] = r

rows = []
# Qwen 一类：每轮的 _记录.json（list，每项有 tag、seed、prompt、refs）
for f in glob.glob(str(ROOT / '**' / '_记录.json'), recursive=True):
    if '旧_' in f:
        continue
    for r in json.load(open(f, encoding='utf-8')):
        if not isinstance(r, dict) or not r.get('prompt'):
            continue
        rows.append({'编号': r.get('tag'), '模型': r.get('model', 'Qwen Image 2.1'), '种子': r.get('seed'),
                     '尺寸': f"{r.get('w')}x{r.get('h')}", '参考图': r.get('refs'),
                     '提示词': r['prompt'], '出处': os.path.relpath(f, BASE)})
# GPT 一类：job_*.json，提示词按 codex_train 的拼法还原
for f in glob.glob(str(ROOT / '**' / 'job_*.json'), recursive=True):
    j = json.load(open(f, encoding='utf-8'))
    for s in j.get('shots', []):
        full = (f"Use $imagegen to generate ONE image, {j['size']}. Pass all attached images to the image tool as reference images. {j['refnote']}\n\n"
                f"Character: {j['id']}\n\nShot: {s['prompt']}\n\n{j['style']}")
        rows.append({'编号': f"{j['prefix']}_{s['n']}", '模型': 'GPT（Codex 订阅）', '种子': None, '尺寸': j['size'],
                     '参考图': j['refs'], '镜头说明': s.get('caption'), '提示词': full, '出处': os.path.relpath(f, BASE)})
# H3 Image 设定表：*_prompt.txt
for f in glob.glob(str(ROOT / '**' / '*_prompt.txt'), recursive=True):
    tag = os.path.basename(f)[:-len('_prompt.txt')]
    rows.append({'编号': tag, '模型': 'H3 Image 设定表', '提示词': open(f, encoding='utf-8').read(), '出处': os.path.relpath(f, BASE)})

seen = set(); out = []
for r in rows:
    if r['编号'] in seen:
        continue
    seen.add(r['编号'])
    s = score.get(r['编号'])
    if s:
        r['用户分数'], r['用户意见'], r['用户选了'] = s.get('分数'), s.get('意见'), s.get('选了')
    out.append(r)
OUT.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in out) + '\n', encoding='utf-8')
print(len(out), 'prompts ->', OUT)
