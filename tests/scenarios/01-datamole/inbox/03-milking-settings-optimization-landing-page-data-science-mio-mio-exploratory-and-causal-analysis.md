---
title: MIO exploratory and causal analysis
space: MSO (Milking Settings Optimization)
breadcrumbs:
  - Milking Settings Optimization Landing Page
  - Data Science
  - MIO
author: Jiří Vošmik
last_modified: '2025-11-24'
---

This document contains the sources and the results of the milking interval analysis conducted in 2024, which was used to evaluate the domain knowledge, assess the usage of interval settings in the field and to define the MIO (milking interval optimization) project.

# Analysis goals

There are several topics of interests, each with several questions to be answered:

- Current access settings on the farms & Effects of global milk access change on the farms
- Effects of milk access transition on the animals
- Visit optimizer behavior

## Glossary

| **Term** | **Notation** | **Descriptiopn** |
| --- | --- | --- |
| *milking interval* | *I* | Time since the last successful milking visit |
| *{Min/Max}. number of milkings* | *N\_{min/max}* | Milk access table setting |
| *{Min/Max} milking interval* | *I\_{min/max}* | Minimum/maximum milking interval, based on *{Min/Max}. number of milkings* |
| *Optimum exp. yield per milking* | *Y\_exp* | Milk access table setting |
|  |  |  |
|  |  |  |

## Current access settings on the farms

Exploratory data analysis

The basic way to control milk access is through milk access table:

The milk access table specifies rules which are used to decide whether the animal is allowed into the milking robot or not based on time since the last visit. The *{Min/Max}. number of milkings* define the minimum and maximum milking intervals (in hours) respectively:

- *I\_max* = (24/*N\_min)\*0.9*
- *I\_min* = (24/*N\_max)\*0.9*

The rules for refusing the animal are as follows:

- The animal is always refused when *I <= I\_min*
- The animal is never refused when *I >= I\_max*
- The animal is is sometimes refused when *I > I\_min* and *I < I\_max*

  - The animal is let in if the astronaut expects it has reached at least 90% of *Y\_exp*

The recommended way to set *Optimum exp. yield per milking* is average herd daily milk yield / 3

### Research questions

- How many farms haven’t changed access settings in the past year?
- How many farms have *Y\_exp* set to average herd daily milk yield / 3?
- How do the farms with *Y\_exp* set to average herd daily milk yield / 3 perform?

  - Fit of the expected milk yield at the start?
  - How does the number of milkings, refusals, failures and milking interval change when milk yield fluctuates?
  - How regular is the interval over time?

    - Coefficient of variation of milking interval
- How do the top and bottom 10% of the animals (in terms of daily milk yield) perform?

  - In terms of number of milkings, refusals, failures, milking interval and milk production rates
- Estimate the effect size of changes of different milk access setting parameters on performance

  - Parameters

    - Maximum number of milkings
    - Minimum number of milkings
    - Optimal milk yield
  - In terms of number of milkings, refusals, failures, milking interval and milk production rates

### Data sources

- AADP - edw.animal\_settings\_ani\_dim

  - All records with `valid_until` > 2022-01-01
- AADP edw.animal\_daily\_fact

  - All records since 1.1.2022

### Report

[Available on Google Drive](https://drive.google.com/file/d/1vvDkoJ1y9l0pzDjPxOFX7ci-0fMM88RV/view?usp=drive_link)

## Effects of milk access transition on the animals

Animals have different milk access during early, mid and late lactation, with sudden changes between the stages. It is hypothesized that these sudden transitions introduce some problems as the animals have to adapt to the new schedule.

### Research Questions

- What is the effect on transitions, 7 days before vs 7 days after?

  - In terms of milk yield, number of milkings, refusals, failures, interval regularity
- How big are the changes?

  - In optimal milk yield
  - In maximum number of milkings
  - In minimum number of milkings

### Data Sources

- AADP - edw.animal\_settings\_ani\_dim

  - All records with `valid_until` > 2022-01-01
- AADP edw.animal\_daily\_fact

  - All records since 1.1.2022

### Report

[Available on Google Drive](https://drive.google.com/file/d/15EyQY1nlUzAvGBh0oDiWa_y-4dUHhHsO/view?usp=drive_link)

## Visit optimizer behavior

Currently, there is already a model optimizing milking intervals on some farms called *visit optimizer*. The SMEs suspect that the *visit optimizer* does not work very well and that it makes a lot of sudden changes.

### Research Questions

- How often does the *visit optimizer* make changes larger than 20% of the current milking interval?
- What is the effect of such changes on interval regularity?

### Data Sources

- AADP - animal daily fact - amo\_\* columns

### Report

[Available on Google Drive](https://drive.google.com/file/d/1WO5aSOxCBvJ9JAaCclNMGJwQE1r-49wt/view?usp=drive_link)

# Sources

The attached documents (related to MIO, provided by SMEs) contain the following:

- The questions
- The milk access table explanation
- Milk access knowledge update is a presentation from FMS international with Denmark and US about how to set milk access table
- T4C visit optimizer explains a bit about the visit optimizer.
