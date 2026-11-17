# 副本（11-17 T0-A 第3轮）：原件 T/codex_train.py，只加了碰到 moderation_blocked 立即停、不重试。
# sons02 版：用 Codex（ChatGPT 订阅）按 job.json 出图，逐张出、从 ~/.codex/generated_images 拷回，已存在的跳过，断网重试 3 次。
# 用法：python3 codex_train.py job.json
# job.json 字段：dir（输出和参考图所在目录）、prefix、refs（逗号分隔，相对 dir）、size、refnote、id、style、shots[{n,prompt,caption}]
import json, os, sys, time, glob, shutil, subprocess, csv, re
CODEX = os.path.expanduser('~/.local/bin/codex')
GEN = os.path.expanduser('~/.codex/generated_images')
j = json.load(open(sys.argv[1], encoding='utf-8'))
d = j['dir']; os.chdir(d)
env = dict(os.environ); env.pop('OPENAI_API_KEY', None)          # 走订阅，不走 API
log = open(os.path.join(d, 'log.txt'), 'a', encoding='utf-8')
mapf = os.path.join(d, 'map.csv')
if not os.path.exists(mapf):
    open(mapf, 'w', encoding='utf-8').write('文件名,镜头表行号,镜头句\n')
def newest_after(t):
    fs = [f for f in glob.glob(GEN + '/**/*.png', recursive=True) if os.path.getmtime(f) > t]
    return max(fs, key=os.path.getmtime) if fs else None
for s in j['shots']:
    name = j['prefix'] + '_' + s['n']; out = os.path.join(d, name + '.png')
    if os.path.exists(out): continue
    p = (f"Use $imagegen to generate ONE image, {j['size']}. Pass all attached images to the image tool as reference images. {j['refnote']}\n\n"
         f"Character: {j['id']}\n\nShot: {s['prompt']}\n\n{j['style']}\n\nWhen done, print the saved file path. Do not modify any other file.")
    t0 = time.time(); got = None
    for tr in range(1, 4):
        tt = time.time()
        cmd = [CODEX, 'exec', '-i', j['refs'], '--skip-git-repo-check', '--sandbox', 'workspace-write']
        r = subprocess.run(cmd, input=p, text=True, env=env, capture_output=True, timeout=900)
        # 并行跑多个任务时只认本次会话目录里的图，避免拿到别的任务的图
        m = re.search(r'session id:\s*([0-9a-f-]{20,})', (r.stdout or '') + (r.stderr or ''))
        got = None
        if m:
            fs = [f for f in glob.glob(os.path.join(GEN, m.group(1), '*.png')) if os.path.getmtime(f) > tt]
            got = max(fs, key=os.path.getmtime) if fs else None
        if 'moderation_blocked' in ((r.stdout or '') + (r.stderr or '')):
            log.write(f'{name} MODERATION_BLOCKED\n'); log.flush(); print('MODERATION_BLOCKED', name, flush=True); sys.exit(3)
        if 'usage limit' in ((r.stdout or '') + (r.stderr or '')):
            log.write(f'{name} USAGE LIMIT\n'); log.flush(); print('USAGE LIMIT', flush=True); sys.exit(2)
        if got: break
        log.write(f'{name} retry {tr} (network)\n'); log.flush(); time.sleep(60)
    sec = int(time.time() - t0)
    if got:
        shutil.copy(got, out)
        with open(mapf, 'a', encoding='utf-8', newline='') as f: csv.writer(f).writerow([name + '.png', s['n'], s['caption']])
        log.write(f'{name} ok {sec} s\n')
    else:
        log.write(f'{name} FAILED {sec} s\n')
    log.flush(); print(name, 'ok' if got else 'FAILED', sec, flush=True)
log.write('ALL DONE\n'); print('ALL DONE')
