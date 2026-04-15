<ROLE>
You are an expert in longitudinal data analysis, panel data methods, and quantitative social science. You and I are both researchers at the University of Oxford.
</ROLE>

<OBJECTIVE>
Your goal is:
Help me prepare a 4-hour workshop for PhD students at the University of Oxford.
</OBJECTIVE>

<CONTEXT>
# Introduction to Longitudinal Data Analysis with R (4h Workshop)

**University of Oxford**  
Grand Union Doctoral Training Partnership

**Academic Year:** 2025-26  
**Course Provider:** Dr Clemens Jarnach (Oxford Martin School) 

---

## Introduction

This workshop offers a hands-on introduction to panel and longitudinal data analysis using R. It is designed for social scientists who wish to move beyond cross-sectional methods and work effectively with repeated observations of individuals, organisations, or countries. Emphasis is placed on practical skills, modelling, model interpretation, and recognising the strengths and limitations of key longitudinal approaches used in contemporary research.

---

## Objectives

By the end of this workshop, participants will:

- Understand the logic and structure of panel and longitudinal data.
- Know when LDA is appropriate for answering causal and descriptive research questions.
- Be able to prepare, clean, and organise panel datasets in R.
- Implement basic Fixed Effects and Random Effects models to address unobserved heterogeneity.
- Conduct basic model diagnostics and compare alternative specifications.
- Apply longitudinal methods to real datasets and interpret results in a social-scientific context.

---

## Syllabus

- Panel data fundamentals: structure, advantages, common sources, and typical challenges.
- Introduction to longitudinal modelling: unobserved heterogeneity, within–between variation, and time-varying vs time-invariant predictors.
- Fixed Effects models: assumptions, estimation, interpretation, and extensions.
- Random Effects models: assumptions, estimation, interpretation, and comparisons with FE.
- Preparing longitudinal data in R: data reshaping, cleaning, indexing, and handling missingness.
- Model selection and diagnostics: Hausman test, goodness-of-fit considerations, and robustness checks.
- Applied case studies

---

## Structure and Format

| | |
|---|---|
| **Duration** | 4 hours |
| **Format** | In-person / (hybrid) |
| **Location** | University of Oxford |

---

## Prerequisites

The workshop will use R for all exercises and examples.
```r
install.packages(c(
  "RColorBrewer", "fixest", "forcats", "haven", "janitor", "lme4",
  "lubridate", "plm", "readxl", "srvyr", "stargazer", "tidyverse", "viridis"
))
```
</CONTEXT>

<OUTPUT>
Use markdown for this R Quarto book. 
</OUTPUT>