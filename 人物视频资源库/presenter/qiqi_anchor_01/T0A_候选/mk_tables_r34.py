# -*- coding: utf-8 -*-
# 第 3 轮 GPT、第 4 轮微笑分档的数据表（从本地拉回的记录、相似度、job.json 生成）。
import json, os
D = os.path.dirname(os.path.abspath(__file__)); NL = chr(10)
def P(j, sh):
    return ("Use $imagegen to generate ONE image, " + j["size"] + ". Pass all attached images to the image tool as reference images. " + j["refnote"]
            + NL + NL + "Character: " + j["id"] + NL + NL + "Shot: " + sh["prompt"] + NL + NL + j["style"] + NL + NL
            + "When done, print the saved file path. Do not modify any other file.")
# 第 3 轮
d3 = os.path.join(D, "第3轮_GPT"); S = json.load(open(os.path.join(d3, "_facesim.json"), encoding="utf-8"))
T = {"g3_full_front": 147, "g3_full_side": 147, "g3_full_back": 122, "g3_waist_half": 134, "g3_waist_point_P022": 132, "g3_waist_heart_P003": 127}
CL = {"g3_full_front": "蝴蝶结✓ 珍珠✓ 短裤翻边✓ 袜子蝴蝶结✓ 短靴✓ 无包✓ 微笑✓",
      "g3_full_side": "蝴蝶结✓ 珍珠✓ 翻边✓ 袜子蝴蝶结✓ 短靴✓ 无包✓ 侧脸微笑✓（正侧面，远侧腿被完全挡住）",
      "g3_full_back": "后颈珍珠扣✓ 翻边✓ 袜子外侧蝴蝶结✓ 短靴✓ 无包✓ 没凭空多东西",
      "g3_waist_half": "景别正好到裤腰✓ 蝴蝶结✓ 珍珠✓ 无包✓ 微笑✓",
      "g3_waist_point_P022": "景别到裤腰✓ 右手食指指镜头✓ 手指正常 无包✓ 微笑✓",
      "g3_waist_heart_P003": "景别到裤腰✓ 右手单手比心✓ 左手扶腰✓ 手指正常 无包✓ 微笑✓"}
L = ["# T0-A 第 3 轮 GPT 数据表（11-17）", "",
     "管线 sons02 `castsery/qiqi_anchor/gpt3/codex_train_mb.py`（原件 T/codex_train.py 的副本，只加了 moderation_blocked 立即停）。走订阅、不占显卡。6 张都一次成功，**没有被拦**。", "",
     "参考图（按 image 顺序）：face_front_a `62824f0a…`、costume_AUT-0066 `2ad26cee…`、qq_full_s233 `5953ef8f…`、r2_heart_P003_s313 `127e4e9f…`。", "",
     "| 成品 | 写的尺寸 | 实际尺寸 | 用时 | 和 front_a 相似度 | 衣服逐项 |", "|---|---|---|---|---|---|"]
for k in T:
    s = S[k + ".png"]["sim"]; full = "full" in k
    L.append("| %s | %s | %s | %d 秒 | %s | %s |" % (k, "1024x1536" if full else "1024x1280", "1024×1536" if full else "1122×1402", T[k],
             "背面无脸" if s is None else "%.3f" % s + ("（侧脸）" if "side" in k else ""), CL[k]))
L += ["", "说明：到腰三张实际是 1122×1402，和 front_a 原图一样大，脸的位置也和 front_a 几乎重合，看起来 GPT 是拿 image 1 当画布改的（表情、衣服、手势都换了，不是照抄）。",
      "另：GPT 往 sons02 gpt3 目录里多存了两份同内容副本（qq_full_AUT-0066_smile.png、qq_profile_right_AUT-0066.png，和 g3_full_front／g3_full_side 一样大），没删。", "", "## 提示词全文", ""]
for f in ("job_full.json", "job_waist.json"):
    j = json.load(open(os.path.join(d3, f), encoding="utf-8"))
    for sh in j["shots"]: L += ["### %s_%s（%s）" % (j["prefix"], sh["n"], sh["caption"]), "", "```", P(j, sh), "```", ""]
open(os.path.join(d3, "数据表_第3轮_GPT_1117.md"), "w", encoding="utf-8").write(NL.join(L))
# 第 4 轮
d4 = os.path.join(D, "第4轮_微笑分档"); S4 = json.load(open(os.path.join(d4, "_facesim_r4.json"), encoding="utf-8"))
R = [r for r in json.load(open(os.path.join(d4, "_记录.json"), encoding="utf-8")) if r["tag"].startswith("r4_")]
G = {"A": 103, "B": 154, "C": 121, "D": 111}; j4 = json.load(open(os.path.join(d4, "job_g4.json"), encoding="utf-8"))
L = ["# T0-A 第 4 轮 微笑分档 数据表（11-17）", "",
     "Qwen：`gen_r4.py`，Picture 1＝front_a `62824f0a…`，Picture 2＝qq_full_s233 `5953ef8f…`，1024×1280，25 步 cfg 1，正文中文（C 档另加一张英文对照，种子同为 317）。",
     "GPT：`codex_train_mb.py`，同样两张参考图，正文中文，4 张都一次成功，**没有被拦**。", "",
     "| 成品 | 档 | 种子 | 实际尺寸 | 用时 | 进程峰值 | 整卡峰值 | 和 front_a 相似度 | 备注 |", "|---|---|---|---|---|---|---|---|---|"]
for r in R:
    t = r["tag"]; k = t.split("_")[1]; note = "英文对照" if "_EN_" in t else ""
    if t == "r4_D_s331": note = "**珍珠外面又多戴了 front_a 戏服上那条铜绿项链（参考图串过来）**"
    L.append("| %s | %s | %d | 1024×1280 | %.1f 秒 | %d MiB | %d MiB | %.3f | %s |" % (t, k, r["seed"], r["sec"], r["proc_peak_mib"], r["card_peak_mib"], S4[t + ".png"]["sim"], note))
for k in "ABCD":
    L.append("| g4_%s | %s | — | 1122×1402 | %d 秒 | — | — | %.3f | GPT |" % (k, k, G[k], S4["g4_%s.png" % k]["sim"]))
L += ["", "整卡峰值 73 GB 左右，是因为 Qwen 跑的时候卡上另有一个约 34 GB 的进程（开跑时空闲 61.8 GB，过了 57 GB 的线）。", "", "## 提示词全文", ""]
for r in R: L += ["### %s（种子 %d，%d 字）" % (r["tag"], r["seed"], r["chars"]), "", "```", r["prompt"], "```", ""]
for sh in j4["shots"]: L += ["### g4_%s（%s）" % (sh["n"], sh["caption"]), "", "```", P(j4, sh), "```", ""]
open(os.path.join(d4, "数据表_第4轮_微笑分档_1117.md"), "w", encoding="utf-8").write(NL.join(L))
print("ok")
