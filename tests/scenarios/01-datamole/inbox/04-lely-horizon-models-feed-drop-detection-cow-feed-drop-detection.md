---
title: 'FDD: Cow feed drop detection'
space: LCHM (Lely - Horizon Models)
breadcrumbs:
  - Lely - Horizon Models Landing Page
  - Other Projects
  - Feed Drop Detection
author: Adam Skluzáček
editor: Ondřej Novák
last_modified: '2024-05-30'
---

- [Baseline feed drop detection model](#FDD:Cowfeeddropdetection-Baselinefeeddropdetectionmodel)
- [Feed intake](#FDD:Cowfeeddropdetection-Feedintake)
- [Feed allowance](#FDD:Cowfeeddropdetection-Feedallowance)
  - [Feed tables](#FDD:Cowfeeddropdetection-Feedtables)
  - [Example feed allowances](#FDD:Cowfeeddropdetection-Examplefeedallowances)
- [Feed drop detection model](#FDD:Cowfeeddropdetection-Feeddropdetectionmodel)

# Baseline feed drop detection model

**Defined by our SME**: Cow has a feed drop if the difference of her 10 days moving average feed intake is below -0.04 [kg].

*Note that we only consider the amount of feed a cow receives in the Astronaut during milking and not the feed received at feed fences for which we don’t have the data available.*

# Feed intake

The `feed_intake_concentrate_kg` column from the `animal_daily_fact` AADP table represents the amount (kilograms) of concentrate fed to the cow in the Astronaut during milking for each day in lactation. The initial exploration showed an unintuitive behaviour that cow’s feed intake can significantly exceed its feed allowance. This is explained in the [Horizon knowledge base](https://horizon-help.lely.com/?page_id=420) as the cows follow a credit system where if they intake less feed than is their feed allowance at a given day, the remaining amount of “feed credit” is added to the next day feed allowance.

Looking at 0.95 and 0.05 quantiles of feed intake and allowance differences we can see that the feed intake can range from +1 to -2.5 kg compared to the feed allowance.

The amount of noise in the feed intake is a problem when applying the baseline cow drop detection model as shown in the example below.

**Due to the noisiness of the feed intake we have decided with the SMEs to use the feed allowance in the drop detection model instead of the feed intake.**

# Feed allowance

The `feed_allowance_kg` column from the `animal_daily_fact` AADP table represents the amount (kilograms) of concentrate that should be fed to the cow in Astronaut during milking over the course of each day in lactation. As mentioned in the section above cow’s intake at a particular day can exceed its feed allowance due to the credit system but over the whole lactation the cow’s intake should be lower or equal to the allowance.

## Feed tables

Feed tables are manually configured tables by the farmers, usually in cooperation with a FMS expert and 3rd parrt companies that specialize in cow feed, based on which the feed allowances are calculated for each cow individually. The feed tables are set on the group level (or herd level alternatively). The feed allowance usually start from a fixed amount of concentrate that is same for all the cows in the group. After a certain number of days in lactation the feed allowance calculation should switch to being computed based on individual cow’s milk production. While the switch to milk production based feed allowance should happen around 60th day in lactation (according to our SMEs), however, we haven’t seen any clear pattern in the data.

Apart from the feed tables the feed allowance can be influenced by additional rules and corrections such as maximum amount of increase or decrease of cow’s feed allowance between two days in lactation. We refer to the combination of all settings that influences the feed allowance calculation as **feed settings** which includes feed tables, additional rules and corrections and any further logic. For more details about the feeding, refer to the [Horizon documentation](https://documentation-horizon.ldf.lely.cloud/feeding/individual_feeding/).

***Note that the feed tables are not available in the AADP as they are stored only locally on the farms.***

## Example feed allowances

The plots below show examples farms' feed allowances per animal lactation colored by their corresponding group.

# Feed drop detection model

The feed drop detection model uses the difference of 10 days moving average feed allowance as feature. The day in lactation is considered to have a drop if the feature drops below a certain threshold (finding the exact threshold value is described in the [Group feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Group-feed-drop-detection.md) section). Due to observed high number of short drops lasting only couple of days which are not of interest to us, there is an additional condition that requires the drops to happen for at least 4 consecutive days (periods of 3 or less consecutive days with a feature value below the threshold are therefore not considered as drop).
