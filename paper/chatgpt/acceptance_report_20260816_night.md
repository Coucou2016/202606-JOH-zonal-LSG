# 验收报告（第十九节）— 2026-08-16 夜

**仓库：** https://github.com/Coucou2016/202606-JOH-zonal-LSG  
**顾问对话：** https://chatgpt.com/c/6a812977-6814-83ea-9a9d-f27c1dbd8a8f  
**本地执行者：** Cursor  
**Python：** `D:\miniforge3\envs\hydromodel\python.exe`

## 1. Git / 推送

- 本轮开始：11 个未提交文件（相对 `f692bf1`）。
- 先推送 v0.3 一致性：`679d6b7` → `origin/master`。
- 本轮结束后再 push v0.4 多轮落地（见最终 commit）。
- **未建 PR、未部署、未改全局 git config、未 hard reset、未强推。**

## 2. ChatGPT 正式迭代（≥5 轮，同一对话）

| 轮次 | 主题 | 链接 | 主要 ADOPT | 主要 REJECT |
|---|---|---|---|---|
| R1 | GitHub 读取证明 + 成熟度 | 同对话 | Burnett 列语义、EOI across-cases、Abstract stage-swap=Carlisle、capacity 软化 | master 仍为 v0.2（本地 urllib 否决）；first zonal LSG |
| R2 | Abstract/Intro/novelty | 同对话 | 可粘贴 gap/novelty 改写；NONE first-claim | first zonal / first REOF–GP |
| R3 | Methods vs `lsg/*.py` | 同对话 | Rule hotspot；CLEAN_PASS 范围收窄；EOI/ZGG/oracle 公式 | 顾问称 eoi.py 仍写 zoning justified（本地否决） |
| R4 | Track B 数据真实性 | 同对话 | Table2 RMSE 方向；B=8 nominal/actual；Burnett 双协议标签 | 无 headline 数字造假 |
| R5 | Results–Discussion–Conclusion + Limitations | 同对话 | Q2/Q3/Limitations/Conclusions 润色 | 唯一机制归因；first zonal |
| R6 | 图表交叉引用 + DOI 终检 | 同对话 | 维持 fig/table/DOI PASS；继续禁止 first-claim | 以公开旧 raw 指未推送差异（本地已修） |

详细记录：`paper/chatgpt/collaboration_log.md`

## 3. 数据真实性审计结论

以 `outputs/evaluation/**` JSON 为准：

- Carlisle B=4：0.1464 → 0.0964；9/9；mean Δ 0.0821；CI [0.0155, 0.1987]（`loocv_bootstrap_ci.json`, rng=42）
- Official 2-fold：significant=false
- Burnett 30-fold：不优；Chowilla：LSG RMSE > LF-only
- EOI 0.057/0.116/0.957；stage-swap ≈ 0.180/0.098/0.098/0.101
- MaxWD 0.988 vs 0.990：sanity only
- **未发现需改写的 headline 数字抄错**；修正的是协议/方向措辞。

## 4. 测试与制品

| 检查 | 结果 |
|---|---|
| `pytest -q` | **39 passed**（11 warnings） |
| `scripts/98_paper_html.py` | HTML 自包含：data-uri=16；external http src=0 |
| DOI 抽查 | Tan/Wang/Fraehr/WRR HEAD 200 → `paper/refs/citation_audit.md` |
| 交付 | `paper/manuscript.md` v0.4；`manuscript.html/.pdf`；`完整研究报告.*`；`outputs/evaluation/**`；SciencePlots 图 |

## 5. 仍【待补充】

- gpflow/SGPR backend sensitivity；Brisbane；真实分区 LSG-TS
- 全折/多案例自动化泄漏审计
- area-weighted pure-EOF oracle sensitivity
- Methods/SI 完整超参表；Chowilla MD5/datum

## 6. 协议遵守

禁止附件上传、禁止发送密钥、禁止创建 PR/部署 — **均遵守**。
