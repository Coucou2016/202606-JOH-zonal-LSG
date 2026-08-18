# R19 reply — ChatGPT figure↔code dual review (round 9)

Archived verbatim from the "图片代码双审 马会" ChatGPT session, 2026-08-19.

---

我以 核心 baseline 60b2e18 和 audit revision 4dd8800 分开重新核了 R19 brief、manuscript、EOI 实现/JSON、重建 audit pack，并逐张检查了 17 张 PNG。结论是：R18 的 #2 event-set scope、#3 n_events_used + scope、#4 Chowilla cross-pool caveat 已实质闭环；#1 provenance 和 #5 official two-fold 还各有一个很小的文字残留。此外新发现 2 个 EOI 定义精度问题。

1. **Figures 1–17｜全部 PNG｜provenance / audit-pack 内部一致性【中高】**：版本链概念已经正确分成 baseline=60b2e18 与 pack revision=4dd8800，但 R19 brief 里的 "Canonical pack URL" 仍指向 `60b2e18/.../figure_code_audit_pack.md`，该历史 commit 上实际还是旧 pack；同时 4dd8800 的新 pack 第 8 行还残留 "all links … pinned to 9e5887d"，虽然正文实际链接已经是 60b2e18。此外新 pack 的 Fig. 8 caption 仍漏了 manuscript 中的 "pooled 99th-percentile display cap"，Fig. 17 caption 仍漏了 "factor-1 independently refitted baseline"。修复建议：canonical pack URL 改 pin 到 4dd8800，header 明写 `Figure/manuscript baseline: 60b2e18; audit-pack revision: 4dd8800`，并再同步 Fig. 8/17 两处 caption。

2. **Figures 15–16｜fig14_eoi.png / fig15_eoi_vs_delta.png｜统计定义 / 代码↔Methods 精确性【中高，新发现】**：§2.4 现在已经正确改成对任意 event set 定义 EOI，但公式仍可能被读成"所有 event-cell absolute residual 的空间方差"；实际代码是先计算每个 cell 的跨事件平均绝对残差 r̄ᵢ(S) = |S|⁻¹ Σ_{e∈S} |h_LF,e,i − h_HF,e,i|，然后 numerator/denominator 都基于这张 event-averaged residual map 做空间方差。修复建议：在 §2.4 先显式定义 r̄ᵢ(S)，再写 EOI = Var_k(r̄ₖ) / Var_i(r̄ᵢ)，彻底消除 pooled cell-event variance 的歧义；无需重算任何数值。

3. **Figures 15–16｜fig14_eoi.png / fig15_eoi_vs_delta.png｜统计定义 / wet-mask 口径【中】**：Methods 现在只称 denominator 使用 "wet mask of the same event set"，但真实 `wet_cell_mask()` 不仅要求该 cell 在至少一个 HF event 中达到 0.03 m，还默认要求该 cell 在事件间具有非零 depth variation；因此实际 EOI active mask 比普通 "HF-wet union mask" 更窄。修复建议：§2.4 将 active mask 明确定义为 "wet in at least one HF event and exhibiting non-zero across-event depth variation"，或若 variation criterion 只是计算便利，则关闭该 criterion 后重新确认 EOI。

4. **Figures 15–16｜fig14_eoi.png / fig15_eoi_vs_delta.png｜代码文档 / scope 元数据【低中】**：R18 #3 的实际机器元数据已经正确——pooled JSON 为 `scope="all_event_pooled"`、fold JSON 为 `scope="train_only"`，字段也已统一为 `n_events_used`；但 eoi.py 文件级 docstring 第二行仍写 EOI 是在 "training wet mask" 上计算，与现在支持 pooled all-event scope 的实现不完全一致。修复建议：把该句改为 "on the active wet mask of the chosen event set"；这是纯文档修复。

5. **Figures 15–16｜fig14_eoi.png / fig15_eoi_vs_delta.png｜术语精度【低】**：manuscript 反复称 residual-free EOI zoning 为 "four-class hydrodynamic partition"，但代码实际上是最多四类的 rule scheme，空类不会进入 EOI；例如 Carlisle pooled EOI 当前只有 n_zones=3。这不是数值错误，但"四类分区"容易让读者以为每个 case/fold 必定存在四个 active zones。修复建议：统一改成 "residual-free hydrodynamic rule with up to four active classes"，或说明 empty classes are omitted。

6. **Figure 7｜fig12_stat_ci.png｜统计措辞 / official two-fold【中低，R18 #5 残留】**：§3.3 和 Fig. 7 caption 现在已经正确说明四个 event-level differences 中每两个共享一个 fitted fold model，并明确该区间是 descriptive、不是 independent-sample CI；但 Discussion §5.1 又写回 "Its confidence interval includes zero"，把刚刚限定掉的 inferential 含义重新带了回来。修复建议：将该句改为 "Its descriptive event-level bootstrap interval includes zero"；Results 中若出现裸写 "95% interval"，也建议统一成 "95% descriptive bootstrap interval"。

视觉方面，这一轮没有发现新的 plotting bug：Fig. 7 标签与 whisker 已分离；Fig. 11 zone colorbar 仍是 0–3 四档；Fig. 14 Carlisle inset 可读；Fig. 16 hollow-square 后 Burnett 密集区明显改善，而且继续不画 EOI threshold line 是合适的。

因此 R20 若只做投稿前收口，我建议优先处理 #2 + #3，因为它们关系到 EOI 数学定义能否被第三方精确复现；然后一次性修 #1 + #4 + #5 + #6 的 provenance/措辞即可。当前没有迹象需要重新计算 Figure 15/16 的 EOI 数值。
