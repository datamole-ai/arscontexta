# Scenario 01 knowledge answer key

Use this file only after the candidate has answered every prompt under `questions/`.
Each question asks for one fact. The first three questions cover each source once. The
last three cover every pair of sources once.

| Question | Kind | Sources |
| --- | --- | --- |
| `01-single-source-mio-data-scientist.md` | Single-source | 01 |
| `02-single-source-herd-setting-count.md` | Single-source | 02 |
| `03-single-source-yield-threshold.md` | Single-source | 03 |
| `04-multi-source-shared-product.md` | Multi-source | 01 + 02 |
| `05-multi-source-team-member-and-author.md` | Multi-source | 01 + 03 |
| `06-multi-source-i-max-setting.md` | Multi-source | 02 + 03 |

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
