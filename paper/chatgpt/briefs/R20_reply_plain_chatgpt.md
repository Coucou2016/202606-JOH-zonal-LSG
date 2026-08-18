# R20 reply — ChatGPT figure↔code dual review (round 10)

Archived verbatim from the "图片代码双审 马会" ChatGPT session, 2026-08-19.

---

我按 R20 核心修改 d866f79、brief revision d9e5821 重新检查了 manuscript、lsg/eoi.py、zoning/plotting 逻辑、audit pack，并复看了 17 张 PNG。总体判断：R19 的 #2、#3、#4、#5 已按原问题闭环；#1 provenance 仍有一个版本号残留；#6 official two-fold 的正文已经闭环，但 Figure 7 caption 开头还残留一个统计术语冲突。另发现一个新的 EOI 文档精度问题。R20 没有新的数值或实际绘图错误。

1. **Figures 1–17｜全部 PNG｜provenance / audit-pack 版本链【中高】**：pack 内的图像、代码和数值链接现在确实统一 pin 到 60b2e18，但 header 仍写 Audit-pack revision: 4dd8800，而 d866f79 本身又实际修改了 figure_code_audit_pack.md；同时 d866f79 也修改了 manuscript，所以继续写 "Figure/manuscript baseline = 60b2e18" 会把"图/数值 baseline"和"当前文字 revision"混在一起。修复建议：header 最终拆成 `Figure/data baseline: 60b2e18; Manuscript revision: d866f79; Audit-pack revision: d866f79; R20 brief revision: d9e5821`。

2. **Figure 7｜fig12_stat_ci.png｜统计表达 / caption 内部一致性【中】**：§3.3、Results、Discussion 已正确把 official 2-fold 定义成 descriptive event-level bootstrap interval，并明确同 fold 的两个 held-out events 共用 fitted model，因此不是 independent-sample CI；但 Figure 7 caption 第一行仍统称四行结果为 "95% bootstrap confidence intervals"，随后第二句又说 official row "do not provide an independent-sample confidence interval"，存在自我冲突。修复建议：caption 开头改成 "95% bootstrap intervals for the mean paired ΔRMSE …"，随后分别称 Carlisle/Burnett LOOCV 为 fold-bootstrap confidence intervals、official 2-fold 为 descriptive event-level interval。

3. **Figures 15–16｜fig14_eoi.png / fig15_eoi_vs_delta.png｜代码文档精度【低中，新发现】**：Methods §2.4 现在已经非常精确地先定义 event-averaged absolute residual r̄ᵢ(S)，再基于该空间场计算 EOI；实际实现也先对事件取 mean(abs(LF-HF), axis=0)。但 eoi.py 顶层 docstring 仍写成简写的 Var(zone-mean |LF−HF|) / Var(cell |LF−HF|)，同时只称 "active wet mask"，没有把"至少一次 HF wet + non-zero across-event variation"的完整条件带过来。计算没错，但代码文档比论文定义少了一层关键运算顺序。修复建议：让 eoi.py 顶层 docstring 直接使用 r̄ᵢ(S)=mean_e |LF−HF|，并把 active-mask 两个条件写全，与 §2.4 一字义对应。

4. **Figure 15｜fig14_eoi.png｜caption self-containment【低】**：与上一项类似，Methods 已消除了"cell-event variance"歧义，但 Fig. 15 caption 又退回到较简略的 "across-zone-mean residual variance / cellwise residual variance"；单独摘出图片时，仍可能被理解为直接对所有 event×cell residual 求方差，而不是对 r̄ᵢ(S) 这张 event-averaged residual map 求空间方差。修复建议：把 caption 中这部分改成 "the unweighted variance across zone means of the event-averaged absolute-residual field r̄ᵢ(S), divided by the spatial variance of r̄ᵢ(S) over active cells"。

视觉层面我没有发现新的需要改图的问题。此前几个高风险点现在都稳定：Fig. 7 数字标签没有再压 whisker，Burnett +0.001 上界可以读出；Fig. 11 仍只有 0–3 四个 zone-ID 且两 panel 坐标格式一致；Fig. 12 是 0.695/0.167 canonical RMSE；Fig. 14 Carlisle inset 清晰；Fig. 16 hollow markers 后 Burnett 密集区的可读性可以接受，也没有重新引入任何 EOI threshold line。

因此这轮已经非常接近图件审计收口。真正值得做的只剩 #1 provenance 和 #2 Figure 7 caption；#3–#4 是定义文档的最后一层精确化，均不需要重算 EOI，也不需要重画 Figure 15/16。
