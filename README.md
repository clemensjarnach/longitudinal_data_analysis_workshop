# Longitudinal Data Analysis with R

A practical introduction to longitudinal and panel data analysis, from foundational theory to applied modelling in R. Developed for the [Grand Union DTP](https://www.granduniondtp.ac.uk) workshop at the University of Oxford, taught by [Dr Clemens Jarnach](https://clemensjarnach.github.io).

---

## Repository Structure

```
.
├── index.qmd                              # Introduction and workshop overview
│
├── 01_exercise_farm_panel_fe.qmd          # Chapter 1: Which Farmers Are More Productive?
├── 02_panel_data_and_fixed_effects.qmd    # Chapter 2: Panel Data Fundamentals and Fixed Effects
├── 03_r_fundamentals.qmd                  # Chapter 3: An R Refresher
├── 04_panel_data_in_r.qmd                 # Chapter 4: Working with Panel Data in R
├── 05_exercise_farm_panel_re.qmd          # Chapter 5: Fixed or Random — Which Model Fits?
│
├── feedback.qmd                           # Workshop feedback form
├── how_to_cite.qmd                        # Citation guidance
├── references.qmd                         # Bibliography page
├── appendix.qmd                           # Appendix
│
├── fig/                                   # Figures and animations
│   ├── NHK_Control.gif
│   └── NHK_FE.gif
│
├── files/                                 # Supplementary files
│   ├── longitudinal_data_analysis_workshop.pdf
│   └── panel_data.csv
│
├── slides/                                # Lecture slides
├── docs/                                  # Rendered HTML output (GitHub Pages)
├── _quarto.yml                            # Quarto book configuration
└── references.bib                         # Bibliography
```

---

## Getting Started

The workshop materials are written in [Quarto](https://quarto.org). To render the book locally:

1. Install [R](https://www.r-project.org) and [Quarto](https://quarto.org/docs/get-started/)
2. Install required R packages:
   ```r
   install.packages(c(
     "RColorBrewer", "fixest", "forcats", "haven", "janitor", "lme4",
     "lubridate", "plm", "readxl", "srvyr", "stargazer", "tidyverse", "viridis"
   ))
   ```
3. Clone the repository and open `longitudinal_data_analysis_with_R_workshop.Rproj` in RStudio
4. Run `quarto render` in the terminal to build the book into the `docs/` folder
