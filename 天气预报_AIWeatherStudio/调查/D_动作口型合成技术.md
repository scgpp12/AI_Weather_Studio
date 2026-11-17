# D 动作、口型、合成技术调查（AI 天气预报主播）

调查日期：2026-11-17。只查资料和读本机笔记，没下载模型、没装东西、没碰 sons02 显卡。

本次做法＝先读本机笔记（`固定做法速查表.md`、`学习笔记\10_H3与Singularity已知缺陷.md`、`攻击研究\研究日志.md`、`攻击研究\research_report.md`、`经验记录\2026-11-09_经验记录.md`、`参考片_次元闲人_1116\对口型覆盖表_v1.md`、memory 里 fl2va／motion／keyframe／latentsync／viggle 几条），再上网补官方资料。已对照错题本：第 36 条（用模型前先查新版本和已知毛病）、第 38 条（先上网查）、第 62 条（测过的做法不自己换喂法）、第 65 条（同名不同格式）。

标注：
- **已验证**：我们自己实测过（写明出处），或官方原文直接写明。
- **待验证**：只有资料、社区说法，或是我的推算，没在我们机器上跑过。
- **存在风险**：资料或实测指向一个会出问题的地方。
- **需要用户确认**：取舍要用户来定。

---

## 0. 结论先说

1. **H3 本体没有姿势控制**。官方模型卡没写 pose/ControlNet（已验证，官方原文）。能控姿势的是阿里 PAI 训练的外挂分支 **H3 Fun ControlNet-Union 2.0**（含 DWPose 骨架、深度等 8 种控制），sons02 上有，我们 11-09 测过：动作会跟骨架走，但第 2 帧会从首帧跳到骨架姿势，首尾都钉也回不到起始姿势（已验证，本机实测）。
2. **「手准确指到地图某一点」这件事，我们没有一条做法测过**。首尾帧钉法管的是起止姿势，中间过程和指尖落点没量过（待验证）。
3. MVP 最稳的思路是**反过来做：不让手去找城市，让地图去找手**。先做几段固定的「指向」动作素材（指左上、左中、左下等），量出每段指尖停住时的画面坐标，再由程序把地图平移、缩放，让目标城市刚好落在指尖上，再叠高亮圈。这样指向精度由程序保证，生成模型只需出几段好看的动作。
4. **口型**：LatentSync 1.6 只改脸部裁切区，不动身体（已验证，本机实测＋官方）；但**全身远景的脸太小**，脸宽不到约 100px 直接报 Face not detected（已验证，本机实测），约 130px 嘴糊、重影（已验证）。所以全身播报镜头要么给脸留够像素（4K 渲染或另拍半身近景），要么口型交给能整帧重生成的模型（InfiniteTalk 之类，但会改身体动作）。
5. **TTS**：IndexTTS-2.5 官方支持日语（已验证，官方模型卡），但不给时间戳；时间戳用 **Qwen3-ForcedAligner-0.6B**（支持中日，Apache-2.0，官方自评比 WhisperX 准，待验证）或我们已有的 faster-whisper 词级时间戳兜底。
6. **合成**：Remotion 免费许可只到「3 人以内的营利组织」，超过要买 Company License（已验证，官方 LICENSE 原文）。不想背许可就用 **FFmpeg＋Python（Pillow/Cairo）逐帧画**，地图投影用 d3-geo（ISC）或 Python 的 pyproj/cartopy。

---

## 1. H3 能不能控姿势

### 1.1 官方与社区资料

| 项 | 内容 | 标注 | 出处 |
|---|---|---|---|
| H3 官方本体 | 模型卡分 FL2VA（文生、首帧、尾帧、首尾帧）和 Ref2VA（最多 9 图、3 段视频、3 段音频，总 12 个文件）。**没提 pose、ControlNet、动作控制**；参考视频在示例里是「被编辑的源视频」，没说能当动作参考 | 已验证（官方原文） | [MiniMaxAI/MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)（访问 2026-11-17） |
| H3 输出上限 | 4–15 秒，短边默认 768px；2K 靠没开源的 H3-Regenerate-2K | 已验证（官方原文） | 同上 |
| H3 原生语音 | 稳定支持 11 种语言，含中文、日语；口型来自提示词里的台词，**没写能用给定的语音音频来驱动口型** | 已验证（官方原文）；「不能喂 TTS 音频对口型」是推断，待验证 | 同上 |
| H3 许可 | MiniMax H3 Community License（2026-08-02）。适用地区排除欧盟、英国、韩国、美国（日本在内）；商用要在产品界面显著标「MiniMax H3」；年收入超 2000 万美元另行授权；输出归使用者 | 已验证（官方原文）；商用是否触发「界面标注」→ **需要用户确认** | [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) |
| **H3 Fun ControlNet-Union 2.0** | 阿里 PAI 基于 H3 训练的控制分支：Canny、Depth、HED、MLSD、Pose（DWPose 骨架）、Scribble、Layout、Gray，另支持视频修补；`control_context_scale` 调强度，0 等于关掉；guidance 必须 1.0；**加载 v1 配置会静默失败** | 已验证（官方模型卡） | [alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0) |
| ComfyUI 用法 | 官方教程：补丁对 fl2va 和 ref2va 都能用；姿势提取用 `sdpose_wholebody`；输出跑偏时才把 strength 调到 1 以上 | 已验证（官方教程） | [docs.comfy.org H3 Fun ControlNet](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet) |
| Singularity v1.3 / PRISM / Pika H3 Flex | 都是社区微调底模或加速 LoRA，**没有姿势控制功能**。本机测过：PRISM 五组复刻 83 分，Singularity v1.3 74 分；Pika Flex「提升有限」 | 已验证（本机） | `固定做法速查表.md` 第 219–232、325–326 行 |
| Viggle Remake（H3 换人版） | 基于 H3：驱动视频给动作和切镜，1–4 张「重画帧」给人和背景。属于「参考视频驱动」 | 已验证（本机实测） | `固定做法速查表.md` 第 236–253 行 |

### 1.2 我们自己测过的（和「指向」有关的部分）

| 测过的事 | 结果 | 标注 | 出处 |
|---|---|---|---|
| ControlNet-Union 2.0 + 蚩尤原片 DWPose 骨架（11-09） | 动作幅度明显变大、跟骨架走；**第 2 帧会从钉住的首帧跳到骨架姿势**；刀形会变；首尾都钉也回不到起始姿势。对策：先按骨架第 1 帧出首帧。另：只能配 fl2va **剪枝**底模，配全量会报 adaln width 错；线稿人台用 DWPose 提不出骨架 | 已验证 | `经验记录\2026-11-09_经验记录.md` 第 71–75 行；速查表第 331 行（AP `cn2/cn2.py`） |
| 姿势和景别跟着参考图走（ref2va 系，11-16） | 喂站姿图写「单膝跪」→ 照样站着（4 正 1 反）；**图和文字同时指向同一姿势才压得过直立先验** | 已验证 | 速查表第 696–767 行 |
| 动作量由首尾帧差决定 | 提示词压不住动作量；首尾只差 0.3 秒动作量掉 30%；fl2va 最后约 1 秒几乎静止；一条最少 22 帧 | 已验证 | memory `motion-comes-from-keyframe`、`slow-motion-root-cause-keyframe-delta`；速查表第 199–201 行 |
| 中间钉帧（MiniMaxH3AddGuide） | 钉 1–2 张中间关键帧最有效（衣服物理 4→7.5）；自画中间帧必须和尾帧物理连贯，否则会「悬着不动」 | 已验证 | memory `fl2va-mid-keyframe-guide`、`h3-mid-keyframe-guide-best` |
| fl2va 首帧里没有的东西会被编 | 只给首帧时，首帧里没有的角色被画成别人 | 已验证 | memory `fl2va-needs-last-frame-for-identity` |
| **「手准确指向某点」** | **没测过**。手部相关的已知问题：两只手都占用会多画第三只手、手部特写会变形（`攻击研究\h3fight_repro\评分\评分表_技能批_1114.md` 第 582 行「像一团粗手指在变形」） | 待验证；手部变形**存在风险** | memory `third-hand-holds-the-fish`；上述评分表 |

**推论（待验证）**：用 fl2va 钉「首帧＝正面站姿、尾帧＝手指着地图某点」能大致到位，但：① 尾帧那张图的指向必须先画准（Qwen 2.1 编辑写姿势要「有依托」，速查表第 106 行）；② 模型最后约 1 秒趋于静止，正好适合「保持指向」，但保持期间指尖会不会漂没量过；③ 从「抬手」到「保持」再到「放下」要分成几条片子各钉首尾，接缝处靠同一张中间帧串起来。

---

## 2. 动作控制方案 A/B/C/D 对比

### 2.1 各方案在说什么

- **A 姿势序列＋H3**：程序或 Blender 生成一段骨架/深度视频（抬手→指→保持→放下），喂 H3 Fun ControlNet-Union 2.0，首帧用主播定妆图。
- **B 参考动作视频＋动作迁移**：真人（或二维/三维假人）录一段动作，用 Viggle Remake、Wan-Animate-2、SCAIL-2 换成主播。
- **C 3D 骨骼动画→AI 换外观**：Blender + Mixamo 动作渲染灰模，再用 B 的模型（或 ControlNet 深度）换成主播外观。
- **D 预制动作素材循环＋程序化地图**：一次性生成十几段标准动作（待机、播报、转身、指左上/左中/左下…、放下、转回），之后每天只换地图、字幕、配音，不再生成主播身体。

### 2.2 资料与本机数据

| 模型 | 要点 | 标注 | 出处 |
|---|---|---|---|
| Viggle Remake swap（H3） | 本机：动作和切镜贴住原片，运动量 85–92%；13 秒约 6 分钟（480p）；736 档清楚但慢 3 倍、进程显存 64–69GB；快速移动的道具会糊；Blender/Mixamo 假人驱动可用，剑在场 99–100% | 已验证 | 速查表第 236–253 行；`攻击研究\研究日志.md` 第 1 轮、规律 6、9 |
| Wan-Animate-2（2026-08-07 开源） | 本机：运动量只有原片 19–43%、不跟切镜、九条全丢剑（手持物做不了）；身体发力最真 | 已验证（本机）；官方说加了文字控视角，待验证 | 速查表第 255–257 行；研究日志规律 14；[Wan-Animate-2 GitHub](https://github.com/Wan-Video/Wan-Animate-2) |
| SCAIL-2（智谱，2026-06-09，Apache-2.0） | 基于 Wan2.1 14B；不用中间骨架图，直接吃驱动视频；ComfyUI 原生节点；有动画模式和替换模式；INT8 约 16.7GB（本机调研笔记） | 待验证（本地没下） | [comfyui-wiki 2026-06-09](https://comfyui-wiki.com/en/news/2026-06-09-scail-2-character-animation)；`攻击研究\environment_report.md` 第 58 行 |
| Wan2.2-S2V-14B（2025-08-26，**超过一年**） | 音频驱动全身/半身，可加 `--pose_video` 做姿势驱动；单卡示例要 ≥80GB；Apache-2.0 | 待验证；旧于一年 | [Wan-AI/Wan2.2-S2V-14B](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B) |
| Mixamo 动作学习 | 本机：纯代码打关键帧的动作没重量（转速只有动捕一半），要从动捕数据出发；库里没有的动作拼不出来 | 已验证 | 研究日志规律 1、2、12 |

### 2.3 对比表

评分是相对比较（高／中／低），括号里写依据来源。「本机」＝我们测过；「资料」＝只看了资料或推断。

| 维度 | A 骨架＋H3 ControlNet 2.0 | B 真人参考视频＋Viggle Remake | C Blender/Mixamo→Viggle 换外观 | D 预制动作素材＋程序地图 |
|---|---|---|---|---|
| 动作准确性（手指到点） | 中：跟骨架走，但第 2 帧会跳、起始姿势回不去（本机）；指尖落点没量过（待验证） | 中高：照驱动视频，运动量 85–92%（本机）；指尖精度没量过（待验证） | 高：3D 里指向可精确到像素再渲染；换外观后的偏差没量过（待验证） | **最高**：素材只做一次，挑出指得准的；城市位置由程序对齐到指尖（推算，待验证） |
| 人物一致性 | 中：首帧锁人，H3 偶尔漂（本机） | 中高：靠重画帧锁人；人和背景边缘对不上（研究日志规律 21） | 同 B | **最高**：每天用同一套素材，完全一致 |
| 自然度 | 中：骨架来自程序时没重量（研究日志规律 2） | 高：真人动作最自然（资料＋本机） | 中：Mixamo 动捕自然，手打关键帧不自然（本机） | 高（素材是 B 或 C 做出来的）；但循环和接缝处要藏好 |
| 可重复性 | 低中：每次重新生成都有随机性 | 中：同驱动片换种子差异小（研究日志第 1 轮 3 个种子几乎一样） | 中 | **最高**：每天不生成身体 |
| 推理时间（每条） | fl2va 剪枝 turbo 约 40 秒／条起（本机），加 ControlNet 没记时间 | 13 秒约 6 分钟（480p）；736 档约 3 倍（本机） | 同 B，外加 Blender 渲染 | 每天只跑口型（LatentSync）＋合成，分钟级（推算） |
| 显存 | H3 剪枝 int8 + 补丁 4.2GB；首中尾钉帧整卡峰值约 78GiB（本机，不含 ControlNet） | 480p 未单独记；736 档进程 64–69GB（本机） | 同 B | 生成素材时同 B/C；日常只要 LatentSync 约 18GB（官方） |
| 开发复杂度 | 中：要做骨架序列和首帧对齐 | 中：要录真人动作、做重画帧、按切点分段 | 高：Blender 绑定、动作、渲染、再换外观 | 低中：主要是程序合成，生成只做一次 |
| 我们测过没有 | 测过 ControlNet 2.0（打斗，11-09），没测指向 | 测过 Viggle（舞蹈、打斗），没测指向 | 测过 Blender/Mixamo→Viggle（打斗），没测指向 | 没测过 |

**需要用户确认**：主播每天的动作是否允许「同一套动作反复用」。如果要求每天动作都不一样，D 不成立，要退回 A/B。

---

## 3. 口型同步

| 方案 | 语言 | 全身远景小脸 | 侧脸 | 会不会动身体 | 显存 | 标注与出处 |
|---|---|---|---|---|---|---|
| **LatentSync 1.6**（2025-06-11，旧于一年；Apache-2.0） | 音频经 Whisper 编码；1.5 版官方写「改善中文视频」；日语官方没写 | **本机**：脸宽 <约 100px 报 Face not detected（婆婆脸 44–71px）；约 130px 嘴糊、上下唇重影；192px 偏软，328px 好 | **本机**：母亲侧脸贴后下唇扭了（1-04） | 不动身体，只换脸部裁切区；但整张对齐脸都过一遍 VAE，鼻梁清晰度掉 39%（本机） | 官方 18GB | 已验证：`对口型覆盖表_v1.md` 第 10、49 行；速查表第 166–171、985–989 行；`试镜\05_LatentSync诊断.md`；[官方仓库](https://github.com/bytedance/LatentSync)。日语效果待验证 |
| MuseTalk 1.5（2025-03-28，旧于一年；MIT） | 官方写支持中文、英文、日语音频 | 脸区 256×256，比 LatentSync 更小，远景更吃亏（推断） | 官方没写 | 只改嘴部区域 | 官方最低测到 4GB 笔记本卡 | 待验证；[MuseTalk](https://github.com/TMElyralab/MuseTalk) |
| InfiniteTalk（2025-08-19，旧于一年；Apache-2.0） | 音频编码器是 chinese-wav2vec2-base，日语没写 | 整帧重生成，脸不需要单独检测（推断） | 第三方说侧脸、强阴影会降一致性（非官方） | **会改**：头、身体姿态、表情都按音频重生成；镜头运动「模仿但不完全一样」 → **会破坏我们设计好的指向动作**（存在风险） | 官方没给数字；基于 Wan2.1 14B | 待验证；[InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) |
| LongCat-Video-Avatar 1.5（2026-05-21） | 换成 Whisper-Large 做音频编码 | 资料说支持全身，没给小脸数据 | 没写 | 以单张图＋音频生成新视频，**不是对现成视频改口型** | 没查到 | 待验证；[HF 模型](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5)、[comfyui-wiki](https://comfyui-wiki.com/en/news/2026-05-21-longcat-video-avatar-1-5) |
| Wan2.2-S2V（2025-08，旧于一年） | 没写 | 全身、半身都支持 | 没写 | 整段重生成，可加 pose 视频约束身体（推断能减轻动作被改） | 单卡示例 ≥80GB | 待验证；见 2.2 节 |
| H3 原生说话 | 官方 11 种语言含中日 | — | — | 口型和动作一起生成，最自然 | 同 H3 | 本机已知坑：开口时刻被截止型时间码带偏、语速偏慢、会自编台词、会烧字幕（`学习笔记\10` 第 4、7、9 条）；**台词字字准确、每天固定音色做不到可控**（存在风险） |

**本机已知坑汇总**（都已验证）：
- 节点内部写死 25fps：进节点前先 ffmpeg 按时间重采到 25，出来再转回（memory `latentsync-25fps`）。
- 画里多张脸：只裁说话人脸框四周约 1.2 个脸宽送进去，否则挑最大那张脸（速查表第 986 行）。
- 闭嘴段会糊：只处理台词区间；不说话的脸要闭嘴就配静音再贴一次（速查表第 168、987 行）。
- 干声要单人（速查表第 989 行）。
- 拼片后字幕整段丢：LatentSync 输出没色彩信息，每段写死 bt709/tv，叠字幕加 `-reinit_filter 0`（速查表第 991–994 行）。
- `--upscale 2.5` 先放大再贴（速查表第 168 行）。

**给天气预报的推算（待验证）**：1920×1080 的全身站立主播，身高约占画面 85% 时脸宽通常只有 60–90px，正好落在「检测不到／嘴糊」区间。办法三选一（**需要用户确认**）：
1. 全身镜头按 4K（或 2560 宽以上）生成和对口型，再缩到 1080 输出，脸宽能到 150px 以上；
2. 剪辑上把「说话」放在半身近景，全身指地图时只说短句或不露正脸；
3. 全身镜头的口型改用整帧重生成方案（InfiniteTalk/S2V），代价是动作会被改。

侧脸（转身时）：LatentSync 本机已出过下唇扭曲。建议转身、侧身那几帧不安排台词，或者转身只占 0.5–1 秒、台词前后错开（推断，待验证）。

---

## 4. TTS

| 模型 | 日语 | 中文 | 时间戳 | 许可 | 标注与出处 |
|---|---|---|---|---|---|
| **IndexTTS-2.5**（本机定版） | 官方支持（中、英、日、西、阿）；可用 `<词|假名>` 控读音；日语分词器**不自动展开数字、日期、百分比**，要写成可读的日文 | 支持 | **不给**，只输出 22.05kHz 波形 | bilibili 模型许可；月活超 1 亿或年收入超 10 亿元人民币要另行授权（镜像资料） | 支持日语：已验证（[官方模型卡](https://huggingface.co/IndexTeam/IndexTTS-2.5)）；数字展开：资料（[vLLM recipe](https://recipes.vllm.ai/IndexTeam/IndexTTS-2.5)）；技术报告日语 WER 9.9%（RL 前）偏高（[arXiv 2601.03888](https://arxiv.org/html/2601.03888)）→ 日语错读**存在风险**；本机只测过中文（速查表第 119–120 行） |
| Qwen3-TTS（2026-01，Apache-2.0） | 10 种语言含日语；3 秒克隆 | 支持 | 没写 | Apache-2.0 | 待验证；[QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) |
| Fun-CosyVoice3-0.5B（2025-12，Apache-2.0） | 9 种语言含日语 | 支持，另有 18 种以上方言 | 没写 | Apache-2.0 | 待验证；[FunAudioLLM/CosyVoice](https://github.com/FunAudioLLM/CosyVoice) |
| Fish Audio S2 | 资料称 80+ 语言 | 支持 | 没查 | 研究许可，商用要另买（资料） | 待验证、**存在风险**（许可） |

**时间戳怎么拿**（我们有原稿文本，所以用「强制对齐」比「转写」准）：
1. **Qwen3-ForcedAligner-0.6B**：给音频＋文本出任意单位的时间戳，5 分钟以内，11 种语言含中日；Apache-2.0；官方自评优于 WhisperX、NeMo Forced Aligner（官方自评，待验证）。出处：[QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR)。
2. **faster-whisper `word_timestamps=True`**：sons02 的 `/home/sons/realtime_meeting/.venv` 已装 faster-whisper 1.1.0，Blackwell 上 CUDA 可用（已验证，memory `blackwell-faster-whisper-cuda`）。中日文的「词」实际接近字级，且转写可能和原稿不一致，要再按原稿对齐（待验证）。
3. 兜底：TTS 按句生成，每句一个文件，句级时间戳天然就有。天气预报里「说到城市名时手刚好指过去」只需要城市名的起点，句级＋句内字数比例估算可能就够（推算，待验证）。

**本机配音做法要沿用**：IndexTTS-2.5 照原脚本原参数；语速后期 `atempo` ≤1.18；句首留 80ms（速查表第 119–129 行）；台词不放破折号（会被念出来，memory `indextts-dash-read-aloud`）。

---

## 5. 视频合成

### 5.1 Remotion

- **许可原文**（已验证，[LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)）：免费许可适用于 "an individual"、"a for-profit organization with up to 3 employees"、"a non-profit or not-for-profit organization"；其余 "You are required to obtain a Company License to use Remotion"；"In Remotion 5.0, the license will slightly change."
- **人数怎么算**（已验证，[License FAQ](https://www.remotion.dev/docs/license/faq)）：按 3 人以内算；外包公司、自由职业者一起操作同一项目时人数合并，满 4 人就要买。客户只收 MP4 成品不算人头。
- **价格**（官方 FAQ）：Creators $25／人／月；Automators 每次渲染 $0.01、每月最低 $100；5.0 起 Automators 遥测强制开启。
- **运行环境**：Node.js（v4 迁移文档写最低 16，官方 Docker 示例用 Node 22）；FFmpeg 已内置不用另装；Chrome Headless Shell 由 `npx remotion browser ensure` 自动管理；Linux 要装一组共享库（Ubuntu 24.04 有清单），不支持 Alpine。出处：[Linux 依赖](https://www.remotion.dev/docs/miscellaneous/linux-dependencies)、[Chrome Headless Shell](https://www.remotion.dev/docs/chrome-headless-shell)。sons02 没装 node（全局 CLAUDE.md），本机 Windows 和 WSL 有 Node 24。
- **需要用户确认**：这个天气预报是个人项目还是公司项目、公司多少人。4 人以上的营利组织用 Remotion 要付费。

### 5.2 不用 Remotion 的替代

| 方案 | 许可 | 优点 | 缺点 | 标注 |
|---|---|---|---|---|
| **Python（Pillow / pycairo / skia-python）逐帧画 → FFmpeg 编码** | Pillow：HPND；FFmpeg：LGPL/GPL 看编译选项 | sons02 已有 Python 3.12 和 Pillow、Noto CJK 字体；和 LatentSync、TTS 同一套语言，全在 sons02 跑 | 动画缓动、文字排版要自己写 | Pillow、字体已验证（全局 CLAUDE.md）；FFmpeg 许可是常识，待验证 |
| FFmpeg filter_complex（overlay、drawtext） | 同上 | 叠主播透明视频、字幕、静态地图最快 | 复杂动画写起来很难维护 | 待验证 |
| Motion Canvas | MIT | 代码驱动动画，TypeScript | 渲染主要在浏览器编辑器里导出，无头批量渲染官方页面没写 | 许可已验证（[GitHub](https://github.com/motion-canvas/motion-canvas)）；无头渲染待验证 |
| Blender（Python 脚本驱动） | GPL（常识） | 地图可做 3D 倾斜、阴影 | 重 | 待验证 |

### 5.3 地图投影库

| 库 | 许可 | 标注 |
|---|---|---|
| d3-geo（JS） | ISC | 已验证（[licenses.dev d3-geo 3.1.1](https://licenses.dev/npm/d3-geo/3.1.1)） |
| pyproj / cartopy / shapely（Python） | MIT / BSD 系（常识） | 待验证 |
| 底图数据 Natural Earth | 公有领域（常识） | 待验证；日本细分县界若用国土数値情報，要看它的利用规约 → **需要用户确认** |

---

## 6. 指向检测（DWPose / RTMPose）

### 6.1 精度资料

DWPose 官方 COCO-WholeBody val 数字（已验证，[IDEA-Research/DWPose](https://github.com/IDEA-Research/DWPose)，Apache-2.0）：

| 模型 | 输入 | 身体 AP | 手 AP | 全身 AP |
|---|---|---|---|---|
| DWPose-l | 256×192 | 0.704 | 0.566 | 0.631 |
| DWPose-l | 384×288 | 0.722 | **0.621** | 0.665 |

**手是最差的一项**（手 AP 比身体低约 0.1）；RTMW 论文也说手因手指和手腕自由度多而难（[arXiv 2407.08634](https://arxiv.org/pdf/2407.08634)）。本机 sons02 的 `comfyui_controlnet_aux` 里有 DWPose（yolox_l + dw-ll_ucoco_384），**本地这一版有颜色通道颠倒、可能出空白骨架的 bug**（`模型学习\8190验证方案_控制变量_1106.md` 第 34 行），线稿人台提不出骨架（11-09 经验记录）。

### 6.2 常见做法（推算，待验证）

1. **主方向用「肘→腕」向量**，不用手指点。肘、腕属于身体关键点，置信度比手指高；延长线和地图平面求交，得到指向点。
2. **手指点只做辅助**：食指根（MCP）→食指尖向量和肘→腕向量夹角小（比如 <25°）才采用，否则退回肘→腕。
3. **保持段取中位数**：在「保持指向」的那 0.5–1 秒里逐帧算交点，取中位数，看标准差判断有没有漂。
4. **精度估算**：1080p 全身画面里前臂（肘到腕）约 100–140px；腕点误差 5–10px 时角度误差约 2–6°；指尖到城市距离 400px 时落点偏差约 15–40px（纯几何推算，**待验证**）。所以别靠「射线命中」去判准不准，而是**反过来用：量出指尖停住的位置，再把城市挪过去**（见第 7 节）。
5. **手指异常检测**：
   - 每只手 21 个点的置信度平均值低于阈值 → 标「需要人看」；
   - 指骨长度比例（同一手指相邻段长度比）超出正常范围、手指数量不对 → 可疑；
   - 同一人检出超过 2 只手（手框数量）→ 多手（本机 memory 有「两只手都占用会多画第三只」）；
   - 逐帧手部关键点跳变（帧间位移超过前臂长度的一定比例）→ 变形或闪烁；
   - **必须做反向对照**：拿已知好的和已知坏的片子各几条先测检测器本身（memory `detector-needs-negative-control`），只测好件会放行废片。
6. 手放大再检：把手腕周围裁出来放大到 256px 以上再单独跑手部模型，比整图跑准（常见做法，待验证）。

---

## 7. MVP 最稳的组合（我的建议）

**一句话：动作素材只做一次、地图跟着手走、口型只贴脸、合成用 Python+FFmpeg。**

1. **主播动作（方案 D，素材用 B 或 C 做）**
   - 先做一套动作素材：待机呼吸循环、正面播报（小幅手势）、转身朝地图、抬右手指向（3–5 个固定高度/方向，各带 1–2 秒保持）、放下手、转回正面。
   - 做法首选 **Viggle Remake**（本机测过、动作保真最高）：真人录一遍动作当驱动视频，1–4 张重画帧锁主播外观。备选 **fl2va 首中尾钉帧**（本机固定做法 B），尾帧是「指着」的姿势图。
   - 每段素材跑 DWPose，**记下保持段指尖的画面坐标**，存成 JSON。手指异常的素材当场淘汰。
2. **地图（程序化）**：Python 按投影画地图；每天按当天要讲的城市，挑最近的那段「指向」素材，**平移、缩放地图让城市落在记录的指尖坐标上**，再叠高亮圈和城市名。指向精度完全由程序保证。
3. **配音**：中文 IndexTTS-2.5（本机定版）；日语先用 IndexTTS-2.5 试（数字、日期改写成假名/汉字读法），日语错读多再试 Qwen3-TTS 或 CosyVoice3。时间戳用 Qwen3-ForcedAligner，兜底 faster-whisper。
4. **口型**：LatentSync 1.6 只贴台词区间。说话尽量安排在**半身或近景**（脸宽 ≥约 190px）；全身指地图时若要说话，按高分辨率出素材后再贴口型。转身那几帧不放台词。
5. **合成**：Python（Pillow/cairo）逐帧画地图、字幕、天气图标，FFmpeg 叠主播层（主播素材需要绿幕或抠像，抠像方案本次没调查）。避开 Remotion 的人数许可问题；如果确定是 3 人以内，用 Remotion 也行。

**我没调查到、但 MVP 会碰到的**：主播素材抠像（绿幕直出还是事后抠）；素材之间的接缝（首尾帧钉同一张待机图可以接上，本机有「整段钉帧」经验，但待机循环没测过）。

---

## 8. 需要用户确认的取舍

1. **动作能不能每天重复用**（决定能不能走 D）。
2. **全身镜头里要不要说话**：要的话得用 4K 级素材或接受整帧重生成改动身体；不要的话说话放在半身镜头。
3. **H3 商用条款**：若是商用产品，许可要求界面显著标「MiniMax H3」；年收入超 2000 万美元另授权。
4. **Remotion**：组织人数是否 ≤3；否则付费，或改走 Python+FFmpeg。
5. **IndexTTS-2.5 许可**：bilibili 模型许可，规模大要另授权；有疑问以官方 LICENSE 为准（我没读到官方原文，只读到镜像）。
6. **日本地图数据源**（Natural Earth 还是国土数値情報等）。
7. **真人录驱动动作谁来录**（方案 B 需要一段真人动作视频）；还是用 Mixamo 动作做灰模（方案 C，本机做过，但手指精度没量）。
8. 第一步实测要不要做（需要 sons02 显卡，要用户点名）：建议先测「Viggle 换人＋DWPose 量指尖保持段漂移」和「LatentSync 在 1080p 全身／4K 全身下的脸宽与口型」两项。

---

## 出处汇总（网上）

- [MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3) ／ [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- [H3 Fun ControlNet-Union 2.0](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union-2.0) ／ [ComfyUI 教程](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fun-controlnet)
- [Wan-Animate-2](https://github.com/Wan-Video/Wan-Animate-2) ／ [SCAIL-2 新闻](https://comfyui-wiki.com/en/news/2026-06-09-scail-2-character-animation) ／ [Wan2.2-S2V](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B)
- [LatentSync](https://github.com/bytedance/LatentSync) ／ [MuseTalk](https://github.com/TMElyralab/MuseTalk) ／ [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) ／ [LongCat-Video-Avatar 1.5](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5) ／ [开源对口型 2026 综述（Creeta，2026-07-09）](https://news.creeta.com/en/open-source-lip-sync-models-2026/)
- [IndexTTS-2.5](https://huggingface.co/IndexTeam/IndexTTS-2.5) ／ [技术报告](https://arxiv.org/html/2601.03888) ／ [vLLM recipe](https://recipes.vllm.ai/IndexTeam/IndexTTS-2.5) ／ [许可镜像](https://scancode-licensedb.aboutcode.org/bilibili-model-ula-2025-09-09.yml)
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) ／ [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) ／ [Qwen3-ASR / ForcedAligner](https://github.com/QwenLM/Qwen3-ASR)
- [Remotion LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) ／ [License FAQ](https://www.remotion.dev/docs/license/faq) ／ [Linux 依赖](https://www.remotion.dev/docs/miscellaneous/linux-dependencies)
- [Motion Canvas](https://github.com/motion-canvas/motion-canvas) ／ [d3-geo 许可](https://licenses.dev/npm/d3-geo/3.1.1)
- [DWPose](https://github.com/IDEA-Research/DWPose) ／ [RTMW 论文](https://arxiv.org/pdf/2407.08634)
