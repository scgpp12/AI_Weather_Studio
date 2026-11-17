# A 本机资产调查（AI Weather Studio · Phase 0）

调查日期：2026-11-17。只读：没改文件、没装东西、没起服务、没访问网页、没 ssh 到 sons02。
标记：**【已验证】** 附路径或证据；**【待验证】** 本机看不到、要上 sons02 或实跑才能确认；**【风险】** 复用时会出问题的地方；**【需用户确认】** 要用户拍板。
根目录简写：`本\` = `C:\Users\sons\Downloads\ClaudeUsers\`。

## 0. 一句话结论

- 现在的系统是**一堆目录、md、按需写的 Python/shell 脚本**，不是一个统一仓库。唯一带数据库和结构化模型的是**幕布平台**（FastAPI + SQLite + React 19）。
- 角色、服装、姿势都有现成库，但**没有统一 ID 体系**，也**没有 presenter_id / outfit_id / voice_id 这种绑定**。角色和服装的关系写在 md 文字和各角色 `定版.json` 的「依据」字段里。
- 姿势库全是**静态图**（线稿人台或真人图），**没有 OpenPose/DWPose 关键点 JSON**。现成库里**没有「主播式指向地图」这类姿势**，只有近似的几个。
- 所有声音资产都是**中文**（普通话和方言），**没找到任何日语音色或日语实测**。
- 天气、地图相关**什么都没有**。Remotion 只有 drama-skills 里一份没装过依赖的字幕叠层源码。

---

## 1. 角色系统

### 1.1 存储方式（三套并存，没有统一）

| 套 | 位置 | 形式 | 状态 |
|---|---|---|---|
| ① 早期 Wan 时代 | `本\characters\沈霜\appearance.md` | md + YAML 头（`name/role/status/verified_from/verified_at`），正文是造型规格表 | 【已验证】只有沈霜一个人；`tools\h3_prompt.py` 会读 `characters/<名>/appearance.md` |
| ② 蚩尤片角色定妆 | `本\审美\定妆\<角色>\定版.json` + `套图\` | 每人一个 JSON，见下方样例；约 37 个角色目录，`定版.json` 至少 20 个 | 【已验证】 |
| ③ 新剧《集魂》 | `本\审美\新剧定妆\集魂_定版清单.md`（311 行，人读）＋ `集魂_定版登记表_1115.json`（机读，351 条） | md 表格带 md5；登记表是唯一准绳 | 【已验证】 |
| 定妆规格（文字） | `本\传奇知识\定妆规格\<角色>.md` | 每条带出处的造型规格 | 【已验证】 |
| 人物卡（剧本用） | `本\传奇剧本\新故事_集魂\小说试写\人物卡_v2_1114.md`、`本\GPT研究\传奇连续剧_从新手开始\人物卡_全.md` | md，性格、状态、关系 | 【已验证】文件在；不含图片引用和声音 ID |
| 旧项目 | `本\new_char\`（滨江、残碑、苏芷等）、`本\试镜\` | 散图、联系表、mp4，没有清单 | 【已验证】资产总表 267 行写明「只作方法参考」 |

**样例 A：`本\审美\定妆\白晶晶\定版.json`（节选，真实内容）**
```json
{"角色": "白晶晶", "期": "期3 圣战宝甲（墨绿金）",
 "依据": "传奇知识\\定妆规格\\白晶晶_装扮拆件_v8.md（md5 08a078b4）；服装设定_圣战宝甲\\圣战宝甲_三视图.png（610724b5，用户 11-07 确认）…",
 "定版": {"01": {"镜头": "正面全身", "文件": "套图/baijingjing_01_front_full_v2.png"},
          "02": {"镜头": "侧面全身", ...}, "03": 背面全身, "04": 四分之三侧,
          "05": 正面胸像, "06": 侧面胸像, "07": 笑, "08": 怒, "09": 痛苦, "10": 战斗, "11": 空手全身}}
```
- 固定 11 张套图（正/侧/背/3/4 全身、正/侧胸像、4 种表情、空手）。这个结构**最接近 reference_images**。【已验证】
- 字段是中文键，没有 `id`，没有服装 ID、声音 ID。服装只在「依据」里以文字和 md5 出现。【已验证】

**样例 B：`集魂_定版登记表_1115.json` 一条**
```json
{"name": "沈烬", "ver": "前期（正面胸像）", "use": "脸/正面胸像",
 "path": "审美\\新剧定妆\\集魂_沈烬\\定版_用户脸\\front_a.png", "md5": "62824f0a…",
 "mtime": "2026-11-13 19:05", "status": "用户定",
 "source": "用户 11-13：「沈烬和陆青的脸用他给的豆包图」…", "replaces": "新脸定妆\\ 那一批", "group": "一、人物"}
```
- 分组统计：人物 10 名、怪物 118 名、武器道具 5、服装与随身 10、场景 2。状态里「未收货（未审）」189 条、「用户定」62 条。【已验证，脚本统计】

### 1.2 LoRA
- Ideogram4 出图 LoRA：小虾米（`loras/xiaxiami_ideogram4_r32_2000.safetensors`，触发词 xxm1n9）、白晶晶。数据集 `本\LoRA候选\`。【已验证：资产总表 128、144 行；LoRA 文件本身在 sons02，本机没核】
- 定论：H3 视频锁脸走参考图（ref2va 0.755）不走 LoRA（0.475）。【已验证：资产总表 127 行、记忆 new-character-pipeline】
- 【风险】Ideogram4 在第二批清理候选里，LoRA 依赖它。

### 1.3 幕布平台里的角色（最接近结构化数据）
- 表 `character`（name, role_type, description）＋ `character_version`（label, description, costume, weapon, **face/front/side/back_asset_id**, is_current）＋ `asset_link`（role＝神态/设定图…）。【已验证：`本\幕布平台\backend\app\db.py` 第 31–37 行】
- 这就是 presenter + reference_images 的雏形；**没有 voice 字段、没有 outfit 表**（服装是 `costume` 一个文本字段）。【已验证】
- 本机库只有开发/测试副本：`data\mubu.db` 20 个角色、`data_release\mubu.db` 18 个、`data_synctest*\mubu.db` 18 个，都是《集魂》。【已验证，只读打开统计】
- 「130 个人物卡」**本机没找到**这个数字。生产库在 sons02 `/mnt/storage/mubu/data/mubu.db`，没读。推测是 `sync_jihun.py` 把登记表里的人物 10 + 怪物 118 一起同步成卡片，合起来约 130，但这只是推测。【待验证】

### 1.4 对天气主播的意义
- 可复用的是**做法**：11 张套图结构、登记表（路径+md5+状态+出处）、幕布的 character_version 表。
- 现有角色全是古装/传奇游戏造型，**没有现代主播形象**。【已验证：目录名和定版清单】要新建主播角色。【需用户确认：主播是新做，还是借某个已定的脸（如选角库 portrait-gallery）】

---

## 2. 服装库

### 2.1 comfyui-costume-gallery（第三方，1407 套）
- 位置 `本\参考图库\comfyui-costume-gallery\`，是 ComfyUI 自定义节点包（`__init__.py`、`catalog.py`、`web\`），素材来自 GitHub `wangweihong/ai-costume-gallery-zh` 提交 28616efb，快照 2026-10-29。【已验证：`library\SOURCE.json`】
- 数据：`library\data\costume-zh.json`（1407 条）、`costume.json`（日文键原版）、`meta-zh.json`、`local-assets.json`（4221 张图）、`translations.csv`。**纯 JSON，没有 sqlite/csv 主表**。【已验证】
- ID 格式：`SPR-0001`（春）/`SUM-`/`AUT-`/`WIN-`…，分类 8 个：夏装 254、冬装 253、秋装 244、春装 215、内衣 199、性感 140、泳装 54、派对 48。【已验证，脚本统计】
- 真实记录：
```json
{"id": "SPR-0001", "分类": "春装", "关键词": ["象牙白","荷叶边","针织","牛仔布","迷你","半身裙","大衣","短袜","白色","运动鞋"],
 "英文关键词": "ivory frill knit denim mini skirt coat socks white sneakers",
 "缩略图": "thumbs/SPR-0001.webp", "预览图": "img/SPR-0001.webp", "原图": "png/SPR-0001.png", "检索": "…"}
```
- **没有多角度**：每套只有一张正面「隐形人台」全身图（thumbs/img/png 是同一张的三种尺寸）。看过 `png\SPR-0003.png`，1366×2048，无头正面。【已验证】
- 没有和角色的绑定字段。自定义上传存在 ComfyUI `user/costume_gallery/data/custom.json`，ID 为 `u-`+UUID（README 所述）。【已验证 README；sons02 上有没有装这个节点包【待验证】】
- 关键词里含「西装/衬衫/职业/通勤/套装」的约 201 条，可能有适合主播的通勤装。【已验证是关键词命中数；适不适合主播没看图，【待验证】】
- 示例工作流 `example_workflows\01_QwenImage2.1_换脸换装与姿态编辑_两阶段.api.json` 等，可直接参考换装做法。【已验证文件在；没实跑】
- `本\参考图库\ai-costume-gallery-zh\` 是同一素材的静态网页版。【已验证】

### 2.2 自建服装库
| 库 | 位置 | 形式 | 多角度 |
|---|---|---|---|
| 传奇衣服高清 | `本\参考图库\传奇衣服高清\`（998 文件） | `v2\NN_3view.png`（三视图）、`NN_attack.png`、`NN_attackseq.png`；生成任务记在 `v2\_q\*.json`（字段 n/refs/w/h/seed/prompt） | 有，三视图拼在一张 |
| 女主衣服库 | `本\参考图库\女主衣服库\`（标题「沈烬的衣服（空间行囊）」） | `img\a_front.png / a_side.png / a_back.png / a_detail.png`… 按套编号 a、b… | 有，正侧背+细节 |
| 角色服装设定 | `本\审美\定妆\白晶晶\服装设定_圣战宝甲\` 等 | 三视图 png | 有 |
| 集魂服装 | 登记表 group「三、服装与随身」10 名 | 路径+md5 | 视条目 |

- 都是**文件夹 + 文件名约定**，没有 schema、没有服装 ID 体系。【已验证】
- 角色↔服装绑定只在：`定版.json` 的「依据」文字、`集魂_定版清单.md` 的文字描述、幕布 `character_version.costume` 文本。【已验证】
- 【风险】全部是古装/传奇装，不能直接给现代天气主播用。

---

## 3. 姿势库

| 库 | 位置 | 数量 | 格式 | 关键点 | 多视角 |
|---|---|---|---|---|---|
| comfyui-pose-gallery | `本\参考图库\comfyui-pose-gallery\library\` | 1439 条（288 个姿势×5 角度，少 1 张） | **线稿无脸人台 PNG**，900×1200 | 无 | 有：正面/侧面/斜侧/俯视/仰视 |
| ai-pose-gallery-zh | `本\参考图库\ai-pose-gallery-zh\` | 同上素材的网页版 + `姿势运用指南.md` | 同上 | 无 | 同上 |
| 传奇攻击姿势库 | `本\参考图库\传奇攻击姿势库\` | `data\pose-zh.json` 301 条（战士120/法师61/道士60/通用60）；`连续动作\57招视频\Gxxx\*_60fps.mp4` 198 个 mp4；`*_seq_f/m.png` 序列拼图 | 人台图 + 视频 + 序列图 | 无 | 有角度字段 |
| 白晶晶姿势库 | `本\参考图库\白晶晶姿势库\` | 292 张 jpg + `res\*_res.json`（269 个）+ `动起来\` 8 个 mp4 | 真人生成图；res 记 prompt 和打分 | 无 | 按人台角度 |
| 陆青姿势库 | `本\参考图库\陆青姿势库\` | 20 png | 真人定版图 | 无 | 单角度 |
| 姿势参考库（持武器） | `本\参考图库\姿势参考库\单手剑\` | 35 png | 真人图 | 无 | — |

**真实记录（comfyui-pose-gallery `pose-zh.json`）**
```json
{"id": "full_sexy_P001_front", "体系": "全身单人・性感系", "姿势编号": "P001", "分类": "站姿",
 "姿势名称": "S形站姿・胯部侧顶", "角度": "正面", "缩略图": "thumbs/full_sexy_P001_front.jpg", "原图": "img/full_sexy_P001_front.png", "检索": "…"}
```
体系：上半身单人 400、全身单人・性感系 399、全身单人・标准系 365、双人缠绵 275。【已验证】

**白晶晶 res JSON 字段**：`n, name, sys, scores[3], best, prompt`（prompt 写「Image 1 is a faceless mannequin…Image 2 outfit…Image 3 face」）。【已验证：`res\full_sexy_P001_res.json`】这就是「人台 + 服装 + 脸」三图合成的现成配方。

**有没有指向/抬手/转身**（grep 姿势名称）：【已验证】
- 指向类：上半身 P022「手指镜头」、P018「手指取景框」；**陆青 `lq_pose_04_pointway.png`「指路」**（真人、古装、持木剑）。
- 转身/回头类：全身标准系 P066「蹲姿・回头」；陆青 `lq_pose_10_walklookback.png`「走路回头」；白晶晶 P017「回眸」（资产总表 11 行）。
- 「抬手」「转身」「介绍」「展示」：**0 命中**。
- 结论：**没有站姿侧身、单臂伸直指向身旁地图的主播姿势**，要新做。【已验证】

**关键点数据**：库里**没有**任何 OpenPose/DWPose JSON。【已验证】sons02 上 ComfyUI 装了 `comfyui_controlnet_aux`，带 DWPose（yolox_l + dw-ll_ucoco_384，**含手部关键点**）和 OpenPose 模型；攻击研究用它写过逐帧评测 `本\攻击研究\solo_slash\eval\pose_eval.py`。【已验证文档：`本\攻击研究\environment_report.md` 66–67 行；sons02 实物【待验证】】
- 另有 `本\攻击研究\mixamo_motion_lab\`（Mixamo/Blender 动作 → 视频驱动实验，27 json、12 mp4）和 Wan Animate 2 课题，可做「转身+指向」动作驱动的参考。【已验证目录；效果见其 reports，本次没评】
- 【风险】速查表 696 行起：H3 里**姿势和景别跟参考图走，提示词改不动**（4 对 1 实证）。指向动作必须靠参考图/关键帧给出，不能只写提示词。

---

## 4. 网页系统

| | 幕布平台 | 8765 参考图库 | Lazy Studio |
|---|---|---|---|
| 跑在 | sons02 :8100（按方案；本机开发 8101） | 本机 127.0.0.1:8765 | sons02 :8787（原版）/ :8788（自写备份） |
| 代码在本机 | 有：`本\幕布平台\` | 只有静态页 + `_make.py` 生成器 | **没有**（只有截图 `本\学习笔记\lazy_studio\`） |
| 技术栈 | 后端 FastAPI + uvicorn + SQLite（WAL）+ Pillow，标准库 http；前端 React 19 + TS + Vite 8 + Tailwind 4 + marked | python http.server（记忆 no-second-8765-server），根目录 `参考图库\`，各库 `index.html` 由 `_make.py` 生成 | 上游 feicaiclub/ad-storyboarder（MIT）的 `studio.py + studio.html`，加我们的 `adapter.py` |
| 数据 | SQLite 19 张表 + review 3 张表；素材复制进 `data\assets\`，记原路径和 md5 | 各库 json（pose-zh.json 等）+ 图片文件 | 读 sons02 各集 segs/*.json、timeline.json、final/；反馈写 `反馈/待处理.md` |
| 证据 | `backend\app\db.py`、`main.py`（约 50 个接口）、`frontend\package.json` | `参考图库\index.html` 列 17 个子库 | 记忆 lazy-studio-review-tool、`总督导看板.md` 57 行 |

**幕布平台页面**（`frontend\src\pages\`）：ScriptPage 剧本、LibraryPage 设定（角色/场景/道具）、StoryboardPage 分镜、FilmPage 短片（播放器+时间轴，`PX_PER_SEC=22`，拖动排序、整集连播、导出）、CutPage 粗剪看片（按秒留意见）、ReviewPage「待你确认」（声线/配乐候选、台词意见）、LorePage 传奇库入口。【已验证】
- 分镜编辑：有（shot 表含 duration/shot_size/camera_move/action/sound/prompt/method，shot_dialogue 一句一行带 start_time）。【已验证】
- 时间轴：有（FilmPage）。【已验证】
- 任务管理：有 `generation_job`（排队/运行/完成/失败/中断、progress、snapshot_json）和 `generation_version`（种子、模型、工作流 JSON、提示词快照）。【已验证】
- **但真出片没接**：`jobs.py` 里只有 `mock` 可用；`d_ref2va_prism`、`d_ref2va_prism_1080` 都 `enabled: False`，注释「阶段 3 接入，只连测试实例 :8191」。【已验证】
- 素材管理：asset + asset_link，按 md5 去重；本机同步脚本 `sync\sync_jihun.py`（经 HTTP 接口推到 sons02:8100，计划任务每 3 分钟）。【已验证】
- 【风险】没有登录（方案写「只局域网用」，后来加了 `auth.py` 共享口令，具体启用状态【待验证】）；sons02 有公网 IPv6 未永久封。
- 【需用户确认】天气模块是做成幕布平台里的一个新项目/新页面，还是独立做一个 Web。

**8765**：纯静态浏览，不能编辑、没有任务。comfyui-pose/costume/portrait/hairstyle 四个是 **ComfyUI 节点包**，它们装没装进 sons02 的 ComfyUI【待验证】。portrait-gallery 有 1499 张脸（`portrait-zh.json`，ID 如 `f71f980dde3`，字段 section/hair/w/h/full/thumb），选角用。【已验证】

---

## 5. 任务队列 / 生成脚本

- **没有统一的任务队列**。架构文档明确「SQLite 状态表、调度器现在不做」。【已验证：`本\架构与要件.md` 6.4 节】
- 现状是各频道各写脚本直接打 ComfyUI API：
  - 本机 `本\scripts\gen_video.py`：`import comfy_client as cc` → `cc.load_workflow` 改节点 → `cc.submit_and_wait`。**`comfy_client.py` 本机没找到**，脚本是 9 月 Wan→H3 迁移期的，现在不是主力。【已验证缺文件】
  - 主力管线全在 sons02：`/mnt/storage/ai-drama-pipeline/tools/`（reroll.py、run_ep.py、make_subs2.py、qi21.py、codex_train.py…）、`/mnt/storage/model-lab/castsery/*.py`（一场戏一个脚本，提示词写死）。**本机没有副本，没读到**。【待验证】
  - 「重试」：reroll.py 有 `--cands N`（凑够 N 个过关候选）和「同一句同一原因连续 3 个种子不过就停」。【已验证：`总督导看板.md` 51 行的描述；代码本身【待验证】】
  - 状态持久化：靠文件（qc/*.json、timeline.json、sidecar `.meta.json`，`本\tools\sidecar.py`）。【已验证 sidecar 代码】
  - GPU 互斥：`本\tools\gpu_lease.sh`（flock 租约，等够 N GB 空闲再跑）；sons02 `launch.sh / wait_pid.sh / wait_queue.sh / gap_run.sh`（按 PID 管）。【gpu_lease 已验证；sons02 脚本【待验证】】
- 唯一像样的队列：**幕布平台 `jobs.py`**——一个后台线程 + `queue.Queue`，一次只跑一个，状态写库，重启后「运行中」标「中断」不自动重跑；**没有自动重试**。【已验证】
- 工作流模板：本机 `本\workflows\h3_fl2va.json / h3_fl2va_lipsync.json / h3_ref2va.json / h3_t2va.json`（旧副本）；现行 `h3_ref2va_prism.json` 在 sons02。【已验证本机文件；sons02 版【待验证】】
- `本\总督导工具\` 只有 gemini_screen.py（已停用）、开工检查.py，不是生成工具。【已验证】
- 【风险】幕布接 ComfyUI 的方案默认只连测试实例 :8191、硬拦 8188；而 :8191 是模型学习频道的测试实例，可能被重启。

---

## 6. TTS / 声音资产

- 现行定版（全部中文）：【已验证：资产总表 50–52 行、速查表 H/I 节】
  - 对白：Drama 3，sons02 :8102，int4，约 43GB 显存。
  - 旁白/克隆：IndexTTS-2.5，sons02 `/mnt/storage/tts/index-tts-v25`，调用 `IndexTTS2(cfg_path, model_dir, use_bf16=True).infer(spk_audio_prompt=参考, text=台词, lang="ZH", output_path=…)`，后期 atempo 1.18；参考声先走 MSST 三步干声。
  - 方言：SoulX-Podcast-1.7B-dialect（四川、粤语）、VoxCPM2（东北），原件 `run_dialect.py`。
  - H3 直出声音（参考声 + 语言标签如 `[Sichuanese Chinese]`）。
- 声优库：`本\试音\v4_定版\` 33 个 mp3 + `_cast_v4.json`（31 角色，字段 `name, gender, dialect, description, note, seed_text, seed_wav, file, source, drift`）——这是**最接近 voice_id 的结构**，以角色名为键。【已验证】
- 本机调用脚本：`本\tools\tts_shots.py`（IndexTTS-2 按分镜配音，`voices/<角色>.wav`）是早期版；`本\声音\tools\` 有 bgm_level、audio_qc、line_cer 等后期工具。【已验证】
- **日语**：`声音\` 下 grep「日语/Japanese/日本語」0 命中；`试音\` 也没有日语样本。**没有任何日语音色、日语实测**。【已验证】
  - 只有 `本\方言TTS选型调研.md` 24 行转述「IndexTTS-2 官方 README 语言含日语」——这条是旧调研的转述，IndexTTS-2.5 实际支持不支持日语、`lang` 参数有没有 JA，**没验证**。【待验证】
  - Drama 3、VoxCPM2、H3 直出能不能说日语：本机没有记录。【待验证】
  - `本\模型学习\HF新模型日报.md` 494 行记了一个日语 TTS「Nichijou_TTS」（11-15），只是日报条目，没试。【已验证条目存在】
- 【风险】Drama 3 和 H3 抢卡（43GB）；记忆规矩「IndexTTS 会念出破折号」「H3 声音描述短句会被念出来」同样适用。
- 【需用户确认】日语播报用哪条路（H3 直出 / 新找日语 TTS / IndexTTS-2.5 试日语），以及中文播报沿用 Drama 3 还是 IndexTTS-2.5。

---

## 7. 天气 / 地图 / Remotion / React 视频合成

- 天气数据、气象 API、地图（MapLibre/Leaflet/Mapbox/GeoJSON）：**全盘没找到**。grep 到的「weather」都是场景提示词里的天气描写。【已验证】
- 「地图」只有游戏地图：`本\传奇知识\场景库\`、`传奇原图库`、地图推进脚本 `mapzoom.py/zoomscan.py`（`传奇知识\动画样片\`）。和真实地理无关。【已验证资产总表 214 行】
- Remotion：`本\drama-skills试跑\.agents\skills\short-drama-edit\assets\remotion\`——Remotion 4.0.418 + React 19 的**字幕/画面文字透明叠层**（Overlay.tsx、Subtitles.tsx、screen\*.tsx），由 `scripts\edit_tool.py render --subtitles remotion` 调用，渲染成 VP8+alpha 再用 ffmpeg 合成。【已验证源码】
  - 工作区 `~\.cache\short-drama-edit\remotion` **不存在**，说明本机**从没 npm install、没跑过**。【已验证】
  - 【风险】Remotion 有自己的商用许可证（README 提醒要核），【需用户确认】是否接受。
- React：幕布平台前端是 React 19 + Vite，可当 Web 编辑器底子。【已验证】
- 合成：幕布 FilmPage/export_job 方案用 ffmpeg 逐镜重编码 + concat 滤镜 + `aresample=async=1`（记忆 concat-copy-audio-drift）。【已验证方案文字；导出实测【待验证】】
- 任务一览 542–545 行已记本任务：用户 11-17 定「目的先走甲＝测 H3 能力，天气只当题材」「指向城市用『地图对准指尖』反向做法」。【已验证】

---

## 8. 可复用清单（按把握排序）

| 可复用 | 用在天气模块哪里 | 标记 |
|---|---|---|
| 幕布平台的库表、jobs 线程、FilmPage 时间轴、asset md5 去重 | Web 编辑、任务状态、素材管理 | 已验证（代码在）；真出片未接 |
| 定版.json 的 11 张套图结构 + 登记表字段 | 主播 reference_images 规范 | 已验证 |
| 白晶晶 res 的「人台+服装+脸」三图提示词配方 | 出主播各姿势定妆 | 已验证配方；现代装效果待验证 |
| pose-gallery 5 角度人台 | 主播站姿参考 | 已验证；无指向姿势 |
| costume-gallery 约 201 条通勤类关键词 | 主播服装候选 | 关键词已验证；适配性待验证 |
| 速查表 D 做法（PRISM ref2va，3–8 秒，1 人开口） | 主播口播镜头 | 已验证文档；日语未测 |
| DWPose（sons02 controlnet_aux） | 量指尖坐标、做「地图对准指尖」 | 文档已验证；实物待验证 |
| gpu_lease.sh、sidecar.py | 显存互斥、产物溯源 | 已验证 |
| Remotion 叠层源码 | 字幕/信息条模板 | 源码在，未安装未跑 |

## 9. 需要用户确认的

1. 主播新建角色，还是借现有选角库的脸。
2. 天气模块放进幕布平台（新项目），还是单独起 Web。
3. 日语语音走哪条路；中文用 Drama 3 还是 IndexTTS-2.5。
4. 是否接受 Remotion 许可证；不接受就全走 ffmpeg/HTML 截帧。
5. 是否允许读 sons02（只读 ssh）补完本报告里的「待验证」项：生产库 130 张卡、reroll.py 重试逻辑、comfy 节点包和 DWPose 是否在、`h3_ref2va_prism.json` 节点。
