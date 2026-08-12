---
title: 'FDD: Group feed drop detection'
space: LCHM (Lely - Horizon Models)
breadcrumbs:
  - Lely - Horizon Models Landing Page
  - Other Projects
  - Feed Drop Detection
author: Adam Skluzáček
editor: Ondřej Novák
last_modified: '2024-05-30'
---

- [Group feed drop detection](#FDD:Groupfeeddropdetection-Groupfeeddropdetection)
  - [Threshold selection](#FDD:Groupfeeddropdetection-Thresholdselection)
  - [Binning vs Rolling window](#FDD:Groupfeeddropdetection-BinningvsRollingwindow)
  - [Are the classifications group specific or farm specific?](#FDD:Groupfeeddropdetection-Aretheclassificationsgroupspecificorfarmspecific?)
  - [Model sensitivity to threshold and ratio of animal lactations with a drop](#FDD:Groupfeeddropdetection-Modelsensitivitytothresholdandratioofanimallactationswithadrop)
  - [Example of model classifications with potential advices](#FDD:Groupfeeddropdetection-Exampleofmodelclassificationswithpotentialadvices)

# Group feed drop detection

While detecting feed drops for a cow is valuable, it might be caused by an individual cow’s issue such as sickness. The goal of this project is to detect suboptimal feed settings for a group of animals rather than treating individual cow issues.

We assume that if more than a certain ratio of animal lactations in a group have a drop at similar time (in terms of days in lactation) then the whole group has suboptimal feed settings. *Note that we refer to the animal lactations rather than animals since one cow can be in the same group for multiple lactations.* **The baseline value for this ratio was set by our SMEs to 25% and the similar time range is enforced by binning the days in lactation into 20 day bins.** The cow feed drop detection described in [FDD: Cow feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Cow-feed-drop-detection.md) is therefore applied to all animal lactations in a given group and if the ratio of animal lactations with at least one drop is at least 25% (and at least 2 animal lactations in absolute numbers) in at least one 20 days bin, the group is classified with suboptimal feed settings.

## Threshold selection

In order to select the threshold for [FDD: Cow feed drop detection](Lely-Horizon-Models-Landing-Page - Other-Projects - Feed-Drop-Detection - FDD-Cow-feed-drop-detection.md) model, our SMEs have defined **the expected ratio of groups with suboptimal feed settings to be 30%.** With this ratio we can find the threshold value for which the number of groups classified with suboptimal feed settings is closest to the 30%.

## Binning vs Rolling window

While binning the days in lactation into 20 days bins is a straightforward approach, we have also tested a group drop detection model with 20 days rolling window. The rolling window model classifies group with suboptimal feed settings when the ratio of animal lactations with a drop is at least 25% in **any** 20 consecutive days in lactation. The rolling window approach makes more sense in theory instead of static bins as drops could be close together in terms of days in lactation despite being put to different bins. However, after comparing the classifications the binning and rolling group drop detection models had different classifications for only about 3% of groups. These two approaches are therefore almost equivalent in performance and therefore we selected the binning approach at it has much simpler implementation.

## Are the classifications group specific or farm specific?

The group drop detection model is used the same on groups from all the farms. This creates a potential risk that all groups from the same farm will be classified the same. The pie chart below shows that out of 45% of farms with at least one group classified with suboptimal feed settings, 30% also have at least one group not classified with suboptimal feed settings. This shows that the group drop detection model truly works on a group level rather than farm level.

## Model sensitivity to threshold and ratio of animal lactations with a drop

The ratio of animal lactations with a drop for a group to be classified with suboptimal feed settings was set to 25% by our SMEs. The contour plot below explores the sensitivity of the model to this ratio by visualising the ratio of group classified with suboptimal feed settings per different threshold and ratio of animal lactations with a drop. The plot shows higher sensitivity to the threshold.

## Example of model classifications with potential advices

Plots below shows feed allowances per group colored by group’s classification (red for suboptimal feed settings, green otherwise), captions of the plots show the potential advices that would be sent to farmers.
