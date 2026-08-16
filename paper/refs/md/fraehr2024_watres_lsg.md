# Fraehr et al. (2024) Water Research — abstract-only entry

> **全文未获取（自动化访问遇 ScienceDirect 机器人验证码；未绕过）。**  
> Crossref / Semantic Scholar 标注该文 **CC BY 4.0 / hybrid OA**，官方页面可人工下载，但本机自动化未拿到合法 PDF。

## Bibliographic record (DOI verified)

- **Authors:** Niels Fraehr, Quan J. Wang, Wenyan Wu, Rory Nathan  
- **Title:** Assessment of surrogate models for flood inundation: The physics-guided LSG model vs. state-of-the-art machine learning models  
- **Journal:** *Water Research*, 252, 121202 (2024)  
- **DOI:** https://doi.org/10.1016/j.watres.2024.121202  
- **PII (Crossref):** S0043135424001027  
- **PMID:** 38290237  
- **License (Crossref VOR):** Creative Commons Attribution 4.0 (`http://creativecommons.org/licenses/by/4.0/`)  
- **Official landing:** https://doi.org/10.1016/j.watres.2024.121202  
- **Local PDF:** *not saved* (`paper/refs/pdf/fraehr2024_watres_lsg.pdf` absent)  
- **Access status:** 摘要 + 书目 only（全文未获取）

## Abstract (PubMed / Semantic Scholar)

Hydrodynamic models can accurately simulate flood inundation but are limited by their high computational demand that scales non-linearly with model complexity, resolution, and domain size. Therefore, it is often not feasible to use high-resolution hydrodynamic models for real-time flood predictions or when a large number of predictions are needed for probabilistic flood design. Computationally efficient surrogate models have been developed to address this issue. The recently developed Low-fidelity, Spatial analysis, and Gaussian Process Learning (LSG) model has shown strong performance in both computational efficiency and simulation accuracy. The LSG model is a physics-guided surrogate model that simulates flood inundation by first using an extremely coarse and simplified (i.e. low-fidelity) hydrodynamic model to provide an initial estimate of flood inundation. Then, the low-fidelity estimate is upskilled via Empirical Orthogonal Functions (EOF) analysis and Sparse Gaussian Process models to provide accurate high-resolution predictions. Despite the promising results achieved thus far, the LSG model has not been benchmarked against other surrogate models. Such a comparison is needed to fully understand the value of the LSG model and to provide guidance for future research efforts in flood inundation simulation. This study compares the LSG model to four state-of-the-art surrogate flood inundation models. The surrogate models are assessed for their ability to simulate the temporal and spatial evolution of flood inundation for events both within and beyond the range used for model training. The models are evaluated for three distinct case studies in Australia and the United Kingdom. The LSG model is found to be superior in accuracy for both flood extent and water depth, including when applied to flood events outside the range of training data used, while achieving high computational efficiency. In addition, the low-fidelity model is found to play a crucial role in achieving the overall superior performance of the LSG model.

## Why this paper is our #1 structural / data reference

- **Data:** public Fraehr Figshare benchmark (Carlisle / Chowilla / Burnett) used by `lsg/fraehr.py`.  
- **Cases & multi-site paradigm:** three-case assessment is the template for our Table 1–2 / Fig. 4.  
- **Method baseline:** global LSG (LF → EOF → Sparse GP) that our Global LSG-Max reproduces conceptually.  
- **Writing / results form:** problem → method modules → multi-case results → honest comparison with other surrogates.

## Acquisition attempts (lawful only; stopped at CAPTCHA)

| Attempt | Result |
|---|---|
| Unpaywall API | `is_oa=true`, CC-BY, but `url_for_pdf=null` |
| nature-downloader `--open-access --no-si` | `oa_not_found` |
| ScienceDirect `/pdf` & `/pdfft` (correct PII) | HTTP 403 HTML |
| Elsevier API PDF (no key) | HTTP 406 |
| Browser → ScienceDirect landing | **“Are you a robot?” CAPTCHA** → stopped per policy |
| Semantic Scholar `openAccessPdf` | points to DOI landing only, not a binary PDF |

**Human next step:** open https://doi.org/10.1016/j.watres.2024.121202 in a normal browser, complete any challenge if shown, download the CC BY PDF, save as `paper/refs/pdf/fraehr2024_watres_lsg.pdf`, then re-run `paper/refs/_pdf_to_md.py` (after adding a job entry).
