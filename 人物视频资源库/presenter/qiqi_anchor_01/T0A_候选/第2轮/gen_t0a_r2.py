# -*- coding: utf-8 -*-
# T0-A 第 2 轮（总督导 11-17 转用户意见：表情要甜美的微笑；半身重出；上半身可爱系挑 2 个开场打招呼动作试验）。
# 本次做法＝Qwen Image 2.1 三图配方（人台＋服装＋脸），qi21.py 固定参数 25 步 cfg 1。
# 原件＝第 1 轮 gen_t0a.py 的 front_prompt（它的原件是 bjjpose/loop4.py）。
# 与原件不同之处：
#  ① 表情句「Give her a natural facial expression…」换成甜美微笑的可见写法（嘴角上扬、露一点上排牙、眼睛微弯、眉头舒展）。
#  ② 半身加景别句「镜头只拍到腰，腰以下在画面外」（总督导给的写法），人台仍是裁到腰的 pose_P017_half.png。
#  ③ 打招呼两张：人台换 upper80v2_P022_front（手指镜头）、upper80v2_P003_front（脸侧手指比心）；
#     手的句子改成各自的动作，保留「左肩上什么都没背」；也加同一句景别句。
#  ④ 种子新开 281/283/293/307/311/313。
import sys, os, time, json, subprocess, threading
sys.path.insert(0, "/mnt/storage/ai-drama-pipeline/tools"); import qi21
sys.path.insert(0, "/mnt/storage/model-lab/castsery"); import seedguard
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"; R = D + "refs/"
COST, FACE = R + "costume_AUT-0066.png", R + "face_front_a.png"
OUTFIT = ("a mustard-yellow silky blouse with a long soft pussy-bow tied at the collar and puffed long sleeves gathered into "
          "buttoned cuffs, the blouse tucked into the shorts; a single-strand pearl necklace at the collar; olive-green wool "
          "shorts with wide turned-up cuffs at the hem; cream-white ribbed over-the-knee socks, each with a wine-red ribbon bow "
          "at the top band; brown suede platform ankle boots with chunky block heels")
NOBAG = "Nothing is carried on her left shoulder."
HAND_DOWN = NOBAG + " Both hands are empty and hang naturally at her sides."
SMILE = ("Her expression is a sweet smile: the corners of her mouth turn up, showing a little of her upper teeth, her eyes "
         "curve slightly, and her brows are relaxed and smooth.")
WAIST = "The camera frames her only down to the waist; everything below the waist is outside the frame."
def P(hands, pose, extra=""):
    return ("Picture 1 is a faceless mannequin showing the exact body pose and framing to copy. Draw the young East Asian woman "
            "with the face and dark hair of Picture 3, preserving Picture 3's facial width, eye shape and spacing, nose proportions, "
            "and full lip shape, wearing the outfit in Picture 2 exactly: " + OUTFIT + ". " + hands + " "
            "Pose name (Chinese): " + pose + ". " + extra + SMILE + " "
            "Photorealistic game-CG style, soft studio light, plain grey background, one person only, no text.")
P_FULL = P(HAND_DOWN, "站立・两手自然垂在身侧（站姿）, her head and body facing the camera")
P_HALF = P(HAND_DOWN, "半身・两手自然垂在身侧（站姿）, her head and body facing the camera", WAIST + " ")
P_POINT = P(NOBAG + " Her right hand reaches forward towards the camera with the index finger pointing straight at the lens; "
            "her left arm hangs relaxed.", "手指镜头（可爱系）, her head and body facing the camera", WAIST + " ")
P_HEART = P(NOBAG + " Her right hand is raised beside her cheek making a small finger heart, thumb and index finger crossed; "
            "her left hand rests on her hip.", "脸侧手指比心（可爱系）, her head and body facing the camera", WAIST + " ")
O = D
JOBS = [("r2_full_s281", [R + "pose_P017_front.png", COST, FACE], P_FULL, 1056, 1408, 281),
        ("r2_full_s283", [R + "pose_P017_front.png", COST, FACE], P_FULL, 1056, 1408, 283),
        ("r2_half_s293", [R + "pose_P017_half.png", COST, FACE], P_HALF, 1104, 1216, 293),
        ("r2_half_s307", [R + "pose_P017_half.png", COST, FACE], P_HALF, 1104, 1216, 307),
        ("r2_point_P022_s311", [R + "pose_upper_P022.png", COST, FACE], P_POINT, 1056, 1408, 311),
        ("r2_heart_P003_s313", [R + "pose_upper_P003.png", COST, FACE], P_HEART, 1056, 1408, 313)]
COMFY_PID = int(subprocess.check_output("pgrep -f 'main.py --listen 0.0.0.0 --port 8188'", shell=True).split()[0])
def smi():
    tot = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]).split()[0])
    pr = 0
    for l in subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]).decode().splitlines():
        a = [x.strip() for x in l.split(",")]
        if len(a) == 2 and a[0].isdigit() and int(a[0]) == COMFY_PID: pr = int(a[1])
    return tot, pr
def md5(p): return subprocess.check_output(["md5sum", p]).decode().split()[0]
recf = D + "_记录.json"
rec = json.load(open(recf, encoding="utf-8")) if os.path.exists(recf) else []
for tag, refs, p, w, h, sd in JOBS:
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
print("T0A_R2_DONE", flush=True)
