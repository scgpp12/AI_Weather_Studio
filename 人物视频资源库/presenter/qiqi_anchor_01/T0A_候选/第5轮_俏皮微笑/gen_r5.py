# -*- coding: utf-8 -*-
# T0-A 第 5 轮 俏皮微笑（总督导 11-17 转用户「看可以加一点 微微露一点舌头，等等」）。由 gen_r4.py 复制，只换档位 E/F/G（写法照 人物视频资源库/expression/研究/03_给出图模型的写法.md）、种子只用 331、前缀 r5_/g5。
# 以下为第 4 轮原注释：T0-A 第 4 轮 微笑分档（总督导 11-17 转用户「表情有点太假了……关于微笑再多多做几个版本」；补充：提示词正文用中文，Picture/image 标记照旧英文，不写否定字）。
# Qwen 部分：本次做法＝Qwen Image 2.1 定妆分支两图（Picture 1 脸 front_a，Picture 2 第1轮选定 qq_full_s233），qi21.py 固定参数 25 步 cfg 1。
# 原件＝castsery/q21_sb8.py 的 HEAD（"Picture 1 is this person's face. Picture 2 is the same person …"）＋ STU 棚拍句。
# 与原件不同之处：正文改中文（用户 11-16 定）；景别改胸口近景（只为看脸）、正面朝镜头、表情按 4 档写；尺寸 1024×1280；
#   种子新开 317/331（每档同一对种子）；C 档另加一张英文版对照（种子 317，和中文那张一样）。
# 用 sys.argv[1] 传 "gpt" 时只生成 GPT 的 job.json（codex_train 用），不跑 Qwen。
import sys, os, time, json, subprocess, threading
TIERS = [
 ("E", "俏皮吐舌尖", "眉头内侧微微抬起，左眼微微眯起、下眼睑隆起，右眼睁着带笑，脸颊向上鼓起，嘴角轻轻上扬，左边比右边略高一点，嘴唇分开一条缝，舌尖从中间露出一点点，头向左歪约十度，肩膀微微缩起，右手握成松松的拳头轻轻贴在右侧太阳穴旁。"),
 ("F", "wink 微笑", "头向右歪约十度，右眼闭成一条弯弯的线，右侧脸颊向上鼓起，左眼睁着、下眼睑微微隆起，眼角挤出细小的笑纹，左眉略扬，嘴角向上弯起，右边嘴角比左边高一点，嘴唇轻轻分开，只露出上排两三颗牙，右手比 V 放在右眼旁边。"),
 ("G", "歪头抿嘴笑", "头向左歪约十五度，下巴微收，眼睛抬起直视镜头，下眼睑微微隆起，眼角挤出细小的笑纹，嘴唇抿在一起、嘴角向上翘，左边嘴角略高一点，右侧脸颊一个浅酒窝，两颊透出淡淡的粉色，右手指尖轻轻贴在右脸颊上。"),
]
C_EN = "As if she has just finished a sentence and is about to go on: her lips naturally slightly parted, the corners of her mouth turned up, the right corner a little higher than the left."
if len(sys.argv) > 1 and sys.argv[1] == "gpt":
    D = "/mnt/storage/model-lab/castsery/qiqi_anchor/gpt5"
    ID = ("她就是 image 1 里的这个人：脸照 image 1 原样——同样的鹅蛋脸、眉毛、大眼睛、鼻子、嘴唇和皮肤，五官和 image 1 一模一样。"
          "干净通透的淡妆，自然平眉，暖棕色眼妆，柔和的蜜桃珊瑚色嘴唇。"
          "发型和 image 1 一样：深色头发在脑后高处松松挽成一个随意的发髻，有几缕碎发，中分，两缕长刘海垂在脸颊两侧到下巴。"
          "她穿 image 2 里那件芥末黄丝质衬衫，领口系着长长的蝴蝶结，戴同一条单圈珍珠项链。")
    job = dict(dir=D, prefix="g5", refs="face_front_a.png,qq_full_s233.png", size="portrait orientation 4:5 (1024x1280)",
               refnote="image 1 是她的脸，认人以它为准。image 2 是她这身衣服。", id=ID,
               style="中性灰纯色棚拍背景，背景平整一体，画面里只有她一个人，柔和均匀的棚灯。真实女演员的真实照片，真实皮肤质感。",
               shots=[dict(n=k, caption=zh, prompt="胸口以上的近景，从头顶到胸口，正面朝镜头，看着镜头。表情：" + e) for k, zh, e in TIERS])
    json.dump(job, open("job_g5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("job ok"); sys.exit(0)

sys.path.insert(0, "/mnt/storage/ai-drama-pipeline/tools"); import qi21
sys.path.insert(0, "/mnt/storage/model-lab/castsery"); import seedguard
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"
REFS = [D + "refs/face_front_a.png", D + "qq_full_s233.png"]
HEAD_ZH = "Picture 1 是这个人的脸。Picture 2 是同一个人穿着全套衣服正面站着。同一个人，同一张脸，同样的身材。"
FRAME_ZH = ("胸口以上的近景：她正面朝镜头、看着镜头，画面从头顶到胸口，穿着和 Picture 2 一样的芥末黄丝质衬衫，领口系着长长的蝴蝶结，"
            "戴着同一条珍珠项链，深色头发和 Picture 1 一样松松挽成发髻、有几缕碎发。表情：")
STU_ZH = "中性灰纯色棚拍背景，背景平整一体，画面里只有她一个人，柔和均匀的棚灯，写实真人肖像照片，真实皮肤和真实布料质感。"
HEAD_EN = ("Picture 1 is this person's face. Picture 2 is the same person standing facing the camera in full costume. "
           "Same person, same face, same build. ")
FRAME_EN = ("Chest-up portrait: she faces the camera and looks into the lens, framed from the top of the head down to the chest, wearing "
            "the same mustard-yellow silky blouse with the long pussy-bow at the collar and the same pearl necklace as picture 2, "
            "her dark hair tied up in the same loose bun with loose pieces as picture 1. Expression: ")
STU_EN = ("Plain flat seamless mid-grey studio background, one person only, soft even studio light, photorealistic "
          "live-action portrait photo, real skin and real fabric.")
JOBS = []
for k, zh, e in TIERS:
    for sd in (331,):
        JOBS.append(("r5_%s_s%d" % (k, sd), HEAD_ZH + FRAME_ZH + e + STU_ZH, sd))
COMFY_PID = int(subprocess.check_output("pgrep -f 'main.py --listen 0.0.0.0 --port 8188'", shell=True).split()[0])
def smi():
    tot = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]).split()[0]); pr = 0
    for l in subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]).decode().splitlines():
        a = [x.strip() for x in l.split(",")]
        if len(a) == 2 and a[0].isdigit() and int(a[0]) == COMFY_PID: pr = int(a[1])
    return tot, pr
def md5(p): return subprocess.check_output(["md5sum", p]).decode().split()[0]
recf = D + "_记录.json"; rec = json.load(open(recf, encoding="utf-8")) if os.path.exists(recf) else []
for tag, p, sd in JOBS:
    out = D + tag + ".png"
    if os.path.exists(out): print("SKIP", tag, flush=True); continue
    seedguard.check(REFS, sd, tag)
    pk = [0, 0]; stop = [False]
    def mon():
        while not stop[0]:
            try:
                t, q = smi(); pk[0] = max(pk[0], t); pk[1] = max(pk[1], q)
            except Exception: pass
            time.sleep(0.5)
    th = threading.Thread(target=mon, daemon=True); th.start(); t0 = time.time()
    try:
        qi21.run(p, out, REFS, 1024, 1280, sd); ok = os.path.exists(out); err = ""
    except Exception as ex:
        ok = False; err = repr(ex)[:400]
    dt = time.time() - t0; stop[0] = True; th.join()
    rec.append(dict(tag=tag, ok=ok, err=err, seed=sd, w=1024, h=1280, sec=round(dt, 1), card_peak_mib=pk[0], proc_peak_mib=pk[1],
                    refs=[[os.path.basename(x), md5(x)] for x in REFS], out=out, out_md5=md5(out) if ok else "", chars=len(p), prompt=p))
    json.dump(rec, open(recf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE" if ok else "FAIL", tag, "%.1fs" % dt, "card %d proc %d MiB" % (pk[0], pk[1]), err, flush=True)
if not os.environ.get("NOFREE"):
    try: qi21.post("/free", {"unload_models": True, "free_memory": True})
    except Exception: pass
print("R5_DONE", flush=True)
