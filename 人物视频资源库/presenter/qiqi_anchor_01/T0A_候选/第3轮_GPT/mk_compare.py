# -*- coding: utf-8 -*-
# 总联系表：同一类放一列（正面全身／半身／侧面／背面／手指镜头／比心），行＝Qwen 第1轮选定、Qwen 第2轮两种子、GPT 第3轮。
# 每格标文件名和与 front_a 的人脸相似度（侧脸单列标「侧脸」，背面无脸）。不挑。
import json, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); U = os.path.dirname(D); R2 = os.path.join(U, "第2轮")
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24); FB = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 30)
S = {}
for f in (os.path.join(U, "_facesim.json"), os.path.join(R2, "_facesim.json"), os.path.join(D, "_facesim.json")):
    if os.path.exists(f): S.update(json.load(open(f, encoding="utf-8")))
COLS = ["正面全身", "半身（到腰）", "侧面全身", "背面全身", "手势 P022 手指镜头", "手势 P003 单手比心"]
ROWS = [("Qwen 第1轮 用户选定", [os.path.join(U, "qq_full_s233.png"), None, os.path.join(U, "qq_side_s269.png"), os.path.join(U, "qq_back_s269.png"), None, None]),
        ("Qwen 第2轮 种子A", [os.path.join(R2, "r2_full_s281.png"), os.path.join(R2, "r2_half_s293.png"), None, None, os.path.join(R2, "r2_point_P022_s311.png"), os.path.join(R2, "r2_heart_P003_s313.png")]),
        ("Qwen 第2轮 种子B", [os.path.join(R2, "r2_full_s283.png"), os.path.join(R2, "r2_half_s307.png"), None, None, None, None]),
        ("GPT 第3轮", [os.path.join(D, x) for x in ("g3_full_front.png", "g3_waist_half.png", "g3_full_side.png", "g3_full_back.png", "g3_waist_point_P022.png", "g3_waist_heart_P003.png")])]
CW, CH, LH, RW = 420, 600, 40, 330
SH = Image.new("RGB", (RW + CW * len(COLS), 50 + len(ROWS) * (CH + LH)), "white"); dr = ImageDraw.Draw(SH)
for i, c in enumerate(COLS): dr.text((RW + i * CW + 8, 8), c, fill="black", font=FB)
for j, (rn, cells) in enumerate(ROWS):
    y0 = 50 + j * (CH + LH); dr.multiline_text((8, y0 + CH // 2 - 30), rn.replace(" ", chr(10), 1), fill="black", font=FB)
    for i, p in enumerate(cells):
        x0 = RW + i * CW
        if not p or not os.path.exists(p):
            dr.text((x0 + 180, y0 + CH // 2), "—", fill="grey", font=FB); continue
        im = Image.open(p).convert("RGB"); im.thumbnail((CW - 10, CH))
        SH.paste(im, (x0 + (CW - im.width) // 2, y0 + LH))
        b = os.path.basename(p); s = S.get(b, {}).get("sim")
        lab = b[:-4] + "  " + ("背面无脸" if s is None else ("%.3f" % s + ("（侧脸）" if "side" in b else "")))
        dr.text((x0 + 6, y0 + 6), lab, fill="black", font=F)
out = os.path.join(U, "总联系表_T0A_Qwen1_Qwen2_GPT3_1117.jpg"); SH.save(out, quality=90); print("OK", SH.size, out)
