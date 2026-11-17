# -*- coding: utf-8 -*-
# 第 4 轮 gen_r4.py → 第 5 轮 gen_r5.py：只换档位（E/F/G 俏皮微笑）、种子只用 331、输出前缀 r5_/g5、GPT 目录 gpt5、去掉英文对照。每处 assert。
p = "gen_r5.py"; s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:40]; s = s.replace(a, b)
i0 = s.index("TIERS = ["); i1 = s.index("]\n", i0) + 2
s = s[:i0] + ('TIERS = [\n'
 ' ("E", "俏皮吐舌尖", "嘴角上扬，舌尖从上下唇中间微微露出一点，一只眼眯起，头稍稍歪向一侧。"),\n'
 ' ("F", "wink 微笑", "右眼眨成一条弯弯的线，左眼睁着带笑，嘴角上扬，露出一点上排牙齿。"),\n'
 ' ("G", "歪头抿嘴笑", "头往一侧歪约 15 度，嘴唇合着、嘴角往上提，下眼睑微微上推，眼睛看着镜头。"),\n'
 ']\n') + s[i1:]
rep('D = "/mnt/storage/model-lab/castsery/qiqi_anchor/gpt4"', 'D = "/mnt/storage/model-lab/castsery/qiqi_anchor/gpt5"')
rep('prefix="g4"', 'prefix="g5"')
rep('open("job_g4.json", "w"', 'open("job_g5.json", "w"')
rep('    for sd in (317, 331):\n        JOBS.append(("r4_%s_s%d" % (k, sd)', '    for sd in (331,):\n        JOBS.append(("r5_%s_s%d" % (k, sd)')
rep('JOBS.append(("r4_C_EN_s317", HEAD_EN + FRAME_EN + C_EN + " " + STU_EN, 317))\n', '')
rep('print("R4_DONE", flush=True)', 'print("R5_DONE", flush=True)')
s = s.replace("# T0-A 第 4 轮 微笑分档", "# T0-A 第 5 轮 俏皮微笑（总督导 11-17 转用户「看可以加一点 微微露一点舌头，等等」）。由 gen_r4.py 复制，只换档位 E/F/G、种子只用 331、前缀 r5_/g5。\n# 以下为第 4 轮原注释：T0-A 第 4 轮 微笑分档", 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
