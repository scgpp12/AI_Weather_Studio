# 第 4 轮：和 front_a 的人脸相似度＋脸框（insightface buffalo_l，CPU），供本地裁脸做联系表
import cv2, numpy as np, glob, os, json
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", root="/mnt/storage/ComfyUI/models/insightface", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640))
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"
def big(p):
    fs = app.get(cv2.imread(p)); return max(fs, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])) if fs else None
a = big(D + "refs/face_front_a.png").normed_embedding; res = {}
for p in sorted(glob.glob(D + "r4_*.png")) + sorted(glob.glob(D + "gpt4/g4_*.png")) + [D + "refs/face_front_a.png"]:
    f = big(p); b = os.path.basename(p)
    res[b] = dict(sim=None, bbox=None) if f is None else dict(sim=round(float(np.dot(a, f.normed_embedding)), 3), bbox=[int(x) for x in f.bbox])
    print(b, res[b], flush=True)
json.dump(res, open(D + "_facesim_r4.json", "w"), indent=1)
