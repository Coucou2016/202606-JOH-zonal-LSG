# nature-skills usage note (this workline)

## Availability (no reinstall)

Skills already present under `C:\Users\Administrator\.codex\skills\`:

- `nature-writing` v1.2.1 — used for drafting
- `nature-polishing` v6.3.1 — used for Abstract / Intro / Discussion thesis pass
- `nature-figure` — **not used** (figure workline owns `outputs/figures`)
- `nature-shared` — loaded via writing/polishing manifest `always_load`

**Decision:** Do not pull/reinstall skills for this session; environment intact; use in place.

## Detected axes

### nature-writing (draft)

- `task`: manuscript
- `paper_type`: methods
- `section`: title, abstract, intro, method, experiments/results, discussion, conclusion
- `language`: en
- `journal`: generic (JOH / WRR methods paradigm; not flagship Nature)

### nature-polishing (this round)

- `paper_type`: methods
- `section`: abstract + intro + discussion (+ light results/methods wording)
- `language`: en
- `journal`: generic

Loaded: polishing `manifest.yaml` → `always_load` stance/failure-modes/output-format + methods playbook + abstract/intro/discussion fragments.

## Workflow applied

1. nature-writing: one-sentence argument + `paper/framework.md` + `paper/manuscript.md` evidence-outward.
2. ChatGPT web-search review (2026-08-16) → local DOI verify (Tan HESS; Wang REOF–SGP 10.1007/s13753-025-00642-5).
3. nature-polishing: narrowed top-line wording (“performance-neutral representation choice”), three RQs, Discussion spine Q1–Q3 reframe, Methods fairness/EOI/stage-swap wording.
4. Regenerated `paper/manuscript.html` / `.pdf` via `scripts/98_paper_html.py`.

## Out of scope this pass

- Full SI rewriting
- gpflow/SGPR re-run
- Brisbane case
