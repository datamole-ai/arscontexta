---
title: MIO
space: MSO (Milking Settings Optimization)
breadcrumbs:
  - Milking Settings Optimization Landing Page
  - Data Science
author: Petr Svarny
last_modified: '2025-11-04'
---

Finding the optimal interval between milkings.

Horizon has it implemented via 3 values:

1. Maximal number of milkings per day
2. Minimal number of milkings per day
3. Minimal expected milk yield

These numbers are set for the animals at the beginning, mid and late in lactation, i.e. 9 total values for the herd/group.

We would like to maximize milk yield and minimize boxtime and bimodality.
As we would adjust the number of milkings, we have to use a fixed interval (e.g., day).

Currently the settings are available in `aadp_prd_007.edw.animal_settings_hie_dim` as:

- `mas{lactation_phase}start_milkings_min`
- `mas{lactation_phase}start_milkings_max`
- `mas{lactation_phase}start_milk_yield_min`
