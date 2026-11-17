# -*- coding: utf-8 -*-
# T0-A 七七主播定妆（AUT-0066，不带包），乙路：Qwen 2.1。总督导 11-17 派。只出候选，不挑。
# 本次做法＝Qwen Image 2.1 人物定妆分支（qi21.py 固定参数：qwen3vl_8b_bf16、25 步、cfg 1、euler/simple、resolution 0）。
# 原件＝① 正面全身／半身：sons02 /mnt/storage/model-lab/bjjpose/loop4.py 的单人提示词（人台＋服装＋脸三图，Image→Picture）；
#        ② 侧面／背面：sons02 /mnt/storage/model-lab/castsery/q21_sb8.py（脸＋全身正面两图，1024×1536，SIDE_HEAD／BACK_HEAD 结构）。
# 与原件不同之处：
#  ① loop4 原件挂 turbo（8 步），这次照总督导「固定参数照 qi21.py」用 25 步不挂 turbo；跑在 8188 不是 8190。
#  ② 脸那句：原件写「long wavy dark hair」（白晶晶），七七是盘发，改成「dark hair of Picture 3」；保留「preserving facial width…」那半句（full_single 系原件有）。
#  ③ 姿势名：人台 full_single_P017_front 原名「站立・回眸顾盼」（头偏），写成「站立・两手自然垂在身侧」＋头和身子朝镜头。
#  ④ 加去包正面写法（总督导定）：左肩上什么都没背，两手空着自然垂在身侧。
#  ⑤ 半身：人台裁到腰（pose_P017_half.png），画幅 1104×1216；全身照原件 1056×1408。
#  ⑥ 侧背的 Picture 2 用正面全身第一张（种子 229），按事先定的规则取，不是挑的；用户挑了别的正面，侧背跟着重出。
#  ⑦ 种子新开，过 seedguard。
import sys, os, time, json, subprocess, threading
sys.path.insert(0, "/mnt/storage/ai-drama-pipeline/tools"); import qi21
sys.path.insert(0, "/mnt/storage/model-lab/castsery"); import seedguard
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"; R = D + "refs/"
POSE_F, POSE_H, COST, FACE = R + "pose_P017_front.png", R + "pose_P017_half.png", R + "costume_AUT-0066.png", R + "face_front_a.png"
OUTFIT = ("a mustard-yellow silky blouse with a long soft pussy-bow tied at the collar and puffed long sleeves gathered into "
          "buttoned cuffs, the blouse tucked into the shorts; a single-strand pearl necklace at the collar; olive-green wool "
          "shorts with wide turned-up cuffs at the hem; cream-white ribbed over-the-knee socks, each with a wine-red ribbon bow "
          "at the top band; brown suede platform ankle boots with chunky block heels")
HAND = "Nothing is carried on her left shoulder; both hands are empty and hang naturally at her sides."
def front_prompt(pose):
    return ("Picture 1 is a faceless mannequin showing the exact body pose and framing to copy. Draw the young East Asian woman "
            "with the face and dark hair of Picture 3, preserving Picture 3's facial width, eye shape and spacing, nose proportions, "
            "and full lip shape, wearing the outfit in Picture 2 exactly: " + OUTFIT + ". " + HAND + " "
            "Pose name (Chinese): " + pose + ". Give her a natural facial expression that fits this pose, with specific facial "
            "muscle actions. Photorealistic game-CG style, soft studio light, plain grey background, one person only, no text.")
P_FULL = front_prompt("站立・两手自然垂在身侧（站姿）, her head and body facing the camera")
P_HALF = front_prompt("半身・两手自然垂在身侧（站姿）, her head and body facing the camera, framed from the top of the head down to the waist")
# 侧背：照 q21_sb8.py
STU = ("Plain flat seamless mid-grey studio background, one person only, soft even studio light, photorealistic "
       "live-action costume photo, real skin and real fabric. Full body from the top of the head down to the feet.")
HEAD = ("Picture 1 is this person's face. Picture 2 is the same person standing facing the camera in full costume. "
        "Same person, same face, same build, same height. ")
SIDE = ("Side view, full body: She stands in profile facing the right edge of the frame, arms relaxed, head "
        "facing the same way as the body with the face seen edge-on from the side, one ear towards the camera. "
        "WEAR EXACTLY THE SAME COSTUME AS PICTURE 2 - every garment, every layer, the same colours, the same "
        "patterns in the same places, the same belt, the same trim, the same footwear. "
        "Keep the mustard-yellow silky blouse with the long pussy-bow at the collar and the puffed sleeves with buttoned cuffs, "
        "the pearl necklace, the olive-green shorts with turned-up cuffs, the cream-white over-the-knee socks with the wine-red "
        "bows at the top, the brown suede platform ankle boots, and her dark hair tied up in a loose bun. Hands empty. ")
BACK = ("Back view, full body: She stands with her back to the camera, arms relaxed, the back of the head "
        "and the whole back of the costume towards the lens. "
        "Back of the hair: her dark hair gathered up into a loose bun at the crown, loose wisps at the nape. "
        "Back of the outfit: the mustard-yellow silky blouse covering her back, its collar band running round the back of the "
        "neck with the pearl necklace's clasp at the nape, the puffed sleeves on both arms down to the buttoned cuffs, the blouse "
        "tucked into the olive-green shorts, the waistband going all the way round, the turned-up cuffs of the shorts, the "
        "cream-white over-the-knee socks with a wine-red bow at the top of each, the brown suede platform ankle boots with block heels. ")
P_SIDE = HEAD + SIDE + STU
P_BACK = HEAD + BACK + STU
O = D  # 产物和 _记录.json 同目录，seedguard 才认得出
FRONT0 = O + "qq_full_s229.png"
JOBS = [("qq_full_s229", [POSE_F, COST, FACE], P_FULL, 1056, 1408, 229),
        ("qq_full_s233", [POSE_F, COST, FACE], P_FULL, 1056, 1408, 233),
        ("qq_full_s239", [POSE_F, COST, FACE], P_FULL, 1056, 1408, 239),
        ("qq_full_s241", [POSE_F, COST, FACE], P_FULL, 1056, 1408, 241),
        ("qq_half_s251", [POSE_H, COST, FACE], P_HALF, 1104, 1216, 251),
        ("qq_half_s257", [POSE_H, COST, FACE], P_HALF, 1104, 1216, 257),
        ("qq_side_s263", [FACE, FRONT0], P_SIDE, 1024, 1536, 263),
        ("qq_side_s269", [FACE, FRONT0], P_SIDE, 1024, 1536, 269),
        ("qq_back_s263", [FACE, FRONT0], P_BACK, 1024, 1536, 263),
        ("qq_back_s269", [FACE, FRONT0], P_BACK, 1024, 1536, 269)]
COMFY_PID = int(subprocess.check_output("pgrep -f 'main.py --listen 0.0.0.0 --port 8188'", shell=True).split()[0])
def smi():
    tot = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]).split()[0])
    pr = 0
    for l in subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]).decode().splitlines():
        a = [x.strip() for x in l.split(",")]
        if len(a) == 2 and a[0].isdigit() and int(a[0]) == COMFY_PID: pr = int(a[1])
    return tot, pr
def md5(p): return subprocess.check_output(["md5sum", p]).decode().split()[0]
only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
recf = D + "_记录.json"
rec = json.load(open(recf, encoding="utf-8")) if os.path.exists(recf) else []
for tag, refs, p, w, h, sd in JOBS:
    if only and tag.split("_")[1] not in only: continue
    out = O + tag + ".png"
    if os.path.exists(out): print("SKIP", tag, flush=True); continue
    seedguard.check(refs, sd, tag)
    pk = [0, 0]; stop = [False]
    def mon():
        while not stop[0]:
            try:
                t, q = smi(); pk[0] = max(pk[0], t); pk[1] = max(pk[1], q)
            except Exception: pass
            time.sleep(0.5)
    th = threading.Thread(target=mon, daemon=True); th.start()
    t0 = time.time()
    try:
        qi21.run(p, out, refs, w, h, sd); ok = os.path.exists(out); err = ""
    except Exception as e:
        ok = False; err = repr(e)[:400]
    dt = time.time() - t0; stop[0] = True; th.join()
    r = dict(tag=tag, ok=ok, err=err, seed=sd, w=w, h=h, sec=round(dt, 1), card_peak_mib=pk[0], proc_peak_mib=pk[1],
             refs=[[os.path.basename(x), md5(x)] for x in refs], out=out, out_md5=md5(out) if ok else "", chars=len(p), prompt=p)
    rec.append(r); json.dump(rec, open(recf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE" if ok else "FAIL", tag, "%.1fs" % dt, "card %d proc %d MiB" % (pk[0], pk[1]), err, flush=True)
if not os.environ.get("NOFREE"):
    try: qi21.post("/free", {"unload_models": True, "free_memory": True})
    except Exception: pass
print("T0A_DONE", flush=True)
