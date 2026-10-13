# Resolve original data relative to this runner, including Rscript's --file form.
full_args <- commandArgs()
file_arg <- grep('^--file=',full_args,value=TRUE)
if (length(file_arg)) {
  setwd(dirname(normalizePath(sub('^--file=','',file_arg[[1L]]))))
} else if ('-f' %in% full_args) {
  setwd(dirname(normalizePath(full_args[[match('-f',full_args)+1L]])))
}
# Run the actual R Markdown research code without Pandoc or document rendering.
args <- commandArgs(trailingOnly=TRUE)
if (!length(args)) stop('Usage: Rscript run_assignment.R Assignment9.Rmd')
file <- args[[1]]
if (!file.exists(file) || !grepl('\\.rmd$', file, ignore.case=TRUE)) stop('Choose an existing R Markdown file')
lines <- readLines(file, warn=FALSE)
inside <- FALSE
chunk <- character()
blocks <- list()
for (line in lines) {
  if (!inside && grepl('^```\\{r', line)) {
    if (grepl('eval\\s*=\\s*FALSE', line)) stop('This runner does not execute eval=FALSE chunks')
    inside <- TRUE
    chunk <- character()
  } else if (inside && grepl('^```\\s*$', line)) {
    blocks[[length(blocks)+1L]] <- paste(chunk, collapse='\n')
    inside <- FALSE
  } else if (inside) chunk <- c(chunk,line)
}
if (inside) stop('Unclosed R code fence')
if (!length(blocks)) stop('No R code chunks found')
dir.create('research-output', showWarnings=FALSE)
pdf(file.path('research-output',paste0(basename(file),'-plots.pdf')))
set.seed(42)
for (i in seq_along(blocks)) {
  cat(sprintf('Executing %s: R chunk %d\n', file, i))
  expressions <- parse(text=blocks[[i]])
  for (expression in expressions) {
    value <- withVisible(eval(expression, envir=.GlobalEnv))
    if (value$visible) print(value$value)
  }
}
dev.off()
writeLines(c(paste('Source:',file),paste('Executed chunks:',length(blocks)),paste('R:',getRversion())),file.path('research-output',paste0(basename(file),'-execution.txt')))
