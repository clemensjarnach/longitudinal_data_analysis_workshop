# =============================================================================
# Simulated Panel Dataset for Workshop Use
# Introduction to Longitudinal Data Analysis with R
# University of Oxford — Grand Union DTP
# Author: Dr Clemens Jarnach
# =============================================================================
#
# This script generates a balanced panel dataset of fictional individuals
# tracked over multiple time periods. The outcome variable (wage) is
# determined by a data-generating process that includes:
#   - Time-invariant individual characteristics (ability, gender, sector)
#   - Time-varying covariates (education, experience, union membership)
#   - An unobserved individual fixed effect (correlated with education)
#   - Year fixed effects
#   - Idiosyncratic error
#
# This structure makes the dataset suitable for demonstrating:
#   - Pooled OLS (biased due to omitted individual effects)
#   - Fixed Effects (within) estimation
#   - Random Effects estimation
#   - Hausman test for model selection
# =============================================================================

library(tidyverse)

set.seed(42)

# -----------------------------------------------------------------------------
# 1. Design parameters
# -----------------------------------------------------------------------------

n_individuals <- 200   # number of unique individuals
n_periods     <- 8     # number of time periods (years: 2016-2023)
years         <- 2016:(2016 + n_periods - 1)

# -----------------------------------------------------------------------------
# 2. Individual-level (time-invariant) characteristics
# -----------------------------------------------------------------------------

individuals <- tibble(
  id     = 1:n_individuals,
  gender = sample(c("Male", "Female"), n_individuals, replace = TRUE,
                  prob = c(0.52, 0.48)),
  sector = sample(c("Public", "Private"), n_individuals, replace = TRUE,
                  prob = c(0.35, 0.65)),

  # Unobserved individual ability (the "fixed effect" we want to control for)
  # Correlated with education to create omitted-variable bias in pooled OLS
  ability = rnorm(n_individuals, mean = 0, sd = 1)
)

# -----------------------------------------------------------------------------
# 3. Expand to panel structure (one row per individual × year)
# -----------------------------------------------------------------------------

panel <- individuals |>
  crossing(year = years) |>                          # balanced panel
  arrange(id, year) |>
  group_by(id) |>
  mutate(
    period = row_number(),                            # within-person time index

    # --- Time-varying: education (years of schooling, increases slowly) ---
    # Baseline education drawn partly from ability (the endogeneity source)
    educ_base  = round(12 + 2 * ability + rnorm(1, sd = 1.5)),
    educ_base  = pmax(8, pmin(educ_base, 20)),        # clamp to [8, 20]
    education  = pmin(educ_base + floor(period / 3), 20),

    # --- Time-varying: labour market experience (years) ---
    exp_base   = pmax(0, round(runif(1, min = 0, max = 15))),
    experience = exp_base + period - 1,

    # --- Time-varying: union membership (binary, sticky) ---
    union_base = rbinom(1, 1, prob = 0.25),
    union      = as.integer(pmin(1, union_base +
                   rbinom(n(), 1, prob = 0.05))),      # small chance of joining

    # --- Year fixed effect (common macro shock) ---
    year_fe    = (year - 2016) * 0.02,                # modest upward trend

    # --- Log wage (outcome) ---
    log_wage = 1.5 +
               0.08  * education  +                   # returns to schooling
               0.04  * experience +                   # returns to experience
              -0.002 * experience^2 +                 # diminishing returns
               0.12  * union +                        # union wage premium
              -0.10  * (gender == "Female") +          # raw gender gap
               0.08  * (sector == "Private") +         # sector premium
               0.30  * ability +                      # unobserved heterogeneity
               year_fe +
               rnorm(n(), mean = 0, sd = 0.15),       # idiosyncratic error

    wage = round(exp(log_wage) * 1000) / 1000         # wage in £'000s/month
  ) |>
  ungroup() |>
  select(id, year, period, gender, sector, education, experience,
         union, ability, wage, log_wage)

# -----------------------------------------------------------------------------
# 4. Introduce a small amount of random missingness (realistic)
# -----------------------------------------------------------------------------

set.seed(99)
missing_idx        <- sample(nrow(panel), size = round(nrow(panel) * 0.03))
panel$wage[missing_idx]    <- NA
panel$log_wage[missing_idx] <- NA

# -----------------------------------------------------------------------------
# 5. Quick summary checks
# -----------------------------------------------------------------------------

cat("=== Panel structure ===\n")
cat(sprintf("Individuals : %d\n", n_distinct(panel$id)))
cat(sprintf("Time periods: %d (%d–%d)\n",
            n_distinct(panel$year), min(panel$year), max(panel$year)))
cat(sprintf("Total rows  : %d\n", nrow(panel)))
cat(sprintf("Missing wage: %d (%.1f%%)\n",
            sum(is.na(panel$wage)),
            mean(is.na(panel$wage)) * 100))

cat("\n=== Outcome variable (wage, £'000s/month) ===\n")
print(summary(panel$wage))

cat("\n=== First 12 rows ===\n")
print(head(panel, 12))

# -----------------------------------------------------------------------------
# 6. Save to CSV
# -----------------------------------------------------------------------------

write_csv(panel, "files/panel_data.csv")
cat("\nData saved to files/panel_data.csv\n")
