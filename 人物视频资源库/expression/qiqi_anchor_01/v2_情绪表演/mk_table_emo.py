# -*- coding: utf-8 -*-
# 情绪表演 v2 数据表：每张一行（情绪、模型、种子、用时、相似度、手、表演核对），后附提示词全文。
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)); NL = chr(10)
S = json.load(open(os.path.join(D, "_facesim.json"), encoding="utf-8"))
Q = {r["tag"]: r for r in json.load(open(os.path.join(D, "_记录.json"), encoding="utf-8"))}
GT = {}
for l in open(os.path.join(D, "log.txt"), encoding="utf-8"):
    m = re.match(r"(g_\S+) ok (\d+) s", l)
    if m: GT[m.group(1)] = int(m.group(2))
E = [("01_kaixin", "开心"), ("02_daxiao", "大笑"), ("03_jingya", "惊讶"), ("04_jingxi", "惊喜"), ("05_nanguo", "难过"), ("06_ku", "哭"),
     ("07_shengqi", "生气"), ("08_danxin", "担心关切"), ("09_haixiu", "害羞"), ("10_sikao", "思考"), ("11_bobao", "认真播报"), ("12_wunai", "无奈")]
# 原尺寸逐张看过的结果（手：能看到的手指数、有没有多手；表演：和要求对不对得上）
CHK = {
 "g_01_kaixin": ("右手 5 指掌心朝上摊开✓；左手在画外", "轻笑✓ 头微侧✓ 手摊在胸前偏外侧"),
 "q_01_kaixin": ("右手 5 指✓", "轻笑✓；**手抬到了肩旁，更像打招呼，不是摊在胸前**"),
 "g_02_daxiao": ("右手 5 指掩嘴✓", "眼睛笑眯✓ 手掩嘴✓ 肩前缩✓"),
 "q_02_daxiao": ("右手 5 指掩嘴✓", "眯眼笑✓ 手掩嘴✓"),
 "g_03_jingya": ("双手 10 指捂嘴✓", "睁眼抬眉✓ 额纹✓ 双手捂嘴✓"),
 "q_03_jingya": ("双手 10 指并拢捂嘴✓", "睁眼抬眉✓ 双手捂嘴✓（人台 P015）"),
 "g_04_jingxi": ("双手合掌✓", "张嘴笑露上牙✓ 合掌✓"),
 "q_04_jingxi": ("双手合掌✓", "张嘴笑✓ 合掌✓（人台 P016）"),
 "g_05_nanguo": ("右手握拳指节擦眼✓", "低头✓ 嘴角下撇✓ 泪痕一道（偏细）"),
 "q_05_nanguo": ("右手手指在眼旁✓ 5 指", "泪痕✓（两边脸颊都有）眼眶红✓"),
 "g_06_ku": ("双手捂住下半张脸✓", "闭眼皱眉✓ 眼下泪痕✓"),
 "q_06_ku": ("双手 10 指✓", "泪痕✓ 皱眉✓；**双手捧着两颊，没捂住半张脸**（人台 P020 本来就是捧脸）"),
 "g_07_shengqi": ("双臂抱胸✓ 手指正常", "皱眉✓ 抿嘴✓ 抱胸✓"),
 "q_07_shengqi": ("双臂抱胸✓ 手指正常", "皱眉✓ 抿嘴✓ 抱胸✓（人台 P041）"),
 "g_08_danxin": ("右手 5 指按胸口✓", "眉心蹙✓ 前倾✓"),
 "q_08_danxin": ("右手 5 指按胸口✓", "眉心蹙✓（略偏生气）"),
 "g_09_haixiu": ("一只手挡半边脸✓", "脸红✓ 抬眼✓"),
 "q_09_haixiu": ("一只手挡半边脸✓", "脸红✓ 抿嘴笑✓（人台 P011）"),
 "g_10_sikao": ("右手食指点下巴✓ 左手托肘✓", "眼往上看✓"),
 "q_10_sikao": ("右手食指点下巴✓ 左手托肘✓", "眼往上看✓"),
 "g_11_bobao": ("双手在画面最下边，只露一点", "平和带笑✓；**交叠的手大半在画外**"),
 "q_11_bobao": ("双手在画面最下边，露一半", "平和带笑✓ 站正✓；手偏低"),
 "g_12_wunai": ("双手 5+5 指掌心朝上摊开✓", "嘴角撇✓；耸肩不明显"),
 "q_12_wunai": ("双手 5+5 指掌心朝上✓", "嘴角撇✓ 耸肩✓ 摊手✓"),
}
POSE = {"03_jingya": "upper80v2_P015 萌袖风・双手掩口", "04_jingxi": "upper80v2_P016 拜托手势（双手合十）", "06_ku": "upper80v2_P020 双手捧脸",
        "07_shengqi": "upper80v2_P041 双臂抱胸", "09_haixiu": "upper80v2_P011 歪头＋手遮单眼"}
L = ["# 七七 情绪表演 v2 数据表（11-17）", "",
     "- 全部 24 张：12 种情绪 × GPT／Qwen 各一张，半身到腰，AUT-0066 无包，中性灰。**没有多手，看得见的手指都是 5 根。**",
     "- GPT：`codex_train_mb.py`（T/codex_train.py 副本，被拦即停），参考图 front_a `62824f0a…`、qq_full_s233 `5953ef8f…`、g3_waist_half `02b2cf94…`；12 张一次成功，**没有被拦**；实际尺寸 1122×1402。",
     "- Qwen：`gen_emo.py`，种子 337，1104×1376，25 步 cfg 1。参考图上限 3 张：有人台的 5 种喂「人台＋g3_waist_half＋front_a」，其余 7 种喂「g3_waist_half 当底＋front_a」。**12 张都拍到腰，没出成全身**（拿到腰的图当底，景别跟着底图走）。",
     "- 相似度：insightface buffalo_l 和 front_a 比；基准线（front_a 对七七其他定版图）0.803–0.885。哭、大笑、惊讶这类脸被手遮住或五官大变形的，分数掉得最多，属正常，照实记。", "",
     "| # | 情绪 | 模型 | 种子 | 人台 | 用时 | 相似度 | 手 | 表演核对 |", "|---|---|---|---|---|---|---|---|---|"]
for n, zh in E:
    g = "g_" + n; q = "q_%s_s337" % n
    L.append("| %s | %s | GPT | — | — | %s 秒 | %.3f | %s | %s |" % (n[:2], zh, GT.get(g, "?"), S[g + ".png"]["sim"], CHK[g][0], CHK[g][1]))
    r = Q[q]
    L.append("| %s | %s | Qwen | 337 | %s | %.1f 秒（进程峰值 %d MiB） | %.3f | %s | %s |" % (n[:2], zh, POSE.get(n, "无（底图法）"), r["sec"], r["proc_peak_mib"], S[q + ".png"]["sim"], CHK["q_" + n][0], CHK["q_" + n][1]))
L += ["", "## 提示词全文", "", "### GPT（codex_train 拼出来的完整文本）", ""]
for i in range(3):
    j = json.load(open(os.path.join(D, "job_emo%d.json" % i), encoding="utf-8"))
    for sh in j["shots"]:
        p = ("Use $imagegen to generate ONE image, " + j["size"] + ". Pass all attached images to the image tool as reference images. " + j["refnote"]
             + NL + NL + "Character: " + j["id"] + NL + NL + "Shot: " + sh["prompt"] + NL + NL + j["style"] + NL + NL
             + "When done, print the saved file path. Do not modify any other file.")
        L += ["#### g_%s（%s）" % (sh["n"], sh["caption"]), "", "```", p, "```", ""]
L += ["### Qwen", ""]
for n, zh in E:
    r = Q["q_%s_s337" % n]
    L += ["#### q_%s_s337（%s，%d 字）" % (n, zh, r["chars"]), "", "参考图：" + "；".join("%s `%s`" % (a, b) for a, b in r["refs"]), "", "```", r["prompt"], "```", ""]
open(os.path.join(D, "数据表_七七情绪表演_v2_1117.md"), "w", encoding="utf-8").write(NL.join(L)); print("ok")
