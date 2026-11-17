# B：sons02 本地能力调查（AI 天气预报视频用）

调查时间：2026-11-17 09:50–10:05。方式：只读（ssh 上 ls/find/cat/grep/nvidia-smi/ss/ps/版本查询，8188 只 GET 了 `/system_stats`、`/object_info`）。没起 GPU 作业、没提交 prompt、没动服务、没装东西，8191 没起。
唯一副作用：`/object_info` 先存成了 sons02 上的 `/tmp/oi_readonly_check.json`（5 MB，只读调查用的临时文件，没删，要清理请用户自己删）。

标记：**已验证**＝本次命令输出或文件里有原话／路径；**待验证**＝装着或文档说能，但我们没跑过；**存在风险**＝已知缺陷或冲突；**需要用户确认**＝要用户拍板。

---

## 0. 先说结论（对天气预报需求逐条）

| 需求 | 本地 H3 现状 | 标记 |
|---|---|---|
| 主播全身、转身、抬手 | H3 ref2va / fl2va 文字提示驱动，能出全身人物；但「指定姿势」要靠下面两条 | 已验证（模型在、节点在） |
| 按骨架控制动作（指向地图某点） | 8188 有原生 `MiniMaxH3FunControlNetApply`（control_video 输入）+ `minimax_h3_fun_controlnet_union_2.0_pruned_int8_convrot`（4.2GB）+ DWPose。11-09 打斗测过：动作跟骨架走，但第 2 帧跳、道具变形；**只能配 fl2va 剪枝底模** | 已验证（存在风险） |
| 照参考视频复刻动作 | viggle 换人（只在 8191 加载）测过，运动量 85–92%；Wan Animate 2 测过，运动量只有 19–43%；ref2va 的 `ref_videos` 输入在 8188 原生节点就有 | viggle 已验证；ref_videos 驱动动作 待验证 |
| 「指到地图上某个城市」的精确位置 | 没有任何节点能把手指钉到画面某像素；只能靠骨架视频里的手位置间接控制 | 待验证（存在风险，建议主播与地图分层合成） |
| 中文 TTS | IndexTTS-2.5（定版在用）、VoxCPM2、SoulX | 已验证 |
| 日语 TTS | IndexTTS-2.5 README 写支持 Japanese，代码里有 `lang=='ja'` 分支；VoxCPM2 30 语言含日语；docker 镜像 `voicevox/voicevox_engine:cpu-latest` 在本机（没在跑） | 待验证（我们一次日语都没跑过） |
| 口型同步（事后贴） | LatentSync 1.6 定版在用（`/mnt/storage/lipsync.py`），25fps 硬锁 | 已验证（存在风险：脸 <100px 检不到） |
| H3 直接吃 TTS 音频生成口型 | 8188 原生 `MiniMaxH3AddGuide` 有 `audio` 输入（把音轨钉到某帧）；8191 的 `comfyui-minimax-h3-audio-T8` 有「avatar 录音驱动 I2VA lock_source」工作流 | 待验证（我们没测过；全身镜头脸小，口型能不能看清是另一回事） |
| H3 Image 出主播定妆 / 城市场景图 | 官方 `minimax_h3_image_pruned_int8_convrot` 已软链进 8188；节点 `MiniMaxH3ImageConditioning`、`PH3ImageConditioning` 在 8188 | 已验证（模型+节点）；出图实测在 8191 做的 |
| 合成（字幕/叠图/渲染） | ffmpeg 6.1.1 带 libass/freetype/harfbuzz/fribidi + NVENC；**sons02 没有 node/npm、没有 chromium** | 已验证 |
| 每条耗时/显存 | H3 1376×768 5 秒约 165 秒、整卡峰值约 78 GiB；1080P 200–230 秒、进程 70–72.5 GiB（独占卡） | 已验证（出处见第 6 节） |

**需要用户确认**：
1. 「指城市」是否接受「主播单独生成 + 地图/城市标记后期合成」，而不是要求 H3 一次画出手指正好落在地图像素上。
2. 日语声音用哪条：IndexTTS-2.5（跟中文同一套克隆声，音色统一）还是 VOICEVOX（日本本地引擎，需起 docker）——都要先试听。
3. 口型走「H3 原声/AddGuide 音频」还是「事后 LatentSync」；全身中景脸可能 <100px，LatentSync 会报 Face not detected。
4. Remotion 类合成要 node+chromium，sons02 没有（装要 sudo/apt，属用户操作）；或改在 Windows（有 Node v24、Chrome）/WSL 做。

---

## 1. H3 模型清单

### 1.1 主模型 `/mnt/storage/ComfyUI/models/diffusion_models/`（已验证，`find -printf "%s %p"`）

| 文件 | 大小 | 类型 |
|---|---|---|
| minimax_h3_fl2va_int8_convrot.safetensors | 34.0 GB | fl2va 首尾帧（全量，非剪枝）|
| minimax_h3_fl2va_pruned_int8_convrot.safetensors | 21.0 GB | fl2va 首尾帧（剪枝）— **ControlNet 2.0 只能配它** |
| minimax_h3_ref2va_pruned_int8_convrot.safetensors | 21.0 GB | ref2va 参考图/视频/音频 |
| minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors | 21.0 GB | fl2va+ref2va 混合 |
| test_yz1114/minimax_h3_hybrid_fl2va_ref2va_b20-49-int8.safetensors | 21.0 GB | 同上另一切点（测试）|
| Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors | 21.0 GB | ref2va 微调（Singularity v1.3）|
| Minimax-h3_Singularity_x_10Eros-Max_PRISM_int8.safetensors | 20.3 GB | ref2va 合并版 PRISM（文戏多人默认）|
| viggle_remake_swap_pruned_int8_convrot.safetensors | 21.0 GB | H3 系 viggle 换人（V2V 动作复刻）|
| test_dasiwa/DasiwaMinimaxH3_V4_int8.safetensors | 21.0 GB | 第三方微调（测试）|
| test_feihou/FeiHou_MiniMax-H3_Remix_HSA_turbo_v0.8_int8_convrotHQ_pruned.safetensors | 23.3 GB | 第三方 turbo（测试）|
| minimax_h3_image_pruned_int8_convrot.safetensors（软链 → `model-lab/learn_nodes/h3image/...`，11-16 13:30 建）| 21.0 GB | **H3 Image** 文生图/参考图 |
| test_vdn1115/stage-dmd-step-250/（linear_branch 4.3GB + adapters）| 约 5.5 GB | OpenVDN 深度引导（测试）|

没有独立的「t2v」文件：ControlNet 节点自述写「Apply … to a text-to-video model」，实际 11-09 接的是 fl2va 剪枝底模。

### 1.2 配套（已验证）
- 文字编码器 `text_encoders/`：qwen3vl_32b_minimax_h3_int8_convrot（27.1GB，**用户 11-12 定的 8 位**）、_nvfp4_awq（15.7GB）、_ultra_uncensored_heretic_int8（26.4GB）。CLIPLoader type=`minimax`。
- VAE `vae/`：minimax_h3_video_vae_fp16（5.2GB）、video_vae_int8_convrot（2.8GB）、**minimax_h3_audio_vae_fp32（0.6GB，音频流）**、minimax_h3_image_vae_fp16（1.2GB，H3 Image 用）、lightvae_lite int8（1.2GB）。
- `model_patches/`：**minimax_h3_fun_controlnet_union_2.0_pruned_int8_convrot（4.5GB）**、qwen_image_2.1_fun_controlnet_union_int8_convrot。
- `latent_upscale_models/`：minimax_h3_latent_upscaler_3d_conv_v1_fp16、_3d_fp16_V2 等（各 0.69GB）。
- `vae_approx/taeh3.safetensors`（预览用）。
- `embeddings/minimaxh3_*`：10 个特效嵌入（bullet_time、kiss_camera 等），跟天气预报无关。
- LoRA（`loras/`，节选与本项目相关的）：fl2v turbo 4step/8step（1.96GB 各）、ref2v turbo 4/8step、pika_h3_flex_turbo_8step_hd_fl2va / _ref2va（3.9GB 各）、fl2v lightx2v 4step rank21、minimax_h3_360_orbit_flf2v_v1（环绕运镜）、H3_speed_slider_1.1、test_dir1115/minimax_h3_lms_v1.0_r64 等；其余是传奇怪物/角色 LoRA 和打斗 LoRA。
- `controlnet/` 目录是空的（SDXL openpose/tile 11-12 已挪走）。`audio_encoders/` 只有 wav2vec2_large_english_fp16（不是 H3 的）。

### 1.3 `/mnt/storage/model-lab/` 下 H3 相关权重（已验证）
- `learn_nodes/h3image/`：H3 Image 主模型（即上面软链的源）+ image VAE。
- `learn_nodes/ph3image/`：PrunaAI p-h3-image 的 VAE int8、LoRA bf16、prompt upsampler w4a8（6.7GB）、text encoder int8（5.1GB）——**extra.yaml 写明只给 :8191**。
- `author_v2/lightvae/`：lightvae-lite-h3 encoder/decoder。

### 1.4 `/mnt/storage/_trash_20261112/`：**不存在**（已验证：`ls: 无法访问 … 没有那个文件或目录`，`find /mnt/storage /home/sons -maxdepth 3 -iname "*trash*"` 无结果）
实际的挪走记录是 `/mnt/storage/_自训LoRA留档_1112/moved_原清单.tsv`（38 行）。目录里现在只剩 13 个自训 LoRA（chulongshen v1、huangquan v2 s250/500/750、shuangtou v1、wushu_action v4/v5/v7、ycdanbing_food v1/v2、zumajiaozhu v1/v2）。清单里其余项（如 **minimax_h3_fun_controlnet_union 1.0 的 int8 与 bf16**、fl2v turbo 4step v1.2/v1.3、ref2v turbo v1.0、SDXL openpose/tile ControlNet、SeedVR2 3B/7B 非 sharp、hunyuan_video_vae、music3 等）已不在该目录，推测已删除（本机有 `模型学习\sons02_已挪走模型_恢复清单_1112.md` 可查）。另：清单里的 `pika_h3_flex_turbo_8step_hd_ref2va` 现在又在 `loras/` 里（已恢复）。

---

## 2. ComfyUI 节点

### 2.1 实例（已验证）
- 正式 8188：ComfyUI **v0.45.4**（git 2aa4d535，11-15），PyTorch 2.11.0+cu128，Python 3.12.3，启动参数 `--listen 0.0.0.0 --port 8188 --disable-pinned-memory`。`object_info` 共 2497 个节点类。
- 测试 8191：**停着**（`ss` 无 8191），按要求未起。
- 另有 `/home/sons/comfy-vram-reaper.py` 守护：8188 队列空闲 90 秒自动调 `/free` 放显存。

### 2.2 custom_nodes 列表（已验证）
- 正式 `/mnt/storage/ComfyUI/custom_nodes/`：audio-separation-nodes-comfyui、ComfyMath、comfy_mtb、comfyui_controlnet_aux、ComfyUI-Custom-Scripts、ComfyUI_essentials、ComfyUI-GGUF、ComfyUI-KJNodes、ComfyUI-LatentSyncWrapper、ComfyUI_LayerStyle、ComfyUI-LTXVideo、ComfyUI-Manager、ComfyUI-SeedVR2_VideoUpscaler、comfyui-SelfLift、ComfyUI_UltimateSDUpscale、ComfyUI-VideoHelperSuite、ComfyUI-WanVideoWrapper、Goohaitools-comfyui、RES4LYF、rgthree-comfy。
- 测试 `/mnt/storage/ComfyUI-test/custom_nodes/`：上面全部 + ComfyUI_FlashVSR、ComfyUI-Frame-Interpolation、**comfyui-minimax-h3-audio-T8（v1.87.0）**、Comfyui_Minimax_h3_latent_Upscaler、ComfyUI-PainterI2V、ComfyUI-PT_H3ConcatAVLatent、ComfyUI-ReservedVRAM、**ComfyUI-YCNodes-MiniMax-H3**；禁用的 ComfyUI-H3Shadow-Negative.disabled、minimax-h3-hybrid-cond.disabled。
- 8191 另通过 `model-lab/learn_nodes/extra.yaml` 加载 `learn_nodes/custom_nodes/`：ComfyUI-H3-FaceRefine、ComfyUI_MiniMaxH3_Director、ComfyUI-MiniMaxH3Mod、**ComfyUI-Viggle-Remake**、ComfyUI-Viggle-Remake-HiRes、ComfyUI-VOSR2、H3-Character-Sheet-Designer。**8188 没有 viggle 节点**。

### 2.3 8188 `/object_info` 里的 H3 本地节点（已验证，节点输入原样）
（`comfy_api_nodes.*` 里的 ComfyCloudMiniMaxH3*、MinimaxHailuo03*、MinimaxH3ImageNode、PikaH3Flex* 都是**云端付费 API 节点，不算本地能力**。）

| 节点（模块） | 必填输入 | 可选输入 | 说明 |
|---|---|---|---|
| EmptyMiniMaxH3LatentAV（comfy_extras） | width 1344 / height 768 / length 124 | — | 视频+音频联合 latent，24fps，17k+5 帧；训练范围约 124–362 帧 |
| MiniMaxH3ImageToVideo | clip, vae, prompt, width, height, length | first_frame, last_frame | fl2va 首尾帧 |
| MiniMaxH3ReferenceToVideo | clip, prompt, width, height, length, ref_image_size(match/max) | vae, audio_vae, **ref_images（≤?）, ref_videos, ref_video_audios, ref_audios（各 ≤3）** | ref2va，提示词里用 `<Picture i>/<Video k>/<Audio j>` |
| **MiniMaxH3AddGuide** | positive, latent, frame_idx | vae, audio_vae, image, **audio** | 自述：「Anchor an image, a short clip, audio, or a clip with its soundtrack at any frame」。可把一段音轨从某帧起钉进去 |
| **MiniMaxH3FunControlNetApply** | model, model_patch, vae, strength 1.0, start/end_percent | **control_video**, mask, source_video | 姿势/深度/边缘等控制视频；mask=1 的区域重画 |
| MiniMaxH3ContextWindows | model, context_length 124, overlap 39, fuse_method, freenoise | — | 长视频分窗 |
| MiniMaxH3SigmaShift | model, shift_video 12, shift_audio 3 | — | |
| MiniMaxH3LatentUpscaleWithModel | 放大模型, samples, 2560×1440 | — | latent 放大 |
| MiniMaxH3ImageConditioning / PH3ImageConditioning | clip, prompt, width, height | vae, images | H3 Image 出图 |
| SelfLiftH3Sampler / SelfLiftH3TST（comfyui-SelfLift） | 两阶段采样 | model_hires 等 | 生产在用 |
| KJNodes：MiniMaxH3MemoryEfficientSageAttentionPatch、MiniMaxLowVRAMAttention、MiniMaxChunkFeedForward、MiniMaxH3TokenCounter | | | 省显存/计 token |

### 2.4 姿势/动作/音频类节点（8188，已验证存在；能否接 H3 逐条标）
- **能直接接 H3**：`MiniMaxH3FunControlNetApply.control_video`（接 DWPose/深度视频）——11-09 实跑过（`model-lab/attackpose/cn2/cn2.py`：VHS_LoadVideoPath → DWPreprocessor → 骨架视频 → FunControlNet，底模 fl2va_pruned）。**已验证**。
- **能直接接 H3（音频）**：`MiniMaxH3AddGuide.audio`、`MiniMaxH3ReferenceToVideo.ref_audios/ref_video_audios`。ref_audios 我们用作「声音参考」（`castsery/h3sheet/h3ref_vid.py` 接了 `陆青_calm.wav`）；**用 AddGuide 把整句 TTS 当驱动音轨钉进去、看口型是否跟着——没测过，待验证**。
- 姿势提取：comfyui_controlnet_aux 的 DWPreprocessor（权重在 `ckpts/yzd-v/DWPose/yolox_l.onnx`、`dw-ll_ucoco_384.onnx`）、OpenposePreprocessor（lllyasviel body/hand/face pth）、DepthAnythingV2（vitl 1.3GB）；原生 SDPose 节点（**SDPose 权重没找到**）；原生 MediaPipe 人脸节点（`.task` 模型文件没找到）。
- 不接 H3、属 Wan 系：WanAnimate2ToVideo / WanAnimateToVideo（有 `wan_animate_2_distill_int8_convrot` 15.5GB）、WanSCAILToVideo、WanVaceToVideo、WanHuMoImageToVideo、WanInfiniteTalkToVideo、WanVideoWrapper 里的 MultiTalk/FantasyTalking/UniAnimate/OneToAll/SCAIL 节点——**这些节点在，但对应权重（S2V、HuMo、InfiniteTalk、MultiTalk、SCAIL、VACE）在 diffusion_models 里都没找到**（`ls | grep -iE "s2v|humo|infinite|multitalk|animate|scail"` 只有 wan_animate_2）。笔记里 09-22 装过的 `wan2.2_s2v_14B_fp8_scaled` 现已不在。
- 8191 独有（待验证、8191 现停）：T8 包的 Avatar 录音驱动 I2VA（`examples/workflows/36-avatar-voice/2026-09-18_T8_avatar_EXP.json`，README 原话「录音驱动I2VA、lock_source」、「单段73帧／24fps≈3.042秒」、示例 512×768）；T8 的 02-audio-control（Audio_Lock_Source 等 4 个）；T8 的 DEPTH_REFERENCE_EXP、DANCE 文档；OpenVDN 深度引导（8191 跑过）。笔记还提到一个 `MiniMaxH3NativeAudioLock`（「锁音频驱动口型」），**8188/8191 的 object_info 里都没有，没装**。
- 云端（不算本地）：KlingLipSync、MinimaxHailuo03MaxLipSyncNode、SyncLipSync、VeedLipsync、HiggsfieldMotionTransfer、KlingMotionControl 等。

---

## 3. 现有工作流与出片脚本（已验证存在；用途来自文件头注释与速查表）

- `/mnt/storage/ComfyUI/user/default/workflows/`：YZ_H3_ultimate.json（YZ 金鱼「H3 终极篇·文武双全」，用 ReferenceToVideo+SigmaShift+SelfLiftH3Sampler）、Qwen2.1_文生图 / 改图_带参考图、Ideogram4_写实、Sulphur2 三个。8191 的 workflows 目录为空。
- `model-lab/castsery/`：各剧选角/定妆/出片总目录。`h3sheet/h3ref_vid.py`＝角色设定表喂 ref2va（Singularity v1.3 + Pika Flex Turbo 8step ref2va LoRA + Sol Attention + 两阶段 SelfLift），走 :8191，带声音参考 `ref_audio`；`cyxr/`＝《次元闲人》复刻出片；`jihun_ep1/`＝《集魂》EP1 批量（`ep1batch2.py` + `want.json` 闸）；`dub_ep1.py`、`asr_chk.py` 配音与转写核对。
- `model-lab/attackpose/shot3/`：打斗三镜（关键帧计划 → Qwen2.1+深度 ControlNet 关键帧 → H3 fl2va 首中尾钉帧）；`cn2/cn2.py`＝**H3 Fun ControlNet 2.0 + DWPose 骨架**测试；`video/atk_anim.py` 公共出片函数。
- `model-lab/viggletest/full_vg.py`、`vg_run.py`＝viggle 换人（:8191）。`dir1115/wen1080.py`、`wen2.py`＝文戏 1080P。`swap1107/wa2_run.py`＝Wan Animate 2。
- 作者仓库 `/mnt/storage/model-lab/review/ganloss-latent-space/workflow/`（共 469 项）里 H3 相关目录/文件：2026-08-05 minmaxH3（t2v/i2v/r2v 基础三份）、08-07 minmax fast、08-11 minmax turbo lora、08-24 minimax latent upscale、08-26 r2v_story_board、08-28 r2v_video_edit、08-31 r2v_video_mask_edit、**09-02 minmax+sam3dbody+blender（含 `minimax_h3_r2v_complex motion.json`：VHS_LoadVideo → ref2va 参考视频带动作）**、**09-04 ref2va-motion-context-step1（用 MiniMaxH3MotionContext* 节点，8188 未装）**、09-07 fused turbo、09-11 face refine、09-15 r2v_3dscene、09-17 taoMate h3、09-22 fasth3、09-28 qwen2.1+fasth3、10-12 fastH3 trim、10-13 H3 refMod、10-19 FastH3 ref2va、10-21 character swap、10-23 singularity v2、10-26 FastH3 omni、10-28 10eros_singularity、11-03 pika h3 flex、11-05 pika flex turbo lora vs 3 model merge、11-09 character designer、11-10 hyperflow flash、11-16 image_minimax_h3_image_character_designer.json。另有 2025-06-24 Minimax-Remover。

---

## 4. 其他可复用模型/工具

| 类别 | 位置 | 状态 |
|---|---|---|
| 姿势：DWPose | `custom_nodes/comfyui_controlnet_aux/ckpts/yzd-v/DWPose/`（yolox_l.onnx 217MB、dw-ll_ucoco_384.onnx 134MB） | 已验证，11-09 实跑过；注意线稿人台提不出骨架 |
| 姿势：OpenPose | `ckpts/lllyasviel/Annotators/`（body/hand/facenet） | 文件在，没单独测 |
| 深度 | `ckpts/depth-anything/Depth-Anything-V2-Large` | 已验证（Qwen 关键帧在用） |
| 人脸 | `models/insightface/models/buffalo_l/`（5 个 onnx）、`ultralytics/bbox/face_yolov8m/n.pt` | 已验证（FaceRefine 在用） |
| RTMPose / MediaPipe .task / SDPose 权重 | 未找到 | — |
| 口型：LatentSync 1.6 | 脚本 `/mnt/storage/lipsync.py`；权重 `custom_nodes/ComfyUI-LatentSyncWrapper/checkpoints/`（latentsync_unet.pt 5.1GB、stable_syncnet 1.6GB、whisper/tiny.pt、vae/、auxiliary/） | 已验证定版：FPS 25、expr 2.5、upscale 2.5（速查表 166–171 行，补充 985–989 行） |
| MuseTalk / Wav2Lip / SadTalker / LivePortrait / EchoMimic | 未找到 | — |
| TTS：IndexTTS-2.5 | 权重 `/mnt/storage/models/IndexTTS-2.5`（11G，含 `multilingual_zh_ja_yue_char_del.tiktoken`），代码 `/mnt/storage/tts/index-tts-v25`（`.venv`） | 中文已验证定版（速查表 119 行，lang="ZH"）；**日语：README「supports Chinese, English, Japanese, Spanish and Arabic」、`infer_v2_5.py` 703–713 行有 `lang=='ja'` 分支，待验证** |
| TTS：VoxCPM2 | `/mnt/storage/models/VoxCPM2`（4.7G），环境 `.venv-vox` | 东北话已验证；README 写 30 语言含 Japanese、可「Voice Design」，日语待验证 |
| TTS：SoulX-Podcast-1.7B-dialect | `/mnt/storage/models/SoulX-Podcast-1.7B-dialect`（5.1G） | 川/粤已验证；日语没写 |
| TTS：VOICEVOX | docker 镜像 `voicevox/voicevox_engine:cpu-latest`（4.5GB），容器没在跑；`realtime_meeting` 的 `dialog_server.py`/`dialog.yaml` 引用了它 | 待验证（日语专用，CPU 版） |
| 其他声音 | `/mnt/storage/tts/` 下还有 CosyVoice、GPT-SoVITS 样例脚本、sglang-omni（Drama 3）、HunyuanVideo-Foley、MSST 分离 | 存在，不展开 |
| ASR：faster-whisper | `~/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3`（另有 small）；`/home/sons/realtime_meeting/.venv` 里 faster_whisper 1.1.0 / ctranslate2 4.8.0；`/srv/sesp-ai-relay/app/models/faster-whisper-large-v3` | 已验证（Blackwell 上 CUDA 可用，见记忆） |
| 超分：SeedVR2 | `models/SEEDVR2/seedvr2_ema_7b_sharp_fp16` + `ema_vae_fp16` | 已验证定版（速查表 152 行） |
| 超分：FlashVSR v1.1（+plus） | `models/FlashVSR/`，节点只在 8191 | 没测过（宽高要 128 倍数） |
| Wan Animate 2 | `diffusion_models/wan_animate_2_distill_int8_convrot`（16.7GB）+ umt5/Wan VAE/clip_vision_h | 测过，备用；动作量偏小（速查表 255–257 行） |
| viggle 换人 | 主模型 21GB + 8191 节点 | 已验证在用（速查表 236–253 行）；480p、一段 13 秒约 6 分钟、最长 345 帧 |
| SAM 3.1 | `checkpoints/sam3.1_multiplex_fp16.safetensors` | 文件在（抠像可用），本次没核结论 |

---

## 5. 合成工具（已验证）

- **node / npm：没有**（`bash: node: 未找到命令`）。
- **chromium / chrome：没有**（`which` 全空；`~/.cache/ms-playwright/` 只有 ffmpeg-1011、webkit-2336，没有 chromium）。→ Remotion 在 sons02 上跑不了，要么用户 sudo 装，要么放 Windows（Node v24 + Chrome 在）或 WSL。
- **ffmpeg 6.1.1-3ubuntu5**：`--enable-libass --enable-libfreetype --enable-libfontconfig --enable-libfribidi --enable-libharfbuzz --enable-libx264 --enable-libx265`；滤镜 `ass`、`subtitles`、`drawtext` 都在；编码器 `h264_nvenc`、`hevc_nvenc`、`av1_nvenc`、`libx264`。
- 日文字体：`fc-list :lang=ja` 有 Noto Serif CJK JP/SC 等（Sans CJK 见全局记忆 `/usr/share/fonts/opentype/noto/`）。
- 已知坑（速查表 991–994 行）：LatentSync 出片 color_range unknown，和 tv/bt709 片拼接时字幕会整段丢，要写死 bt709/tv 并加 `-reinit_filter 0`。

---

## 6. 显存与耗时（只摘已有实测，不跑新测）

| 活 | 画布/长度 | 用时 | 显存 | 出处 |
|---|---|---|---|---|
| H3 fl2va 出片（首中尾钉帧） | 1376×768，5 秒 | 约 165 秒/条 | 整卡峰值约 78 GiB | `固定做法速查表.md` 第 970 行 |
| H3 文戏 D 节（PRISM ref2va）→ 丁 1080P | 1376×768 → 1920×1088，124 帧 | 单人近景 110→181 秒；两人中景 131→220 秒；三人 121→215 秒 | 进程 59.5→69.1 / 61.3→72.0 GiB | 速查表 第 504–508 行 |
| H3 文戏 1080P 三张参考图 | 1920×1088，124 帧 | 每条多约 20 秒 | 进程峰值 71–72 GiB，独占卡 | 速查表 第 513 行 |
| H3 一人物+一场景 | 1920×1088 | 200.8 秒 | 整卡 76101 / 进程 70760 MiB | 速查表 第 518 行 |
| H3 文戏 1080P 汇总 | 124 帧 | 200–230 秒/条 | 进程 70–72.5 GiB，整卡 75–78.6 GiB | `模型学习\sons02_用卡排法_1115.md` 第二节表格 |
| H3 出片 L-05h3i | — | 220.7 秒 | 整卡峰值 77094 MiB | `模型学习\H3Image参考图对照结果_1116.md` 第 19 行 |
| H3 Image 角色设定表（新节点 1.4.4） | 3840×1536 | 20.0–28.3 秒（含装模型 28.3 / 36.1 秒） | 进程约 50–51 GiB，整卡 55.3–56.2 GiB | `模型学习\H3角色设定表_1116\测试结果.md` 第 14、78–80、118–119、141 行 |
| 官方 H3 Image 单图 | 2688×1504 | 首张 20.0 秒、之后 10.0 秒 | 进程 47118–48000 MiB，整卡 52309–53191 MiB | `模型学习\H3Image对比结果_1116.md` 第 27 行 |
| H3 Image 参考图出图 | — | 32.0 秒 | 进程峰值 50196 MiB | `H3Image参考图对照结果_1116.md` 第 17 行 |
| OpenVDN 深度引导（全量 fl2va） | 1280×736，124 帧 | 440–510 秒 | 进程 85–87 GiB，整卡 91–93 GiB（独占） | `模型学习\OpenVDN深度引导_拆解_1115.md` 第 124–127、175–176、203 行 |
| FaceRefine 修脸 | — | FR5 45 秒 | 整卡峰值约 69 GB | 速查表 第 163 行 |
| viggle 换人 | 480p，13 秒一段 | 约 6 分钟/段 | **未记录** | 速查表 第 252 行 |
| 打斗 B2（turbo） / C（20 步） | 56 帧 | 约 40 秒 / 8–13 分钟 | 未记录 | 速查表 第 199 行 |
| PiD 4 倍放大 | — | 约 25 秒/张 | 进程约 22 GiB | 速查表 第 529 行 |
| Qwen Image 2.1 出图 | — | 首张 21 秒、之后 8–15 秒 | 进程 34.7 / 整卡 39.9 GiB | `sons02_用卡排法_1115.md` |
| llama-swap Qwen3.8 | 256K ctx | 按需载，300 秒自卸 | 36.4 GiB | 同上 |
| **LatentSync** | — | **没找到实测耗时/显存记录** | **没找到** | 只查到 `试镜\05_LatentSync诊断.md` 讲参数与 bug，无耗时 |
| **H3 + ControlNet 2.0** | — | **没找到耗时/显存记录** | **没找到** | `经验记录\2026-11-09_经验记录.md` 71–75 行只有效果结论 |
| **TTS（IndexTTS/VoxCPM）** | — | **本次没找到耗时记录** | — | — |

**存在风险**：H3 出片（进程 70–87 GiB）属于独占档，和 Qwen3.8（36.4 GiB）、Qwen 出图（34.7 GiB）都不能同时跑（`sons02_用卡排法_1115.md` 第三节）；Blackwell 上剩余 <17 GiB 时 ComfyUI 会静默出灰图。

### 6.1 当前 nvidia-smi（2026-11-17 09:57，已验证）
- 整卡 97887 MiB，已用 **5597 MiB**，GPU 0%，P8。
- 进程：realtime_meeting（pid 2998）4342 MiB、ComfyUI 8188（pid 2988）664 MiB、Bernini 7860（pid 2987）550 MiB、gnome-shell 8 MiB。
- 8188 `system_stats`：vram_free 96128598016（约 89.5 GiB），RAM 98.7 GB 中空闲 37.7 GB。
- llama-swap 当前没加载模型（不在 GPU 进程里）；vl8b（8001）、vLLM 32B（8000 那个不是 vLLM，见下）、8191 都没在跑。

---

## 7. 端口占用

（公开仓库里删去了内网端口和服务清单，原件在本机。）

## 8. 读不了 / 找不到的
- `/mnt/storage/_trash_20261112/` 不存在（见 1.4）。
- 没找到 `h3ref_vid.py` 以外名为 `shot3/` 的独立出片脚本说明文档，只按文件头注释和速查表描述。
- LatentSync、H3+ControlNet、viggle、TTS 的耗时/显存实测记录没找到。
- SDPose、MediaPipe `.task`、RTMPose 权重没找到；S2V/HuMo/InfiniteTalk/MultiTalk/SCAIL/VACE 权重没找到（节点在、权重不在）。
- 8191 是停的，T8 avatar / viggle / VDN 等节点的现行输入项本次没法从 object_info 核（`model-lab/learn_nodes/object_info_8191.json` 是 11-04 的旧快照，不含 T8 新版节点）。
