# Scenario 01 knowledge answer key

Use this file only after the candidate has answered every prompt under `questions/`.
Each question is one pass/fail check. Questions 01 through 03 cover the original sources
individually, and questions 04 through 06 cover every pair of original sources once.
Questions 07 through 12 require reasoning across the Feed Drop Detection sources.

| Question | Kind | Sources |
| --- | --- | --- |
| `01-single-source-mio-data-scientist.md` | Single-source | 01 |
| `02-single-source-herd-setting-count.md` | Single-source | 02 |
| `03-single-source-yield-threshold.md` | Single-source | 03 |
| `04-multi-source-shared-product.md` | Multi-source | 01 + 02 |
| `05-multi-source-team-member-and-author.md` | Multi-source | 01 + 03 |
| `06-multi-source-i-max-setting.md` | Multi-source | 02 + 03 |
| `07-multi-source-research-vs-deployment-minimum-count.md` | Multi-source | 05 + 06 |
| `08-multi-source-research-vs-deployment-duration.md` | Multi-source | 04 + 05 + 06 |
| `09-multi-source-intake-vs-allowance.md` | Multi-source | 04 + 05 |
| `10-multi-source-threshold-calibration.md` | Multi-source | 05 + 06 |
| `11-multi-source-group-advice-fallback.md` | Multi-source | 05 + 06 |
| `12-multi-source-binning-choice.md` | Multi-source | 05 + 06 |

## `01-single-source-mio-data-scientist.md`

Required fact:

- `Antonín Hruška`

Source evidence:

- `inbox/01-milking-settings-optimization-landing-page.md` lists Antonín Hruška as `Data Scientist (MIO)` in the Datamole team table.

## `02-single-source-herd-setting-count.md`

Required fact:

- `9` total values

Source evidence:

- `inbox/02-milking-settings-optimization-landing-page-data-science-mio.md` says Horizon uses three values at each of the beginning, middle, and end of lactation, for nine total values per herd or group.

## `03-single-source-yield-threshold.md`

Required fact:

- At least `90%` of `Y_exp`

Source evidence:

- `inbox/03-milking-settings-optimization-landing-page-data-science-mio-mio-exploratory-and-causal-analysis.md` says an animal between `I_min` and `I_max` is let in if the Astronaut expects at least 90% of `Y_exp`.

## `04-multi-source-shared-product.md`

Required fact:

- `Horizon`

Source evidence:

- `inbox/02-milking-settings-optimization-landing-page-data-science-mio.md` identifies Horizon as the system that implements MIO's nine values per herd or group.
- `inbox/01-milking-settings-optimization-landing-page.md` identifies Kimberlee Mesu as Lely's contact for integrating MSO into Horizon.

## `05-multi-source-team-member-and-author.md`

Required fact:

- `Jiří Vošmik`

Source evidence:

- `inbox/01-milking-settings-optimization-landing-page.md` lists Jiří Vošmik on the Datamole team as responsible for models.
- `inbox/03-milking-settings-optimization-landing-page-data-science-mio-mio-exploratory-and-causal-analysis.md` credits Jiří Vošmik as the analysis author.

## `06-multi-source-i-max-setting.md`

Required fact:

- Minimum number of milkings per day, denoted `N_min`

Source evidence:

- `inbox/02-milking-settings-optimization-landing-page-data-science-mio.md` lists the minimum number of milkings per day as one of Horizon's three values for each lactation phase.
- `inbox/03-milking-settings-optimization-landing-page-data-science-mio-mio-exploratory-and-causal-analysis.md` defines `I_max = (24 / N_min) * 0.9`, where `N_min` is the minimum number of milkings.

## `07-multi-source-research-vs-deployment-minimum-count.md`

Required fact:

- The group satisfies the research rule only. Two out of eight is `25%`, and the research rule accepts a minimum of two qualifying animal lactations, while the deployed default requires at least three.

Source evidence:

- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` classifies a group when at least 25% and at least two animal lactations have a drop in the same 20-day bin.
- `inbox/06-lely-horizon-models-feed-drop-detection-deployment.md` sets `MODEL_ANIMAL_LACTATIONS_WITH_DROP_RATIO` to `0.25` and `MODEL_MIN_DROP_ANIMAL_LACTATIONS` to `3` by default.

## `08-multi-source-research-vs-deployment-duration.md`

Required fact:

- The group satisfies the deployed defaults only. The research description requires at least four consecutive drop days, while deployment accepts three; `-0.13` is at or below the deployed `-0.12` threshold, and three out of twelve satisfies both deployed group minimums.

Source evidence:

- `inbox/04-lely-horizon-models-feed-drop-detection-cow-feed-drop-detection.md` requires a cow-level drop to last at least four consecutive days.
- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` uses a 25% ratio within a 20-day bin.
- `inbox/06-lely-horizon-models-feed-drop-detection-deployment.md` defaults to a feature threshold of `-0.12`, three consecutive days, a 25% ratio, and at least three animal lactations.

## `09-multi-source-intake-vs-allowance.md`

Required fact:

- No. The final cow-level model detects drops in feed allowance, not actual feed intake, and the group model aggregates those cow-level allowance drops.

Source evidence:

- `inbox/04-lely-horizon-models-feed-drop-detection-cow-feed-drop-detection.md` explains that the credit system makes daily feed intake noisy, so the model switched to feed allowance.
- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` applies the cow feed-drop detector to the animal lactations before aggregating them into a group classification.

## `10-multi-source-threshold-calibration.md`

Required fact:

- The calibration target was `30%` of groups classified with suboptimal feed settings, and the deployed feature threshold is `-0.12`.

Source evidence:

- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` says the subject-matter experts expected 30% of groups to have suboptimal settings and that this share was used to select the cow-level threshold.
- `inbox/06-lely-horizon-models-feed-drop-detection-deployment.md` sets the default `MODEL_FEATURE_THRESHOLD` to `-0.12`.

## `11-multi-source-group-advice-fallback.md`

Required fact:

- No. The classification concerns a group-level feed-setting problem. Horizon's generic advice supports only animal entities, so the pipeline attaches the group warning to the animal with the steepest drop as a delivery fallback.

Source evidence:

- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` distinguishes group-level suboptimal settings from individual cow issues.
- `inbox/06-lely-horizon-models-feed-drop-detection-deployment.md` says generic advice cannot target a group, so the job uses the animal with the steepest drop.

## `12-multi-source-binning-choice.md`

Required fact:

- Deployment uses fixed 20-day bins. Fixed bins and rolling windows disagreed for only about `3%` of groups, so the project chose the simpler fixed-bin implementation.

Source evidence:

- `inbox/05-lely-horizon-models-feed-drop-detection-group-feed-drop-detection.md` reports about 3% classification disagreement and selects fixed 20-day bins because they are simpler.
- `inbox/06-lely-horizon-models-feed-drop-detection-deployment.md` includes a computed `bin` in the model input and implements the documented group detector.
