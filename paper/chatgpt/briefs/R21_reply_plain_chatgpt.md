# R21 reply — ChatGPT figure↔code dual review (round 11)

Archived verbatim from the "图片代码双审 马会" ChatGPT session, 2026-08-19.

---

结论：从科学内容、绘图代码、统计数值和实际 PNG 渲染看，R21 已经基本达到"图↔码审计收口"状态。我重新检查了 17 张图，R20 的四项均已实质闭环：Figure 7 caption 的 inferential/descriptive distinction 已正确拆开；§2.4 与 eoi.py 对 r̄ᵢ(S) 和 active mask 的定义一致；Figure 15 caption 已明确 event-averaged residual field；最新 HEAD 6462f90 的 pack header 也已正确 pin 到 e608559 manuscript。

不过我仍发现 3 个很小但具体的文字/provenance 残留。它们都不需要重算、不需要重画任何图。

1. **Figures 1–17｜全部 PNG｜provenance / canonical-pack pointer【低】**：最新 HEAD 6462f90 中的 pack header 本身已经修对，明确为 Figure/data baseline=60b2e18、Manuscript revision=e608559，manuscript URL 也正确 pin 到 e608559；但 R21 brief 的 "Canonical figure↔code pack" 仍指向历史版 e608559 pack，而真正包含最终 hash-pin header 的版本是在 6462f90。因此从 brief 点击 canonical link 会看到修 header 之前的版本。一句修复建议：把 R21 brief 的 canonical pack 指针改 pin 到 6462f90；其余 provenance 不必再动。

2. **Figure 7｜fig12_stat_ci.png｜统计表达 / Abstract consistency【中】**：Methods、Results、Figure 7 caption、Discussion 和 Conclusion 现在都正确把 official two-fold 的区间限定为 descriptive event-level bootstrap interval，并明确四个 held-out events 中每两个共享同一 fitted fold model；但 Abstract 仍写 "The corresponding official two-fold sensitivity analysis was not statistically significant." 这又赋予了该结果正式显著性检验的含义，与 R20/R21 刚收紧的推断边界不完全一致。一句修复建议：Abstract 改为类似 "The corresponding official two-fold sensitivity gave a much smaller difference, and its descriptive event-level bootstrap interval included zero."，不要再用 statistically significant。

3. **Figure 15｜fig14_eoi.png｜数据范围术语 / scope precision【中低】**：§2.4、§4.4、Fig. 15 caption 和 audit pack 均写 pooled EOI 使用 "all available events"，并列 Burnett n=30；但 manuscript 的 benchmark section 同时明确 Burnett archive 有 74 events，当前研究只使用其中一个 30-event max-surface extract。所以 "all available events" 对 Carlisle/Chowilla 尚容易理解，对 Burnett 则字面上会与 74-event archive 冲突。一句修复建议：统一改成 "all events available in the analysis extract" 或 "all events in the EOI analysis set (Carlisle n=9, Burnett n=30, Chowilla n=29)"；数值完全不变。

除此之外，我没有发现需要开启 R22 级别重新审图的问题。Figure 7 当前 error-bar 标签已经与 whisker 分离且 Burnett +0.001 上界可辨；Figure 11 是严格四档 zone ID；Figure 12 的 0.695/0.167 与 canonical LOOCV 口径一致；Figure 14 inset 已解决 Carlisle 尺度问题；Figure 15/16 的 EOI 定义、residual-free partition、train-only/all-event scope 与代码已经一致；Figure 16 hollow markers 的密集区也可接受。

因此我的判断是：图件和代码本身可以正式收口。上面 #1–#3 更适合作为一次最后的文字/元数据 commit 直接扫掉；处理后，我不建议继续做 R22 式逐图迭代，除非 manuscript 后续又发生会影响 figure/caption/data provenance 的实质修改。
