# Reproducibility boundaries

Run from the repository root; workstation-specific dataset paths now resolve by original basename. Original studies require their original datasets; no fabricated replacement is supplied.

## Missing input files

No uncommitted inputs found by the local-path check.

## Execution

Use R with packages: AER, car, clubSandwich, dplyr, fixest, lavaan, lmtest, mvtnorm, plm, sandwich. Render coursework with `Rscript -e 'rmarkdown::render("FILE.Rmd")'`. An isolated R 4.3.3 runtime now verifies five original assignments (44 chunks); run_assignment.R executes their code without document rendering. The remaining assignment/package and remote-data paths are not verified. The Greene TableF4-1 URL requires live access.
