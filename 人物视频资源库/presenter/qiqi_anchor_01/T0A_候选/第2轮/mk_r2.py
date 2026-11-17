# -*- coding: utf-8 -*-
# 第 2 轮联系表＋数据表。联系表：front_a、第 1 轮选定 s233 做对照，后面 6 张；数据表从 _记录.json 取 r2_ 那几行。
import json, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__)); U = os.path.dirname(D)
F = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
S = json.load(open(os.path.join(D, "_facesim.json"), encoding="utf-8"))
R = [r for r in json.load(open(os.path.join(D, "_记录.json"), encoding="utf-8")) if r["tag"].startswith("r2_")]
items = [(os.path.join(U, "_refs/face_front_a.png"), "front_a（脸参考）"), (os.path.join(U, "qq_full_s233.png"), "第1轮选定 s233  %.3f" % S["qq_full_s233.png"]["sim"])]
for r in R: items.append((os.path.join(D, r["tag"] + ".png"), "%s  %.3f" % (r["tag"][3:], S[r["tag"] + ".png"]["sim"])))
H = 640; tiles = []
for p, lab in items:
    im = Image.open(p).convert("RGB"); im = im.resize((int(im.width * H / im.height), H))
    t = Image.new("RGB", (max(im.width, 330), H + 44), "white"); t.paste(im, (0, 44)); ImageDraw.Draw(t).text((6, 6), lab, fill="black", font=F); tiles.append(t)
rows = [tiles[:4], tiles[4:]]
W = max(sum(t.width for t in r) for r in rows); SH = Image.new("RGB", (W, 2 * (H + 44)), "white")
for j, r in enumerate(rows):
    x = 0
    for t in r: SH.paste(t, (x, j * (H + 44))); x += t.width
SH.save(os.path.join(D, "联系表_T0A_第2轮_1117.jpg"), quality=90)
CL = {"full": "蝴蝶结✓ 珍珠✓ 短裤翻边✓ 袜子蝴蝶结✓ 短靴✓ 包已去✓；微笑✓",
      "half": "六项在、包已去、微笑✓；**景别仍不到腰**",
      "point": "蝴蝶结✓ 珍珠✓ 翻边✓ 袜子蝴蝶结✓ 短靴只露靴口 包已去✓；手指镜头✓ 微笑✓；景别到膝",
      "heart": "蝴蝶结✓ 珍珠✓ 翻边✓ 袜子蝴蝶结✓ 短靴出画 包已去✓；单手比心✓ 另手扶腰✓ 微笑✓；景别到大腿"}
FR = {"r2_half_s293": "拍到膝下、靴口", "r2_half_s307": "拍到大腿中段"}
L = ["# T0-A 第 2 轮 数据表（11-17）", "", "基准线：front_a 对七七其他定版图 0.803–0.885；第 1 轮选定 qq_full_s233 是 0.847。", "",
     "| 成品 | 种子 | 尺寸 | 实际用时 | 进程峰值 | 整卡峰值 | 和 front_a 相似度 | 衣服和表情核对 | 成品 md5 |", "|---|---|---|---|---|---|---|---|---|"]
for r in R:
    k = r["tag"].split("_")[1]; c = CL[k] + ("（" + FR[r["tag"]] + "）" if r["tag"] in FR else "")
    L.append("| %s | %d | %d×%d | %.1f 秒 | %d MiB | %d MiB | %.3f | %s | `%s` |" % (r["tag"], r["seed"], r["w"], r["h"], r["sec"], r["proc_peak_mib"], r["card_peak_mib"], S[r["tag"] + ".png"]["sim"], c, r["out_md5"]))
L += ["", "## 参考图和提示词全文", ""]
for r in R:
    L += ["### %s（种子 %d，%d 字）" % (r["tag"], r["seed"], r["chars"]), "", "参考图（按 Picture 顺序）：" + "；".join("%s `%s`" % (a, b) for a, b in r["refs"]), "", "```", r["prompt"], "```", ""]
open(os.path.join(D, "数据表_T0A_第2轮_1117.md"), "w", encoding="utf-8").write("\n".join(L))
print("OK", SH.size, sum(r["sec"] for r in R))
