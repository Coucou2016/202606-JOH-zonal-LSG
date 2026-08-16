# -*- coding: utf-8 -*-
"""Deep per-figure / per-panel Chinese explanations for the full research report.

Used only by scripts/99_full_report_zh.py. Numbers are injected from Track B data
dicts — do not hard-code conflicting values here without reading JSON.
"""
from __future__ import annotations


def fmt(v, spec=".4f"):
    if isinstance(v, (int, float)):
        return format(float(v), spec)
    return str(v)


def deep_explains(d: dict) -> dict[str, str]:
    """Return HTML explanation blocks keyed by figure filename."""
    G4, R4, K4 = d["G4"], d["R4"], d["K4"]
    G6, R6, K6 = d["G6"], d["R6"], d["K6"]
    G8, R8, K8 = d["G8"], d["R8"], d["K8"]
    LF = d["LF"]
    impr4 = d["impr4"]
    L4, L6 = d["L4"], d["L6"]
    official = d["official"]
    eoi_ts = float(d.get("eoi_ts", 0.51))
    eoi_max = d.get("eoi_max") or {}
    eoi_c = float(eoi_max.get("carlisle", float("nan")))
    eoi_w = float(eoi_max.get("chowilla", float("nan")))
    eoi_bmax = float(eoi_max.get("burnettrv", float("nan")))
    bloo = d["bloo_rule"]
    csi = d["csi"]
    cb = d["cb"]
    ch_lf, ch_g, ch_r = d["ch_lf"], d["ch_g"], d["ch_r"]
    b_lf, b_g, b_r = d["b_lf"], d["b_g"], d["b_r"]
    ss = d.get("stage_swap") or {}
    ss_sum = ((ss.get("loocv") or {}).get("summary") or {})
    gg_m = (ss_sum.get("GG") or {}).get("mean_rmse")
    zz_m = (ss_sum.get("ZZ") or {}).get("mean_rmse")
    gz_m = (ss_sum.get("GZ") or {}).get("mean_rmse")
    zg_m = (ss_sum.get("ZG") or {}).get("mean_rmse")

    out = {}

    out["fig01_workflow.png"] = f"""
<p><strong>（a）本图在全篇中的作用。</strong>它不给出可引用的 RMSE，而是把“分区发生在哪一步”钉死：分区必须发生在经验正交函数（Empirical Orthogonal Function，EOF）与高斯过程（Gaussian Process，GP）之前。若只在事后误差图上按区上色，分区只是诊断，不能改变模态所张成的空间。</p>
<p><strong>（b）如何读流程对照图。</strong>左列是全局 LSG（Low-fidelity–Spatial analysis–Gaussian Process，低保真—空间分析—高斯过程）：低保真（Low-Fidelity，LF）场插值到高保真（High-Fidelity，HF）网格 → 全部湿单元一次全局 EOF → 一个 GP 把 LF 展开系数映射到 HF 系数 → 重建最大淹没面（LSG-Max）。右列在 EOF/GP 前插入水动力分区（规则或 KMeans），每区各自 EOF+GP，再拼回整张水面。</p>
<p><strong>（c）元素含义。</strong>“湿单元”指水深 ≥ 0.03 m 的格子；EOF 把多场最大水深矩阵分解为空间模态与事件系数；GP 在低维系数空间学习 LF→HF。模态预算 B 是两边允许使用的总模态数上限。</p>
<p><strong>（d）能得出什么结论。</strong>方法学结论是：本文检验的是“表示空间是否水动力中性”，不是“再发明一种 GP”。示意图本身不含 Track B 数字。</p>
<p><strong>（e）给非专业读者。</strong>可以把它想成：先把整张洪水地图当成一张照片压成几笔素描（全局），还是先把河道、滩地、边缘分开，各自压成几笔再拼回去（分区）。后面所有真实验都在回答：在素描笔数（B）一样多时，哪一种更准。</p>
<p class="note">本图来自示意管线，不可当作论文 RMSE。可引用数字以 registry 与 JSON 为准。</p>
"""

    out["fig02_zone_maps_real.png"] = f"""
<p><strong>（a）背景与作用。</strong>证明分区发生在真实 Carlisle 几何（LISFLOOD-FP，581,061 格）上，而不是 30×40 玩具网格。它给读者建立“水从哪来、往哪摊”的空间直觉，并为后文规则/KMeans 对照提供视觉锚点。</p>
<p><strong>（b）如何读多面板地图。</strong>先看地形高低与河道走向，再看颜色分区是否贴合主槽与滩地，最后读湿单元计数条/饼，理解各区样本量是否极度不均。</p>
<p><strong>（c）子图含义。</strong>
<ul>
<li><strong>子图 (a) 地形：</strong>东西向深色带为主槽输送通道；两侧黄褐为滩地与阶地。读图时应沿河道走一遍，再看南北高地。</li>
<li><strong>子图 (b) K=4 湿区：</strong>蓝色大致贴主槽，粉红细带追随河道，青色大块在北侧连续滩地，红色破碎区对应深浅交错滩地。颜色≠行政区，而是训练期特征聚类。</li>
<li><strong>子图 (c) 湿单元计数：</strong>四区合计湿单元约 238,946（约占全网格四成）。区占比大致约 42.0% / 23.5% / 7.4% / 27.1%。小区往往是全局模态最容易“牺牲”的特殊力学区。</li>
</ul></p>
<p><strong>（d）结论。</strong>真实泛滥平原的湿区结构高度异质；把全部湿单元塞进同一组 EOF，等于强迫深槽与边缘浅水共享同一组正交基。</p>
<p><strong>（e）日常语言。</strong>河道像高速公路，滩地像停车场，边缘像偶尔积水的路肩。硬用同一套“素描笔”同时画这三类地方，笔数一紧就容易画糊。</p>
<p>图题中的平均 |LF−HF| 量级与仅用 LF 的 RMSE {fmt(LF)} m 同属“LF 已不太差、但仍有结构误差”的故事，二者不是同一指标。规则分区地图未单独成图，其物理切法见表 2 的 E2。</p>
"""

    out["fig03_mode_budget.png"] = f"""
<p><strong>（a）背景与作用。</strong>这是 Carlisle 等预算主证据的核心曲线：在总模态数 B 相同的前提下，全局、规则分区、KMeans 的面积加权 RMSE 如何随 B 变化。它直接回答标题“全局 EOF 何时不够”。</p>
<p><strong>（b）如何读 RMSE–B 曲线。</strong>横轴离散取 B=4/6/8（不是连续光滑函数）；纵轴越小越好。比较三条线的高度差（谁更准）与斜率（加模态是帮还是害）。</p>
<p><strong>（c）曲线含义。</strong>圆点实线=全局；方点虚线=规则；三角点线=KMeans。B=4：全局 {fmt(G4)} m，规则 {fmt(R4)} m（相对降幅 {impr4:.1f}%），KMeans {fmt(K4)} m。B=6：全局跳至 {fmt(G6)} m；B=8：全局 {fmt(G8)} m，规则 {fmt(R8)} m 仍最低。全局 B=8 实际模态仅 7（审计 MISMATCH），即便少用 1 个仍最差。</p>
<p><strong>（d）结论。</strong>在 Carlisle、等预算下，<strong>增加全局模态不是补救，而是过拟合</strong>。分区把有限 B 分配到更均匀的子域，相当于给每个子问题更合适的秩（隐式容量约束）。</p>
<p><strong>（e）日常语言。</strong>考试复习时，把全部精力花在背噪音细节，分数可能更差；把精力按章节分开复习，往往更稳。B 就是“复习时间总量”，分区就是按章节分配。</p>
"""

    out["fig09_csi_budget.png"] = f"""
<p><strong>（a）背景与作用。</strong>防止只报对自己有利的 RMSE。临界成功指数（Critical Success Index，CSI）衡量 0.03 m 阈值下的湿/干范围命中，惩罚漏报与空报。</p>
<p><strong>（b）如何读。</strong>纵轴越大越好；灰线为仅用 LF。看 LSG 三条线是否越过 LF，以及分区是否系统性更高。</p>
<p><strong>（c）数值。</strong>仅用 LF 的 CSI={fmt(csi['lf'])}；B=4 时全局 {fmt(csi['g4'])}、规则 {fmt(csi['r4'])}、KMeans {fmt(csi['k4'])}，均低于 LF。JSON 显示 LSG 探测率（POD）接近 1，但空报率（FAR）更高。</p>
<p><strong>（d）结论。</strong>分区主要校准<strong>水深数值</strong>，并不自动赢得湿干范围。摘要必须以 RMSE 为主，CSI 作诚实对照。</p>
<p><strong>（e）日常语言。</strong>好比天气预报：雨量预报准了（RMSE），不代表“会不会下雨”的范围预报（CSI）也全面更好；模型可能把一些浅水格判得偏湿。</p>
"""

    out["fig13_mae_bias.png"] = f"""
<p><strong>（a）作用。</strong>把“过拟合”从单一 RMSE 扩展到平均绝对误差（Mean Absolute Error，MAE）与偏差（bias）：多模态是否把整张水面系统推偏。</p>
<p><strong>（b）读法。</strong>左图 MAE（对极端格不如 RMSE 敏感）；右图偏差（正=预测偏深，负=偏浅）。关注符号翻转与分区是否贴零线。</p>
<p><strong>（c）含义。</strong>左图形态与 RMSE 图相似：全局随 B 上升最快。右图：全局 B=4 偏差 {fmt(cb['budgets']['4']['global']['bias_area'])} m，B=8 变为 {fmt(cb['budgets']['8']['global']['bias_area'])} m（符号翻转并增大）；规则偏差始终更近 0。</p>
<p><strong>（d）结论。</strong>多出来的全局模态不是“补细结构”，而是把系统偏差推离 HF——支持容量误用叙事。</p>
<p><strong>（e）日常语言。</strong>不是某一处画错一点，而是整张图被整体涂深或涂浅了。</p>
"""

    out["fig08_per_event_bootstrap.png"] = f"""
<p><strong>（a）作用。</strong>把表 3 的“平均好看”升级为“每一场留出事件是否都更好”。这是统计主声称（9 折事件 LOOCV）的可视化。</p>
<p><strong>（b）读法。</strong>横轴事件 0–8；纵轴该折检验 RMSE。实线=全局 B=4，虚线=规则 B=4。逐点确认虚线是否始终更低。</p>
<p><strong>（c）关键点。</strong>9/9 折分区更优；事件 1 全局尖峰约 {fmt(L4['items'][1]['global_rmse'])} m，规则压回约 {fmt(L4['items'][1]['zonal_rmse'])} m（单折 Δ≈{fmt(L4['items'][1]['delta_rmse'])} m）。平均 ΔRMSE={fmt(L4['mean'])} m，95% 自助法区间 [{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]。</p>
<p><strong>（d）结论。</strong>改善包含“一场全局失败被分区救回”，不是每场都小幅磨一点。这也解释官方 2 折为何可能不显著：若没抽到事件 1 类灾难点，均值会被拉平。</p>
<p><strong>（e）日常语言。</strong>九次考试里，分区每次都更高分；其中有一次全局考砸到接近 0.7 m 误差，分区把它拉回来。</p>
<p class="note">文件名含 bootstrap，本图绘制的是逐折 RMSE；区间数字以表 4 与森林图为准。</p>
"""

    out["fig11_loocv_scatter.png"] = f"""
<p><strong>（a）作用。</strong>用 1:1 散点把九折结果压成“是否系统性地落在对角线下方”。</p>
<p><strong>（b）读法。</strong>横轴全局 RMSE，纵轴规则 RMSE；虚线 1:1。点在下方=分区更好；远离原点=该折误差大。</p>
<p><strong>（c）含义。</strong>九点全在下方；事件 1 远离原点，贡献大部分平均增益。</p>
<p><strong>（d）结论。</strong>方向一致（9/9）+ 含灾难折救援 → 支持把 9 折 LOOCV 作为主声称。</p>
<p><strong>（e）日常语言。</strong>每个点是一场“盲测洪水”。全部落在“分区更准”一侧，且有一场差距特别大。</p>
"""

    out["fig12_stat_ci.png"] = f"""
<p><strong>（a）作用。</strong>把四种检验协议画成森林图（forest plot）：一眼看出谁能当主声称、谁必须诚实写不显著。</p>
<p><strong>（b）读法。</strong>横轴平均 ΔRMSE=全局−分区；正=分区更好。须（误差条）为 95% 自助法区间；跨过 0 就不能声称显著。</p>
<p><strong>（c）四行。</strong>
<ul>
<li>Carlisle B=4：[{fmt(L4['ci'][0])}, {fmt(L4['ci'][1])}]，不含 0，{L4['improved']}/{L4['n']} 折改善。</li>
<li>Carlisle B=6：[{fmt(L6['ci'][0])}, {fmt(L6['ci'][1])}]，仍显著但均值更小。</li>
<li>官方 2 折：均值 {fmt(official['mean_delta_rmse'])}，区间 [{fmt(official['ci_95_lower'])}, {fmt(official['ci_95_upper'])}]，跨 0，significant=false。</li>
<li>Burnett 30 折：均值 {fmt(bloo['mean_delta_rmse'])}，区间跨 0，仅 6/30 折分区更好。</li>
</ul></p>
<p><strong>（d）结论。</strong>可辩护的主声称是 Carlisle 事件级 9 折；官方 2 折与 Burnett 不得改写成“也显著”。</p>
<p><strong>（e）日常语言。</strong>像四场比赛的净胜分：前两场稳定赢且置信区间不碰平局线；后两场可能略赢或略输，但统计上分不清。</p>
"""

    out["fig04_three_case.png"] = f"""
<p><strong>（a）作用。</strong>全文“地图”：成功（Carlisle）、无额外增益（Burnett）、帮倒忙（Chowilla）三种模式并列，防止把三案例都写成分区成功。</p>
<p><strong>（b）读法。</strong>每组三柱：蓝=仅用 LF，橙=全局 LSG，绿=规则分区。只在<strong>组内</strong>比相对高低；组间绝对高度反映洪水尺度，不宜直接比输赢。</p>
<p><strong>（c）数值。</strong>Carlisle：{fmt(LF)} / {fmt(G4)} / {fmt(R4)} m。Chowilla：LF {fmt(ch_lf)} m，LSG≈{fmt(ch_g)} m（橙绿几乎重叠冲高）。Burnett（12 事件划分）：LF {fmt(b_lf)} m，全局≈规则≈{fmt(b_g)} m。</p>
<p><strong>（d）结论。</strong>分区收益是<strong>条件性</strong>的；Novelty 应写成等预算条件性分区+边界诚实报告，勿写“首次 zonal LSG”。</p>
<p><strong>（e）日常语言。</strong>三个城市用同一套“校正眼镜”：甲城明显更清晰；乙城戴不戴分区镜差不多；丙城一戴反而更糊——说明眼镜不是万金油。</p>
"""

    out["fig10_burnett_loocv.png"] = f"""
<p><strong>（a）作用。</strong>负例主图：高一阶 EOI（{eoi_bmax:.3f}）并不保证等预算分区获益。</p>
<p><strong>（b）读法。</strong>对照 Carlisle 图 6：这里两条线应纠缠而非系统分离。纵轴到数米是洪水尺度使然。</p>
<p><strong>（c）数值。</strong>30 折均值：全局 {fmt(bloo['mean_global_rmse'])} m，规则 {fmt(bloo['mean_zonal_rmse'])} m，Δ={fmt(bloo['mean_delta_rmse'])} m（负=分区更差），6/30 折，区间含 0。</p>
<p><strong>（d）结论。</strong>高 EOI 在此度量的是 LF 系统性偏移的空间组织；B=4 切成每区约 1 个模态无法消化米级偏差。一阶 EOI 不能当分区开关。</p>
<p><strong>（e）日常语言。</strong>误差虽然“成块”，但每块错得太深、样本又被切碎，分区反而帮倒忙或无益。</p>
"""

    out["fig08_runtime.png"] = f"""
<p><strong>（a）作用。</strong>精度–代价前沿：规则分区是否“稍慢一点、明显更准”。</p>
<p><strong>（b）读法。</strong>横轴墙钟时间（秒），纵轴 RMSE。左下更优。</p>
<p><strong>（c）要点。</strong>仅用 LF≈0 s、RMSE≈{fmt(LF)} m；全局约 0.7–0.9 s；规则 B=4≈1.3 s、RMSE≈{fmt(R4)} m；KMeans 约 7–9 s。JSON：B=4 全局 {fmt(cb['budgets']['4']['global']['time_s'], '.2f')} s，规则 {fmt(cb['budgets']['4']['rule']['time_s'], '.2f')} s，KMeans {fmt(cb['budgets']['4']['kmeans']['time_s'], '.2f')} s。</p>
<p><strong>（d）结论。</strong>规则分区几乎不增加计算负担即可获得主要 RMSE 收益；KMeans 更贵且 B=8 时又慢又差。</p>
<p><strong>（e）日常语言。</strong>花一点额外时间按河道结构切区，比花很多时间做复杂聚类更划算。</p>
"""

    out["fig14_eoi.png"] = f"""
<p><strong>（a）作用。</strong>展示三案例最大淹没面残差组织指数（Error Organization Index，EOI=区间方差/总方差），并对照预注册高结构阈值 0.30。</p>
<p><strong>（b）读法。</strong>柱越高=残差越“成块”。若 EOI 是分区开关，应看到高 EOI→高增益；本图将被后文证伪。</p>
<p><strong>（c）数值。</strong>Carlisle {eoi_c:.3f}（低），Chowilla {eoi_w:.3f}（低），Burnett {eoi_bmax:.3f}（高）。历史时序 EOI（Carlisle {eoi_ts:.2f}）是另一协议，不可与最大面混用。</p>
<p><strong>（d）结论。</strong>若用本图先验筛选，会预测 Burnett 该分区、Carlisle 不该——与表 3/30 折恰好相反。一阶 EOI 只是描述统计，不是部署开关。</p>
<p><strong>（e）日常语言。</strong>知道“错误成片出现”不等于知道“切开就能修好”。</p>
"""

    out["fig15_eoi_vs_delta.png"] = f"""
<p><strong>（a）作用。</strong>在折内直接检验“更高训练期 EOI → 更大规则分区 ΔRMSE”。</p>
<p><strong>（b）读法。</strong>横轴折内 EOI，纵轴 ΔRMSE（正=分区更好）。正斜率才支持开关假说。</p>
<p><strong>（c）观察。</strong>点云不呈正斜率；Carlisle/Burnett 折级相关约为负（约 −0.58 / −0.43，见正文）。</p>
<p><strong>（d）结论。</strong>在最大面、等预算 B=4 协议下，直接否证“高 EOI→分区获益”。</p>
<p><strong>（e）日常语言。</strong>把“残差成块程度”和“分区有没有帮上忙”画在一起，看不出越成块越有用。</p>
"""

    out["fig19_modal_eoi.png"] = f"""
<p><strong>（a）作用。</strong>二阶诊断：区–全局解释方差缺口（Zone–Global Gap，ZGG）与等预算纯 EOF 重建 oracle（无 GP）。用来回答收益是否来自“分区把 HF 截断得更好”。</p>
<p><strong>（b）读法。</strong>ZGG&gt;0 表示局部基在区内解释力高于同秩全局基；oracle ΔRMSE&gt;0 才表示纯截断也让分区更好。</p>
<p><strong>（c）登记结果。</strong>三案例 ZGG 均为正，但 oracle ΔRMSE 均为负（Carlisle −0.076 m，Burnett −0.198 m，Chowilla −0.066 m）→ 判读 ZGG_POSITIVE_ORACLE_LOSS。</p>
<p><strong>（d）结论。</strong>排除“等预算纯 EOF 截断变好”。Carlisle 上 LSG 分区增益必须在耦合的 LF→HF 管线里解释（与 stage-swap 一致），而不是更好的 HF-EOF 截断。</p>
<p><strong>（e）日常语言。</strong>光把照片按区域分开压缩，并不会自动更像原图；要在“用粗图去猜细图”的学习步骤里引入分区结构，收益才出现。</p>
"""

    out["fig16_official_maxwd_r2.png"] = f"""
<p><strong>（a）作用。</strong>在 Fraehr 官方湿网格/九折协议上，把本文 LSG-Max 与已发表五模型的最大水深 R²（MaxWD R²）对照。</p>
<p><strong>（b）读法。</strong>R² 越近 1 越好。注意：已发表 RMSE 多为时序湿网格指标，不可与本文面积加权 RMSE 混比；本图主比 MaxWD R² / CSI。</p>
<p><strong>（c）数值。</strong>已发表 LSG-TS MaxWD R²≈0.990；本文规则 LSG-Max≈0.988；全局 LSG-Max≈0.915（被事件 1 类折拉低）。CSI：已发表 LSG-TS≈0.937 vs 本文规则≈0.905（已发表另有独立范围模型）。</p>
<p><strong>（d）结论。</strong>在最大面协议上，规则分区接近已发表时序 LSG 的峰值水深技巧；不等于已经复现全部 LSG-TS 产品能力。</p>
<p><strong>（e）日常语言。</strong>同一张“期末卷”上，分区版最大水深打分已经贴近名校时序模型，但范围题仍略逊。</p>
"""

    out["fig17_lf_degradation.png"] = f"""
<p><strong>（a）作用。</strong>稳健性探针：LF 网格空间加粗（×1/×2/×4）后，仅用 LF / 全局 / 规则是否同步崩溃。</p>
<p><strong>（b）读法。</strong>横轴加粗倍数，纵轴 RMSE。关注规则线是否几乎水平。</p>
<p><strong>（c）要点。</strong>×1：LF≈0.160、全局≈0.146、规则≈0.094 m。×2：LF→0.274，规则几乎不动。×4：LF→0.667，规则≈0.103 m。</p>
<p><strong>（d）结论。</strong>分区 LSG 对 LF 变粗不敏感，因为它学的是系统偏差流形，不是复制 LF 细节。</p>
<p><strong>（e）日常语言。</strong>粗地图越来越糊，但“粗→细”的校正器仍能工作，只要粗图还抓住主导地形。</p>
"""

    out["fig18_channel_distance.png"] = f"""
<p><strong>（a）作用。</strong>可公开复现的物理切区：距主槽线（Carlisle_MCL）距离带，对比纯规则与残差热点。</p>
<p><strong>（b）读法。</strong>比较各分区方案的面积加权 RMSE/CSI；越低越好。</p>
<p><strong>（c）要点。</strong>规则+主槽距离≈0.094 m，略优于纯规则≈0.096 m；仅用距离四分位带≈0.112 m，仍明显优于全局≈0.146 m。</p>
<p><strong>（d）结论。</strong>物理河道距离不使用检验期残差，泄漏风险低于残差热点叠加，是备选切区。</p>
<p><strong>（e）日常语言。</strong>按“离河多远”切区，几乎不输按水深–频率规则，说明水动力先验本身就有用。</p>
"""

    # Synthetic / conflict appendix figures — deepen pedagogy, keep non-citable
    out["fig03_eof_variance.png"] = """
<p><strong>（a）本图角色。</strong>附录教学图：用累计解释方差说明“分区后局部场往往更简单”，帮助理解为何等预算下局部基可能更省秩。它<strong>不是</strong> Track B 主证据。</p>
<p><strong>（b）如何读。</strong>横轴模态数、纵轴累计方差比例；对比全局曲线与分区曲线的爬升速度。爬升越快，说明同样方差可用更少模态覆盖。</p>
<p><strong>（c）子图/曲线含义。</strong>若分区曲线在低模态处更高，表示局部同质性；若全局曲线缓慢爬升，表示异质湿区共享一组基时需要更多秩。务必区分两件事：达到某一累计解释方差所需的模态数 ≠ 等预算实验中强制对齐的总保留模态数 B。前者是方差解释，后者是公平比较约束。</p>
<p><strong>（d）能/不能得出的结论。</strong>能：建立“分区可能降低所需秩”的直觉。不能：用本图声称真实 Carlisle 需要数十个全局模态，也不能用其数字替代表 3 的面积加权 RMSE。</p>
<p><strong>（e）与正文对齐。</strong>真实等预算实验锁在 B=4/6/8（见 fig03_mode_budget）。引用请改去那张 Track B 曲线。</p>
<p class="note">协议标签：合成/示意 · 数字不可引用 · 仅教学。该图用于说明诊断量/算法流程的读取方式；其合成案例中的方向性结果不参与 Track B 实证推断，若与公开基准结果不一致，以 Track B 真实案例为准。</p>
"""
    out["fig04_metric_boxplots.png"] = """
<p><strong>（a）本图角色。</strong>附录箱线对照，提醒读者存在 LSG-TS（全时段）与 LSG-Max（最大面）两条产品线；本文主结果只锁 Max。</p>
<p><strong>（b）如何读箱线。</strong>每个箱子的抽样单位是折/事件（非网格单元）。箱体=四分位距（IQR），中线=中位数（≠面积加权均值），须=1.5×IQR 惯例，点=离群折。若面板同时出现 TS 与 Max，必须先分清协议再比高低；方向上 RMSE 越小越好、CSI 越大越好。</p>
<p><strong>（c）子图含义。</strong>各指标面板只反映该图生成时所用网格与变体。真实数据上的全时段分区 LSG-TS 仍为【待补充】，故箱线中位数不可替换表 3。</p>
<p><strong>（d）结论边界。</strong>可用作“不要把 Max 写成 TS”的警示；不可用作投稿主结果。</p>
<p><strong>（e）日常语言。</strong>这是练习册上的示意图，不是期末考试成绩单。</p>
<p class="note">协议标签：合成/混协议风险 · 数字不可引用。该图用于说明诊断量/算法流程的读取方式；其合成案例中的方向性结果不参与 Track B 实证推断，若与公开基准结果不一致，以 Track B 真实案例为准。</p>
"""
    out["fig06_zone_metrics.png"] = """
<p><strong>（a）本图角色。</strong>展示“分区分误差”方向与假说一致（深槽/边缘误差形态不同），属于早期概念验证。</p>
<p><strong>（b）如何读。</strong>先确认区定义（训练期水深/频率或 KMeans），再读各区面积或湿单元占比，最后读局地 RMSE/CSI。区级指标如何汇总到全域面积加权值，必须以面积 A<sub>i</sub> 加权，不能对各区取算术平均冒充全域。</p>
<p><strong>（c）数据来源。</strong>数值来自 30×40 玩具网格，不是 Carlisle 581,061 格的面积加权 Track B。</p>
<p><strong>（d）结论边界。</strong>方向可教学；幅度不可引用。真实分区分误差请回到等预算 LOOCV 与面积加权表。</p>
<p><strong>（e）日常语言。</strong>像沙盘推演：格局对，但不能拿沙盘上的厘米当真实城市的米。</p>
<p class="note">协议标签：合成 · 数字不可引用。该图用于说明诊断量/算法流程的读取方式；其合成案例中的方向性结果不参与 Track B 实证推断，若与公开基准结果不一致，以 Track B 真实案例为准。</p>
"""
    out["fig07_budget_zones.png"] = f"""
<p><strong>（a）本图角色。</strong>历史草稿图，曾试图同时展示预算与分区数；现与 Track B 真等预算曲线<strong>冲突</strong>，仅保留供审计对照。</p>
<p><strong>（b）冲突点。</strong>本图左翼全局几乎水平；真等预算中全局 RMSE 从 {fmt(G4)} m（B=4）升到 {fmt(G8)} m（B=8）。若读者只看本图，会误以为“加全局模态无害”。</p>
<p><strong>（c）面板语义。</strong>读任何子图前先确认：纵轴是 RMSE 还是 CSI、参考场是 HF 还是 LF、差值符号（正=分区更好还是全局更好）、湿掩膜是否共用。本图不承载机制证明。</p>
<p><strong>（d）结论。</strong>保留冲突图是为了防止旧图回流进正文，不是提供第二套可引用结果。</p>
<p><strong>（e）日常语言。</strong>这是被更正作废的旧成绩单复印件，钉在墙上只为提醒“别再用它”。</p>
<p class="note">协议标签：与 Track B 冲突 · 禁止引用数字。该图用于说明诊断量/算法流程的读取方式；其合成案例中的方向性结果不参与 Track B 实证推断，若与公开基准结果不一致，以 Track B 真实案例为准。</p>
"""
    out["fig07_training_size.png"] = f"""
<p><strong>（a）本图角色。</strong>合成敏感性示意：训练事件比例变化时全局/分区曲线如何移动。</p>
<p><strong>（b）读法陷阱。</strong>图上全局 RMSE 约 0.03–0.05 m，与真实 Carlisle 仅用 LF 的 {fmt(LF)} m 不在同一实验量级。</p>
<p><strong>（c）子图含义。</strong>横轴训练比例、纵轴误差；若分区曲线更低，只说明该玩具设定下的样本效率假说，不能外推真实案例。面板色标/线型勿与 Track B 预算图混读。</p>
<p><strong>（d）结论边界。</strong>不能声称“真实 Carlisle 上分区更样本高效”。真实主证据仍是等预算 B=4 的 9 折 LOOCV。</p>
<p><strong>（e）日常语言。</strong>练习题里的“少做几套卷子也能考好”，不能直接写成真实考场结论。</p>
<p class="note">协议标签：合成 · 数字不可引用。该图用于说明诊断量/算法流程的读取方式；其合成案例中的方向性结果不参与 Track B 实证推断，若与公开基准结果不一致，以 Track B 真实案例为准。</p>
"""

    # Stage-swap narrative block (not a figure file, but used by 99)
    if gg_m is not None:
        out["_stage_swap_html"] = f"""
<p>阶段互换（stage-swap）把 LSG 管线拆成两段：<strong>表示</strong>（EOF 坐标）与<strong>映射</strong>（GP）。四臂定义为：</p>
<ul>
<li><span class="term">GG</span>：全局 EOF + 全局 GP（基线）；</li>
<li><span class="term">ZZ</span>：分区 EOF + 分区 GP（完整规则分区）；</li>
<li><span class="term">GZ</span>：全局 EOF（切到各区并 QR 正交化）+ 分区 GP（近似）；</li>
<li><span class="term">ZG</span>：分区 EOF 系数拼接 + 单个全局风格 GP 栈（近似）。</li>
</ul>
<p>若收益<strong>仅仅</strong>来自区私有 GP，应观察到 GZ≈ZZ≪GG 且 ZG≈GG。实际 9 折 LOOCV 均值：GG≈{fmt(gg_m)} m，ZZ≈{fmt(zz_m)} m，GZ≈{fmt(gz_m)} m，ZG≈{fmt(zg_m)} m，即 <strong>GZ≈ZG≈ZZ≪GG</strong>。任一段引入分区结构，几乎收回全部 ZZ 增益。</p>
<p>与纯 EOF oracle（ΔRMSE&lt;0）合读：收益不是“HF 截断变好”，而是分区结构进入耦合的<strong>表示→映射</strong>管线。GZ/ZG 为强近似（见 JSON limitations），故不能把收益唯一钉死在区私有 GP 上；推荐表述与 <code>stage_swap.json</code> 的 recommended_wording 一致。</p>
<p><strong>给非专业读者：</strong>校正流水线有两道工序——“用什么坐标系描述水面”和“如何把粗系数翻译成细系数”。只要其中一道按河道/滩地分开处理，Carlisle 上的大部分好处就会回来；两道都分开（ZZ）是完整方案，但不是唯一有效开关。</p>
"""
    else:
        out["_stage_swap_html"] = '<p class="pending">【待补充】未找到 stage_swap.json 的 LOOCV 摘要。</p>'

    return out


def deep_glossary_html() -> str:
    return """
<h3 id="s2-3">2.4　术语与符号全量溯源（授课式）</h3>
<p>下列条目在正文首次出现处已给简称；此处集中给出物理意义、理论溯源与本文引入原因，避免裸缩写。</p>
<ul>
<li><span class="term">HF / LF</span>（High-/Low-Fidelity）：高/低保真水动力模型。HF 网格细、物理过程更完整但贵；LF 粗网格或简化求解，快但有系统偏差。多保真的出发点是保留 LF 的物理轮廓，再学习指向 HF 的修正。</li>
<li><span class="term">EOF</span>（Empirical Orthogonal Function，经验正交函数）：对时空/多事件场的协方差做特征分解，得到按方差排序的空间模态与系数。气象海洋学中的经典降维工具；在 LSG 中用于把高维淹没面压到少数系数，以便 GP 学习。等价视角是 PCA（Principal Component Analysis，主成分分析）作用于湿单元集合。</li>
<li><span class="term">GP / GPR / SGPR</span>：高斯过程回归把函数先验放在函数空间，用核（kernel）编码平滑与相关长度；后验给出映射与不确定度。SGPR（Sparse GP Regression）用诱导点近似以服务大数据。本文 Track B 数字来自 sklearn GPR；gpflow SGPR【待补充】。</li>
<li><span class="term">LSG / LSG-Max / LSG-TS</span>：Fraehr 框架三步（LF 场 → 空间 EOF → GP 系数映射）。Max 只学最大淹没面；TS 学全时段。本文主结果为 LSG-Max；真实数据分区 LSG-TS【待补充】。</li>
<li><span class="term">模态预算 B</span>：全局与分区模型允许的 EOF 模态总数。真等预算要求两边实际总模态数对齐，否则“分区更好”可能只是参数更多。</li>
<li><span class="term">面积加权 RMSE / MAE / bias</span>：误差按网格面积 A<sub>i</sub> 加权，避免大小格子一视同仁。RMSE 对大误差更敏感；MAE 更稳健；bias 揭示系统偏深/偏浅。</li>
<li><span class="term">CSI / POD / FAR</span>：临界成功指数 / 探测率 / 空报率，基于湿润阈值 0.03 m 的二值命中表。CSI=Hit/(Hit+Miss+FA)。</li>
<li><span class="term">EOI</span>（Error Organization Index）：区间方差/总方差。度量残差是否成块。本文强调：最大面一阶 EOI 不能当分区开关；时序 EOI 与最大面 EOI 协议不同。</li>
<li><span class="term">ZGG</span>（Zone–Global Gap）：二阶诊断，比较区局部基与同秩全局基在区内的解释方差缺口。</li>
<li><span class="term">stage-swap（GG/ZZ/GZ/ZG）</span>：交叉表示与映射的区/全局属性，定位收益落在管线哪一段。</li>
<li><span class="term">LOOCV</span>：按事件留一交叉验证；ΔRMSE=RMSE<sub>global</sub>−RMSE<sub>zonal</sub>，正值表示分区更好。</li>
<li><span class="term">规则分区 / KMeans</span>：规则用训练期最大水深与淹没频率切深槽、常淹、间歇、边缘；KMeans 在训练特征上聚 K=4。二者均不得看见检验事件。</li>
</ul>
"""
