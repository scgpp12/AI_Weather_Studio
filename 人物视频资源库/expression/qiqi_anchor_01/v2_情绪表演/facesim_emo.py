# 情绪表演 v2：和 front_a 的人脸相似度（insightface buffalo_l，CPU）
import cv2, numpy as np, glob, os, json
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", root="/mnt/storage/ComfyUI/models/insightface", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640))
D = "/mnt/storage/model-lab/castsery/qiqi_anchor/"
def big(p):
    fs = app.get(cv2.imread(p)); return (max(fs, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])), len(fs)) if fs else (None, 0)
a = big(D + "refs/face_front_a.png")[0].normed_embedding; res = {}
for p in sorted(glob.glob(D + "emo2/g_*.png")) + sorted(glob.glob(D + "emo2q/q_*.png")):
    f, n = big(p); b = os.path.basename(p)
    res[b] = dict(sim=None if f is None else round(float(np.dot(a, f.normed_embedding)), 3), faces=n)
    print(b, res[b], flush=True)
json.dump(res, open(D + "_facesim_emo2.json", "w"), indent=1)
