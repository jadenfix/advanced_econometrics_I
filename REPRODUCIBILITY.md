# Reproducibility boundaries

Run from the repository root; workstation-specific dataset paths now resolve by original basename. Original studies require their original datasets; no fabricated replacement is supplied.

## Missing input files

No uncommitted inputs found by the local-path check.

## Execution

Use R with packages: AER, car, clubSandwich, dplyr, fixest, lavaan, lmtest, mvtnorm, plm, sandwich. Render coursework with `Rscript -e 'rmarkdown::render("FILE.Rmd")'`. An isolated R 4.3.3 runtime now verifies five original assignments (44 chunks); run_assignment.R executes their code without document rendering. The remaining assignment/package and remote-data paths are not verified. The Greene TableF4-1 URL requires live access.

`verified_factor_scores.R` is a separate correction layer for the archived
one-factor exercise. It fits the same model to `standby.RData`, canonicalizes the
otherwise unidentified factor-loading sign, and computes model-implied
posterior scores with the fitted specific variances. Its receipt and demo are
source-pinned and checked in CI. This evidence is limited to reproduction on the
committed historical data; it is not a causal, forecasting, or external-validity
claim.
