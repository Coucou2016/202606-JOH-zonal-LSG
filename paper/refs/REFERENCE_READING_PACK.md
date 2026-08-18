# 参考阅读包 — JOH zonal LSG 新论文

**仓库：** `I:\Projects\202606-JOH-zonal-LSG`  
**生成日期：** 2026-08-16（**2026-08-17 更新：用户手工提供 3 份 PDF，Fraehr 2024 全文阻塞已解除**）  
**用途：** 供用户审阅「我们实际建立在哪几篇之上」，并对照图/表/分析范式是否模仿到位。  
**Git：** 仅本地新增文件，**未 commit / 未 push**。  
**SI：** 本批未下载 Supporting Information（正文阅读包；`--no-si`）。

---

## 0. 核心结论（先看这里）

**我们这篇新论文主要模仿的结构与呈现范式，是 Fraehr et al. (2024) *Water Research*（LSG vs 其他代理模型、Carlisle/Chowilla/Burnett 三案例评估）。**  
方法骨架来自 **Fraehr et al. (2022) WRR**（LF + EOF + GP = LSG）。  
**Tan et al. (2025) HESS** 是 novelty boundary（已有 regionalized LSG），不是结构模仿对象。

| 排序 | 角色 | 论文 | 获取状态 |
|---:|---|---|---|
| **1** | **主要模仿对象（结构/数据/案例/结果呈现）** | Fraehr et al. 2024 *Water Research* | **全文 PDF + MD**（2026-08-17 用户提供） |
| **2** | **方法起源（LSG 公式与工作流）** | Fraehr et al. 2022 *WRR* | **全文 PDF + MD** |
| **3** | **Novelty boundary（regionalized LSG 先例）** | Tan et al. 2025 *HESS* | **全文 PDF + MD** |
| 4 | LSG 谱系（时序 LSG 全流程） | Fraehr et al. 2023a *WRR* | **全文 PDF + MD**（2026-08-17 用户提供） |
| 5 | 训练事件生成/选择（可用于 Limitations 与 SI 论证） | Fraehr et al. 2025 *J. Environ. Manage.* | **全文 PDF + MD**（2026-08-17 用户提供） |

次要但不进本阅读包全文：Wang et al. 2025 REOF–SGP（局部化 EOF 先例）；Lu et al. 2025 JOH（写作模板：固定 LSG 框 → 内部设计选择）；Fraehr 2023b *Nature Water*；Wang–Wang–Nathan WRR Brisbane strategies。

> **说明（2026-08-17）：** 用户手工放入 `paper/refs/pdf/` 的 3 份 PDF 身份已由 PDF 文本层（标题 + DOI）逐一核实，未凭文件名假设，核实脚本 `paper/refs/_identify_pdfs.py`。其中 `1-s2.0-S0043135424001027-main.pdf` 即此前被 ScienceDirect 验证码阻塞的 **Fraehr 2024**；另两份此前不在阅读包内，属新增。

---

## 1. 排序清单：为何这几篇是「实际参考」

依据：`paper/manuscript.md`、`paper/framework.md`、`paper/refs/citation_audit.md`、`paper/chatgpt/*`，以及 `lsg/fraehr.py` / `lsg/fraehr_metrics.py` / `lsg/baseline_lsg.py` / `lsg/zonal_lsg.py`。

### 主要（1–3）

| # | 论文 | 我们借了什么 |
|---:|---|---|
| 1 | **Fraehr et al. 2024** Water Research DOI `10.1016/j.watres.2024.121202` | **数据**（Figshare 三案例）、**案例角色**（Carlisle/Chowilla/Burnett）、**全局 LSG 基线与评测叙事**、**多案例结果表/误差图呈现**。`framework.md` 写明 imitated architecture 以 Fraehr WRR/Water Research 为主。代码路径 `data/external/fraehr2024/` + `lsg/fraehr*.py`。 |
| 2 | **Fraehr et al. 2022** WRR DOI `10.1029/2022WR032248` | **方法**：LF 水动力 + EOF 降维 + Sparse GP 系数映射 = LSG。我们 Global/Zonal LSG-Max 的可执行骨架。 |
| 3 | **Tan et al. 2025** HESS DOI `10.5194/hess-29-3833-2025` | **Novelty 边界**：regionalized LSG training 已用于局地流速降维误差 → 禁止声称 “first zonal/regionalized LSG”。对照我们「equal-B zoning + EOI falsification」贡献定位。 |

### 次要（引用/边界，非本包全文）

| 论文 | 角色 |
|---|---|
| Wang et al. 2025 IJDRS `10.1007/s13753-025-00642-5` | REOF–SGP / 局部化 EOF prior；非 equal-B zoning 测试 |
| Lu et al. 2025 JOH `10.1016/j.jhydrol.2025.132949` | JOH 写作范式：固定 LSG → 改内部设计 |
| Fraehr et al. 2023 WRR / Nature Water | LSG 发展谱系 / intro 定位 |
| Wang, Wang & Nathan WRR `10.1029/2025WR042481` | 设计问题式 WRR 模板；**不是**我们的 Brisbane 实验 |
| Figshare `10.26188/24312658` | 基准数据（非论文，但与 #1 绑定） |

---

## 2. 各篇阅读条目

### 2.1 Fraehr et al. (2024) — 主要模仿对象

- **书目：** Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2024). Assessment of surrogate models for flood inundation: The physics-guided LSG model vs. state-of-the-art machine learning models. *Water Research*, 252, 121202.  
- **DOI：** https://doi.org/10.1016/j.watres.2024.121202 （Crossref/HEAD 已核验；PII `S0043135424001027`；CC BY 4.0）  
- **获取状态：** **全文**（2026-08-17 用户手工提供；此前为「仅摘要」，因 ScienceDirect 验证码阻塞）  
- **本地路径：**  
  - PDF: `paper/refs/pdf/1-s2.0-S0043135424001027-main.pdf`（15 页，Elsevier OA，CC BY）  
  - MD（全文）: `paper/refs/md/fraehr2024_watres_lsg_fulltext.md`  
  - MD（旧摘要条目，保留备查）: `paper/refs/md/fraehr2024_watres_lsg.md`  
- **实测章节结构（`paper/refs/_outline.py`）：** 1 Introduction → 2 Surrogate models for comparison（2.1 选型标准；2.2.1–2.2.5 五个模型）→ 3 Evaluation（3.1.1 flood extent / 3.1.2 peak water depth / 3.1.3 depth hydrographs；3.2 training and validation）→ 4 Case studies（4.1 Carlisle / 4.2 Chowilla / 4.3 Burnett / 4.4 application）→ 5 Results（5.1 extent → 5.2 peak depth → 5.3 hydrographs → 5.4 computational efficiency → 5.5 extrapolation → 5.6 summary）→ 6 Discussion → 7 Conclusion → Open research。**共 11 图 + 3 表。**  
- **这篇给了我们什么（3–6 句）：**  
  1. 公开三案例基准与「LSG vs 其他代理」比较框架。  
  2. 全局 LSG（粗网格 LF → EOF → Sparse GP）作为我们 Global 臂的对标。  
  3. 水深/范围误差、训练内外事件、多站点并列的结果展示习惯。  
  4. 我们保留官方两折等协议作 sensitivity，而主声称改为 equal-B LOOCV。  
  5. 写作骨架：问题 → 方法模块 → 多案例 → 诚实边界（我们再加 zoning/EOI/stage-swap）。

### 2.2 Fraehr et al. (2022) — 方法起源

- **书目：** Fraehr, N., Wang, Q. J., Wu, W., & Nathan, R. (2022). Upskilling low-fidelity hydrodynamic models of flood inundation through spatial analysis and Gaussian Process learning. *Water Resources Research*, 58, e2022WR032248.  
- **DOI：** https://doi.org/10.1029/2022WR032248 （OA，CC BY-NC；已核验）  
- **获取状态：** **全文**  
- **本地路径：**  
  - PDF: `paper/refs/pdf/fraehr2022_wrr_lsg.pdf`  
  - MD: `paper/refs/md/fraehr2022_wrr_lsg.md`  
- **这篇给了我们什么：**  
  1. LSG 三件套定义与 flowchart 式方法叙述。  
  2. EOF 空间模态 + GP 系数映射的数学/算法表述。  
  3. Chowilla 类平坦漫滩上的 LF→HF 提升证据（我们把 Chowilla 标为 LSG 适用性边界）。  
  4. 图表类型：工作流示意、淹没图、误差曲线/散点。  
  5. 我们的 novelty 不在「发明 LSG」，而在 **equal retained-mode budget 下的分区诊断**。

### 2.3 Tan et al. (2025) — Novelty boundary

- **书目：** Tan, Z., Xu, D., Taraphdar, S., Ma, J., Bisht, G., & Leung, L. R. (2025). An efficient hybrid downscaling framework to estimate high-resolution river hydrodynamics. *Hydrology and Earth System Sciences*, 29, 3833–3852.  
- **DOI：** https://doi.org/10.5194/hess-29-3833-2025 （Copernicus OA，CC BY；已核验）  
- **获取状态：** **全文**  
- **本地路径：**  
  - PDF: `paper/refs/pdf/tan2025_hess_regionalized_lsg.pdf`  
  - MD: `paper/refs/md/tan2025_hess_regionalized_lsg.md`  
- **这篇给了我们什么：**  
  1. 在 LSG 框架上做高分辨率水深/流速降尺度。  
  2. **Regionalized training** 降低流速侧降维误差 → 直接封死 “first regionalized LSG”。  
  3. 误差分解（降维 vs 映射）分析方式，可对照我们的 stage-swap / EOI。  
  4. 案例图、误差统计、加速比等结果呈现。  
  5. 我们声称必须改成：equal-B 下 zoning 是否改变 depth skill + 机制诊断，而非「首次分区」。

---

## 3. 对照表：参考论文范式 → 我们新论文

| 参考论文的图/表/分析范式 | 我们新论文对应处 |
|---|---|
| Fraehr 2024：三案例（Carlisle / Chowilla / Burnett）并列评估 | Table 1 案例角色；Table 2 / Fig. 4 three-case RMSE |
| Fraehr 2024：LSG 相对其他代理 / LF 的精度对比 | Global vs Rule/KMeans；另报 LF-only；MaxWD R² 仅作 sanity（Fig. 16） |
| Fraehr 2024：淹没深度/范围误差与事件内外泛化 | §3.1–3.2 预算曲线 + LOOCV；官方两折作 sensitivity |
| Fraehr 2022：LSG 工作流（LF→EOF→GP→重建） | Fig. 1 workflow；§2.2 Global/Zoned LSG-Max |
| Fraehr 2022：空间场 / 模态示意 | Fig. 2 zone maps（我们的分区版） |
| Fraehr 家族：全局单一 EOF 域 | 我们的 **Global** 臂；质疑其在紧预算下是否 performance-neutral |
| Tan 2025：regionalized LSG 训练降低局地 DR 误差 | Intro/Discussion **novelty boundary**；禁止 first-claim |
| Tan 2025：误差源分解（降维 vs 其他） | §2.4 / §3.4 EOI、pure-EOF oracle、stage-swap（GG/ZZ/GZ/ZG） |
| （我们新增，非模仿）equal total mode budget B | Fig. 3 / 9 / 13 预算扫描；B=8 MISMATCH 诚实披露 |
| （我们新增）面积加权指标 + train-only zoning | §2.3；area-weighted RMSE/MAE/bias/CSI |
| （我们新增）条件性结论 + Burnett/Chowilla 边界 | Discussion Q1–Q3；Conclusions 条件句 |

**结构模仿判定：** 章节骨架与多案例诚实边界 ≈ **Fraehr 2024**；方法模块措辞 ≈ **Fraehr 2022**；贡献边界校准 ≈ **Tan 2025**。JOH 句式可再参照 Lu 2025（次要，未收入本包全文）。

---

## 3b. 篇幅实测对标（2026-08-17，首次可直接测量）

在拿到 Fraehr 2024 全文之前，逐节篇幅目标是由 Fraehr 2022 / Tan 2025 **外推估计**的。现已可直接测量模板本身（脚本 `paper/refs/_length_benchmark.py`，只统计正文散文，排除参考文献、图表题注与前后事项）：

| 模板节（Fraehr 2024） | 实测词数 | 我们对应节 | 当前词数 |
|---|---:|---|---:|
| 1 Introduction | 1049 | 1. Introduction | 489 |
| 2 Surrogate models + 3 Evaluation + 4 Case studies | 1828 + 1231 + 1106 = **4165** | 2. Methods | 1223 |
| 5 Results | 2055 | 3. Results | 884 |
| 6 Discussion | 1900 | 4. Discussion | 848 |
| 7 Conclusion | 430 | 5. Conclusions | 149 |
| **正文合计（1–7）** | **9599** | **正文合计** | **3593** |

**比值：0.37×。** 说明：模板把「模型族对比 + 评价指标 + 三案例描述」写成三个独立大节（合计 4165 词），而我们压缩进单一 Methods；模板 Results 覆盖 extent / peak depth / hydrographs / 效率 / 外推五类产出，我们聚焦 LSG-Max 深度误差。因此 **1:1 复制 9599 词并不合适**（此前顾问轮次 R7 也判定不必追 13–15k）；但 Introduction、Results、Discussion 三节确有实质扩写空间，且扩写必须来自已有真实证据，不得灌水。

---

## 4. 下载与转换记录

### 4.1 成功

| shortname | 来源 | 命令/工具 |
|---|---|---|
| `tan2025_hess_regionalized_lsg` | Copernicus OA PDF | `curl -L` → `https://hess.copernicus.org/articles/29/3833/2025/hess-29-3833-2025.pdf` |
| `fraehr2022_wrr_lsg` | Melbourne Minerva OA bitstream（CC BY-NC） | `curl -L` → Minerva `.../bitstreams/716f4e5b-.../retrieve`（Wiley pdfdirect 曾返回非 PDF） |

**转换：**

```text
D:\miniforge3\envs\hydromodel\python.exe -m pip install pymupdf
D:\miniforge3\envs\hydromodel\python.exe paper\refs\_pdf_to_md.py
```

工具：**PyMuPDF (`fitz`) 1.28/1.29**，文本层抽取（非 OCR）。

### 4.1b 用户手工提供（2026-08-17）

自动化此前无法合法取得的文件，由用户在普通浏览器下载后放入 `paper/refs/pdf/`。身份逐一核实（PDF 文本层标题 + DOI），未凭文件名假设：

| 文件名 | 实际是哪篇 | DOI（PDF 内文确认） | 页数 |
|---|---|---|---:|
| `1-s2.0-S0043135424001027-main.pdf` | **Fraehr et al. 2024** *Water Research* 252, 121202 | `10.1016/j.watres.2024.121202` | 15 |
| `Water Resources Research - 2023 - Fraehr - Development of a Fast and Accurate Hybrid Model for Floodplain Inundation.pdf` | **Fraehr et al. 2023a** *WRR* 59, e2022WR033836 | `10.1029/2022WR033836` | 22 |
| `1-s2.0-S0301479724035564-main.pdf` | **Fraehr et al.** Generation and selection of training events for surrogate flood inundation models, *J. Environ. Manage.* **373 (2025) 123570** | `10.1016/j.jenvman.2024.123570` | 15 |

> 第三份此前**不在**我们参考清单内，与手稿现有引文均不重复；它讨论「有限高保真预算下如何生成/挑选训练事件」，与我们 Limitations 中「Burnett 30 事件抽取、74 事件未全用」直接相关，可作为后续扩写的**真实文献支撑**（是否入正文 bib 待定，不得为凑引用而加）。

### 4.2 未获取

| shortname | 原因 |
|---|---|
| — | **无。** `fraehr2024_watres_lsg` 此前因 ScienceDirect 机器人验证码未取得（自动化未绕过，符合硬约束），已于 2026-08-17 由用户手工提供全文，阻塞解除。 |

### 4.3 DOI 核验（非伪引）

| DOI | 核验 |
|---|---|
| `10.1029/2022WR032248` | Unpaywall OA + Minerva PDF 标题匹配 Fraehr 2022 |
| `10.1016/j.watres.2024.121202` | Crossref title/PII/CC BY；PubMed 38290237；Semantic Scholar isOpenAccess；**2026-08-17 追加：用户提供的 PDF 内文首页标题/DOI/卷期页均匹配** |
| `10.5194/hess-29-3833-2025` | Copernicus 正式页 + PDF 内文标题匹配 Tan 2025 |
| `10.1029/2022WR033836` | **2026-08-21 起用**：PDF 内文确认 `e2022WR033836`、标题 “Development of a Fast and Accurate Hybrid Model for Floodplain Inundation Simulations”；与手稿 Ref#2（Fraehr 2023a）一致 |
| `10.1016/j.jenvman.2024.123570` | PDF 内文确认期刊 *Journal of Environmental Management* **373 (2025) 123570**，Accepted 30 Nov 2024 / Available online 6 Dec 2024。**注意年份陷阱：** DOI 串含 `2024`，正式卷期为 **2025**；若入 bib 须写 2025 卷 373 |

---

## 5. 建议阅读顺序

1. 本文件 §0–§3b（定位、对照表、篇幅实测）  
2. `md/fraehr2022_wrr_lsg.md`（或 PDF）— 弄清 LSG 方法  
3. `md/fraehr2024_watres_lsg_fulltext.md` — **主要模仿对象全文**，对照三案例呈现与 5.1–5.6 结果组织  
4. `md/tan2025_hess_regionalized_lsg.md` — 核对我们 novelty 边界是否写紧  
5. `md/fraehr2023a_wrr_floodplain.md`、`md/fraehr2025_jem_training_events.md` — 谱系与训练事件论证（按需）  
6. 对照 `paper/manuscript.md`（当前 v1.0-rc，图 1–21 连续编号）与上表

---

## 6. 路径索引

```text
paper/refs/REFERENCE_READING_PACK.md          ← 本索引
paper/refs/citation_audit.md                  ← 既有 DOI 审计
paper/refs/_pdf_to_md.py                      ← PDF→MD 转换脚本（PyMuPDF）
paper/refs/_identify_pdfs.py                  ← 身份核实（标题/DOI，不信文件名）
paper/refs/_outline.py                        ← 章节大纲 + 图表题注抽取
paper/refs/_length_benchmark.py               ← 逐节篇幅实测对标

paper/refs/pdf/fraehr2022_wrr_lsg.pdf                     ← 全文（方法起源）
paper/refs/pdf/tan2025_hess_regionalized_lsg.pdf          ← 全文（novelty 边界）
paper/refs/pdf/1-s2.0-S0043135424001027-main.pdf          ← 全文（Fraehr 2024，主要模仿对象）
paper/refs/pdf/Water Resources Research - 2023 - Fraehr - ....pdf   ← 全文（Fraehr 2023a）
paper/refs/pdf/1-s2.0-S0301479724035564-main.pdf          ← 全文（JEM 训练事件，新增）

paper/refs/md/fraehr2022_wrr_lsg.md
paper/refs/md/tan2025_hess_regionalized_lsg.md
paper/refs/md/fraehr2024_watres_lsg_fulltext.md           ← 全文转换（新）
paper/refs/md/fraehr2024_watres_lsg.md                    ← 旧摘要条目（保留备查）
paper/refs/md/fraehr2023a_wrr_floodplain.md               ← 全文转换（新）
paper/refs/md/fraehr2025_jem_training_events.md           ← 全文转换（新）
```
