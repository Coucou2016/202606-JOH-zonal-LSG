# Citation audit (updated after ChatGPT formal analysis)

ChatGPT conversation: https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f  
Local extract: `paper/chatgpt/01_formal_analysis_extract.txt`

## PASS (independent DOI check)

| Citation | DOI | Decision |
|---|---|---|
| Fraehr et al. 2022 WRR | 10.1029/2022WR032248 | ADOPT |
| Fraehr et al. 2023 WRR | 10.1029/2022WR033836 | ADOPT |
| Fraehr et al. 2023 Nature Water | 10.1038/s44221-023-00132-2 | ADOPT (intro positioning) |
| Fraehr et al. 2024 Water Research | 10.1016/j.watres.2024.121202 | ADOPT |
| Fraehr et al. 2025 J. Environ. Manage. training events | 10.1016/j.jenvman.2024.123570 | ADOPT (related LSG design) |
| Figshare benchmark | 10.26188/24312658 | ADOPT (data) |
| Lu et al. 2025 JOH kernels | 10.1016/j.jhydrol.2025.132949 | ADOPT (JOH template) |
| Bentivoglio et al. 2022 HESS DL review | 10.5194/hess-26-4345-2022 | ADOPT (background only) |
| Teng et al. 2017 EMS | 10.1016/j.envsoft.2017.01.006 | ADOPT |
| Bates 2022 Annu. Rev. Fluid Mech. | 10.1146/annurev-fluid-030121-113138 | ADOPT |
| Carreau & Guinot 2021 Adv. Water Res. | 10.1016/j.advwatres.2020.103821 | ADOPT |
| Zhou et al. 2022 WRR USRR | 10.1029/2022WR033214 | ADOPT |
| Zhou et al. 2021 EMS SRR framework | 10.1016/j.envsoft.2021.105112 | ADOPT (confirm volume/pages in final bib) |
| Tan et al. 2025 HESS regionalized LSG | 10.5194/hess-29-3833-2025 | ADOPT as **novelty boundary** |
| Wang et al. 2025 REOF–SGP (IJDRS) | 10.1007/s13753-025-00642-5 | ADOPT as **localized EOF prior** (not equal-B zoning test) |
| Wang, Wang & Nathan WRR Brisbane strategies | 10.1029/2025WR042481 | ADOPT as related WRR template; **not** our Brisbane run; authors verified **Wen Wang, Quan J. Wang, Rory Nathan (2026)** |

## 2026-08-16 night re-verify (Cursor executor; DOI HEAD/GET)

| DOI | HTTP | Landing |
|---|---|---|
| 10.5194/hess-29-3833-2025 | 200 | hess.copernicus.org |
| 10.1007/s13753-025-00642-5 | 200 | Springer/IJDRS |
| 10.1029/2025WR042481 | 200 | AGU WRR |
| 10.1029/2022WR032248 | 200 | AGU WRR |
| 10.1016/j.watres.2024.121202 | 200 | Elsevier Water Research |

No DOI invented this round. Donnelly truncated DOI remains HOLD.

## HOLD / use carefully

| Item | Note |
|---|---|
| Donnelly et al. 2022 Water Research GP emulation | ChatGPT DOI truncated in UI; verify full DOI before final bib |
| Kabir / Xie / Liao / Chang JOH-CNN papers | Useful related work; add only if Intro needs breadth |
| Zhang et al. 2025 REOF–SGP | Related hybrid; optional |

## REJECT / novelty traps (ADOPT ChatGPT warning; local confirm)

| Trap | Why rejected |
|---|---|
| “First zonal / regionalized LSG” | Tan et al. 2025 already does regionalized LSG training |
| “First spatial reduction / localized EOF for flood surrogates” | Carreau–Guinot 2021; Zhou SRR/USRR; Wang et al. 2025 REOF–SGP |
| Loose “hydrodynamically neutral” as top-line claim | Prefer “performance-neutral representation choice” (EOF is statistical) |
| Head-to-head Rule Max 0.988 vs published LSG-TS 0.990 as equal comparison | Different Max vs TS / backend; sanity check only |
| Official 2-fold as primary significance | Track B: significant=false |
| CLEAN_PASS as novelty | Protocol hygiene, not contribution |
| Invented prior “equal-B stage-swap EOI” paper matching Track B | Not found |

## Local executor stance

ChatGPT framing ADOPTED for novelty: conditional equal-B zoning + EOI falsification + stage-swap mechanism + honest boundaries.  
Manuscript already rewritten Intro accordingly (`paper/manuscript.md`).
