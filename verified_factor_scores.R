# Verified correction layer for the one-factor wait-time exercise in
# Assignment16.Rmd. The original coursework is intentionally left unchanged.

args <- commandArgs(trailingOnly = TRUE)
output_dir <- if (length(args)) args[[1L]] else "research-output"

load("standby.RData")
rides <- c("PeterPan", "SpaceMtn", "HauntedMansion", "SplashMtn", "WinniePooh")
cleaned <- data[complete.cases(data[, rides]) & data$HR >= 10 & data$HR <= 20, ]
Y <- as.matrix(cleaned[, rides])
J <- ncol(Y)

negative_log_likelihood <- function(parameters) {
  beta <- parameters[seq_len(J)]
  lambda <- parameters[J + seq_len(J)]
  sigma <- parameters[2L * J + seq_len(J)]
  covariance <- tcrossprod(lambda) + diag(sigma^2)
  -sum(mvtnorm::dmvnorm(Y, mean = beta, sigma = covariance, log = TRUE))
}

fit <- optim(
  par = c(rep(10, J), rep(1, J), rep(1, J)),
  fn = negative_log_likelihood,
  method = "BFGS",
  hessian = TRUE,
  control = list(maxit = 1000)
)
stopifnot(fit$convergence == 0L, is.finite(fit$value))

beta <- fit$par[seq_len(J)]
lambda <- fit$par[J + seq_len(J)]
sigma_sd <- abs(fit$par[2L * J + seq_len(J)])
names(beta) <- rides
names(lambda) <- rides
names(sigma_sd) <- rides

# A one-factor model is invariant to flipping both the factor and all loadings.
# Canonicalize the sign so receipts and rankings are reproducible.
if (sum(lambda) < 0) lambda <- -lambda

specific_covariance <- diag(sigma_sd^2)
precision_weight <- solve(specific_covariance, lambda)
posterior_denominator <- 1 + drop(crossprod(lambda, precision_weight))
centered <- sweep(Y, 2L, beta, FUN = "-")

# E[theta_i | Y_i] under theta ~ N(0, 1). This replaces the unweighted
# rowMeans((Y - beta) / lambda) shortcut used in the archived assignment.
posterior_score <- drop(centered %*% precision_weight / posterior_denominator)
naive_score <- rowMeans(sweep(centered, 2L, lambda, FUN = "/"))

top_index <- which.max(posterior_score)
specific_index <- which(cleaned$date == "01/19/2016" & cleaned$HR == 11)
stopifnot(length(specific_index) == 1L)

one_off_specific <- drop(
  crossprod(lambda, solve(specific_covariance, Y[specific_index, ] - beta)) /
    posterior_denominator
)

# Regression checks validate the fitted workflow, not causal validity or an
# external benchmark. Tolerances allow small BLAS differences across runners.
stopifnot(
  nrow(cleaned) == 8998L,
  all(is.finite(posterior_score)),
  abs(posterior_score[specific_index] - one_off_specific) < 1e-10,
  cleaned$date[top_index] == "12/31/2017",
  cleaned$HR[top_index] == 14,
  abs(posterior_score[top_index] - 6.324) < 0.02,
  abs(naive_score[top_index] - posterior_score[top_index]) > 0.5
)

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

summary_values <- c(
  rows = nrow(cleaned),
  convergence = fit$convergence,
  top_date = cleaned$date[top_index],
  top_hour = cleaned$HR[top_index],
  posterior_score = sprintf("%.6f", posterior_score[top_index]),
  naive_score = sprintf("%.6f", naive_score[top_index]),
  specific_score = sprintf("%.6f", posterior_score[specific_index])
)
for (ride in rides) {
  summary_values[paste0("loading_", ride)] <- sprintf("%.6f", lambda[ride])
  summary_values[paste0("wait_", ride)] <- cleaned[top_index, ride]
}

receipt <- data.frame(
  key = names(summary_values),
  value = unname(summary_values),
  stringsAsFactors = FALSE
)
write.csv(receipt, file.path(output_dir, "factor-score-receipt.csv"), row.names = FALSE)

cat(sprintf("Verified %d observations\n", nrow(cleaned)))
cat(sprintf(
  "Posterior top: %s %02d:00, score %.6f (naive %.6f)\n",
  cleaned$date[top_index], cleaned$HR[top_index],
  posterior_score[top_index], naive_score[top_index]
))
cat("Scope: committed historical queue data; statistical reproduction only\n")
