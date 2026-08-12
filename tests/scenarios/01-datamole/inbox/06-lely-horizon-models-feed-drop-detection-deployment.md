---
title: 'FDD: Deployment'
space: LCHM (Lely - Horizon Models)
breadcrumbs:
  - Lely - Horizon Models Landing Page
  - Other Projects
  - Feed Drop Detection
author: Adam Skluzáček
editor: Ondřej Novák
last_modified: '2024-05-30'
---

- [Overview](#FDD:Deployment-Overview)
- [Job parameters](#FDD:Deployment-Jobparameters)
- [feed-drop-data-downloader](#FDD:Deployment-feed-drop-data-downloader)
  - [Filtering and preprocessing](#FDD:Deployment-Filteringandpreprocessing)
- [feed-drop-detector](#FDD:Deployment-feed-drop-detector)
- [feed-drop-advice-sender](#FDD:Deployment-feed-drop-advice-sender)
- [feed-drop-monitoring](#FDD:Deployment-feed-drop-monitoring)

## Overview

The Feed drop detection model is deployed in Databricks `dbr-prototypers-dev` group as a Databricks Job/Workflow which consists of 4 consecutive notebook tasks.

## Job parameters

Configuration of the Job is set through Job parameters which include infrastructure parameters such as secret names as well as feed drop detection model configuration. Brief description of the job parameters is given in the table below.

| **Key** | **Description** |
| --- | --- |
| `ADVICE_SENDER_OUTPUT_TABLE` | Path to the Delta table of the output of the `feed-drop-advice-sender` task. |
| `ADVICE_TABLES_KEYVAULT` | Name of the Azure Key Vault with connection strings for advice tables. |
| `ADVICE_TRANSLATIONS_PRD_CS_KEY` | Name of the secret with the connection string to the Production advice translations Azure table. |
| `ADVICE_TRANSLATIONS_UAT_CS_KEY` | Name of the secret with the connection string to the UAT advice translations Azure table. |
| `ADVICES_PRD_CS_KEY` | Name of the secret with the connection string to the Production advices Azure table. |
| `ADVICES_UAT_CS_KEY` | Name of the secret with the connection string to the UAT advices Azure table. |
| `DAYS_TO_DOWNLOAD` | Number of days into the past to be downloaded. Default = `90`. |
| `DAYS_TO_RESEND_ADVICE` | Number of days for the detected drop to be sent again. Default = `100`. |
| `DEPLOYMENT_FARMS` | Dictionary of farms on which the feed drop detector is running. Dictionary keys are the `farm_license_key`s and values denote farm’s environment (`"prd"` or `"uat"`). |
| `MODEL_ANIMAL_LACTATIONS_WITH_DROP_RATIO` | Ratio of animal lactations required to have a detected feed drop in order to classify group feed drop. For more details see [FDD: Group feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Group-feed-drop-detection.md). Default = `0.25`. |
| `MODEL_FEATURE` | Name of the feature used in the feed drop detection. |
| `MODEL_FEATURE_THRESHOLD` | Threshold value of the `MODEL_FEATURE` below (or equal) which the rows are classified as feed drop. For more details see [FDD: Cow feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Cow-feed-drop-detection.md) and [FDD: Group feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Group-feed-drop-detection.md). Default = `-0.12`. |
| `MODEL_INPUT_TABLE` | Path to the Delta table of the input of the `feed-drop-detector` task. |
| `MODEL_MIN_DROP_ANIMAL_LACTATIONS` | Absolute number of animal lactations required to have a detected feed drop in order to classify group feed drop. For more details see [FDD: Group feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Group-feed-drop-detection.md). Default = `3`. |
| `MODEL_MIN_DROP_DAYS` | Minimum number of consecutive days in lactation with `MODEL_FEATURE` below the `MODEL_FEATURE_THRESHOLD` for the period to be classified as feed drop. Default = `3`. |
| `MODEL_OUTPUT_TABLE` | Path to the Delta table of the otuput of the `feed-drop-detector` task. |
| `SEND_ADVICES` | Debugging flag that controls whether the actual advices are being sent to Horizon. **Given the nature of the model it is recommended to first run the model without sending the advices when adding new farms.** |

## feed-drop-data-downloader

Downloads and prepares data for the feed drop detector and saves them to the `MODEL_INPUT_TABLE` Delta table. The resulting table contains the following columns (for more details about the columns see the previous sections):

| `_MODEL_INPUT_TABLE` | |
| --- | --- |
| **Column** | **Source** |
| `farm_dim_bk` | `animal_daily_fact` |
| `animal_dim_bk` | `animal_daily_fact` |
| `group_dim_bk` | `group_dim` and `animal_to_group_bridge` |
| `lactation_number` | `animal_daily_fact` |
| `days_in_lactation` | `animal_daily_fact` |
| `feed_allowance_kg` | `animal_daily_fact` |
| `feed_allowance_kg_ma_10_days_diff` | Computed from `feed_allowance_kg` |
| `bin` | Computed from `days_in_lactation` |

### Filtering and preprocessing

- Data from the last 90 days (`DAYS_TO_DOWNLOAD`)
- `days_in_lactation` between 30 and 200
- Valid group data (`validity_from` >= `datetime_wall` <= `validity_to`)
- No duplicated `days_in_lactation` per animal lactation
- No animals for which the group changed in the data
- Fill days missing in `animal_daily_fact`, `feed_allowance_kg` is linearly interpolated

## feed-drop-detector

Implementation of the Feed drop detector as defined in [FDD: Group feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Group-feed-drop-detection.md). The detected drops are written to the `MODEL_OUTPUT_TABLE` Delta table.

*Additionally for each detected feed drop, animal with the steepest drop is identified due to the advices being sent in a fall-back format described in the section below.*

## feed-drop-advice-sender

The detected drops are shown to farmers in Horizon as generic advices (described in [Generic Advices](Lely-Horizon-Models-Landing-Page - Active-Projects - GenericBeta-Advice-Widget - GenericBeta-Advices.md)).

The Horizon’s generic advices currently don’t support sending advices for any entity other than animal. Until this functionality is added, the advices are sent in a fall-back format, where the group drop is sent for a specific animal (animal with the steepest drop from the given group).

For the advice to show, it must be written into a corresponding Azure table (translations must also be written). The job accesses the Azure tables through connection strings that are stored as secrets. The Azure Key Vault as well as the secret’s names are passed as Job parameters `ADVICE_TABLES_KEYVAULT`, `ADVICE_TRANSLATIONS_PRD_CS_KEY`, `ADVICE_TRANSLATIONS_UAT_CS_KEY`, `ADVICES_PRD_CS_KEY` and `ADVICES_UAT_CS_KEY` respectively. Advice phrasings and translations are also defined and written in this task.

The generic advices also requires some additional fields such as farm license key or t4c animal id that are downloaded and joined with rows from the `MODEL_OUTPUT_TABLE` Delta table. The group name and days in lactation range of the detected drop are added to the advice as advice measures as the advice body doesn’t support dynamic evaluation. Each advice is sent if the advice for the same group wasn’t sent in the last `DAYS_TO_RESEND_ADVICE` days and the `SEND_ADVICES` flag is enabled. Whether the drop was or wasn’t sent as an advice is saved to the `ADVICE_SENDER_OUTPUT_TABLE` Delta table.

## feed-drop-monitoring

Simple monitoring that shows the number of farms, groups and animal lactations processed by the job for the last 10 runs. Each detected group drop is also visualised. Databricks jobs persist tasks' notebook outputs per run which allows to see the metrics for any past runs.
