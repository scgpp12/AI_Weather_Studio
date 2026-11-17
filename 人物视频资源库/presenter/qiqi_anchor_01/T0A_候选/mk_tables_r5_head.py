# -*- coding: utf-8 -*-
# ① 第 5 轮俏皮微笑数据表；② 所有轮次＋情绪表演的「头宽 ÷ 肩宽」汇总表（DWPose，>0.4 标红，另列七七定版图当参照）。
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)); NL = chr(10)
H = json.load(open(os.path.join(D, "_headratio_all_1117.json"), encoding="utf-8"))
METHOD = ("算法：DWPose wholebody（ComfyUI controlnet_aux 里的 yolox_l.onnx＋dw-ll_ucoco_384.onnx，CPU 跑）。"
          "头宽＝脸部 68 点下颌轮廓最左点（第 0 点）到最右点（第 16 点）的距离，只量脸、不含头发；"
          "肩宽＝身体关键点右肩到左肩的距离，是肩关节中心，比衣服外沿窄。所以这个比值天生偏大：七七定版图自己就在 0.443–0.47。")
def hr(b):
    r = H.get(b)
    if not r or r.get("ratio") is None: return "—"
    v = r["ratio"]
    if "side" in b or "back" in b: return "—（%s，侧／背面不适用）" % v
    return ('<span style="color:red">**%.3f**</span>' % v) if v > 0.4 else "%.3f" % v
# ① 第 5 轮
d5 = os.path.join(D, "第5轮_俏皮微笑"); S = json.load(open(os.path.join(d5, "_facesim_r5.json"), encoding="utf-8"))
R = {r["tag"]: r for r in json.load(open(os.path.join(d5, "_记录.json"), encoding="utf-8")) if r["tag"].startswith("r5_")}
GT = {m.group(1): int(m.group(2)) for m in (re.match(r"(g5_\S+) ok (\d+) s", l) for l in open(os.path.join(d5, "log.txt"), encoding="utf-8")) if m}
CHK = {"r5_E_s331": "舌尖露出✓ 一只眼眯✓ 拳贴太阳穴✓；**眉头皱着，看着像不耐烦**",
       "g5_E": "眯眼✓ 拳贴太阳穴✓；**舌尖没露出来，只是抿嘴笑**",
       "r5_F_s331": "她的右眼闭成弯线✓ 左眼睁着✓ 露一点上牙✓ V 字手指正常✓",
       "g5_F": "她的右眼闭✓ 露一点上牙✓ V 字手指正常✓",
       "r5_G_s331": "歪头✓ 抿嘴上翘✓ 指尖贴脸颊✓",
       "g5_G": "歪头✓ 抿嘴上翘✓ 指尖贴脸颊✓"}
L = ["# T0-A 第 5 轮 俏皮微笑 数据表（11-17）", "",
     "- 做法同第 4 轮（Qwen 两图 front_a＋qq_full_s233，1024×1280，25 步 cfg 1，种子 331；GPT 同两张参考图），正文中文。E/F/G 写法照表情研究频道 `expression/研究/03_给出图模型的写法.md`。",
     "- 头身比例那句（11-17 用户定）来的时候这轮已经出完，照「已出完的不重跑」没有加。GPT 3 张一次成功，**没有被拦**。", "- " + METHOD, "",
     "| 成品 | 档 | 模型 | 种子 | 实际尺寸 | 用时 | 和 front_a 相似度 | 头宽÷肩宽 | 核对（手、表情） |", "|---|---|---|---|---|---|---|---|---|"]
for k, zh in (("E", "俏皮吐舌尖"), ("F", "wink 微笑"), ("G", "歪头抿嘴笑")):
    q = "r5_%s_s331" % k; r = R[q]
    L.append("| %s | %s %s | Qwen | 331 | 1024×1280 | %.1f 秒（进程峰值 %d MiB） | %.3f | %s | %s |" % (q, k, zh, r["sec"], r["proc_peak_mib"], S[q + ".png"]["sim"], hr(q + ".png"), CHK[q]))
    g = "g5_" + k
    L.append("| %s | %s %s | GPT | — | 1122×1402 | %s 秒 | %.3f | %s | %s |" % (g, k, zh, GT.get(g, "?"), S[g + ".png"]["sim"], hr(g + ".png"), CHK[g]))
L += ["", "## 提示词全文", ""]
for q, r in R.items(): L += ["### %s（%d 字）" % (q, r["chars"]), "", "```", r["prompt"], "```", ""]
j = json.load(open(os.path.join(d5, "job_g5.json"), encoding="utf-8"))
for sh in j["shots"]:
    p = ("Use $imagegen to generate ONE image, " + j["size"] + ". Pass all attached images to the image tool as reference images. " + j["refnote"]
         + NL + NL + "Character: " + j["id"] + NL + NL + "Shot: " + sh["prompt"] + NL + NL + j["style"] + NL + NL + "When done, print the saved file path. Do not modify any other file.")
    L += ["### g5_%s（%s）" % (sh["n"], sh["caption"]), "", "```", p, "```", ""]
open(os.path.join(d5, "数据表_第5轮_俏皮微笑_1117.md"), "w", encoding="utf-8").write(NL.join(L))
# ② 汇总
G = [("七七定版图（参照）", ["face_front_a.png", "front_b.png", "mid_b.png", "late_b.png", "full_front.png"]),
     ("T0-A 第 1 轮 Qwen", sorted(k for k in H if k.startswith("qq_"))), ("T0-A 第 2 轮 Qwen", sorted(k for k in H if k.startswith("r2_"))),
     ("T0-A 第 3 轮 GPT", sorted(k for k in H if k.startswith("g3_"))), ("T0-A 第 4 轮 Qwen", sorted(k for k in H if k.startswith("r4_"))),
     ("T0-A 第 4 轮 GPT", sorted(k for k in H if k.startswith("g4_"))), ("T0-A 第 5 轮", sorted(k for k in H if k.startswith(("r5_", "g5_")))),
     ("情绪表演 v2 GPT", sorted(k for k in H if k.startswith("g_"))), ("情绪表演 v2 Qwen", sorted(k for k in H if k.startswith("q_")))]
L = ["# 七七 头宽 ÷ 肩宽 汇总（11-17）", "", "- " + METHOD,
     "- 按总督导给的线，**超过 0.4 的标红**；但这个量法下七七自己的定版图（含脸的准绳 front_a）全都超过 0.4，所以几乎每张都红。",
     "- 用户说「头太大」的 r2_half_s293 是 **0.543**，正面图里第二高（最高是情绪表演 GPT 无奈 g_12 的 0.545，那张耸着肩、肩点被抬高）。按这个量法，「比定版图最大值 0.47 高出 10% 以上」约等于 **0.52**，能把 s293 这类挑出来。用哪条线请定。",
     "- 侧面、背面这个比值没有意义（侧面两肩重叠，背面看不到下颌），只列数不判。", ""]
for t, ks in G:
    L += ["## " + t, "", "| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |", "|---|---|---|---|"]
    for k in ks:
        r = H.get(k) or {}
        L.append("| %s | %s | %s | %s |" % (k, r.get("head", "—"), r.get("shoulder", "—"), hr(k)))
    L.append("")
open(os.path.join(D, "头宽除肩宽_汇总_DWPose_1117.md"), "w", encoding="utf-8").write(NL.join(L))
print("ok")
