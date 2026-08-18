# R22 — Final polish (3 minor text/provenance fixes)

Repos: https://github.com/Coucou2016/202606-JOH-zonal-LSG (branch `master`)

This round closes the three remaining issues you raised in R21. All are
one-line wording/provenance fixes; no numbers, figures, or analyses changed.

## Fixes applied

### 1. R21 brief canonical pack pointer (provenance)
The R21 brief's canonical audit-pack URL pointed to a stale commit. Repointed to
`6462f90`:

- `https://raw.githubusercontent.com/Coucou2016/202606-JOH-zonal-LSG/6462f90/paper/chatgpt/figure_code_audit_pack.md`

### 2. Abstract — official two-fold wording (Abstract consistency)
Removed the "statistically significant" claim, which over-claimed a descriptive
bootstrap. The abstract now reads:

> The corresponding official two-fold sensitivity gave a much smaller
> difference, and its descriptive event-level bootstrap interval included zero.

### 3. "all available events" → "all events in the analysis extract" (scope precision)
"all available events" could be misread against the Burnett 74-event archive
(when only a 30-event max-surface extract is used). Replaced everywhere in the
live manuscript and the audit pack:

- Methods §2.4 (pooled EOI descriptor sentence)
- Results §4.4 (pooled EOI scope sentence)
- Figure 15 caption (audit pack included)
- `figure_code_audit_pack.md` Figure 15 caption

## Verification
- Data audit: **PASS 54/54, FAIL 0**
- Manuscript HTML/PDF regenerated; both Chinese research reports regenerated.
- Backed up manuscript as `paper/manuscript_v1.0rc_R22after_20260819_0505.md`.

## What to review (final confirmation)
1. Confirm the Abstract no longer uses "statistically significant" for the
   official two-fold result.
2. Confirm "all events in the analysis extract" is used consistently in §2.4,
   §4.4, and the Figure 15 caption (manuscript + audit pack).
3. Any remaining wording/logic issues you would flag before this is considered
   manuscript-final? If none, this closes the review loop.
