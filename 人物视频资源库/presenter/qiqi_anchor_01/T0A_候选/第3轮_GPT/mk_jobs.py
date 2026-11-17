# -*- coding: utf-8 -*-
# 第 3 轮 GPT 出图的 job.json（喂 sons02 T/codex_train.py）。
# 本次做法＝GPT（Codex 订阅）整张出；原件＝T/codex_train.py（管线）＋ castsery/peiju/genSJ2.sh（七七定妆的提示词写法：ID 句、H 发型句、STU 棚拍句、全身 2:3 1024x1536、胸像 4:5 1024x1280）。
# 与原件不同之处：衣服换 AUT-0066（写明不要包）；参考图 4 张（front_a／AUT-0066／第1轮 s233／第2轮 r2_heart_P003_s313）；表情统一甜美微笑；加半身到腰和两个开场手势。
import json
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/gpt3"
REFS = "face_front_a.png,costume_AUT-0066.png,qq_full_s233.png,r2_heart_P003_s313.png"
NOTE = ("Image 1 is her face and the authority for who she is. Image 2 is the outfit. Image 3 shows how the outfit is worn on her. "
        "Image 4 shows her sweet smile.")
ID = ("The woman is exactly the same person as image 1: copy her face exactly — the same oval face, brows, large eyes, nose, lips "
      "and skin; do not change her features. Clean translucent makeup, straight natural brows, soft warm brown eye makeup, soft peach-coral lips. "
      "Same hair as image 1: dark hair loosely gathered high at the back of the head into a casual bun with loose pieces, centre part, "
      "two long strands of fringe hanging by the cheeks to the jaw.")
LOOK = ("She wears exactly the outfit in image 2, worn the way image 3 shows it: a mustard-yellow silky blouse with a long soft pussy-bow "
        "tied at the collar and puffed long sleeves gathered into buttoned cuffs, tucked into the shorts; a single-strand pearl necklace; "
        "olive-green wool shorts with wide turned-up cuffs; cream-white ribbed over-the-knee socks, each with a wine-red ribbon bow at the "
        "top band; brown suede platform ankle boots with chunky block heels. No bag: the small plaid chain bag in image 2 is not part of "
        "the outfit, her shoulders carry nothing.")
SMILE = ("Expression: a sweet smile like image 4 — the corners of her mouth turn up showing a little of her upper teeth, her eyes curve "
         "slightly, her brows are relaxed and smooth.")
STU = ("Plain flat seamless mid-grey studio background, one person only, soft even studio light. A real photograph of a real actress, real skin.")
full = dict(dir=D, prefix="g3_full", refs=REFS, size="portrait orientation 2:3 (1024x1536)", refnote=NOTE, id=ID + " " + LOOK, style=STU, shots=[
  dict(n="front", caption="正面全身", prompt="Natural relaxed standing pose facing the camera, weight even, arms hanging naturally at her sides with empty hands. " + SMILE + " Full body from the top of the head to the boots."),
  dict(n="side", caption="侧面全身", prompt="Side view: she stands in profile facing the right edge of the frame, arms relaxed, the face seen from the side with the same sweet smile. The bun and the fringe strands seen from the side. Full body from the top of the head to the boots."),
  dict(n="back", caption="背面全身", prompt="Back view: she stands with her back to the camera, arms relaxed. Back of the hair: the loose high bun with loose pieces. Back of the outfit: the mustard-yellow blouse across her back with its collar band round the back of the neck, the pearl necklace clasp at the nape, the puffed sleeves down to the buttoned cuffs, the olive-green shorts with turned-up cuffs, the cream-white over-the-knee socks with the wine-red bows, the brown suede platform ankle boots. Full body from the top of the head to the boots.")])
bust = dict(dir=D, prefix="g3_waist", refs=REFS, size="portrait orientation 4:5 (1024x1280)", refnote=NOTE, id=ID + " " + LOOK, style=STU, shots=[
  dict(n="half", caption="半身到腰", prompt="Waist-up shot: the frame shows her from the top of the head down to the waistband of the shorts and ends there; facing the camera, arms hanging relaxed at her sides. " + SMILE),
  dict(n="point_P022", caption="开场手势 手指镜头", prompt="Waist-up shot: the frame shows her from the top of the head down to the waistband of the shorts and ends there; facing the camera, a TV presenter greeting the audience: her right hand reaches toward the camera with the index finger pointing straight at the lens, her left arm relaxed. " + SMILE),
  dict(n="heart_P003", caption="开场手势 脸侧单手比心", prompt="Waist-up shot: the frame shows her from the top of the head down to the waistband of the shorts and ends there; facing the camera, a TV presenter greeting the audience: her right hand raised beside her cheek making a small finger heart with thumb and index finger crossed, her left hand resting on her hip. " + SMILE)])
for n, j in (("job_full.json", full), ("job_waist.json", bust)):
    json.dump(j, open(n, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
