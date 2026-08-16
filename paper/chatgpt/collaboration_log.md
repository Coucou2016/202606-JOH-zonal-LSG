# ChatGPT collaboration log — JOH zonal LSG paper workline

**Date:** 2026-08-16  
**Local executor:** Cursor agent  
**External advisor:** ChatGPT Pro (`pjn xdq Pro`)  
**Git:** no commit / push / PR

## Conversation 1 — Literature + framework + novelty

| Field | Value |
|---|---|
| URL | https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f |
| Title | 学术顾问任务确认 |
| Web search | Enabled; UI showed “已搜索 15/17 个网站” |
| Protocol | CONTEXT 1/3 → 2/3 → 3/3 then formal A–D |

### Adopt / reject

| Item | Decision | Note |
|---|---|---|
| Keep web-search + primary DOI discipline | ADOPT | |
| Track B numbers as locked facts | ADOPT | |
| Novelty ≠ “first zonal LSG” | ADOPT | Tan et al. 2025 HESS regionalized training is real prior art |
| Novelty = conditional equal-B + EOI falsification + stage-swap mechanism + boundaries | ADOPT | Aligned with Track B |
| Prefer JOH first; WRR if stronger mechanism story | ADOPT (working) | |
| Official 2-fold as primary claim | REJECT | significant=false |
| Max R² 0.988 vs published TS 0.990 as head-to-head | REJECT as equal comparison | Sanity check only |
| CLEAN_PASS as novelty | REJECT | |
| Fraehr Nature Water / WRR / Water Research / JEM / Lu JOH / Carreau / Zhou / Tan HESS / Wang WRR Brisbane | ADOPT after DOI check | See `refs/citation_audit.md` |
| Truncated Donnelly DOI in UI paste | HOLD | Verify before final bib |
| Clipboard pollution from other agent prompts | N/A | Ignored |

### Related prior chats (context only, not fact sources)

- https://chatgpt.com/c/6a809da8-ea3c-83ea-8625-a8cdc145b4e9 — Zonal LSG Analysis
- Sidebar project: `LSG WRR paper`

---

## Conversation 1 — Round 2 progress audit (2026-08-16 PM)

| Field | Value |
|---|---|
| URL | https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f (same thread) |
| Web search | Enabled; UI showed searching ~16 sites |
| Tasks | Novelty re-check; manuscript argument-chain critique; Chinese-report figure deepen list |

### Adopt / reject (local executor)

| Item | Decision | Note |
|---|---|---|
| Novelty package still defensible; verdict **TWEAK** | ADOPT | No 2024–2026 killer of equal-B + EOI falsification + stage-swap combo |
| Prefer “performance-neutral representation choice” | ADOPT | Applied in manuscript |
| Soften “residual structure & capacity interact” | ADOPT | Replaced with coupled pipeline wording |
| Title “Insufficient in” vs “for” | ADOPT | Applied |
| Add Wang et al. 2025 REOF–SGP | ADOPT after DOI check | 10.1007/s13753-025-00642-5 |
| Discussion spine: drop “why larger Global B hurts” as Q2 | ADOPT | Reframed Q1–Q3 |
| EOI = exploratory falsification | ADOPT | Methods wording |
| 9-fold = principal paired stability; 2-fold = sensitivity | ADOPT | Avoid appearing to demote official split only because n.s. |
| stage-swap ≠ four production models | ADOPT | Methods wording |
| Deepen synthetic appendix figs a–e + standard disclaimer | ADOPT | `_deep_fig_zh.py` |
| Claim transferable zoning selector exists | REJECT | Explicitly stated as not established |
| gpflow/SGPR required before any draft | HOLD / pending | Flagged limitation; not blocking this audit round |
| Public GitHub for ChatGPT | N/A | No remote configured; text CONTEXT only |

---

## Conversation 1 — Round 3 GitHub publish + review (2026-08-16 evening)

| Field | Value |
|---|---|
| URL | https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f (intended same thread) |
| Also attempted | New chat with web search ON; UI repeatedly redirected to unrelated threads (XAJ-Snow / hemodynamics) |
| Web search | Requested; prior rounds in this thread already used web search |
| GitHub | https://github.com/Coucou2016/202606-JOH-zonal-LSG (public) |
| ChatGPT GitHub read | **NOT confirmed this round** — browser automation could not complete a clean send/receive proving raw.githubusercontent.com access. Do not claim ChatGPT read the repo. Fallback: text CONTEXT + local independent DOI checks. |

### Local independent DOI checks (executor)

| Item | Verdict | Evidence |
|---|---|---|
| Tan et al. 2025 HESS 10.5194/hess-29-3833-2025 | PASS | Copernicus HESS page; regionalized LSG training for velocity DR error — blocks “first zonal LSG” |
| Wang et al. 2025 IJDRS 10.1007/s13753-025-00642-5 | PASS | Springer/HEP; REOF–SGP LF–EOF–SGP pipeline; authors include Li & Liu (seed list updated) |
| Fraehr / Lu / Zhou / Carreau / Bentivoglio seed DOIs | HOLD from prior audit | See `refs/citation_audit.md` |

### Adopt / reject (this round)

| Item | Decision | Note |
|---|---|---|
| Publish public GitHub baseline | ADOPT | Done: commit `3e2059f` + follow-up push |
| Deepen synthetic fig captions (eof_variance / boxplots / zone_metrics / fig07_*) | ADOPT | From prior ChatGPT deepen list + local pedagogy |
| Claim ChatGPT successfully read GitHub | REJECT | No proof this round |
| “First zonal LSG” | REJECT | Tan + Wang prior art |
| Invent transferable zoning selector | REJECT | Still not established |

---

## Conversation 1 — Round 4 GitHub-read closed loop (2026-08-16 late)

| Field | Value |
|---|---|
| URL | https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f （同一线程；未串到无关会话） |
| Web search | Enabled；回复含 raw.githubusercontent.com / GitHub / HESS / Springer 等引用芯片 |
| GitHub | https://github.com/Coucou2016/202606-JOH-zonal-LSG （public，`master` @ `f692bf1`） |
| **GitHub 读取** | **成功** |

### 读取证明（ChatGPT 原文要点；本地已核对）

1. `paper/manuscript.md` Discussion **Q2** 标题为 “Why can zoning help when it does?”；pure-EOF oracle 排除 truncation-only。  
2. `lsg/eoi.py` 存在函数 **`modal_subspace_diagnostic()`**，注释定义 ZGG + equal-budget pure-EOF oracle。  
3. `outputs/evaluation/carlisle/stage_swap.json`：`B=4`；LOOCV means GG/ZZ/GZ/ZG ≈ **0.18023 / 0.09789 / 0.09798 / 0.10096**；hypothesis 为 mapping-only 假说被双侧 zoning 否决。  

注：ChatGPT 称当时抓到的 `master` raw 状态行仍显示 v0.2、故改用 `f692bf1` commit-specific raw；**本地用 `urllib` 拉取 `master/paper/manuscript.md` 确为 v0.3**（可能为其侧缓存/指针歧义）。证明条目本身与仓库内容一致。

### Local independent DOI checks (this round)

| DOI | Verdict |
|---|---|
| 10.1029/2022WR032248 | PASS (HTTP 200 → AGU) |
| 10.1016/j.watres.2024.121202 | PASS |
| 10.1016/j.jhydrol.2025.132949 | PASS |
| 10.5194/hess-29-3833-2025 | PASS |
| 10.1007/s13753-025-00642-5 | PASS |
| 10.1016/j.envsoft.2025.106654 | PASS |
| 10.5194/hess-30-459-2026 | PASS |
| 10.1029/2025WR042481 | PASS；作者确认为 **Wen Wang, Quan J. Wang, Rory Nathan (2026)** |
| 10.1016/j.envsoft.2025.106562 | PASS |

### Adopt / reject (local executor)

| Item | Decision | Note |
|---|---|---|
| Novelty package ADOPT + TWEAK；禁止 “首次 zonal LSG” | ADOPT | 与既有锁定一致 |
| B=8 退出 “true equal-B”；改 audited protocol | ADOPT | `paper/manuscript.md` §2.3 / Abstract / Conclusion 2 |
| EOI：`pre-fit` → training-data diagnostic；修 `eoi.py` docstring | ADOPT | manuscript + `lsg/eoi.py` |
| ZGG docstring 去掉 “needs its own basis” | ADOPT | `lsg/eoi.py` |
| 正文写明 GZ/ZG 为 diagnostic approximations | ADOPT | manuscript §2.4 / §3.4 |
| framework Q2 同步为 “Why can zoning help…” | ADOPT | `paper/framework.md` |
| 软化中文 fig03/fig13/fig10 过拟合/容量误用/无法消化句 | ADOPT | `scripts/_deep_fig_zh.py` + `99_full_report_zh.py`；已重跑 `99` |
| MaxWD 0.988 vs 0.990 加 not head-to-head | ADOPT | manuscript §3.5 |
| Ref 14 作者/年份修正 | ADOPT | verified DOI page |
| Abstract “Most evaluations treat…performance-neutral” 心理立场句 | ADOPT | 改为 baseline commonly employ… |
| 中文 §5.1 标题“真等预算”→预算对照与审计；表 4 CI 措辞 | ADOPT | `99_full_report_zh.py` |
| 中文 Burnett/Chowilla 机制过强句 | ADOPT | 改为未唯一识别 / LSG-vs-LF 边界 |
| 新增 Taghizadeh / Markert 进正文参考文献表 | HOLD | DOI PASS；非本轮最小必需；可后续补 bib |
| Claim transferable zoning selector | REJECT | |
| Push / commit | **未做** | 默认仅本地；paper/scripts 已改但未强制同步 remote |
