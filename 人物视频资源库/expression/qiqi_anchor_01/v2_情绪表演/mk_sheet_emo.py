# -*- coding: utf-8 -*-
# 情绪表演 v2 联系表：每种情绪一行，GPT 和 Qwen 并排；12 行分两栏（左 1–6，右 7–12）。每格标情绪、模型、相似度。
import json, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24); FB = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 28)
S = json.load(open(os.path.join(D, "_facesim.json"), encoding="utf-8"))
E = [("01_kaixin", "开心"), ("02_daxiao", "大笑"), ("03_jingya", "惊讶"), ("04_jingxi", "惊喜"), ("05_nanguo", "难过"), ("06_ku", "哭"),
     ("07_shengqi", "生气"), ("08_danxin", "担心关切"), ("09_haixiu", "害羞"), ("10_sikao", "思考"), ("11_bobao", "认真播报"), ("12_wunai", "无奈")]
CW, CH, LH, RW = 400, 500, 34, 150
BW = RW + 2 * CW + 30
SH = Image.new("RGB", (2 * BW, 46 + 6 * (CH + LH)), "white"); dr = ImageDraw.Draw(SH)
for b in range(2):
    dr.text((b * BW + RW + 8, 8), "GPT", fill="black", font=FB); dr.text((b * BW + RW + CW + 8, 8), "Qwen", fill="black", font=FB)
for i, (n, zh) in enumerate(E):
    b, r = divmod(i, 6); x0 = b * BW; y0 = 46 + r * (CH + LH)
    dr.text((x0 + 8, y0 + CH // 2), "%s\n%s" % (n[:2], zh), fill="black", font=FB)
    for k, f in enumerate(("g_%s.png" % n, "q_%s_s337.png" % n)):
        p = os.path.join(D, f); cx = x0 + RW + k * CW
        if not os.path.exists(p): dr.text((cx + 150, y0 + CH // 2), "缺", fill="red", font=FB); continue
        im = Image.open(p).convert("RGB"); im.thumbnail((CW - 8, CH)); SH.paste(im, (cx + (CW - im.width) // 2, y0 + LH))
        s = S.get(f, {}).get("sim"); dr.text((cx + 4, y0 + 4), "%s  %s" % (f[:-4], "无脸" if s is None else "%.3f" % s), fill="black", font=F)
SH.save(os.path.join(D, "联系表_七七情绪表演_v2_1117.jpg"), quality=90); print("OK", SH.size)
