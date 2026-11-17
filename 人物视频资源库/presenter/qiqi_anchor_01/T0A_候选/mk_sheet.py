# -*- coding: utf-8 -*-
# T0-A 联系表：front_a 在最前，10 张候选按顺序排，每张标文件名、种子、人脸相似度。
import json, os, glob
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
sim = json.load(open(os.path.join(D, "_facesim.json"), encoding="utf-8"))
items = [("_refs/face_front_a.png", "front_a（脸参考）"), ("_refs/costume_AUT-0066.png", "AUT-0066（服装参考）")]
for p in sorted(glob.glob(os.path.join(D, "qq_*.png")), key=lambda q: (["full","half","side","back"].index(os.path.basename(q).split("_")[1]), q)):
    b = os.path.basename(p); s = sim.get(b, {}).get("sim")
    items.append((b, "%s  相似度 %s" % (b[:-4], "无脸" if s is None else "%.3f" % s)))
H = 640; cols = 6; tiles = []
for p, lab in items:
    im = Image.open(os.path.join(D, p)).convert("RGB"); im = im.resize((int(im.width * H / im.height), H))
    t = Image.new("RGB", (im.width, H + 44), "white"); t.paste(im, (0, 44)); ImageDraw.Draw(t).text((6, 6), lab, fill="black", font=F); tiles.append(t)
rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
W = max(sum(t.width for t in r) for r in rows); S = Image.new("RGB", (W, len(rows) * (H + 44)), "white")
for j, r in enumerate(rows):
    x = 0
    for t in r: S.paste(t, (x, j * (H + 44))); x += t.width
S.save(os.path.join(D, "联系表_T0A_七七主播定妆_1117.jpg"), quality=90)
print("OK", S.size)
