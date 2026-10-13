# advanced_econometrics_I
## Execute checked coursework code

```bash
Rscript -e 'install.packages(c("knitr","dplyr","mvtnorm"), repos="https://cloud.r-project.org")'
Rscript run_assignment.R Assignment3.rmd
Rscript run_assignment.R Assignment5.Rmd
Rscript run_assignment.R Assignment9.Rmd
Rscript run_assignment.R Exam1_DataAnalysis.Rmd
Rscript run_assignment.R Assignment16.Rmd
```

The runner executes original fenced R code and saves plots/execution text without requiring Pandoc or HTML document rendering. It stops on errors and uses committed datasets. Five assignments (44 code chunks) were verified end to end; other assignments require their specific packages or the original external Greene CSV. Execution is not a peer review of causal assumptions or interpretation.
