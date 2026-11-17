# -*- coding: utf-8 -*-
# 第 4 轮联系表：每张裁脸放大，按档一列（A/B/C/D，C 档旁加英文对照一列），行＝Qwen 种子 317、Qwen 种子 331、GPT；最左一列放 front_a 的脸当参照。
import json, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); U = os.path.dirname(D)
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24); FB = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 28)
S = json.load(open(os.path.join(D, "_facesim_r4.json"), encoding="utf-8"))
def crop(p, b):
    im = Image.open(p).convert("RGB")
    if not b: return im.resize((420, int(420 * im.height / im.width)))
    x0, y0, x1, y1 = b; w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; s = max(w, h) * 1.6
    c = im.crop((int(cx - s / 2), int(cy - s * 0.55), int(cx + s / 2), int(cy + s * 0.65)))
    return c.resize((420, int(420 * c.height / c.width)), Image.LANCZOS)
COLS = [("参照", None), ("A 抿嘴浅笑", "A"), ("B 眼里带笑", "B"), ("C 说话间的笑", "C"), ("C 英文对照", "C_EN"), ("D 轻笑露齿", "D")]
ROWS = [("Qwen 种子317", lambda k: "r4_%s_s317.png" % k), ("Qwen 种子331", lambda k: None if k == "C_EN" else "r4_%s_s331.png" % k), ("GPT", lambda k: None if k == "C_EN" else "g4_%s.png" % k)]
CW, CH, LH, RW = 430, 520, 36, 190
SH = Image.new("RGB", (RW + CW * len(COLS), 46 + len(ROWS) * (CH + LH)), "white"); dr = ImageDraw.Draw(SH)
for i, (c, _) in enumerate(COLS): dr.text((RW + i * CW + 8, 8), c, fill="black", font=FB)
for j, (rn, fn) in enumerate(ROWS):
    y0 = 46 + j * (CH + LH); dr.text((8, y0 + CH // 2), rn, fill="black", font=FB)
    for i, (_, k) in enumerate(COLS):
        x0 = RW + i * CW
        if k is None:
            if j > 0: continue
            b = "face_front_a.png"; p = os.path.join(U, "_refs", b)
        else:
            b = fn(k)
            if not b: continue
            p = os.path.join(D, b)
        if not os.path.exists(p): dr.text((x0 + 180, y0 + CH // 2), "缺", fill="red", font=FB); continue
        im = crop(p, S.get(b, {}).get("bbox")); im = im.crop((0, 0, im.width, min(im.height, CH)))
        SH.paste(im, (x0 + 5, y0 + LH))
        s = S.get(b, {}).get("sim"); dr.text((x0 + 6, y0 + 4), "%s  %s" % (b[:-4], "无脸" if s is None else "%.3f" % s), fill="black", font=F)
out = os.path.join(D, "联系表_第4轮_微笑分档_脸部放大_1117.jpg"); SH.save(out, quality=92); print("OK", SH.size)
