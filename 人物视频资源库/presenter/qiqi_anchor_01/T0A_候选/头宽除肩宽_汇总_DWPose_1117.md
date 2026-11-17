# 七七 头宽 ÷ 肩宽 汇总（11-17）

- 算法：DWPose wholebody（ComfyUI controlnet_aux 里的 yolox_l.onnx＋dw-ll_ucoco_384.onnx，CPU 跑）。头宽＝脸部 68 点下颌轮廓最左点（第 0 点）到最右点（第 16 点）的距离，只量脸、不含头发；肩宽＝身体关键点右肩到左肩的距离，是肩关节中心，比衣服外沿窄。所以这个比值天生偏大：七七定版图自己就在 0.443–0.47。
- 按总督导给的线，**超过 0.4 的标红**；但这个量法下七七自己的定版图（含脸的准绳 front_a）全都超过 0.4，所以几乎每张都红。
- 用户说「头太大」的 r2_half_s293 是 **0.543**，正面图里第二高（最高是情绪表演 GPT 无奈 g_12 的 0.545，那张耸着肩、肩点被抬高）。按这个量法，「比定版图最大值 0.47 高出 10% 以上」约等于 **0.52**，能把 s293 这类挑出来。用哪条线请定。
- 侧面、背面这个比值没有意义（侧面两肩重叠，背面看不到下颌），只列数不判。

## 七七定版图（参照）

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| face_front_a.png | 285.1 | 643.7 | <span style="color:red">**0.443**</span> |
| front_b.png | 283.6 | 621.8 | <span style="color:red">**0.456**</span> |
| mid_b.png | 294.7 | 640.7 | <span style="color:red">**0.460**</span> |
| late_b.png | 286.9 | 642.2 | <span style="color:red">**0.447**</span> |
| full_front.png | 112.5 | 239.3 | <span style="color:red">**0.470**</span> |

## T0-A 第 1 轮 Qwen

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| qq_back_s263.png | 30.7 | 208.2 | —（0.147，侧／背面不适用） |
| qq_back_s269.png | 28.7 | 212.7 | —（0.135，侧／背面不适用） |
| qq_full_s229.png | 96.3 | 201.2 | <span style="color:red">**0.479**</span> |
| qq_full_s233.png | 97.1 | 198.2 | <span style="color:red">**0.490**</span> |
| qq_full_s239.png | 98.1 | 196.1 | <span style="color:red">**0.500**</span> |
| qq_full_s241.png | 97.2 | 194.4 | <span style="color:red">**0.500**</span> |
| qq_half_s251.png | 90.0 | 181.7 | <span style="color:red">**0.495**</span> |
| qq_half_s257.png | 92.3 | 177.0 | <span style="color:red">**0.521**</span> |
| qq_side_s263.png | 76.3 | 37.2 | —（2.05，侧／背面不适用） |
| qq_side_s269.png | 80.2 | 80.5 | —（0.996，侧／背面不适用） |

## T0-A 第 2 轮 Qwen

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| r2_full_s281.png | 100.9 | 195.2 | <span style="color:red">**0.517**</span> |
| r2_full_s283.png | 98.7 | 193.3 | <span style="color:red">**0.511**</span> |
| r2_half_s293.png | 123.4 | 227.4 | <span style="color:red">**0.543**</span> |
| r2_half_s307.png | 135.6 | 261.8 | <span style="color:red">**0.518**</span> |
| r2_heart_P003_s313.png | 159.8 | 316.5 | <span style="color:red">**0.505**</span> |
| r2_point_P022_s311.png | 156.0 | 299.0 | <span style="color:red">**0.522**</span> |

## T0-A 第 3 轮 GPT

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| g3_full_back.png | 32.3 | 226.5 | —（0.143，侧／背面不适用） |
| g3_full_front.png | 122.2 | 241.7 | <span style="color:red">**0.505**</span> |
| g3_full_side.png | 86.8 | 44.1 | —（1.967，侧／背面不适用） |
| g3_waist_half.png | 279.5 | 589.5 | <span style="color:red">**0.474**</span> |
| g3_waist_heart_P003.png | 273.6 | 548.2 | <span style="color:red">**0.499**</span> |
| g3_waist_point_P022.png | 284.3 | 540.2 | <span style="color:red">**0.526**</span> |

## T0-A 第 4 轮 Qwen

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| r4_A_s317.png | 90.7 | 186.9 | <span style="color:red">**0.485**</span> |
| r4_A_s331.png | 146.4 | 301.1 | <span style="color:red">**0.486**</span> |
| r4_B_s317.png | 92.6 | 185.0 | <span style="color:red">**0.501**</span> |
| r4_B_s331.png | 146.9 | 302.0 | <span style="color:red">**0.486**</span> |
| r4_C_EN_s317.png | 91.2 | 178.4 | <span style="color:red">**0.511**</span> |
| r4_C_s317.png | 129.8 | 273.3 | <span style="color:red">**0.475**</span> |
| r4_C_s331.png | 146.6 | 303.3 | <span style="color:red">**0.483**</span> |
| r4_D_s317.png | 118.0 | 227.9 | <span style="color:red">**0.518**</span> |
| r4_D_s331.png | 155.4 | 308.9 | <span style="color:red">**0.503**</span> |

## T0-A 第 4 轮 GPT

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| g4_A.png | 292.3 | 682.3 | <span style="color:red">**0.428**</span> |
| g4_B.png | 355.4 | 790.5 | <span style="color:red">**0.450**</span> |
| g4_C.png | 320.8 | 753.5 | <span style="color:red">**0.426**</span> |
| g4_D.png | 341.8 | 749.9 | <span style="color:red">**0.456**</span> |

## T0-A 第 5 轮

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| g5_E.png | 360.3 | 728.0 | <span style="color:red">**0.495**</span> |
| g5_F.png | 353.1 | 793.5 | <span style="color:red">**0.445**</span> |
| g5_G.png | 353.5 | 777.2 | <span style="color:red">**0.455**</span> |
| r5_E_s331.png | 216.5 | 436.3 | <span style="color:red">**0.496**</span> |
| r5_F_s331.png | 242.2 | 524.7 | <span style="color:red">**0.462**</span> |
| r5_G_s331.png | 165.3 | 337.0 | <span style="color:red">**0.490**</span> |

## 情绪表演 v2 GPT

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| g_01_kaixin.png | 278.1 | 568.6 | <span style="color:red">**0.489**</span> |
| g_02_daxiao.png | 284.6 | 545.2 | <span style="color:red">**0.522**</span> |
| g_03_jingya.png | 278.9 | 573.5 | <span style="color:red">**0.486**</span> |
| g_04_jingxi.png | 280.9 | 575.1 | <span style="color:red">**0.488**</span> |
| g_05_nanguo.png | 270.3 | 567.4 | <span style="color:red">**0.476**</span> |
| g_06_ku.png | 280.4 | 562.8 | <span style="color:red">**0.498**</span> |
| g_07_shengqi.png | 271.6 | 549.3 | <span style="color:red">**0.494**</span> |
| g_08_danxin.png | 289.5 | 605.2 | <span style="color:red">**0.478**</span> |
| g_09_haixiu.png | 264.1 | 600.9 | <span style="color:red">**0.439**</span> |
| g_10_sikao.png | 280.5 | 582.6 | <span style="color:red">**0.481**</span> |
| g_11_bobao.png | 268.3 | 551.9 | <span style="color:red">**0.486**</span> |
| g_12_wunai.png | 283.5 | 520.7 | <span style="color:red">**0.545**</span> |

## 情绪表演 v2 Qwen

| 图 | 头宽(px) | 肩宽(px) | 头宽÷肩宽 |
|---|---|---|---|
| q_01_kaixin_s337.png | 216.1 | 443.9 | <span style="color:red">**0.487**</span> |
| q_02_daxiao_s337.png | 242.5 | 529.8 | <span style="color:red">**0.458**</span> |
| q_03_jingya_s337.png | 252.7 | 556.8 | <span style="color:red">**0.454**</span> |
| q_04_jingxi_s337.png | 247.3 | 535.7 | <span style="color:red">**0.462**</span> |
| q_05_nanguo_s337.png | 262.2 | 547.4 | <span style="color:red">**0.479**</span> |
| q_06_ku_s337.png | 266.0 | 570.8 | <span style="color:red">**0.466**</span> |
| q_07_shengqi_s337.png | 241.4 | 525.4 | <span style="color:red">**0.459**</span> |
| q_08_danxin_s337.png | 223.4 | 481.8 | <span style="color:red">**0.464**</span> |
| q_09_haixiu_s337.png | 257.8 | 545.9 | <span style="color:red">**0.472**</span> |
| q_10_sikao_s337.png | 241.4 | 532.2 | <span style="color:red">**0.454**</span> |
| q_11_bobao_s337.png | 225.3 | 467.4 | <span style="color:red">**0.482**</span> |
| q_12_wunai_s337.png | 227.7 | 490.9 | <span style="color:red">**0.464**</span> |
