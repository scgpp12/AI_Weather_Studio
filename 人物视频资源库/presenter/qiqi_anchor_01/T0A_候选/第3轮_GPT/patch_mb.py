# 复制 codex_train.py，只加一条：碰到 moderation_blocked 立即停、不重试
p = "codex_train_mb.py"
s = open(p, encoding="utf-8").read()
a = "        if 'usage limit' in ((r.stdout or '') + (r.stderr or '')):"
assert s.count(a) == 1
BS = chr(92)
add = ("        if 'moderation_blocked' in ((r.stdout or '') + (r.stderr or '')):\n"
       "            log.write(f'{name} MODERATION_BLOCKED" + BS + "n'); log.flush(); "
       "print('MODERATION_BLOCKED', name, flush=True); sys.exit(3)\n")
s = s.replace(a, add + a)
s = "# 副本（11-17 T0-A 第3轮）：原件 T/codex_train.py，只加了碰到 moderation_blocked 立即停、不重试。\n" + s
open(p, "w", encoding="utf-8").write(s)
