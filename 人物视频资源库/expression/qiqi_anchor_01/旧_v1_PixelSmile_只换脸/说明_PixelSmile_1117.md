# 七七表情库（PixelSmile，11-17）

本次做法＝照官方 `Ammmob/PixelSmile` 的 `pixelsmile/infer.py` 和 `linear_conditioning.py` 的参数，在 :8191 上用 ComfyUI 搭出来。原件＝官方 infer.py。与原件不同之处见下面「和官方不一样的地方」。

## 模型

- LoRA：HF `PixelSmile/PixelSmile` 的 `PixelSmile-preview.safetensors`，849543736 字节，sha256 `9bb2f7981e8cd59a5d6e31c2ca08cc0961ac46c267b81af9bce7f8d542ca319a`，和 HF 上登记的一致。下载走的是公开地址，没带任何登录凭证。
- 放在 sons02 `learn_nodes/pixelsmile/loras/`，只给 :8191 用。`extra.yaml` 里加了 `pixelsmile` 一段；改之前的原样备份在 `learn_nodes/旧_extra_1117_加pixelsmile前.yaml`。

## 官方怎么接线（读的是官方代码原文）

- **中性图和目标图不是两张图。** 只喂一张输入图。编码两次提示词，两次都带这张图：目标句 `Edit the person to show a {表情} expression`，中性句 `Edit the person to show a neutral expression`。
- **强度不是 LoRA 强度。** LoRA 固定 1.0。强度 s 加在提示词编码上，官方默认的 `score_one_all` 是把两段编码按「中性 + s ×（目标 − 中性）」混合。我用 ComfyUI 自带的 ConditioningAverage 节点做这一步（to＝目标，from＝中性，to_strength＝s），公式一样。没装社区节点。
- **采样参数：** 50 步，true_cfg_scale 0，也就是 cfg 1、不用负面提示词；种子 42。输入图先缩到 512×512；输出尺寸官方没给，管线默认按 1024×1024 面积算，所以出 1024×1024。
- **表情只有 12 个：** angry、confused、contempt、confident、disgust、fear、happy、sad、shy、sleepy、surprised、anxious。官方 README 示例的强度是 0、0.5、1.0、1.5。
- 社区那份 ComfyUI 工作流用的是 Lightning 8 步，照你说的不算数，没照它。

## 和官方不一样的地方

1. **底模：** 官方用 diffusers bf16 整模。我们用盘上的 ComfyUI 版 `qwen_image_edit_2511_fp8mixed`，文字编码器 `qwen_2.5_vl_7b_fp8_scaled`，VAE `qwen_image_vae`。原因有两个：官方环境锁死 torch 2.6，跑不了我们这块 Blackwell 卡；bf16 整模还得另下约 58 GB。
2. **调度：** 官方是 FlowMatch 动态 shift。我按 1024×1024 算出 shift＝2.0008，填进 ModelSamplingAuraFlow。官方配置里还有一项 shift_terminal 0.02，ComfyUI 里没有对应的项，所以没做。
3. **参考潜变量方式：** 用 index_timestep_zero。2511 的配置里写的是 zero_cond_t＝true，这和 diffusers 的做法一致。
4. **输入图：** 官方是整张图从中间裁成 512。我们照你的要求先裁成胸像，再缩到 512。
5. **第一批作废：** 第一批我误把输出设成 512×512，出来的脸被放大、构图变了，那批作废，挪到 `模型学习\PixelSmile_1117\旧_512\`。表情库里的都是 1024 那批。

## 看到的（原尺寸看过）

- **开心：** 0.0–0.5 基本看不出笑，0.6 是闭嘴浅笑，0.8 露出牙齿，1.0 大笑。变化集中在 0.5 到 0.6 之间，不是均匀变的。最像真人主播浅笑的是 **0.6**。
- **认真（confident 代）：** 0.3 接近平静、略微严肃，0.4 开始皱眉，0.6 已经像不耐烦。播报能用的只有 0.3。
- **关切（anxious 代）：** 0.4 眉头轻皱，0.6 皱眉加撇嘴。
- **惊喜（surprised 代）：** 0.3、0.4 几乎看不出来，0.6 直接张大嘴，像受了惊吓，不像惊喜。官方没有「惊喜」这一项，surprised 不是这个意思。
- **难过（sad，加测）：** 0.6 撇嘴、下巴皱。
- **平静：** 强度 0，也就是只用中性那句提示词。
- **脸会变：** 原图胸像和 front_a 的相似度是 0.849，出来的图是 0.44–0.76。连强度 0（只改成中性表情）也掉到 0.618。说明即使不加表情，经这条管线过一遍脸就会变一截；表情越大，掉得越多。官方说能保脸，但用我们这套 fp8 底模没做到。
- 很多负面表情都带着下巴皱起、撇嘴，看起来有点赌气。

## 文件

- 16 张出图。`表情库.jsonl` 每张一行，记了表情、强度、来源图和喂入图的 md5、模型、参数、种子、和 front_a 的相似度、用时、显存。
- `qq_bust_512_来源.png`：实际喂进去的胸像。
- `联系表_七七表情_PixelSmile_1117.jpg`：每个表情一行，按强度从左到右排。
- 脚本：`模型学习\PixelSmile_1117\pixelsmile_run.py`。

**每张的数：** 用时 36–45 秒，8188 同时在出图时到 60–84 秒。进程峰值约 29.6 GB，整卡峰值 35–74 GB（高的那几次是 8188 同时在跑）。
