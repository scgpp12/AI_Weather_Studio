# -*- coding: utf-8 -*-
# 七七 情绪表演 v2（总督导 11-17 转用户：「表情库……没有姿势，不自然，哭没有眼泪……重新做」）。12 种，脸＋手＋身体一起演，半身到腰，AUT-0066 无包，中性灰。
# Qwen：本次做法＝Qwen Image 2.1，qi21.py 固定参数 25 步 cfg 1。参考图最多 3 张（速查表），所以：
#   有相近人台的 5 种（惊讶 P015、惊喜 P016、哭 P020、生气 P041、害羞 P011）：Picture 1 人台＋Picture 2 g3_waist_half＋Picture 3 front_a（原件＝bjjpose/loop4.py 三图配方）；
#   其余 7 种：Picture 1 g3_waist_half 当底（景别、衣服照它）＋Picture 2 front_a（原件＝castsery/q21_sb8.py 两图写法，姿势照提示词改）。
#   与原件不同之处：正文中文；表演按 12 种写（只写看得见的，不写情绪名词）；第 1 轮 s233 不喂 Qwen（3 张上限）；尺寸 1104×1376；种子 337。
# GPT：传 "gpt" 时生成 3 个 job.json（各 4 张，并行跑），原件＝T/codex_train.py（用 codex_train_mb.py 副本：被拦即停）＋ peiju/genSJ2.sh 写法；参考图 front_a、s233、g3_waist_half。
import sys, os, time, json, subprocess, threading
CLOTH = ("芥末黄丝质衬衫，领口系着长长的蝴蝶结，泡泡长袖收进带扣的袖口，衬衫塞进短裤里；单圈珍珠项链；橄榄绿呢料高腰短裤")
FRAME = "画面从头顶拍到腰，裤腰在画面最下边。"
EMO = [
 ("01_kaixin", "开心", None, "嘴角轻轻上扬、嘴唇合着，头微微歪向一侧，右手掌心朝上摊在胸前，像在给观众介绍东西，左手自然垂在身侧。"),
 ("02_daxiao", "大笑", None, "笑得眼睛眯成两道弯，脸颊鼓起，右手手背朝外掩在嘴前，两边肩膀往前缩，上身微微前倾。"),
 ("03_jingya", "惊讶", "upper80v2_P015_front.png", "眼睛睁得很大，眉毛高高抬起，额头有几道横纹，双手手指并拢捂在嘴上，上身微微往后仰。"),
 ("04_jingxi", "惊喜", "upper80v2_P016_front.png", "嘴张开在笑，露出上排牙齿，眼睛发亮，双手在胸前合掌，肩膀轻轻耸起，身体轻快地往上一提。"),
 ("05_nanguo", "难过", None, "眼眶泛红，一行泪从左眼下沿滑到脸颊中间，泪痕发亮，嘴角往下撇，头低着、眼睛往下看，右手手背抬到右眼旁边轻轻擦泪。"),
 ("06_ku", "哭", "upper80v2_P020_front.png", "满脸是泪，两边脸颊湿亮，泪痕从眼角一直流到下巴，双手掌心捂住下半张脸，眼睛紧闭，眉头皱成一团，两边肩膀缩起。"),
 ("07_shengqi", "生气", "upper80v2_P041_front.png", "眉头紧皱、两道眉往中间压，嘴唇抿成一条线，双臂交叉抱在胸前，下巴微微抬起，眼睛直盯着镜头。"),
 ("08_danxin", "担心关切", None, "眉心微微皱起，眼睛关切地看着镜头，右手掌心按在胸口，上身往前倾。"),
 ("09_haixiu", "害羞", "upper80v2_P011_front.png", "两边脸颊泛着红晕，头低着、眼睛往上抬看着镜头，右手掌心挡住左半边脸，嘴角抿着一点笑。"),
 ("10_sikao", "思考", None, "眼睛往右上方看，右手食指轻点在下巴上，左手横在胸前托着右手肘，嘴唇微抿。"),
 ("11_bobao", "认真播报", None, "嘴角带一点浅浅的笑意，眼睛平和地看着镜头，双手交叠放在腹前，肩膀放平，站得端正。"),
 ("12_wunai", "无奈", None, "嘴角往一边撇，眉毛一高一低，两边肩膀耸起，双手手肘弯着、掌心朝上向两边摊开。"),
]
STU = "中性灰纯色棚拍背景，背景平整一体，画面里只有她一个人，柔和均匀的棚灯，写实真人照片，真实皮肤和真实布料质感。"
if len(sys.argv) > 1 and sys.argv[1] == "gpt":
    D = "/mnt/storage/model-lab/castsery/qiqi_anchor/emo2"
    ID = ("她就是 image 1 里的这个人：脸照 image 1 原样——同样的鹅蛋脸、眉毛、大眼睛、鼻子、嘴唇和皮肤，五官和 image 1 一模一样。"
          "干净通透的淡妆，自然平眉，暖棕色眼妆，柔和的蜜桃珊瑚色嘴唇。发型和 image 1 一样：深色头发在脑后高处松松挽成发髻，有几缕碎发，中分，两缕长刘海垂在脸颊两侧。"
          "她穿 image 2 里这身衣服：" + CLOTH + "。两边肩上空着。景别和 image 3 一样：" + FRAME)
    for i in range(3):
        sh = [dict(n=n, caption=zh, prompt="她正面朝镜头，用脸、手和身体一起表演：" + e) for n, zh, _, e in EMO[i * 4:(i + 1) * 4]]
        job = dict(dir=D, prefix="g", refs="face_front_a.png,qq_full_s233.png,g3_waist_half.png", size="portrait orientation 4:5 (1024x1280)",
                   refnote="image 1 是她的脸，认人以它为准。image 2 是她这身衣服。image 3 是这次要的景别（拍到腰）。", id=ID, style=STU, shots=sh)
        json.dump(job, open("job_emo%d.json" % i, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("jobs ok"); sys.exit(0)

sys.path.insert(0, "/mnt/storage/ai-drama-pipeline/tools"); import qi21
sys.path.insert(0, "/mnt/storage/model-lab/castsery"); import seedguard
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"; R = D + "refs/"; O = D + "emo2q/"; os.makedirs(O, exist_ok=True)
WAIST, FACE = D + "gpt3/g3_waist_half.png", R + "face_front_a.png"
SD = 337; W, H = 1104, 1376
def prompt(pose, e):
    if pose:
        return ("Picture 1 是一个线稿人台，照它的身体姿势和两只手的位置来摆。画的是 Picture 3 这个年轻东亚女人，脸和发型照 Picture 3，"
                "穿 Picture 2 里这身衣服：" + CLOTH + "。两边肩上空着。景别照 Picture 2：" + FRAME + "她正面朝镜头，用脸、手和身体一起表演：" + e + STU)
    return ("Picture 1 是这个人到腰的半身照，景别、衣服、发型、光线都照 Picture 1。Picture 2 是她的脸，脸照 Picture 2。"
            "她穿着同一身衣服：" + CLOTH + "。两边肩上空着。" + FRAME + "她正面朝镜头，换成这个姿势，用脸、手和身体一起表演：" + e + STU)
COMFY_PID = int(subprocess.check_output("pgrep -f 'main.py --listen 0.0.0.0 --port 8188'", shell=True).split()[0])
def smi():
    tot = int(subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]).split()[0]); pr = 0
    for l in subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]).decode().splitlines():
        a = [x.strip() for x in l.split(",")]
        if len(a) == 2 and a[0].isdigit() and int(a[0]) == COMFY_PID: pr = int(a[1])
    return tot, pr
def md5(p): return subprocess.check_output(["md5sum", p]).decode().split()[0]
recf = O + "_记录.json"; rec = json.load(open(recf, encoding="utf-8")) if os.path.exists(recf) else []
for n, zh, pose, e in EMO:
    tag = "q_%s_s%d" % (n, SD); out = O + tag + ".png"
    if os.path.exists(out): print("SKIP", tag, flush=True); continue
    refs = ([R + pose, WAIST, FACE] if pose else [WAIST, FACE]); p = prompt(pose, e)
    seedguard.check(refs, SD, tag)
    pk = [0, 0]; stop = [False]
    def mon():
        while not stop[0]:
            try:
                t, q = smi(); pk[0] = max(pk[0], t); pk[1] = max(pk[1], q)
            except Exception: pass
            time.sleep(0.5)
    th = threading.Thread(target=mon, daemon=True); th.start(); t0 = time.time()
    try:
        qi21.run(p, out, refs, W, H, SD); ok = os.path.exists(out); err = ""
    except Exception as ex:
        ok = False; err = repr(ex)[:400]
    dt = time.time() - t0; stop[0] = True; th.join()
    rec.append(dict(tag=tag, emo=zh, pose=pose, ok=ok, err=err, seed=SD, w=W, h=H, sec=round(dt, 1), card_peak_mib=pk[0], proc_peak_mib=pk[1],
                    refs=[[os.path.basename(x), md5(x)] for x in refs], out=out, out_md5=md5(out) if ok else "", chars=len(p), prompt=p))
    json.dump(rec, open(recf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE" if ok else "FAIL", tag, "%.1fs" % dt, "card %d proc %d MiB" % (pk[0], pk[1]), err, flush=True)
if not os.environ.get("NOFREE"):
    try: qi21.post("/free", {"unload_models": True, "free_memory": True})
    except Exception: pass
print("EMO_Q_DONE", flush=True)
